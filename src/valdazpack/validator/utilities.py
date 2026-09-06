import gzip
import re
import tempfile

from contextlib import contextmanager
from difflib import SequenceMatcher
from pathlib import Path
from typing import cast, BinaryIO, Generator, NamedTuple, Never

import numpy as np
import OpenImageIO as oiio

from fs.base import FS
from fs.errors import InvalidCharsInPath
from fs.info import Info
from fs.path import basename, combine, splitext

from .validationdata import ImageCache, ValidationData

OIIO_EXTENSION_LIST = oiio.get_string_attribute("extension_list")
oiio_format_extensions: dict[str, list[str]] = {}
for entry in OIIO_EXTENSION_LIST.split(";"):
	if ":" in entry:
		format, extensions = entry.split(":", 1)
		oiio_format_extensions[format.lower()] = ['.' + e.lower() for e in extensions.split(",")]

class Step(NamedTuple):
	"""Typing information for pyFilesystem2 Step"""

	path: str
	dirs: list[Info]
	files: list[Info]

alpha_numeric_regex = re.compile(r'[^0-9A-Za-z]')
def alpha_numeric(string: str) -> str:
	"""Remove all non alphanumeric characters from a string.

	Arguments:
		string (str): String to process.
	"""

	return alpha_numeric_regex.sub('', string)

def _looks_like_tangent_space_normal_map(image_buf: oiio.ImageBuf, pd: bool = False) -> tuple[bool, dict[str, bool | tuple[bool, bool | float]]]:
	"""Return whether OpenImageIO ImageBuf object contains pixel data that looks like a tangent-space normal map.

	This is a weak heuristic that samples pixel data and applies multiple filters and checks to
	evaluate whether an image resembles a tangent-space normal map. The function filters out
	invalid pixels (transparent, black, white, and low-blue), then checks for three valid
	patterns: flat neutral maps, textured maps with neutral base, or smooth gradients with
	coherent blue-dominant directionality.

	Applies statistical filters, vector normalization checks, Z-reconstruction tests,
	and channel correlation metrics to evaluate whether an image encodes tangent-space normal vectors.

	Arguments:
		image_buf (oiio.ImageBuf): OpenImageIO ImageBuf object containing the image data.
		pd (bool): If True, print debugging statistics for each validation check.

	Returns:
		bool: True if the image appears to be a tangent-space normal map, False otherwise.
	"""

	SAMPLE_LIMIT = 50000
	MIN_SAMPLES = 100

	# -------------------------------------------------------------
	# Heuristic Threshold Constants
	# -------------------------------------------------------------
	# Global Color & Grayscale Limits
	MAX_MONOCHROME_CHROMA = 0.05            # Max chroma (max(RGB) - min(RGB)) for a pixel to be considered grayscale
	MAX_MONOCHROME_FRACTION = 0.90          # Max fraction of grayscale pixels allowed before rejection
	MIN_BLUE_THRESHOLD = 0.3                # Minimum blue channel pixel value for valid sample inclusion
	MIN_MEAN_BLUE = 0.70                    # Baseline minimum mean blue channel across the sampled map
	STEEP_SLOPE_BLUE_REDUCTION = 0.10       # Reduction in MIN_MEAN_BLUE allowed for steep textured normal maps

	# Tangent-Space Slope Bounds (X^2 + Y^2 <= 1.0)
	MIN_VALID_XY_MAG_FRACTION = 0.90        # Minimum fraction of pixels satisfying X^2 + Y^2 <= 1.0
	EXPANDED_RANGE_MIN_XY_FRACTION = 0.99   # Minimum XY compliance fraction required to unlock expanded tolerances
	XY_BOUND_EPSILON = 1.001                # Float rounding tolerance for X^2 + Y^2 <= 1.0 check

	# 3D Vector Magnitude Thresholds (||V|| ≈ 1.0)
	MIN_UNIT_MAG_MEAN = 0.90                # Baseline minimum mean ||V|| vector magnitude
	MAX_UNIT_MAG_MEAN = 1.10                # Baseline maximum mean ||V|| vector magnitude
	EXPANDED_UNIT_MAG_MEAN = 0.05           # Magnitude offset applied when XY compliance is high (0.85 - 1.15)
	MAX_UNIT_MAG_STD = 0.18                 # Baseline maximum ||V|| magnitude dispersion (standard deviation)
	EXPANDED_UNIT_MAG_STD = 0.04            # Dispersion offset applied when Z-reconstruction is highly accurate
	STABLE_MAG_STD_THRESHOLD = 0.10         # ||V|| std threshold required to unlock expanded Z-reconstruction error

	# Z-Channel Reconstruction & Vector Direction Thresholds
	MAX_Z_RECONSTRUCTION_ERROR = 0.18       # Baseline max mean error |Z_actual - sqrt(1 - X^2 - Y^2)|
	EXPANDED_Z_RECONSTRUCTION_ERROR = 0.04  # Reconstruction error offset applied for high-compliance textures
	ACCURATE_Z_RECON_THRESHOLD = 0.08       # Reconstruction error threshold required to unlock expanded magnitude std
	STEEP_SLOPE_MAX_Z_RECON_ERROR = 0.10    # Reconstruction error threshold required to confirm steep slope maps
	MIN_POSITIVE_Z_FRACTION = 0.90          # Minimum fraction of vectors pointing out from surface (Z > 0)

	# Structural Pattern Matching Thresholds
	MAX_MEAN_XY_OFFSET = 0.15               # Max distance of average (R, G) from neutral (0.5, 0.5)
	MAX_NEUTRAL_XY_OFFSET = 0.20            # Max per-pixel distance from neutral (0.5, 0.5) to count as near-neutral
	MIN_XY_VARIANCE = 0.08                  # Min standard deviation of XY magnitude to qualify as textured
	MIN_NEUTRAL_COMPONENT_FRACTION = 0.20   # Min fraction of near-neutral pixels for textured maps
	MIN_FLAT_NEUTRAL_FRACTION = 0.80        # Min fraction of near-neutral pixels for flat maps

	# Neutral Reference Vector Constants
	NEUTRAL_NORMAL = np.array([0.5, 0.5, 1.0], dtype=np.float32)
	NEUTRAL_NORMAL_TOLERANCE = 0.02         # Absolute RGB tolerance for identifying flat neutral normal vectors

	# -------------------------------------------------------------
	# Data Extraction & Normalization
	# -------------------------------------------------------------
	pixels = image_buf.get_pixels()
	if pixels is None or pixels.size == 0 or pixels.shape[-1] < 3:
		return False, { 'insufficient_data': True }

	flat = pixels.reshape(-1, pixels.shape[-1])
	if flat.shape[0] > SAMPLE_LIMIT:
		indices = np.linspace(0, flat.shape[0] - 1, SAMPLE_LIMIT, dtype=np.int64)
		sample = flat[indices]
	else:
		sample = flat

	if sample.shape[0] < MIN_SAMPLES:
		return False, { 'insufficient_data': True }

	if np.issubdtype(pixels.dtype, np.integer):
		max_val = np.iinfo(pixels.dtype).max
		sample = sample.astype(np.float32) / float(max_val)
	else:
		sample = sample.astype(np.float32)

	# Filter invalid / dead pixels
	valid = np.ones(sample.shape[0], dtype=bool)
	if sample.shape[1] >= 4:
		valid &= sample[:, 3] > 0.0
	valid &= ~np.all(sample[:, :3] == 1.0, axis=1)
	valid &= ~np.all(sample[:, :3] == 0.0, axis=1)
	valid &= sample[:, 2] > MIN_BLUE_THRESHOLD
	sample = sample[valid]

	if sample.shape[0] < MIN_SAMPLES:
		return False, { 'insufficient_data': True }

	sample = sample[:, :3]

	# Early exit for flat single-color images
	if np.all(np.ptp(sample, axis=0) == 0):
		is_neutral = bool(np.allclose(sample[0], NEUTRAL_NORMAL, atol=NEUTRAL_NORMAL_TOLERANCE))
		return is_neutral, { 'single_color': True }

	# Convert normalized RGB [0, 1] to tangent-space vector [-1, 1]
	vectors = sample * 2.0 - 1.0

	# -------------------------------------------------------------
	# Phase 1: Basic Color & Global Summary Statistics
	# -------------------------------------------------------------
	mean_r, mean_g, mean_b = np.mean(sample, axis=0)
	mean_xy_offset = float(np.hypot(mean_r - NEUTRAL_NORMAL[0], mean_g - NEUTRAL_NORMAL[1]))
	positive_z_fraction = float(np.mean(vectors[:, 2] > 0.0))

	pixel_chroma = np.ptp(sample, axis=1)
	monochrome_fraction = float(np.mean(pixel_chroma < MAX_MONOCHROME_CHROMA))
	not_grayscale = monochrome_fraction <= MAX_MONOCHROME_FRACTION

	# -------------------------------------------------------------
	# Phase 2: Physical Vector Validation (With Conditional Gates)
	# -------------------------------------------------------------
	xy_sq_mag = vectors[:, 0]**2 + vectors[:, 1]**2
	valid_xy_fraction = float(np.mean(xy_sq_mag <= XY_BOUND_EPSILON))

	xy_mags = np.sqrt(xy_sq_mag)
	vector_mags = np.sqrt(xy_sq_mag + vectors[:, 2]**2)
	mean_vec_mag = float(np.mean(vector_mags))
	std_vec_mag = float(np.std(vector_mags))

	z_expected = np.sqrt(np.maximum(0.0, 1.0 - xy_sq_mag))
	z_actual = vectors[:, 2]
	z_recon_error = float(np.mean(np.abs(z_actual - z_expected)))

	# Gate 1: Mean Vector Magnitude Bounds (Unlocked by High XY Compliance)
	uses_expanded_mag = valid_xy_fraction >= EXPANDED_RANGE_MIN_XY_FRACTION
	active_min_mag = MIN_UNIT_MAG_MEAN - (EXPANDED_UNIT_MAG_MEAN if uses_expanded_mag else 0.0)
	active_max_mag = MAX_UNIT_MAG_MEAN + (EXPANDED_UNIT_MAG_MEAN if uses_expanded_mag else 0.0)

	# Gate 2: Vector Magnitude Standard Deviation (Unlocked by Accurate Z-Reconstruction)
	uses_expanded_std = z_recon_error <= ACCURATE_Z_RECON_THRESHOLD
	active_max_std = MAX_UNIT_MAG_STD + (EXPANDED_UNIT_MAG_STD if uses_expanded_std else 0.0)

	# Gate 3: Z-Reconstruction Error (Unlocked by Low Std Dev OR High XY Compliance)
	uses_expanded_z_recon = (std_vec_mag <= STABLE_MAG_STD_THRESHOLD) or (valid_xy_fraction >= EXPANDED_RANGE_MIN_XY_FRACTION)
	active_max_z_recon = MAX_Z_RECONSTRUCTION_ERROR + (EXPANDED_Z_RECONSTRUCTION_ERROR if uses_expanded_z_recon else 0.0)

	unit_length_valid = (
		active_min_mag <= mean_vec_mag <= active_max_mag
		and std_vec_mag <= active_max_std
	)
	z_recon_valid = z_recon_error <= active_max_z_recon

	# -------------------------------------------------------------
	# Phase 3: Structural Pattern Matching (With Steep Slope Gate)
	# -------------------------------------------------------------
	neutral_xy = 0.5 * xy_mags
	xy_magnitude_std = float(np.std(neutral_xy))
	near_neutral_fraction = float(np.mean(neutral_xy <= MAX_NEUTRAL_XY_OFFSET))

	# Gate 4: Minimum Mean Blue (Unlocked by Verified Steep Slope Texture)
	is_steep_textured_map = xy_magnitude_std >= MIN_XY_VARIANCE and z_recon_error <= STEEP_SLOPE_MAX_Z_RECON_ERROR
	active_min_mean_blue = MIN_MEAN_BLUE - (STEEP_SLOPE_BLUE_REDUCTION if is_steep_textured_map else 0.0)
	mean_b_valid = mean_b >= active_min_mean_blue

	flat_neutral_map = near_neutral_fraction >= MIN_FLAT_NEUTRAL_FRACTION
	textured_map = xy_magnitude_std >= MIN_XY_VARIANCE and near_neutral_fraction >= MIN_NEUTRAL_COMPONENT_FRACTION
	continuous_gradient_map = mean_b_valid and mean_xy_offset <= MAX_MEAN_XY_OFFSET and positive_z_fraction >= MIN_POSITIVE_Z_FRACTION
	xy_structure_valid = flat_neutral_map or textured_map or continuous_gradient_map

	is_normal_map = bool(
		not_grayscale
		and valid_xy_fraction >= MIN_VALID_XY_MAG_FRACTION
		and unit_length_valid
		and z_recon_valid
		and positive_z_fraction >= MIN_POSITIVE_Z_FRACTION
		and xy_structure_valid
		and mean_b_valid
		and mean_xy_offset <= MAX_MEAN_XY_OFFSET
	)

	details: dict[str, bool | tuple[bool, bool | float]] = {
		'not_grayscale': bool(not_grayscale),
		'valid_xy_fraction': (bool(valid_xy_fraction >= MIN_VALID_XY_MAG_FRACTION), float(valid_xy_fraction)),
		'mean_vec_mag': (bool(active_min_mag <= mean_vec_mag <= active_max_mag), float(mean_vec_mag)),
		'std_vec_mag': (bool(std_vec_mag <= active_max_std), float(std_vec_mag)),
		'z_recon_error': (bool(z_recon_valid), float(z_recon_error)),
		'positive_z_fraction': (bool(positive_z_fraction >= MIN_POSITIVE_Z_FRACTION), float(positive_z_fraction)),
		'flat_neutral_map': bool(flat_neutral_map),
		'textured_map': bool(textured_map),
		'continuous_gradient_map': bool(continuous_gradient_map),
		'xy_structure_valid': bool(xy_structure_valid),
		'mean_b': (bool(mean_b_valid), float(mean_b)),
		'mean_xy_offset': (bool(mean_xy_offset <= MAX_MEAN_XY_OFFSET), float(mean_xy_offset)),
	}

	return is_normal_map, details

def thumbnailsFor(fs: FS, path: str) -> tuple[list[str], list[str]]:
	"""Get list of thumbnails (and tip images) for a file.

	Returns a tuple of existing files in
		[filename.png, basefilename.png]
		[basefilename.tip.png]

	Arguments:
		fs (fs.FS): PyFilesystem2 filesystem to use.
		path (str): File to get thumbnails from.
	"""

	thumbnails: list[str] = []
	tips: list[str] = []

	if fs.exists(file := path + '.png'):
		thumbnails.append(file)
	if fs.exists(file := splitext(path)[0] + '.png'):
		thumbnails.append(file)

	if fs.exists(file := splitext(path)[0] + '.tip.png'):
		tips.append(file)

	return (thumbnails, tips)

def checkDirectoryHasSelfAsChild(fs: FS, dir: str) -> bool:
	"""Check directory does not contain subdirectory with same name.

	Arguments:
		data (ValidationData): validation data of product to validate.
		dir (str): Root directory to check
	"""

	return fs.isdir(dir) and fs.isdir(combine(dir, basename(dir)))

def checkVendorDirsOnly(data: ValidationData, dir: str) -> list[str]:
	"""Check directory contains only subdirectories.

	Adds subdirectories to data.vendor_paths and returns a list of files in directory.

	Arguments:
		data (ValidationData): validation data of product to validate.
		dir (str): Root directory to check
	"""

	# Get case sensitive version of path from filesystem
	_, del_path = data.product_fs.delegate_path(dir)

	root_files: list[str] = []

	if data.product_fs.isdir(del_path):
		for entry in data.product_fs.scandir(del_path):
			if entry.is_file:
				root_files.append(entry.name)
			else:
				data.vendor_paths.setdefault(entry.name, set()).add(entry.make_path(del_path))

	return root_files

def checkImage(data: ValidationData, file: str) -> ImageCache | dict[Never, Never]:
	"""Check details of an image file.

	Caches details in data.cache['images'] and returns ImageCache if valid image.

	Arguments:
		data (ValidationData): validation data of product to validate.
		file (str): File path to image to check.
	"""

	LOSSY_FORMATS = {"jpeg", "heic", "dds"}
	LOSSY_COMPRESSIONS = {"lossy", "jpeg", "dwaa", "dwab", "b44", "b44a", "pxr24"}

	file = str(file).lstrip('/')

	if file in data.cache['images']:
		return data.cache['images'][file]

	if not data.filesystem.isfile(file):
		data.cache['images'][file] = {}
		return {}

	cleanup_temp: Path | None = None
	cache: ImageCache | dict[Never, Never] = {}

	try:
		try:
			img_sys_path = data.filesystem.getsyspath(file)
		except Exception:
			temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file).suffix)
			cleanup_temp = Path(temp_file.name)

			with temp_file:
				with data.filesystem.openbin(file) as f:
					while chunk := f.read(1024 * 1024):  # 1MB chunk streaming
						temp_file.write(chunk)

			img_sys_path = temp_file.name

		if (img := oiio.ImageBuf(img_sys_path)) and img.read():
			spec = img.spec()
			format_name = img.file_format_name.lower()
			compression = str(spec.get("compression", "")).lower()

			cache = cast(ImageCache, cache)
			cache['alpha'] = spec.alpha_channel >= 0
			cache['channels'] = spec.nchannels
			cache['bit_depth'] = spec.get_int_attribute("oiio:BitsPerSample", spec.format.size() * 8)
			cache['dimensions'] = (spec.width, spec.height)
			cache['format'] = img.file_format_name

			# Check for lossy compression
			cache['lossy'] = None
			if format_name in LOSSY_FORMATS or compression in LOSSY_COMPRESSIONS:
				cache['lossy'] = f"{format_name}{f' ({compression})' if compression else ''}"
			elif format_name == "webp" and not spec.get("webp:lossless", None):
				cache['lossy'] = "webp (lossy)"
			elif format_name in {"heif", "heic", "avif"}:
				quality = spec.get("heif:Quality", None) or spec.get("avif:Quality", None)
				if quality is not None:
					if int(quality) < 100:
						cache['lossy'] = f"{format_name} (quality={quality})"
				elif "lossless" not in compression:
					cache['lossy'] = f"{format_name} (lossy)"

			# Check for grayscale images
			cache['grayscale'] = False
			if cache['channels'] - cache['alpha'] == 1:
				cache['grayscale'] = True
			elif cache['channels'] - cache['alpha'] >= 3:
				if (pixels := img.get_pixels()) is not None:
					r, g, b = pixels[..., 0], pixels[..., 1], pixels[..., 2]
					if cache['lossy']:
						cache['grayscale'] = bool(np.allclose(r, g, atol=1e-3) and np.allclose(g, b, atol=1e-3))
					else:
						cache['grayscale'] = bool(np.array_equal(r, g) and np.array_equal(g, b))

			# Check for single color images
			if (stats := oiio.ImageBufAlgo.computePixelStats(img)) and stats.min == stats.max:
				dtype = np.dtype(str(spec.format))
				if np.issubdtype(dtype, np.integer):
					max_val = np.iinfo(dtype).max
					cache['single_color'] = [int(round(c * max_val)) for c in stats.min]
				else:
					cache['single_color'] = stats.min
			else:
				cache['single_color'] = []

			# Check normal map heuristic
			cache['looks_like_tangent_space_normal_map'], cache['looks_like_tangent_space_normal_map_details'] = _looks_like_tangent_space_normal_map(img)

		elif img.has_error:
			img.geterror()	# Discard error

	finally:
		if cleanup_temp and cleanup_temp.exists():
			cleanup_temp.unlink()

	data.cache['images'][file] = cache
	return cache

def checkImageDir(data: ValidationData, dir: str, preferred_suffixes: set[str]) -> tuple[list[str], list[str], list[str], dict[str, str]]:
	"""Check Image directory only contains supported images.

	Returns a tuple of (
		non image files: list[str],
		supported image files without preferred suffixes: list[str],
		unreadable image files (for filetypes supported by both DS and `PIL`): list[str],
		image files with incorrect file extensions and their detected MIME type: list[tuple[str, str]]
	)

	Arguments:
		data (ValidationData): validation data of product to validate.
		dir (str): Root directory to check.
		preferred_suffixes (set[str]): List of preferred file extensions.
	"""

	# TODO: I did not document where these extensions came from; find documentation (move to data/daz/image_file_extensions.txt?)
	DS_SUPPORTED_TEXTURE_SUFFIXES = set(['.bmp', '.bum', '.gif', '.jpeg', '.jpg', '.png', '.hdr', '.exr', '.tif', '.tiff', '.tga'])
	OIIO_UNSUPPORTED_IMAGE_SUFFIXES = set(['.dsi', '.svg'])

	non_image_files: list[str] = []
	atypical_image_files: list[str] = []
	unreadable_image_files: list[str] = []
	incorrect_image_suffixes: dict[str,str] = {}

	if data.product_fs.isdir(dir):
		for file in data.product_fs.walk.files(dir): # pyright: ignore[reportUnknownMemberType]
			path = Path(file)
			suffix = path.suffix.lower()
			if suffix not in preferred_suffixes.union(DS_SUPPORTED_TEXTURE_SUFFIXES):
				non_image_files.append(file)
			else:
				if suffix not in preferred_suffixes:
					atypical_image_files.append(file)

				if img_cache_data := checkImage(data, file):
					img_cache = cast(ImageCache, img_cache_data)
					if suffix not in oiio_format_extensions.get(img_cache['format'].lower(), []):
						incorrect_image_suffixes[file] = img_cache['format']

				elif suffix not in OIIO_UNSUPPORTED_IMAGE_SUFFIXES:
						unreadable_image_files.append(file)

	return (non_image_files, atypical_image_files, unreadable_image_files, incorrect_image_suffixes)

def trackDependencyIfExists(data: ValidationData, file: str, used_by_file: str) -> bool:
	"""Check if file exists (case insensitive) and track dependency.

	Adds file to data.dependency_files and returns true if file exists.

	Arguments:
		data (ValidationData): validation data of product to validate.
		file (str): File path to check existence of.
		used_by_file (str): File path to record as cause of dependency.
	"""

	exists = True

	try:
		# Get case sensitive version of path from filesystem
		_, del_path = data.filesystem.delegate_path(file)

		if not data.filesystem.exists(del_path):
			exists = False
		elif data.product_fs.exists(del_path):
			data.referenced_files.setdefault(del_path, set()).add(used_by_file)
		else:
			fs_name, _ = data.filesystem_unwrapped.which(del_path)
			fs_name = cast(str, fs_name)
			data.dependency_files.setdefault(fs_name, {}).setdefault(del_path, set()).add(used_by_file)
	except InvalidCharsInPath:
		exists = False

	return exists

def checkTypo(string: str, known_strings: list[str], ratio: float = 0.8) -> list[str]:
	"""Check string is in list or a near match for element in list.

	Returns a list of matches or near matches.

	Arguments:
		string (str): String to check.
		known_strings (list[str]): List of strings to check against.
		ratio (float): Minimum `SequenceMatcher` ratio to match.
	"""

	s = SequenceMatcher(b = string)	# b parameter is cached
	matches = [e for e in known_strings if s.set_seq1(e) or s.ratio() > ratio]

	return matches

@contextmanager
def decompressDSON(file: BinaryIO) -> Generator[BinaryIO, None, None]:
	"""Decompress DSON file if necessary.

	Returns a BinaryIO.

	Arguments:
		file (BinaryIO): File to decompress
	"""
	try:
		g = gzip.open(file, 'r')
		g.peek(1)
		file = cast(BinaryIO, g)
	except gzip.BadGzipFile:
		file.seek(0)

	yield file

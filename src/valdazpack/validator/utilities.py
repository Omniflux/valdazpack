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

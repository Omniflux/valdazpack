import gzip
import re

from contextlib import contextmanager
from difflib import SequenceMatcher
from mimetypes import add_type, guess_all_extensions
from pathlib import Path
from typing import cast, BinaryIO, Generator, NamedTuple

from fs.base import FS
from fs.errors import InvalidCharsInPath
from fs.info import Info
from fs.path import basename, combine, splitext
from PIL import Image

from .validationdata import ValidationData

add_type('image/x-tga', '.tga')

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
		[filename.tip.png, basefilename.tip.png]

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

	if fs.exists(file := path + '.tip.png'):
		tips.append(file)
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

def checkImageDir(fs: FS, dir: str, preferred_suffixes: set[str]) -> tuple[list[str], list[str], list[str], dict[str, str]]:
	"""Check Image directory only contains supported images.

	Returns a tuple of (
		non image files: list[str],
		supported image files without preferred suffixes: list[str],
		unreadable image files (for filetypes supported by both DS and `PIL`): list[str],
		image files with incorrect file extensions and their detected MIME type: list[tuple[str, str]]
	)

	Arguments:
		fs (fs.FS): PyFilesystem2 filesystem to use.
		dir (str): Root directory to check.
		preferred_suffixes (set[str]): List of preferred file extensions.
	"""

	DS_SUPPORTED_TEXTURE_SUFFIXES = set(['.bmp', '.bum', '.gif', '.jpeg', '.jpg', '.png', '.hdr', '.exr', '.tif', '.tiff', '.tga'])
	PIL_UNSUPPORTED_IMAGE_SUFFIXES = set(['.dsi', '.svg', '.hdr', '.exr', '.bum'])

	non_image_files: list[str] = []
	atypical_image_files: list[str] = []
	unreadable_image_files: list[str] = []
	incorrect_image_suffixes: dict[str,str] = {}

	if fs.isdir(dir):
		for file in fs.walk.files(dir):
			path = Path(file)
			suffix = path.suffix.lower()
			if suffix not in preferred_suffixes.union(DS_SUPPORTED_TEXTURE_SUFFIXES):
				non_image_files.append(file)
			else:
				if suffix not in preferred_suffixes:
					atypical_image_files.append(file)
				try:
					with Image.open(fs.openbin(file)) as im:
						im.verify()
						if (mime_type := cast(str | None, im.get_format_mimetype())) and suffix not in guess_all_extensions(mime_type):  # pyright: ignore[reportGeneralTypeIssues, reportUnknownMemberType]
							incorrect_image_suffixes[file] = mime_type
				except Exception:
					if suffix not in PIL_UNSUPPORTED_IMAGE_SUFFIXES:
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
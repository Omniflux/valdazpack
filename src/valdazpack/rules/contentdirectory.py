import re

from collections import defaultdict
from fs.path import splitext
from itertools import chain
from pathlib import Path
from typing import cast

from ..issues import contentdirectory as issues
from ..validator.resources import read_list_from
from ..validator.ruleset import ProductRuleset, rule
from ..validator.schema import SchemaCheckedJSON
from ..validator.utilities import Step, checkTypo, thumbnailsFor, trackDependencyIfExists

_TEXTURES_DIR = 'Runtime/Textures'
_NON_USER_FACING_DIRECTORIES = [d.lower() for d in read_list_from('daz/user_facing_excluded_directories.txt')]
_USER_FACING_FILE_EXTENSIONS = [f'*.{ext.lower()}' for ext in read_list_from('daz/native_file_extensions.txt')]


class ValidateContentDirectory(ProductRuleset):
	"""Perform validation of product.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()
		self._checkCaseInsensitivePathCollisions()
		self._checkExcessContentDirectory()
		self._checkEmptyDirectories()
		self._checkRootDirectories()
		self._checkRootFiles()
		self._checkGratuitousFiles()
		self._checkEmptyFiles()
		self._checkDazJsonLinkFiles()
		self._checkLegacyFormatFiles()
		self._checkAssetThumbnails()
		self._checkUnexpectedUserFacingFiles()

		# data.referenced_files must be populated by ValidateDSONFiles, etc. before this step
		self._checkUnreferencedTextureFiles()

		# data.missing_referenced_files must be populated by ValidateDSONFiles, etc. before this step
		self._checkInvalidFileReferences()

		# data.vendor_paths must be populated by ValidateRuntimeDirectory, ValidateDataDirectory, etc. before this step
		self._checkDazVendorDirectories()

	@rule
	def _checkCaseInsensitivePathCollisions(self) -> None:
		"""Check product for case insensitive path collisions."""

		case_insensitive_path_count: dict[str, list[str]] = defaultdict(list)
		for entry in self.data.product_fs_unwrapped.walk.info():  # pyright: ignore[reportUnknownMemberType]
			case_insensitive_path_count[entry[0].lower()].append(entry[0])
		
		if case_insensitive_collisions := [entries for entries in case_insensitive_path_count.values() if len(entries) > 1]:
			self._addIssue(issues.CaseInsensitivePathCollision(case_insensitive_collisions))

	@rule
	def _checkExcessContentDirectory(self) -> None:
		"""Check product for content directory in content directory."""

		if self.data.product_fs.isdir('Content'):
			self._addIssue(issues.ExcessContentDirectoryIssue(['Content/Content']))

	@rule
	def _checkEmptyDirectories(self) -> None:
		"""Check product for empty directories."""

		empty_dirs: set[str] = set()
		for directory in self.data.product_fs.walk(search='depth'):  # pyright: ignore[reportUnknownMemberType]
			directory = cast(Step, directory)
			if not directory.files and (not directory.dirs or
				set(((Path(directory.path) / d.name).as_posix() for d in directory.dirs)).issubset(empty_dirs)):
				empty_dirs.add(Path(*Path(directory.path).parts[1:]).as_posix())

		if empty_dirs:
			self._addIssue(issues.EmptyDirectoriesIssue(empty_dirs))

	@rule
	def _checkRootDirectories(self) -> None:
		"""Check product for uncommon directories in root content directory."""

		expected_directories = [d for d in chain(read_list_from('daz/common_content_directories.txt'), read_list_from('daz/user_facing_excluded_directories.txt'))]
		expected_directories_lc = [d.lower() for d in expected_directories]

		unexpected_directory_alternatives: dict[str, list[str]] = {}
		if unexpected_directories := [entry.name for entry in self.data.product_fs.scandir('') if entry.is_dir and not entry.name.lower() in expected_directories_lc]:
			for dir in unexpected_directories:
				matches = checkTypo(dir, expected_directories, 0.5)
				unexpected_directory_alternatives[dir] = matches if matches and dir.lower() != 'content' else []

		if unexpected_directory_alternatives:
			self._addIssue(issues.UncommonDirectoryInRootOfContentDirectoryIssue(unexpected_directory_alternatives))

	@rule
	def _checkRootFiles(self) -> None:
		"""Check product for files in root content directory."""

		if root_files := [entry.name for entry in self.data.product_fs.scandir('') if entry.is_file]:
			self._addIssue(issues.FilesInRootOfContentDirectoryIssue(root_files))

	@rule
	def _checkGratuitousFiles(self) -> None:
		"""Check product for gratuitous files."""

		GRATUITOUS_FILES = ['Thumbs.db', 'InstallManagerFileRegister.json']

		gratuitous_files: list[str] = []
		for file in (file.lstrip('/') for file in self.data.product_fs.walk.files()):  # pyright: ignore[reportUnknownMemberType]
			path = Path(file)
			if path.name.startswith('.') or '__MACOSX' in path.parts or path.name.lower() in [x.lower() for x in GRATUITOUS_FILES]:
				gratuitous_files.append(file)

		for directory in (dir.lstrip('/') for dir in self.data.product_fs.walk.dirs()):  # pyright: ignore[reportUnknownMemberType]
			path = Path(directory)
			if path.name.startswith('.') or '__MACOSX' in path.parts:
					gratuitous_files.append(directory)

		if gratuitous_files:
			self._addIssue(issues.GratuitousFilesIssue(gratuitous_files))

	@rule
	def _checkEmptyFiles(self) -> None:
		"""Check product for empty files."""

		# NOTE: There are valid use cases for 0 byte files such as Instructions.duf with Instructions.png being the relevant part
		# May need to modify this check

		if empty_files := [file.lstrip('/') for file, info in self.data.product_fs.walk.info(namespaces=['details']) if info.is_file and info.size == 0]:  # pyright: ignore[reportUnknownMemberType]
			self._addIssue(issues.EmptyFilesIssue(empty_files))

	@rule
	def _checkDazJsonLinkFiles(self) -> None:
		"""Check DAZ JSON Link files."""

		invalid_djl_files: dict[str, Exception] = {}
		unnecessary_thumbnails_for_djl_files: dict[str, list[str]] = {}
		for file in (file.lstrip('/') for file in self.data.product_fs.walk.files(filter=['*.djl'])):  # pyright: ignore[reportUnknownMemberType]
			thumbnails = [t for lst in thumbnailsFor(self.data.product_fs, file) for t in lst]

			try:
				json = SchemaCheckedJSON(self.data.product_fs.openbin(file), 'djl.schema.json')
			except Exception as e:
				invalid_djl_files[file] = e
			else:
				# NOTE: DS writes .djl file paths as all lowercase, so check filesystem as case insensitive
				if not trackDependencyIfExists(self.data, json.data['path'], file):
					self.data.missing_referenced_files.setdefault(json.data['path'], set()).add(file)

				if thumbnails:
					target_thumbnails = [t for lst in thumbnailsFor(self.data.filesystem, json.data['path']) for t in lst]
					if target_thumbnails:
						unnecessary_thumbnails_for_djl_files[file] = thumbnails

		if invalid_djl_files:
			self._addIssue(issues.InvalidDJLFilesIssue(invalid_djl_files))

		if unnecessary_thumbnails_for_djl_files:
			self._addIssue(issues.UnnecessaryThumbnailsForDJLIssue(unnecessary_thumbnails_for_djl_files))


	@rule
	def _checkLegacyFormatFiles(self) -> None:
		"""Check for legacy serialized binary files."""

		# http://docs.daz3d.com/doku.php/public/software/dazstudio/4/referenceguide/tech_articles/file_extensions/start#serialized_binary
		LEGACY_FILE_EXTENSIONS = ['*.daz', '*.ds']

		if legacy_format_files := [entry.lstrip('/') for entry in self.data.product_fs.walk.files(filter=LEGACY_FILE_EXTENSIONS)]:  # pyright: ignore[reportUnknownMemberType]
			self._addIssue(issues.LegacyFilesIssue(legacy_format_files))

	@rule
	def _checkDazVendorDirectories(self) -> None:
		"""Check DAZ vendor directories."""

		if not self.data.daz_original and (daz_vendor_dirs := [dir for vendor in self.data.vendor_paths.keys() for dir in self.data.vendor_paths[vendor] if vendor.lower().startswith('daz')]):
			self._addIssue(issues.FilesInVendorDazDirectoryIssue(daz_vendor_dirs))
		
	@rule
	def _checkInvalidFileReferences(self) -> None:
		"""Check invalid file references."""

		if self.data.missing_referenced_files:
			absoluteRegex = re.compile(r'^\/([a-z]:)?\/', re.IGNORECASE)
	
			absoluteFileReferences: dict[str, set[str]] = {}
			missingFileReferences: dict[str, set[str]] = {}
			for k, v in self.data.missing_referenced_files.items():
				if absoluteRegex.match(k):
					absoluteFileReferences[k] = v
				else:
					missingFileReferences[k] = v

			if absoluteFileReferences:
				self._addIssue(issues.FilesReferenceAbsolutePathsIssue(absoluteFileReferences))

			if missingFileReferences:
				self._addIssue(issues.FilesReferenceNonexistentFilesIssue(missingFileReferences))

	@rule
	def _checkUnreferencedTextureFiles(self) -> None:
		"""Check product for unreferenced files in Runtime/Textures directory."""
		# NOTE: This test is here instead of in ValidateRuntimeDirectory due to test dependencies.

		if self.data.product_fs.isdir(_TEXTURES_DIR):
			referenced_files_lc = {f.lower() for f in self.data.referenced_files}
			if unreferenced_files := [file for file in self.data.product_fs.walk.files(_TEXTURES_DIR) if not '/' + file.lower() in referenced_files_lc]:  # pyright: ignore[reportUnknownMemberType]
				self._addIssue(issues.UnreferencedFilesInTexturesDirectoryIssue(unreferenced_files))

	@rule
	def _checkAssetThumbnails(self) -> None:
		"""Check product thumbnails."""

		missingThumbnails: list[str] = []

		for file in (file.lstrip('/') for file in self.data.product_fs.walk.files(filter=_USER_FACING_FILE_EXTENSIONS, exclude_dirs=_NON_USER_FACING_DIRECTORIES)):  # pyright: ignore[reportUnknownMemberType]
			fullExtThumbnail = f'{file}.png'

			if not self.data.product_fs.exists(fullExtThumbnail):
				if not self.data.product_fs.exists(f'{splitext(file)[0]}.png'):
					missingThumbnails.append(file)

		if missingThumbnails:
			self._addIssue(issues.MissingThumbnailsIssue(missingThumbnails))

	@rule
	def _checkUnexpectedUserFacingFiles(self) -> None:
		"""Check for unexpected files in user facing directories."""

		unexpectedFiles: list[str] = []
		fullExtensionTipFiles: list[str] = []

		for file in (file.lstrip('/') for file in self.data.product_fs.walk.files(exclude=_USER_FACING_FILE_EXTENSIONS + ['*.djl'], exclude_dirs=_NON_USER_FACING_DIRECTORIES)):  # pyright: ignore[reportUnknownMemberType]
			if file.lower().endswith('.png'):
				splitFile = splitext(file)[0]
				if not self.data.product_fs.exists(splitFile):
					if not any(self.data.product_fs.exists(f) for f in (splitFile + e[1:] for e in _USER_FACING_FILE_EXTENSIONS + ['*.djl'])):
						if splitFile.lower().endswith('.tip'):
							splitFile = splitext(splitFile)[0]
							if self.data.product_fs.exists(splitFile):
								fullExtensionTipFiles.append(file)
							else:
								if not any(self.data.product_fs.exists(f) for f in (splitFile + e[1:] for e in _USER_FACING_FILE_EXTENSIONS + ['*.djl'])):
									unexpectedFiles.append(file)
						else:
							unexpectedFiles.append(file)
			else:
				unexpectedFiles.append(file)

		if unexpectedFiles:
			self._addIssue(issues.UnexpectedFilesInUserFacingDirectoriesIssue(unexpectedFiles))

		if fullExtensionTipFiles:
			self._addIssue(issues.FullExtensionTipFilesIssue(fullExtensionTipFiles))
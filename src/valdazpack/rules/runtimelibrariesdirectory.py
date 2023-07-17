import zlib

from ..issues import libraries as issues
from ..validator.resources import read_list_from
from ..validator.ruleset import ProductRuleset, rule
from ..validator.utilities import checkDirectoryHasSelfAsChild

_LIBRARIES_DIR = 'Runtime/Libraries'

class ValidateRuntimeLibrariesDirectory(ProductRuleset):
	"""Perform Runtime/Libraries validation of product.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()
		if self.data.poser and \
		self.data.product_fs.isdir(_LIBRARIES_DIR):
			self._checkExcessLibrariesDirectory()
			self._checkUnexpectedDirectoriesInLibrariesDirectory()
			self._checkRootFiles()
			self._checkValidCompressedFiles()

	@rule
	def _checkExcessLibrariesDirectory(self) -> None:
		"""Check product for Libraries directory in Runtime/Libraries directory."""

		if checkDirectoryHasSelfAsChild(self.data.product_fs, _LIBRARIES_DIR):
			self._addIssue(issues.ExcessRuntimeLibrariesDirectoryIssue())

	@rule
	def _checkUnexpectedDirectoriesInLibrariesDirectory(self) -> None:
		"""Check product for unexpected directories in Runtime/Libraries."""

		expected_runtime_directories = [l.lower() for l in read_list_from('poser/expected_libraries_directories.txt')]

		if unexpected_dirs := [entry.name for entry in self.data.product_fs.scandir(_LIBRARIES_DIR) if entry.is_dir and entry.name.lower() not in expected_runtime_directories]:
			self._addIssue(issues.UnexpectedDirectoriesInRuntimeLibrariesDirectoryIssue(unexpected_dirs))

	@rule
	def _checkRootFiles(self) -> None:
		"""Check product for files in root Runtime/Libraries directory."""

		if root_files := [entry.name for entry in self.data.product_fs.scandir(_LIBRARIES_DIR) if entry.is_file]:
			self._addIssue(issues.FilesInRootOfRuntimeLibrariesDirectoryIssue(root_files))

	@rule
	def _checkValidCompressedFiles(self) -> None:
		"""Check compressed files in Runtime/Libraries directory are valid zlib compressed files."""

		POSER_COMPRESSED_FILE_SUFFIXES = set(['*.cmz', '*.crz', '*.fcz', '*.hdz', '*.hrz', '*.ltz', '*.mcz', '*.mz5', '*.p2z', '*.ppz', '*.pzz'])

		invalid_zlib_files: list[str] = []
		for file in self.data.product_fs.walk.files(_LIBRARIES_DIR, filter=POSER_COMPRESSED_FILE_SUFFIXES):  # pyright: ignore[reportUnknownMemberType]
			try:
				# NOTE: Poser compressed files should be zlib compressed, but DAZ Studio can read gzip as well, so allow it.
				zlib.decompress(self.data.product_fs.readbytes(file), zlib.MAX_WBITS|32)
			except zlib.error:
				invalid_zlib_files.append(file)

		if invalid_zlib_files:
			self._addIssue(issues.InvalidCompressedFilesInRuntimeLibrariesDirectoryIssue(invalid_zlib_files))

	@rule
	def _getContentTypeOfFiles(self) -> None:
		"""Get content type of files."""

		for file in self.data.product_fs.walk.files(_LIBRARIES_DIR, filter=['*.mt5', '*.mz5', '*.mc6', '*.mcz']):  # pyright: ignore[reportUnknownMemberType]
			self.data.shader_users[file] = {'mt5' if file.endswith('5') else 'mc6'}
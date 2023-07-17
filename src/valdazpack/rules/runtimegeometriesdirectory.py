import zlib

from fs.path import combine, split

from ..issues import geometries as issues
from ..validator.ruleset import ProductRuleset, rule
from ..validator.utilities import checkDirectoryHasSelfAsChild, checkVendorDirsOnly

_GEOMETRIES_DIR = 'Runtime/Geometries'

class ValidateRuntimeGeometriesDirectory(ProductRuleset):
	"""Perform Runtime/Geometries validation of product.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()
		if self.data.product_fs.isdir(_GEOMETRIES_DIR):
			self._checkExcessGeometriesDirectory()
			self._checkVendorDirsOnlyInGeometriesDirectory()
			self._checkValidCompressedGeometryFiles()
			self._checkGeometriesFiles()

			# TODO: Validate .obj and .mtl files

	@rule
	def _checkExcessGeometriesDirectory(self) -> None:
		"""Check product for Textures directory in Runtime/Geometries directory."""

		if checkDirectoryHasSelfAsChild(self.data.product_fs, _GEOMETRIES_DIR):
			self._addIssue(issues.ExcessGeometriesDirectoryIssue([combine(_GEOMETRIES_DIR, split(_GEOMETRIES_DIR)[1])]))

	@rule
	def _checkVendorDirsOnlyInGeometriesDirectory(self) -> None:
		"""Check product has only Vendor directories in Runtime/Geometries.

		Updates `data.vendor_paths` with found vendor directories.
		"""

		if geometries_root_files := checkVendorDirsOnly(self.data, _GEOMETRIES_DIR):
			self._addIssue(issues.FilesInRootOfGeometriesDirectoryIssue(geometries_root_files))

	@rule
	def _checkValidCompressedGeometryFiles(self) -> None:
		"""Check compressed files in Runtime/Geometries directory are valid zlib compressed files."""

		invalid_zlib_files: list[str] = []
		for file in self.data.product_fs.walk.files(_GEOMETRIES_DIR, filter=['*.obz']):  # pyright: ignore[reportUnknownMemberType]
			try:
				# NOTE: Poser compressed files should be zlib compressed, but DAZ Studio can read gzip as well, so allow it.
				zlib.decompress(self.data.product_fs.readbytes(file), zlib.MAX_WBITS|32)
			except zlib.error:
				invalid_zlib_files.append(file)

		if invalid_zlib_files:
			self._addIssue(issues.InvalidCompressedFilesInRuntimeGeometriesDirectoryIssue(invalid_zlib_files))

	@rule
	def _checkGeometriesFiles(self) -> None:
		"""Check files in Runtime/Geometries."""

		if unexpected_files := [file for file in self.data.product_fs.walk.files(_GEOMETRIES_DIR, exclude=['*.obj', '*.obz', '*.mtl'])]:  # pyright: ignore[reportUnknownMemberType]
			self._addIssue(issues.UnexpectedFilesInRuntimeGeometriesDirectoryIssue(unexpected_files))
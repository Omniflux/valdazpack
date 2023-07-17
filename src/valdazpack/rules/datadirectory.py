from fs.path import combine, join, iteratepath

from ..issues import data as issues
from ..validator.ruleset import ProductRuleset, rule
from ..validator.utilities import checkDirectoryHasSelfAsChild

_DATA_DIR = 'data'
_ITEM_SUBDIRECTORIES_WITH_VENDOR_SUBDIRECTORIES = ['add-ons', 'morphs', 'uv sets', 'projection morphs']
_ITEM_SUBDIRECTORIES_TO_SKIP_REFERENCE_CHECK = ['projection templates', 'tools']

# http://docs.daz3d.com/doku.php/public/software/dazstudio/4/referenceguide/tech_articles/file_extensions/start#serialized_binary
_LEGACY_FILE_EXTENSIONS = ['*.dsd', '*.dso', '*.dsv']


class ValidateDataDirectory(ProductRuleset):
	"""Perform data validation of product.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()
		if self.data.product_fs.isdir(_DATA_DIR):
			self._checkExcessDataDirectory()
			self._checkAutoAdaptedDirectory()
			self._checkLegacyDirectories()
			self._checkVendorDirectories()
			self._checkRootFiles()
			self._checkLegacyFormatFiles()
			self._checkUserFacingFiles()
			self._checkVendorDirectoriesHaveFiles()
			self._checkVendorProductDirectoriesHaveFiles()
			self._checkUnreferencedFiles()

	@rule
	def _checkExcessDataDirectory(self) -> None:
		"""Check product for data directory in data directory."""

		if checkDirectoryHasSelfAsChild(self.data.product_fs, _DATA_DIR):
			self._addIssue(issues.ExcessDataDirectoryIssue([combine(_DATA_DIR, _DATA_DIR)]))

	@rule
	def _checkAutoAdaptedDirectory(self) -> None:
		"""Check product for auto_adapted in data directory."""

		AUTO_DIR = combine(_DATA_DIR, 'auto_adapted')
		if self.data.product_fs.isdir(AUTO_DIR):
			self._addIssue(issues.AutoAdaptedInDataDirectoryIssue([AUTO_DIR]))

	@rule
	def _checkLegacyDirectories(self) -> None:
		"""Check product for legacy directories in data directory."""

		LEGACY_DIRECTORIES = ['3_0', '4_0', '4_0_2']

		if legacy_directories := [dir for dir in LEGACY_DIRECTORIES if self.data.product_fs.isdir(combine(_DATA_DIR, dir))]:
			self._addIssue(issues.LegacyDirectoriesInDataDirectoryIssue(legacy_directories))

	@rule
	def _checkRootFiles(self) -> None:
		"""Check product for files in root data directory."""

		if root_files := [entry.name for entry in self.data.product_fs.scandir(_DATA_DIR) if entry.is_file]:
			self._addIssue(issues.FilesInRootOfDataDirectoryIssue(root_files))

	@rule
	def _checkVendorDirectories(self) -> None:
		"""Check product for data/Vendor, data/Vendor/Product/Item/*/Vendor directories.

		Updates `data.vendor_paths` with found vendor directories.
		"""

		# NOTE: This is guesswork as the directory structure is not required, just common

		for path, info in self.data.product_fs.walk.info(_DATA_DIR):  # pyright: ignore[reportUnknownMemberType]
			if info.is_file:
				path_parts = iteratepath(path)
				# data / Vendor / Product / Item / ? / Vendor / Base / File
				if len(path_parts) > 6 and path_parts[4].lower() in _ITEM_SUBDIRECTORIES_WITH_VENDOR_SUBDIRECTORIES:
					self.data.vendor_paths.setdefault(path_parts[5], set()).add(join(*path_parts[:6]))
				elif len(path_parts) > 2:
					self.data.vendor_paths.setdefault(path_parts[1], set()).add(combine(path_parts[0], path_parts[1]))

	@rule
	def _checkVendorDirectoriesHaveFiles(self) -> None:
		"""Check product for files in data/Vendor directories."""

		vendor_root_files: list[str] = []
		for vendor in self.data.product_fs.scandir(_DATA_DIR):
			if vendor.is_dir:
				vendor_root_files.extend([entry.make_path(vendor.name) for entry in self.data.product_fs.scandir(vendor.make_path(_DATA_DIR)) if entry.is_file])

		if vendor_root_files:
			self._addIssue(issues.FilesInDataVendorDirectoryIssue(vendor_root_files))

	@rule
	def _checkVendorProductDirectoriesHaveFiles(self) -> None:
		"""Check product for files in data/Vendor/Product directories."""

		product_root_files: list[str] = []
		for vendor in self.data.product_fs.scandir(_DATA_DIR):
			if vendor.is_dir:
				vendorPath = vendor.make_path(_DATA_DIR)
				for product in self.data.product_fs.scandir(vendorPath):
					product_root_files = [entry.make_path(combine(vendor.name, product.name)) for entry in self.data.product_fs.scandir(vendorPath) if entry.is_file]

		if product_root_files:
			self._addIssue(issues.FilesInDataProductDirectoryIssue(product_root_files))

	@rule
	def _checkLegacyFormatFiles(self) -> None:
		"""Check product for legacy format files in data directory."""

		if legacy_format_files := [entry.lstrip('/') for entry in self.data.product_fs.walk.files(_DATA_DIR, filter=_LEGACY_FILE_EXTENSIONS)]:  # pyright: ignore[reportUnknownMemberType]
			self._addIssue(issues.LegacyFilesInDataDirectoryIssue(legacy_format_files))

	@rule
	def _checkUserFacingFiles(self) -> None:
		"""Check product for user facing files in data directory."""

		if duf_files := [entry.lstrip('/') for entry in self.data.product_fs.walk.files(_DATA_DIR, filter=['*.duf']) if entry not in self.data.postload_files]:  # pyright: ignore[reportUnknownMemberType]
			self._addIssue(issues.DufFilesInDataDirectoryIssue(duf_files))

	@rule
	def _checkUnreferencedFiles(self) -> None:
		"""Check product for unreferenced files in data directory."""

		# TODO: Filter out _ITEM_SUBDIRECTORIES_WITH_VENDOR_SUBDIRECTORIES files in a better manner for other products?

		referenced_files_lc = {f.lower() for f in self.data.referenced_files}

		unreferenced_files: list[str] = []
		for file in self.data.product_fs.walk.files(_DATA_DIR, exclude=_LEGACY_FILE_EXTENSIONS):  # pyright: ignore[reportUnknownMemberType]
			if (not '/' + file.lower() in referenced_files_lc
				and not (len(filepath := iteratepath(file)) > 4 and filepath[4].lower() in _ITEM_SUBDIRECTORIES_WITH_VENDOR_SUBDIRECTORIES + _ITEM_SUBDIRECTORIES_TO_SKIP_REFERENCE_CHECK)):
				unreferenced_files.append(file)

		if unreferenced_files:
			self._addIssue(issues.UnreferencedFilesInDataDirectoryIssue(unreferenced_files))
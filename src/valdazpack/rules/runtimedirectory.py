from urllib.parse import urlparse

from fs.path import combine, split
from PIL import Image

from ..issues import runtime as issues
from ..validator.resources import read_list_from
from ..validator.ruleset import ProductRuleset, rule
from ..validator.utilities import checkDirectoryHasSelfAsChild, checkImageDir, checkVendorDirsOnly

_RUNTIME_DIR = 'Runtime'
_TEXTURES_DIR = 'Runtime/Textures'
_TEMPLATES_DIR = 'Runtime/Templates'
_WEBLINKS_DIR = 'Runtime/WebLinks'

class ValidateRuntimeDirectory(ProductRuleset):
	"""Perform Runtime validation of product.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()
		if self.data.product_fs.isdir(_RUNTIME_DIR):
			self._checkExcessRuntimeDirectory()
			self._checkExcessTexturesDirectory()
			self._checkExcessTemplatesDirectory()
			self._checkUnexpectedDirectoriesInRuntimeDirectory()
			self._checkRootFiles()
			self._checkVendorDirsOnlyInTexturesDirectory()
			self._checkVendorDirsOnlyInTemplatesDirectory()
			self._checkTextureImageFiles()
			self._checkTemplateImageFiles()
			self._checkWebLinks()

	@rule
	def _checkExcessRuntimeDirectory(self) -> None:
		"""Check product for Runtime directory in Runtime directory."""

		if checkDirectoryHasSelfAsChild(self.data.product_fs, _RUNTIME_DIR):
			self._addIssue(issues.ExcessRuntimeDirectoryIssue([combine(_RUNTIME_DIR, split(_RUNTIME_DIR)[1])]))

	@rule
	def _checkExcessTexturesDirectory(self) -> None:
		"""Check product for Textures directory in Runtime/Textures directory."""

		if checkDirectoryHasSelfAsChild(self.data.product_fs, _TEXTURES_DIR):
			self._addIssue(issues.ExcessTexturesDirectoryIssue([combine(_TEXTURES_DIR, split(_TEXTURES_DIR)[1])]))

	@rule
	def _checkExcessTemplatesDirectory(self) -> None:
		"""Check product for Templates directory in Runtime/Templates directory."""

		if checkDirectoryHasSelfAsChild(self.data.product_fs, _TEMPLATES_DIR):
			self._addIssue(issues.ExcessTemplatesDirectoryIssue([combine(_TEMPLATES_DIR, split(_TEMPLATES_DIR)[1])]))

	@rule
	def _checkUnexpectedDirectoriesInRuntimeDirectory(self) -> None:
		"""Check product for unexpected directories in Runtime."""

		expected_runtime_directories = [l.lower() for l in read_list_from('daz/expected_runtime_directories.txt')]
		if self.data.poser:
			expected_runtime_directories.extend([l.lower() for l in read_list_from('poser/expected_runtime_directories.txt')])

		if unexpected_dirs := [entry.name for entry in self.data.product_fs.scandir(_RUNTIME_DIR) if entry.is_dir and entry.name.lower() not in expected_runtime_directories]:
			self._addIssue(issues.UnexpectedDirectoriesInRuntimeDirectoryIssue(unexpected_dirs))

	@rule
	def _checkRootFiles(self) -> None:
		"""Check product for files in root Runtime directory."""

		if root_files := [entry.name for entry in self.data.product_fs.scandir(_RUNTIME_DIR) if entry.is_file]:
			self._addIssue(issues.FilesInRootOfRuntimeDirectoryIssue(root_files))

	@rule
	def _checkVendorDirsOnlyInTexturesDirectory(self) -> None:
		"""Check product has only Vendor directories in Runtime/Textures.

		Updates `data.vendor_paths` with found vendor directories.
		"""

		if texture_root_files := checkVendorDirsOnly(self.data, _TEXTURES_DIR):
			self._addIssue(issues.FilesInRootOfTexturesDirectoryIssue(texture_root_files))

	@rule
	def _checkVendorDirsOnlyInTemplatesDirectory(self) -> None:
		"""Check product has only Vendor directories in Runtime/Templates.

		Updates `data.vendor_paths` with found vendor directories.
		"""

		if templates_root_files := checkVendorDirsOnly(self.data, _TEMPLATES_DIR):
			self._addIssue(issues.FilesInRootOfTemplatesDirectoryIssue(templates_root_files))

	@rule
	def _checkTextureImageFiles(self) -> None:
		"""Check images files in Runtime/Textures."""

		# This is a guess
		PREFERRED_TEXTURE_SUFFIXES = set(['.png', '.exr', '.hdr', '.jpeg', '.jpg', '.tiff', '.tif', '.tga', '.dsi'])

		(non_image_texture_files,
		atypical_image_texture_files,
		unreadable_image_texture_files,
		incorrect_image_texture_file_extensions) = checkImageDir(self.data.product_fs, _TEXTURES_DIR, PREFERRED_TEXTURE_SUFFIXES)

		if non_image_texture_files:
			self._addIssue(issues.NonImageFilesInTexturesDirectoryIssue(non_image_texture_files))

		if atypical_image_texture_files:
			self._addIssue(issues.AtypicalImageFilesInTexturesDirectoryIssue(atypical_image_texture_files))

		if unreadable_image_texture_files:
			self._addIssue(issues.UnreadableImageFilesInTexturesDirectoryIssue(unreadable_image_texture_files))

		if incorrect_image_texture_file_extensions:
			self._addIssue(issues.ImageHasIncorrectFileExtensionIssue(incorrect_image_texture_file_extensions))

		single_color_image_files: list[str] = []
		if self.data.product_fs.isdir(_TEXTURES_DIR):
			for file in self.data.product_fs.walk.files(_TEXTURES_DIR):  # pyright: ignore[reportUnknownMemberType]:
				try:
					with Image.open(self.data.product_fs.openbin(file)) as im:
						if (colors := im.getcolors()) and len(colors) == 1:
							single_color_image_files.append(file)
				except Exception:
					pass

		if single_color_image_files:
			self._addIssue(issues.SingleColorImageIssue(single_color_image_files))

		# TODO: check bump and displacement maps are 16+bit greyscale? normal maps 16+bit? ensure none are jpg?
		# Use wand / imagemagick instead of Pillow?

	@rule
	def _checkTemplateImageFiles(self) -> None:
		"""Check images files in Runtime/Templates."""

		# This is a guess
		PREFERRED_TEMPLATE_SUFFIXES = set(['.svg', '.png', '.jpeg', '.jpg', '.tiff', '.tif', '.tga',])

		(non_image_template_files,
		atypical_image_template_files,
		unreadable_image_template_files,
		incorrect_image_template_file_extensions) = checkImageDir(self.data.product_fs, _TEMPLATES_DIR, PREFERRED_TEMPLATE_SUFFIXES)

		if non_image_template_files:
			self._addIssue(issues.NonImageFilesInTemplatesDirectoryIssue(non_image_template_files))

		if atypical_image_template_files:
			self._addIssue(issues.AtypicalImageFilesInTemplatesDirectoryIssue(atypical_image_template_files))

		if unreadable_image_template_files:
			self._addIssue(issues.UnreadableImageFilesInTemplatesDirectoryIssue(unreadable_image_template_files))

		if incorrect_image_template_file_extensions:
			self._addIssue(issues.ImageHasIncorrectFileExtensionIssue(incorrect_image_template_file_extensions))

	@rule
	def _checkWebLinks(self) -> None:
		"""Check product for WebLinks files."""

		if self.data.product_fs.isdir(_WEBLINKS_DIR):
			if self.data.poser:
				if unexpected_files := [file.lstrip('/') for file in self.data.product_fs.walk.files(_WEBLINKS_DIR, exclude=['*.pzs'])]:  # pyright: ignore[reportUnknownMemberType]:
					self._addIssue(issues.UnexpectedFilesInWebLinksDirectoryIssue(unexpected_files))

				invalid_files: list[str] = []
				for file in (file.lstrip('/') for file in self.data.product_fs.walk.files(_WEBLINKS_DIR, filter=['*.pzs'])):  # pyright: ignore[reportUnknownMemberType]:
					try:
						# NOTE: This is just a rough check, it will pass many invalid strings...
						result = urlparse(self.data.product_fs.readtext(file))
						if not all([result.scheme, result.netloc]):
							raise ValueError
					except ValueError:
						invalid_files.append(file)

				if invalid_files:
					self._addIssue(issues.InvalidPZSFileIssue(invalid_files))
			else:
				self._addIssue(issues.WebLinksIssue([_WEBLINKS_DIR]))
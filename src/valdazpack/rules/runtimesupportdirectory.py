from pathlib import Path

from PIL import Image

from ..issues import support as issues
from ..validator.ruleset import ProductRuleset, rule

_SUPPORT_DIR = 'Runtime/Support'

class ValidateRuntimeSupportDirectory(ProductRuleset):
	"""Perform Runtime/Support validation of product.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()
		if self.data.product_fs.isdir(_SUPPORT_DIR):
			self._checkDirectoriesInSupportDirectory()
			self._checkMetadataFiles()
		else:
			self._addIssue(issues.MissingMetadataFilesIssue())

	@rule
	def _checkDirectoriesInSupportDirectory(self) -> None:
		"""Check product for directories in Runtime/Support directory."""

		if subdirectories := [entry.name for entry in self.data.product_fs.scandir(_SUPPORT_DIR) if entry.is_dir]:
			self._addIssue(issues.SubdirectoriesInRuntimeSupportIssue(subdirectories))

	@rule
	def _checkMetadataFiles(self) -> None:
		"""Check metadata files in Runtime/Support directory."""

		IMAGE_SUFFIXES = set(['.jpg', '.png'])

		# User guide states icon should be 114x148 (or 100×143 for old DAZ products),
		# but reference guide states icon may be larger and will be automatically
		# scaled as needed.
		IMAGE_MINIMUM_DIMENSIONS = (114, 148)

		metadata: dict[str, list[str]] = {}
		for file in [Path(f) for f in self.data.product_fs.walk.files(_SUPPORT_DIR)]:  # pyright: ignore[reportUnknownMemberType]
			if not file.stem in metadata:
				metadata[file.stem] = []
			metadata[file.stem].append(file.suffix)

		dsx_files: list[str] = []
		unexpected_files: list[str] = []
		missing_icon_files: list[str] = []
		missing_script_files: list[str] = []
		redundant_icon_files: list[str] = []
		undersized_icon_files: dict[str, tuple[int, int]] = {}
		supportDirPath = Path(_SUPPORT_DIR)
		for entry in metadata:
			if not '.dsx' in metadata[entry]:
				for suffix in metadata[entry]:
					unexpected_files.append((supportDirPath / f"{entry}{suffix}").as_posix())
			else:
				dsx_files.append((supportDirPath / f"{entry}.dsx").as_posix())
				if not '.dsa' in metadata[entry]:
					missing_script_files.append((supportDirPath / f"{entry}.dsa").as_posix())

				if not any (suffix in IMAGE_SUFFIXES for suffix in metadata[entry]):
					missing_icon_files.append((supportDirPath / f"{entry}.({'|'.join([s.lstrip('.') for s in IMAGE_SUFFIXES])})").as_posix())
				else:
					image_suffixes = IMAGE_SUFFIXES.intersection(metadata[entry])
					if len(image_suffixes) > 1:
						for suffix in image_suffixes:
							redundant_icon_files.append((supportDirPath / f"{entry}{suffix}").as_posix())

					for suffix in image_suffixes:
						with self.data.product_fs.openbin((supportDirPath / f"{entry}{suffix}").as_posix()) as file:
							dimensions = Image.open(file).size
							if any (i < j for i, j in zip(dimensions, IMAGE_MINIMUM_DIMENSIONS)):
								undersized_icon_files[(supportDirPath / f"{entry}{suffix}").as_posix()] = dimensions

				if unexpected_suffixes := list(set(metadata[entry]) - set(['.dsa', '.dsx']) - IMAGE_SUFFIXES):
					for suffix in unexpected_suffixes:
						unexpected_files.append((supportDirPath / f"{entry}{suffix}").as_posix())

		if not dsx_files:
			self._addIssue(issues.MissingMetadataFilesIssue())

		if unexpected_files:
			self._addIssue(issues.UnexpectedFilesInRuntimeSupportIssue(unexpected_files))

		if missing_icon_files:
			self._addIssue(issues.MissingMetadataIconFilesIssue(missing_icon_files))

		if missing_script_files:
			self._addIssue(issues.MissingMetadataScriptFilesIssue(missing_script_files))

		if redundant_icon_files:
			self._addIssue(issues.RedundantMetadataIconFilesIssue(redundant_icon_files))

		if undersized_icon_files:
			self._addIssue(issues.UndersizedMetadataIconFilesIssue(undersized_icon_files))
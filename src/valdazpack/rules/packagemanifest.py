from ..issues import manifest as issues
from ..validator.package import Package
from ..validator.ruleset import PackageRuleset, rule
from ..validator.schema import SchemaCheckedXML

_DSX_FILES = ['Manifest.dsx', 'Supplement.dsx']

class ValidatePackageManifests(PackageRuleset):
	"""Perform manifest validation of package.

	Arguments:
		data (ValidationData): validation data of package to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()

		invalid_manifest_files: dict[str, Exception] = {}
		self.missing_manifest_files: dict[str, list[str]] = {}
		self.unlisted_manifest_files: dict[str, list[str]] = {}
		self.extraneous_root_files: dict[str, list[str]] = {}
		for package in self.data.packages:
			try:
				manifest = SchemaCheckedXML(package.root_fs.openbin('Manifest.dsx'), 'Manifest.xsd').tree
			except Exception as e:
				invalid_manifest_files[package.path.as_posix()] = e
			else:
				self.manifest_files = [e.attrib['VALUE'] for e in manifest.xpath("/DAZInstallManifest/File[@ACTION='Install']")]

				self._checkMissingManifestFiles(package)
				self._checkUnlistedManifestFiles(package)
				self._checkRootExtraneousFiles(package)

		if invalid_manifest_files:
			self._addIssue(issues.InvalidPackageManifestIssue(invalid_manifest_files))

		if self.missing_manifest_files:
			self._addIssue(issues.MissingPackageManifestFilesIssue(self.missing_manifest_files))

		if self.unlisted_manifest_files:
			self._addIssue(issues.MissingPackageManifestRecordIssue(self.unlisted_manifest_files))

		if self.extraneous_root_files:
			self._addIssue(issues.RootFilesInPackageIssue(self.extraneous_root_files))

	@rule
	def _checkMissingManifestFiles(self, package: Package) -> None:
		"""Check for files listed in Manifest but not included in zip file."""

		if missing_files := [f for f in self.manifest_files if not package.root_fs.exists(f)]:
			self.missing_manifest_files[package.path.name] = missing_files

	@rule
	def _checkUnlistedManifestFiles(self, package: Package) -> None:
		"""Check for files not listed in Manifest but included in zip file."""

		if extra_files := [file for file in (file.lstrip('/') for file in package.root_fs.walk.files()) if not file in self.manifest_files + _DSX_FILES]:
			self.unlisted_manifest_files[package.path.name] = extra_files

	@rule
	def _checkRootExtraneousFiles(self, package: Package) -> None:
		"""Check for unexpected files in root of zip file."""

		if root_files := [file for file in (entry.name.lstrip('/') for entry in package.root_fs.scandir('') if entry.is_file and not entry.name in _DSX_FILES)]:
			self.extraneous_root_files[package.path.name] = root_files
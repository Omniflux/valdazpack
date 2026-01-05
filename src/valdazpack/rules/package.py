from ..issues import package as issues
from ..validator.package import Package, PackageType
from ..validator.ruleset import PackageRuleset, rule

class ValidatePackages(PackageRuleset):
	"""Perform package validation of product.

	Arguments:
		data (ValidationData): validation data of package to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()

		self.bad_package_names: list[str] = []
		self.bad_custom_pkgs: list[str] = []
		self.bad_standard_pkgs: list[str] = []
		self.unicodeFilenames: dict[str, list[str]] = {}
		self.nonASCIIFilenames: dict[str, list[str]] = {}

		for package in self.data.packages:
			self._checkPackageNameParseable(package)
			self._checkDAZPackageType(package)
			self._checkOtherPackageType(package)
			self._checkReadMeIncluded(package)
			self._checkNonASCIIFilenames(package)

		if self.bad_package_names:
			self._addIssue(issues.PackageNameIssue(self.bad_package_names))

		if self.bad_custom_pkgs:
			self._addIssue(issues.CustomPackageNameIssue(self.bad_custom_pkgs))

		if self.bad_standard_pkgs:
			self._addIssue(issues.StandardPackageNameIssue(self.bad_standard_pkgs))

		if self.unicodeFilenames:
			self.data.issues.package.append(issues.UnicodeFilenamesInPackage(self.unicodeFilenames))

		if self.nonASCIIFilenames:
			self.data.issues.package.append(issues.NonASCIIFilenamesInPackage(self.nonASCIIFilenames))

	@rule
	def _checkPackageNameParseable(self, package: Package) -> None:
		"""Check package filename is parseable."""

		if not package.parsed:
			self.bad_package_names.append(package.path.name)

	@rule
	def _checkDAZPackageType(self, package: Package) -> None:
		"""Check DAZ distributed package type is STANDARD."""

		if self.data.daz and package.type != PackageType.STANDARD:
			self.bad_custom_pkgs.append(package.path.name)

	@rule
	def _checkOtherPackageType(self, package: Package) -> None:
		"""Check non DAZ distributed package type is CUSTOM."""

		if not self.data.daz and package.type != PackageType.CUSTOM:
			self.bad_standard_pkgs.append(package.path.name)

	@rule
	def _checkReadMeIncluded(self, package: Package) -> None:
		"""Check ReadMe.pdf included in package."""

		if package.root_fs.isfile('ReadMe.pdf'):
			package.readme = True
		else:
			self._addIssue(issues.NoPackageReadMeIssue())

	@rule
	def _checkNonASCIIFilenames(self, package: Package) -> None:
		"""Check product zip file for non ASCII filenames.

		DIM does not support Unicode filenames in ZIP files due to using the minizip 1.01 library.
		Examining official DAZ packages reveals Windows-1252 encoding is used. Packages with
		filenames using non ASCII characters may not extract correctly on OS X.
		"""

		for entry in package.root_fs._zip.namelist():  # pyright: ignore[reportPrivateUsage]
			if not entry.isascii():
				try:
					entry.encode('Windows-1252')
				except UnicodeEncodeError:
					self.unicodeFilenames.setdefault(package.path.name, []).append(entry)
				else:
					self.nonASCIIFilenames.setdefault(package.path.name, []).append(entry)

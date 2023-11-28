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
		for package in self.data.packages:
			self._checkPackageNameParseable(package)
			self._checkDAZPackageType(package)
			self._checkOtherPackageType(package)
			self._checkReadMeIncluded(package)

		if self.bad_package_names:
			self._addIssue(issues.PackageNameIssue(self.bad_package_names))

		if self.bad_custom_pkgs:
			self._addIssue(issues.CustomPackageNameIssue(self.bad_custom_pkgs))

		if self.bad_standard_pkgs:
			self._addIssue(issues.StandardPackageNameIssue(self.bad_standard_pkgs))

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
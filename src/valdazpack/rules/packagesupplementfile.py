from fs.errors import ResourceNotFound

from ..issues import supplementfile as issues
from ..validator.package import Package
from ..validator.ruleset import PackageRuleset, rule
from ..validator.schema import SchemaCheckedXML
from ..validator.utilities import alpha_numeric

class ValidateSupplementFiles(PackageRuleset):
	"""Perform supplement file validation of package.

	Arguments:
		data (ValidationData): validation data of package to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()

		missing_supplement_files: list[str] = []
		invalid_supplement_files: dict[str, Exception] = {}
		self.embeded_supplement_files: dict[str, list[str]] = {}
		self.name_mismatch: dict[str, tuple[str, str]] = {}
		self.store_idx_mismatch: dict[str, tuple[str, str]] = {}
		for package in self.data.packages:
			try:
				self.supplement = SchemaCheckedXML(package.root_fs.openbin('Supplement.dsx'), 'Supplement.xsd').tree
			except ResourceNotFound:
				missing_supplement_files.append(package.path.as_posix())
			except Exception as e:
				invalid_supplement_files[package.path.as_posix()] = e
			else:
				self._checkPackageSupplementEmbeddedExclusionElements(package)
				self._checkPackageSupplementProductName(package)
				self._checkPackageSupplementProductStoreIDX(package)

		if missing_supplement_files:
			self._addIssue(issues.MissingPackageSupplementIssue(missing_supplement_files))

		if invalid_supplement_files:
			self._addIssue(issues.InvalidPackageSupplementIssue(invalid_supplement_files))

		if self.embeded_supplement_files:
			self._addIssue(issues.EmbeddedPackageSupplementElementIssue(self.embeded_supplement_files))

		if self.name_mismatch:
			self._addIssue(issues.MismatchedPackageSupplementProductNameIssue(self.name_mismatch))

		if self.store_idx_mismatch:
			self._addIssue(issues.IncorrectPackageSupplementProductStoreIDXIssue(self.store_idx_mismatch))

	@rule
	def _checkPackageSupplementEmbeddedExclusionElements(self, package: Package) -> None:
		"""Check for excluded elements in embedded package supplement file."""

		embeded_elements: list[str] = []
		for element_name in ['UserOrderId', 'UserOrderDate', 'InstallerDate', 'ProductFileGuid']:
			if len(self.supplement.xpath(f"/ProductSupplement/{element_name}")):
				embeded_elements.append(element_name)

		if embeded_elements:
			self.embeded_supplement_files[package.path.as_posix()] = embeded_elements

	@rule
	def _checkPackageSupplementProductName(self, package: Package) -> None:
		"""Check product name in package filename is simplified version of ProductName in package supplement file.

		Updates `package.product_name` to value of ProductName in package supplement file.
		"""

		package.product_name = self.supplement.xpath("/ProductSupplement/ProductName")[0].attrib['VALUE']

		if package.parsed and package.parsed['name'] != (simplified_name := alpha_numeric(package.product_name)):
			self.name_mismatch[package.path.as_posix()] = (simplified_name, package.parsed['name'])

	@rule
	def _checkPackageSupplementProductStoreIDX(self, package: Package) -> None:
		"""Check product and package ID in package filename matches ProductStoreIDX in package supplement file."""

		if package.parsed and (element := self.supplement.xpath("/ProductSupplement/ProductStoreIDX")):
			if len(element) and element[0].attrib['VALUE'] != package.product_store_idx:
				self.store_idx_mismatch[package.path.as_posix()] = (element[0].attrib['VALUE'], package.product_store_idx or '')
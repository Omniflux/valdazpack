from . import PackageNotice, PackageWarning

class MissingPackageSupplementIssue(PackageNotice):
	title = 'Missing Package Supplement File'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_supplement_file/'
	description = "A Package Supplement File 'Supplement.dsx' is recommended"

class InvalidPackageSupplementIssue(PackageWarning):
	title = 'Invalid Package Supplement File'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_supplement_file/'
	description = "Package Supplement File 'Supplement.dsx' is invalid"

class EmbeddedPackageSupplementElementIssue(PackageWarning):
	title = 'Inexpedient Element in Embedded Package Supplement File'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_supplement_file/'
	description = "Embedded Package Supplement File should not contain element"

class MismatchedPackageSupplementProductNameIssue(PackageNotice):
	title = 'Supplement File Product Name / Package Filename Mismatch'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_naming/'
	description = "The package filename does not appear to be a simplified version of the Supplement File product name"

class IncorrectPackageSupplementProductStoreIDXIssue(PackageWarning):
	title = 'Incorrect ProductStoreIDX in Package Supplement File'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_supplement_file/'
	description = "Package Supplement File contains ProductStoreIDX with incorrectly encoded source prefix"

from . import PackageNotice, PackageWarning

class PackageNameIssue(PackageWarning):
	title = 'Invalid Package Filename'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_naming/'
	description = (
		"Package filenames must match the regular expression "
		"'^([A-Z][0-9A-Z]{0,6})(?=\\d{8})(\\d{8})(-(\\d{2}))?_([0-9A-Za-z]+)\\.zip$'")

class CustomPackageNameIssue(PackageWarning):
	title = 'Custom Package Filename'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_naming/'
	description = "Packages distributed by Daz Productions, Inc should have a source prefix of 'IM', 'DZ', 'DAZ', 'DAZ3D', or 'TAFI'"

class StandardPackageNameIssue(PackageWarning):
	title = 'Standard Package Filename'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_naming/'
	description = "Packages not distributed by Daz Productions, Inc must not have a source prefix of 'IM', 'DZ', 'DAZ', 'DAZ3D', or 'TAFI'"

class NoPackageReadMeIssue(PackageNotice):
	title = 'No Package ReadMe included'
	description = "Packages may include a 'ReadMe.pdf' file in the root accessible by clicking the ReadMe button in Install Manager"
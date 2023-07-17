from . import PackageWarning

class InvalidPackageManifestIssue(PackageWarning):
	title = 'Invalid Package Manifest'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_manifest/'
	description = "Package Manifest 'Manifest.dsx' is invalid"

class MissingPackageManifestFilesIssue(PackageWarning):
	title = 'Missing file(s) in Package'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_manifest/'
	description = "Package Manifest lists file not included in package"

class MissingPackageManifestRecordIssue(PackageWarning):
	title = 'File(s) missing from Package Manifest'
	reference = 'http://docs.daz3d.com/doku.php/public/software/install_manager/referenceguide/tech_articles/package_manifest/'
	description = "Package includes file not listed in Package Manifest"

class RootFilesInPackageIssue(PackageWarning):
	title = 'Unexpected root file(s) in Package'
	description = "All files in Package except for Manifest.dsx and Supplement.dsx must be in subdirectories"

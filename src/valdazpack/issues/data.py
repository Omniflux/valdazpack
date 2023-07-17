from . import ProductNotice, ProductWarning

class ExcessDataDirectoryIssue(ProductWarning):
	title = 'Data contains sub "data" directory'
	description = "Data directory tree should be in root of data directory"

class FilesInRootOfDataDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in root of data directory'
	description = "Files in data directory should be in 'data/Vendor/Product/Item/'"

class FilesInDataVendorDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in data/Vendor directory'
	description = "Files in data directory should be in 'data/Vendor/Product/Item/'"

class FilesInDataProductDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in data/Vendor/Product directory'
	description = "Files in data directory should be in 'data/Vendor/Product/Item/'"

class AutoAdaptedInDataDirectoryIssue(ProductWarning):
	title = 'auto_adapted directory in data directory'
	description = "Assets loaded from non-native formats should be resaved as Support Assets"
	reference = 'https://www.daz3d.com/forums/discussion/comment/604443/#Comment_604443'

class LegacyDirectoriesInDataDirectoryIssue(ProductNotice):
	title = 'Legacy director(y|ies) (3_0, 4_0, 4_0_2) in data directory'
	description = "Support Assets in legacy formats should be resaved as DSON Support Assets with correct Vendor/Product/Item except when maintaining compatibility with previously distributed items"

class LegacyFilesInDataDirectoryIssue(ProductNotice):
	title = 'Legacy file(s) (*.dsd, *.dso, *.dsv) in data directory'
	description = "Support Assets in legacy formats should be resaved as DSON Support Assets except when maintaining compatibility with previously distributed items"

class DufFilesInDataDirectoryIssue(ProductNotice):
	title = 'DSON User File(s) (*.duf) in data directory without PostLoad reference'
	description = ("DSON User Files in data directory cannot be accessed by users directly but may be accessed via another method such as a script")

class UnreferencedFilesInDataDirectoryIssue(ProductNotice):
	title = 'Unreferenced file(s) in data directory'
	description = ("Files in data directory cannot be accessed by users directly. Validation can detect references from DSON user files (*.duf) in most cases, "
	               "but not by scripts (*.dsa, *.dsb, *.dse), legacy files (*.daz, *.ds), or as modifiers to other products. Legacy file types (*.dsd, *.dso, *.dsv) and "
	               "files in the standard directory structure '/data/Vendor/Product/Item/{add-ons, morphs, uv sets, projection morphs, projection templates, tools}/Vendor/*/' "
	               "are ignored for this test. There may be false positives in this list.")
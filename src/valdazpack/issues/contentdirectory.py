from . import ProductWarning, ProductNotice

class CaseInsensitivePathCollision(ProductWarning):
	title = 'Case Insensitive Path Collision(s)'
	description = "Path collisions found for case insensitive file systems"

class FilesInRootOfContentDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in root of Content directory'
	description = "No files should be in root of content directory"

class ExcessContentDirectoryIssue(ProductWarning):
	title = 'Content contains sub "content" directory'
	description = "Content directory tree should be in root of Content directory"

class EmptyDirectoriesIssue(ProductWarning):
	title = 'Empty director(y|ies) in Content directory'
	description = "Content directory tree includes directory with no files"

class GratuitousFilesIssue(ProductWarning):
	title = 'Gratuitous file(s) in Content directory'
	description = "Content directory includes files which are likely gratuitous"

class EmptyFilesIssue(ProductWarning):
	title = 'Empty file(s) in Content directory'
	description = "Content directory contains files with no content"

class InvalidDJLFilesIssue(ProductWarning):
	title = 'Invalid Daz JSON Link file(s) in Content directory'
	description = "Content directory contains invalid *.djl file"

class UnnecessaryThumbnailsForDJLIssue(ProductWarning):
	title = 'Unnecessary thumbnails exist for Daz JSON Link file(s) in Content directory'
	description = "Content directory contains thumbnail for *.djl file where *.djl target thumbnail exists"

class UncommonDirectoryInRootOfContentDirectoryIssue(ProductWarning):
	title = 'Uncommon director(y|ies) in root of Content directory'
	description = "Directory may be spelled or located incorrectly. Common near matches will be listed when possible."

class FilesInVendorDazDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in reserved Vendor directory'
	description = "No files should be in directories for vendor DAZ"

class FilesReferenceNonexistentFilesIssue(ProductWarning):
	title = 'Invalid file reference(s)'
	description = "File references nonexistent files. This may indicate a missing dependency while validating."

class FilesReferenceAbsolutePathsIssue(ProductWarning):
	title = 'Absolute file path reference(s)'
	description = "File references should be relative to Content directory"

class LegacyFilesIssue(ProductWarning):
	title = 'Legacy file(s) (*.daz, *.ds) in Content directory'
	description = "Assets in legacy formats should be resaved as DSON Assets"

class MissingThumbnailsIssue(ProductWarning):
	title = 'Missing thumbnail(s)'
	description = "Assets should have thumbnails"

class FullExtensionThumbnailsIssue(ProductWarning):
	title = 'Full extension thumbnail(s)'
	description = "Distributed assets should have asset extension removed from thumbnail name to prevent user from overwriting when resaving"

class UnexpectedFilesInUserFacingDirectoriesIssue(ProductWarning):
	title = 'Unexpected file(s) in user facing directory'
	description = ("Files in user facing directories should consist of *.duf, *.dsa, *.dsb, *.dse and accompanying thumbnails (*.png) and tips (*.tip.png). "
	               "These files may be misplaced or better located in the data, ReadMe's, or Runtime directories.")

class FullExtensionTipFilesIssue(ProductWarning):
	title = 'Full extension tip file(s)'
	description = "Tip files must not include the extension of the accompanying asset file"

class UnreferencedFilesInTexturesDirectoryIssue(ProductNotice):
	title = 'Unreferenced file(s) in Textures directory'
	description = ("Files in Runtime/Textures directory should be referenced by a user facing file. Validation can detect references from most DSON user files (*.duf) in most cases, "
	               "but not by scripts (*.dsa, *.dsb, *.dse) or legacy files (*.daz, *.ds). There may be false positives in this list.")
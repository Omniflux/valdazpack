from . import ProductWarning

class ExcessRuntimeLibrariesDirectoryIssue(ProductWarning):
	title = 'Runtime/Libraries contains sub "Libraries" directory'
	description = "Runtime/Libraries directory tree should be in root of Runtime/Libraries directory"

class FilesInRootOfRuntimeLibrariesDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in root of Libraries directory'
	description = "No files should be in root of Libraries directory"

class UnexpectedDirectoriesInRuntimeLibrariesDirectoryIssue(ProductWarning):
	title = 'Unexpected directories(s) in Runtime/Libraries directory'
	description = "Non standard directory in Runtime/Libraries directory"

class InvalidCompressedFilesInRuntimeLibrariesDirectoryIssue(ProductWarning):
	title = 'Invalid compressed file(s) in Runtime/Libraries directory'
	description = "Invalid compressed file in Runtime/Libraries directory"
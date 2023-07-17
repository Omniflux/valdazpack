from . import ProductWarning

class ExcessGeometriesDirectoryIssue(ProductWarning):
	title = 'Runtime/Geometries contains sub "geometries" directory'
	description = "Runtime/Geometries directory tree should be in root of Runtime/Geometries directory"

class FilesInRootOfGeometriesDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in root of Geometries directory'
	description = "No files should be in root of Runtime/Geometries directory"

class UnexpectedFilesInRuntimeGeometriesDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in Runtime/Geometries directory'
	description = "Only wavefront *.obj and *.mtl files should be in Runtime/Geometries directory"

class InvalidCompressedFilesInRuntimeGeometriesDirectoryIssue(ProductWarning):
	title = 'Invalid compressed file(s) in Runtime/Geometries directory'
	description = "Invalid compressed file in Runtime/Geometries directory"
from . import ProductNotice, ProductWarning

class ExcessRuntimeDirectoryIssue(ProductWarning):
	title = 'Runtime contains sub "runtime" directory'
	description = "Runtime directory tree should be in root of Runtime directory"

class ExcessTexturesDirectoryIssue(ProductWarning):
	title = 'Runtime/Textures contains sub "textures" directory'
	description = "Runtime/Textures directory tree should be in root of Runtime/Textures directory"

class ExcessTemplatesDirectoryIssue(ProductWarning):
	title = 'Runtime/Templates contains sub "templates" directory'
	description = "Runtime/Templates directory tree should be in root of Runtime/Templates directory"

class FilesInRootOfRuntimeDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in root of Runtime directory'
	description = "No files should be in root of Runtime directory"

class UnexpectedDirectoriesInRuntimeDirectoryIssue(ProductWarning):
	title = 'Unexpected directories(s) in Runtime directory'
	description = "Non standard directory in Runtime directory"

class FilesInRootOfTexturesDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in root of Textures directory'
	description = "No files should be in root of Runtime/Textures directory"

class FilesInRootOfTemplatesDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in root of Templates directory'
	description = "No files should be in root of Runtime/Templates directory"

class NonImageFilesInTexturesDirectoryIssue(ProductWarning):
	title = 'Unexpected non image file(s) in Textures directory'
	description = "Only image files should be in Runtime/Textures/Vendor directory"

class NonImageFilesInTemplatesDirectoryIssue(ProductWarning):
	title = 'Unexpected non image file(s) in Templates directory'
	description = "Only image files should be in Runtime/Templates/Vendor directory"

class AtypicalImageFilesInTexturesDirectoryIssue(ProductNotice):
	title = 'Atypical image file type(s) in Textures directory'
	description = "Consider using PNG, JPEG or OpenEXR"

class AtypicalImageFilesInTemplatesDirectoryIssue(ProductNotice):
	title = 'Atypical image file type(s) in Templates directory'
	description = "Consider using SVG, PNG, or JPEG"

class UnreadableImageFilesInTexturesDirectoryIssue(ProductWarning):
	title = 'Unreadable image file(s) in Textures directory'
	description = "Image file is invalid"

class UnreadableImageFilesInTemplatesDirectoryIssue(ProductWarning):
	title = 'Unreadable image file(s) in Templates directory'
	description = "Image file is invalid"

class ImageHasIncorrectFileExtensionIssue(ProductWarning):
	title = 'Image(s) with incorrect file extension'
	description = "Image file extension does not match detected image type"

class UnexpectedFilesInWebLinksDirectoryIssue(ProductWarning):
	title = 'Unexpected file(s) in WebLinks directory'
	description = "Only *.pzs files should be in WebLinks directory"

class InvalidPZSFileIssue(ProductWarning):
	title = 'Invalid WebLink file(s) in WebLinks directory'
	description = "WebLinks directory contains *.pzs file with invalid URL"

class WebLinksIssue(ProductWarning):
	title = 'Unexpected WebLinks directory'
	description = "WebLinks should only be provided for Poser content"
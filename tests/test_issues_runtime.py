from valdazpack.validator import ValidationData
from valdazpack.issues.runtime import (
	ExcessRuntimeDirectoryIssue,
	ExcessTexturesDirectoryIssue,
	ExcessTemplatesDirectoryIssue,
	FilesInRootOfRuntimeDirectoryIssue,
	UnexpectedDirectoriesInRuntimeDirectoryIssue,
	FilesInRootOfTexturesDirectoryIssue,
	FilesInRootOfTemplatesDirectoryIssue,
	NonImageFilesInTexturesDirectoryIssue,
	NonImageFilesInTemplatesDirectoryIssue,
	AtypicalImageFilesInTexturesDirectoryIssue,
	AtypicalImageFilesInTemplatesDirectoryIssue,
	UnreadableImageFilesInTexturesDirectoryIssue,
	UnreadableImageFilesInTemplatesDirectoryIssue,
	ImageHasIncorrectFileExtensionIssue,
	UnexpectedFilesInWebLinksDirectoryIssue,
	InvalidPZSFileIssue,
	WebLinksIssue
)

def test_ExcessRuntimeDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ExcessRuntimeDirectoryIssue) for x in validatorINVALID.issues.product)

def test_ExcessTexturesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ExcessTexturesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_ExcessTemplatesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ExcessTemplatesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_FilesInRootOfRuntimeDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesInRootOfRuntimeDirectoryIssue) for x in validatorINVALID.issues.product)

def test_UnexpectedDirectoriesInRuntimeDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UnexpectedDirectoriesInRuntimeDirectoryIssue) for x in validatorINVALID.issues.product)

def test_FilesInRootOfTexturesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesInRootOfTexturesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_FilesInRootOfTemplatesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesInRootOfTemplatesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_NonImageFilesInTexturesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, NonImageFilesInTexturesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_NonImageFilesInTemplatesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, NonImageFilesInTemplatesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_AtypicalImageFilesInTexturesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, AtypicalImageFilesInTexturesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_AtypicalImageFilesInTemplatesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, AtypicalImageFilesInTemplatesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_UnreadableImageFilesInTexturesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UnreadableImageFilesInTexturesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_UnreadableImageFilesInTemplatesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UnreadableImageFilesInTemplatesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_ImageHasIncorrectFileExtensionIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ImageHasIncorrectFileExtensionIssue) for x in validatorINVALID.issues.product)

def test_UnexpectedFilesInWebLinksDirectoryIssue(validatorINVALIDPoser: ValidationData):
	assert any(isinstance(x, UnexpectedFilesInWebLinksDirectoryIssue) for x in validatorINVALIDPoser.issues.product)

def test_InvalidPZSFileIssue(validatorINVALIDPoser: ValidationData):
	assert any(isinstance(x, InvalidPZSFileIssue) for x in validatorINVALIDPoser.issues.product)

def test_WebLinksIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, WebLinksIssue) for x in validatorINVALID.issues.product)
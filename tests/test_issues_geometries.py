from valdazpack.validator import ValidationData
from valdazpack.issues.geometries import (
	ExcessGeometriesDirectoryIssue,
	FilesInRootOfGeometriesDirectoryIssue,
	UnexpectedFilesInRuntimeGeometriesDirectoryIssue,
	InvalidCompressedFilesInRuntimeGeometriesDirectoryIssue,
)

def test_ExcessGeometriesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ExcessGeometriesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_FilesInRootOfGeometriesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesInRootOfGeometriesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_UnexpectedFilesInRuntimeGeometriesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UnexpectedFilesInRuntimeGeometriesDirectoryIssue) for x in validatorINVALID.issues.product)

def test_InvalidCompressedFilesInRuntimeGeometriesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, InvalidCompressedFilesInRuntimeGeometriesDirectoryIssue) for x in validatorINVALID.issues.product)
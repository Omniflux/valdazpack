from valdazpack.validator import ValidationData
from valdazpack.issues.data import (
	ExcessDataDirectoryIssue,
	FilesInRootOfDataDirectoryIssue,
	FilesInDataVendorDirectoryIssue,
	FilesInDataProductDirectoryIssue,
	AutoAdaptedInDataDirectoryIssue,
	LegacyDirectoriesInDataDirectoryIssue,
	LegacyFilesInDataDirectoryIssue,
	DufFilesInDataDirectoryIssue,
	UnreferencedFilesInDataDirectoryIssue
)

def test_ExcessDataDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ExcessDataDirectoryIssue) for x in validatorINVALID.issues.product)

def test_FilesInRootOfDataDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesInRootOfDataDirectoryIssue) for x in validatorINVALID.issues.product)

def test_FilesInDataVendorDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesInDataVendorDirectoryIssue) for x in validatorINVALID.issues.product)

def test_FilesInDataProductDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesInDataProductDirectoryIssue) for x in validatorINVALID.issues.product)

def test_AutoAdaptedInDataDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, AutoAdaptedInDataDirectoryIssue) for x in validatorINVALID.issues.product)

def test_LegacyDirectoriesInDataDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, LegacyDirectoriesInDataDirectoryIssue) for x in validatorINVALID.issues.product)

def test_LegacyFilesInDataDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, LegacyFilesInDataDirectoryIssue) for x in validatorINVALID.issues.product)

def test_DufFilesInDataDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, DufFilesInDataDirectoryIssue) for x in validatorINVALID.issues.product)

def test_UnreferencedFilesInDataDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UnreferencedFilesInDataDirectoryIssue) for x in validatorINVALID.issues.product)
from valdazpack.validator import ValidationData
from valdazpack.issues.manifest import (
	InvalidPackageManifestIssue,
	MissingPackageManifestFilesIssue,
	MissingPackageManifestRecordIssue,
	RootFilesInPackageIssue
)

def test_InvalidPackageManifestIssue(validatorINVALIDdsx: ValidationData):
	assert any(isinstance(x, InvalidPackageManifestIssue) for x in validatorINVALIDdsx.issues.package)

def test_MissingPackageManifestFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MissingPackageManifestFilesIssue) for x in validatorINVALID.issues.package)

def test_MissingPackageManifestRecordIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MissingPackageManifestRecordIssue) for x in validatorINVALID.issues.package)

def test_RootFilesInPackageIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, RootFilesInPackageIssue) for x in validatorINVALID.issues.package)
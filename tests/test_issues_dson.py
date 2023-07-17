from valdazpack.validator import ValidationData
from valdazpack.issues.dsonfiles import (
	InvalidDSONFilesIssue,
	AssetIDMismatchFilesIssue,
	GeometryInDUFFilesIssue,
	UVSetInDUFFilesIssue,
	MorphInDUFFilesIssue,
	ShaderInDUFFilesIssue,
	ActiveMorphsInDSFFilesIssue
)

def test_InvalidDSONFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, InvalidDSONFilesIssue) for x in validatorINVALID.issues.product)

def test_AssetIDMismatchFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, AssetIDMismatchFilesIssue) for x in validatorINVALID.issues.product)

def test_GeometryInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, GeometryInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_UVSetInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UVSetInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_MorphInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MorphInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_MaterialInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ShaderInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_ActiveMorphsInDSFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ActiveMorphsInDSFFilesIssue) for x in validatorINVALID.issues.product)
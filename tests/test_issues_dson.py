from valdazpack.validator import ValidationData
from valdazpack.issues.dsonfiles import (
	InvalidDSONFilesIssue,
	SourceFileReferencesIssue,
	AssetIDMismatchFilesIssue,
	DuplicateIDsInFilesIssue,
	GeometryInDUFFilesIssue,
	UVSetInDUFFilesIssue,
	MorphInDUFFilesIssue,
	ShaderInDUFFilesIssue,
	FavoriteInMaterialInDUFFilesIssue,
	FavoriteInNodePropertyInDUFFilesIssue,
	NormalMapInNonNormalMapChannelInDUFFilesIssue,
	NonNormalMapInNormalMapChannelInDUFFilesIssue,
	TextureMapSavedInLossyFormatIssue,
	TextureMapSavedWithInsufficientBitDepthIssue,
	TextureMapSavedWithTooManyChannelsIssue,
	ActiveMorphsInDSFFilesIssue,
	MorphLoaderGroupInDSFFilesIssue,
	HiddenParameterNotInHiddenCategoryInFilesIssue,
	NonHiddenParameterInHiddenCategoryInFilesIssue,
)

def test_InvalidDSONFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, InvalidDSONFilesIssue) for x in validatorINVALID.issues.product)

def test_SourceFileReferencesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, SourceFileReferencesIssue) for x in validatorINVALID.issues.product)

def test_AssetIDMismatchFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, AssetIDMismatchFilesIssue) for x in validatorINVALID.issues.product)

def test_DuplicateIDsInFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, DuplicateIDsInFilesIssue) for x in validatorINVALID.issues.product)

def test_GeometryInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, GeometryInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_UVSetInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UVSetInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_MorphInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MorphInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_ShaderInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ShaderInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_FavoriteInMaterialInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FavoriteInMaterialInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_FavoriteInNodePropertyInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FavoriteInNodePropertyInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_NormalMapInNonNormalMapChannelInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, NormalMapInNonNormalMapChannelInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_NonNormalMapInNormalMapChannelInDUFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, NonNormalMapInNormalMapChannelInDUFFilesIssue) for x in validatorINVALID.issues.product)

def test_TextureMapSavedInLossyFormatIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, TextureMapSavedInLossyFormatIssue) for x in validatorINVALID.issues.product)

def test_TextureMapSavedWithInsufficientBitDepthIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, TextureMapSavedWithInsufficientBitDepthIssue) for x in validatorINVALID.issues.product)

def test_TextureMapSavedWithTooManyChannelsIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, TextureMapSavedWithTooManyChannelsIssue) for x in validatorINVALID.issues.product)

def test_ActiveMorphsInDSFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ActiveMorphsInDSFFilesIssue) for x in validatorINVALID.issues.product)

def test_MorphLoaderGroupInDSFFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MorphLoaderGroupInDSFFilesIssue) for x in validatorINVALID.issues.product)

def test_HiddenParameterNotInHiddenCategoryInFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, HiddenParameterNotInHiddenCategoryInFilesIssue) for x in validatorINVALID.issues.product)

def test_NonHiddenParameterInHiddenCategoryInFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, NonHiddenParameterInHiddenCategoryInFilesIssue) for x in validatorINVALID.issues.product)

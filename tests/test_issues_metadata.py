from valdazpack.validator import ValidationData
from valdazpack.issues.metadatafile import (
	InvalidProductMetadataIssue,
	MetadataFilenameIssue,
	PackageProductNotMetadataProductIssue,
	MetadataFileContainsMultipleStoreIDsIssue,
	MetadataStoreIDIsDAZ3DIssue,
	MetadataStoreIDIsNotDAZ3DIssue,
	MetadataStoreIDIsNotLocalUserIssue,
	MetadataMissingProductTokenIssue,
	MetadataMissingArtistIssue,
	MetadataUnexpectedAssetsIssue,
	MetadataUnexpectedSupportAssetsIssue,
	MetadataUnlistedAssetsIssue,
	MetadataInvalidSupportAssetFileRefIssue,
	MetadataMissingContentTypeIssue,
	MetadataMissingAudienceIssue,
	MetadataNonStandardAudienceIssue,
	MetadataMissingCategoriesIssue,
	MetadataMissingTagsIssue,
#	MetadataMissingCompatibilitiesIssue,
#	MetadataMissingCompatibilityBaseIssue,
	MetadataHasDescriptionIssue,
	MetadataHasUserwordsIssue,
	MetadataDuplicateCategoriesUsedIssue,
	MetadataParentCategoriesUsedIssue,
	MetadataSpecialCategoriesUsedIssue,
	MetadataUserCategoriesUsedIssue,
	MetadataDeprecatedContentTypeIssue,
	MetadataDeprecatedCategoriesIssue,
	MetadataWrongShaderTypeIssue,
	MetadataNonspecificShaderTypeIssue
)

def test_InvalidProductMetadataIssue(validatorINVALIDdsx: ValidationData):
	assert any(isinstance(x, InvalidProductMetadataIssue) for x in validatorINVALIDdsx.issues.product)

def test_MetadataFilenameIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataFilenameIssue) for x in validatorINVALID.issues.product)

def test_PackageProductNotMetadataProductIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, PackageProductNotMetadataProductIssue) for x in validatorINVALID.issues.product)

def test_MetadataFileContainsMultipleStoreIDsIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataFileContainsMultipleStoreIDsIssue) for x in validatorINVALID.issues.product)

def test_MetadataStoreIDIsDAZ3DIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataStoreIDIsDAZ3DIssue) for x in validatorINVALID.issues.product)

def test_MetadataStoreIDIsDAZ3DNonIssue(validatorINVALIDdazOriginal: ValidationData):
	assert not any(isinstance(x, MetadataStoreIDIsDAZ3DIssue) for x in validatorINVALIDdazOriginal.issues.product)

def test_MetadataStoreIDIsNotDAZ3DIssue(validatorINVALIDdazOriginal: ValidationData):
	assert any(isinstance(x, MetadataStoreIDIsNotDAZ3DIssue) for x in validatorINVALIDdazOriginal.issues.product)

def test_MetadataStoreIDIsNotDAZ3DNonIssue(validatorINVALID: ValidationData):
	assert not any(isinstance(x, MetadataStoreIDIsNotDAZ3DIssue) for x in validatorINVALID.issues.product)

def test_MetadataStoreIDIsNotLocalUserIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataStoreIDIsNotLocalUserIssue) for x in validatorINVALID.issues.product)

def test_MetadataMissingProductTokenIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataMissingProductTokenIssue) for x in validatorINVALID.issues.product)

def test_MetadataMissingArtistIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataMissingArtistIssue) for x in validatorINVALID.issues.product)

def test_MetadataUnexpectedAssetsIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataUnexpectedAssetsIssue) for x in validatorINVALID.issues.product)

def test_MetadataUnexpectedSupportAssetsIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataUnexpectedSupportAssetsIssue) for x in validatorINVALID.issues.product)

def test_MetadataUnlistedAssetsIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataUnlistedAssetsIssue) for x in validatorINVALID.issues.product)

def test_MetadataInvalidSupportAssetFileRefIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataInvalidSupportAssetFileRefIssue) for x in validatorINVALID.issues.product)

def test_MetadataMissingContentTypeIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataMissingContentTypeIssue) for x in validatorINVALID.issues.product)

def test_MetadataMissingAudienceIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataMissingAudienceIssue) for x in validatorINVALID.issues.product)

def test_MetadataNonStandardAudienceIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataNonStandardAudienceIssue) for x in validatorINVALID.issues.product)

def test_MetadataMissingCategoriesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataMissingCategoriesIssue) for x in validatorINVALID.issues.product)

def test_MetadataMissingTagsIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataMissingTagsIssue) for x in validatorINVALID.issues.product)

#def test_MetadataMissingCompatibilitiesIssue(validatorINVALID: ValidationData):
#	assert any(isinstance(x, MetadataMissingCompatibilitiesIssue) for x in validatorINVALID.issues.product)

#def test_MetadataMissingCompatibilityBaseIssue(validatorINVALID: ValidationData):
#	assert any(isinstance(x, MetadataMissingCompatibilityBaseIssue) for x in validatorINVALID.issues.product)

def test_MetadataHasDescriptionIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataHasDescriptionIssue) for x in validatorINVALID.issues.product)

def test_MetadataHasUserwordsIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataHasUserwordsIssue) for x in validatorINVALID.issues.product)

def test_MetadataDuplicateCategoriesUsedIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataDuplicateCategoriesUsedIssue) for x in validatorINVALID.issues.product)

def test_MetadataParentCategoriesUsedIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataParentCategoriesUsedIssue) for x in validatorINVALID.issues.product)

def test_MetadataSpecialCategoriesUsedIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataSpecialCategoriesUsedIssue) for x in validatorINVALID.issues.product)

def test_MetadataUserCategoriesUsedIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataUserCategoriesUsedIssue) for x in validatorINVALID.issues.product)

def test_MetadataDeprecatedContentTypeIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataDeprecatedContentTypeIssue) for x in validatorINVALID.issues.product)

def test_MetadataDeprecatedCategoriesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataDeprecatedCategoriesIssue) for x in validatorINVALID.issues.product)

def test_MetadataWrongShaderTypeIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataWrongShaderTypeIssue) for x in validatorINVALID.issues.product)

def test_MetadataNonspecificShaderTypeIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MetadataNonspecificShaderTypeIssue) for x in validatorINVALID.issues.product)
from . import ProductNotice, ProductWarning

class InvalidProductMetadataIssue(ProductWarning):
	title = 'Invalid Metadata file'
	description = "Metadata file is invalid"

class MetadataFilenameIssue(ProductWarning):
	title = "Metadata filename does not match expected value"
	description = "Metadata filename does not match auto generated filename"

class PackageProductNotMetadataProductIssue(ProductNotice):
	title = "Package product name not in metadata product names"
	description = "There is no metadata product with the same name as the package product"

class MetadataFileContainsMultipleStoreIDsIssue(ProductWarning):
	title = "Metadata file contains multiple StoreIDs"
	description = "Metadata file contains products with differing StoreIDs"

class MetadataStoreIDIsDAZ3DIssue(ProductWarning):
	title = "Metadata StoreID is 'DAZ 3D'"
	description = "Only officially supplied DAZ 3D products should have a StoreID of 'DAZ 3D'"

class MetadataStoreIDIsNotDAZ3DIssue(ProductWarning):
	title = "Metadata StoreID is not 'DAZ 3D'"
	description = "Official DAZ 3D products should have a StoreID of 'DAZ 3D'"

class MetadataStoreIDIsNotLocalUserIssue(ProductNotice):
	title = "Metadata StoreID is not 'LOCAL USER'"
	description = "If StoreID does not already exist on users system, 'LOCAL USER' will be used instead"

class MetadataMissingProductTokenIssue(ProductWarning):
	title = "Metadata missing product token"
	description = "Metadata contains no product token for product with StoreID not set to 'LOCAL USER'"

class MetadataMissingArtistIssue(ProductWarning):
	title = "Metadata missing artist"
	description = "Metadata contains no artist entries"

class MetadataUnexpectedAssetsIssue(ProductWarning):
	title = "Unexpected Asset(s) in metadata"
	description = "Metadata contains Asset for non existent file"

class MetadataUnexpectedSupportAssetsIssue(ProductWarning):
	title = "Unexpected Support Asset(s) in metadata"
	description = "Metadata contains Support Asset for non existent file"

class MetadataUnlistedAssetsIssue(ProductWarning):
	title = "File(s) not listed as Assets or SupportAssets"
	description = "Metadata does not list all files as Assets or SupportAssets"

class MetadataInvalidSupportAssetFileRefIssue(ProductWarning):
	title = "Invalid metadata SupportAssets file reference"
	description = "Metadata SupportAssets value should refer to file reference is in"

class MetadataMissingContentTypeIssue(ProductWarning):
	title = "Missing Content Type for Assets(s) in metadata"
	reference = [
		'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/packaging_genesis_morph_products/start',
		'http://docs.daz3d.com/doku.php/public/dson_spec/format_description/metadata/content_types/start']
	description = "Metadata contains no Content Type for Asset"

class MetadataMissingAudienceIssue(ProductWarning):
	title = "Missing Audience for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/adding_metadata/start'
	description = "Metadata contains no Audience for Asset"

class MetadataNonStandardAudienceIssue(ProductWarning):
	title = "Non standard Audience for Assets(s) in metadata"
	description = "Metadata contains non standard Audience for Asset. Audience will be reassigned at import."

class MetadataMissingCategoriesIssue(ProductWarning):
	title = "Missing Categories for Assets(s) in metadata"
	reference = [
		'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/adding_metadata/start',
		'http://docs.daz3d.com/doku.php/public/dson_spec/format_description/metadata/categories/start']
	description = "Metadata contains no Categories for Asset"

# Note - Degrading Warning to Notice
# DAZ3D QA has recommendations for Tags to add, but does not follow this recommendation themselves
class MetadataMissingTagsIssue(ProductNotice):
	title = "Missing Tags for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/adding_metadata/start'
	description = "Metadata contains no Tags for Asset. DAZ QA recommends adding a number of search terms here, but rarely does so themselves."

class MetadataMissingCompatibilitiesIssue(ProductWarning):
	title = "Missing Compatibilities for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/adding_metadata/start'
	description = "Metadata contains no Compatibilities for Asset"

class MetadataMissingCompatibilityBaseIssue(ProductWarning):
	title = "Missing Compatibility Base for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/adding_metadata/start'
	description = "Metadata contains no Compatibility Base for Asset"

class MetadataHasDescriptionIssue(ProductNotice):
	title = "Description for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/adding_metadata/start'
	description = "Asset Description should usually be left blank"

class MetadataHasUserwordsIssue(ProductWarning):
	title = "Userwords for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/adding_metadata/start'
	description = "Asset Userwords are reserved for end users and should not be included in metadata"

class MetadataDuplicateCategoriesUsedIssue(ProductWarning):
	title = "Duplicate Categories for Assets(s) in metadata"
	description = "Metadata Categories for Asset should only be listed once per asset"

class MetadataParentCategoriesUsedIssue(ProductWarning):
	title = "Non most specific Categories for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/adding_metadata/start'
	description = "Metadata Categories for Asset should only list the most specific sub-categories"

class MetadataSpecialCategoriesUsedIssue(ProductWarning):
	title = "Special Categories for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/referenceguide/interface/panes/smart_content/products_page/category_view/start'
	description = "Metadata Categories for Asset should not include Special categories"

class MetadataUserCategoriesUsedIssue(ProductWarning):
	title = "User Categories for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/referenceguide/interface/panes/smart_content/products_page/category_view/start'
	description = "Metadata Categories for Asset should not include User categories"

class MetadataDeprecatedContentTypeIssue(ProductWarning):
	title = "Deprecated Content Type for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/dson_spec/format_description/metadata/content_types/start'
	description = "Metadata contains deprecated Content Type for Asset"

class MetadataDeprecatedCategoriesIssue(ProductWarning):
	title = "Deprecated Categor(y|ies) for Assets(s) in metadata"
	reference = 'http://docs.daz3d.com/doku.php/public/dson_spec/format_description/metadata/categories/start'
	description = "Metadata contains deprecated Category for Asset"

class MetadataWrongShaderTypeIssue(ProductWarning):
	title = "Wrong Material or Shader type for Assets(s) in metadata"
	description = "Metadata contains the wrong Material or Shader type for Asset"

class MetadataNonspecificShaderTypeIssue(ProductNotice):
	title = "Nonspecific Material or Shader type for Assets(s) in metadata"
	description = "Metadata Content Type for Material and Shader Asset should specify the Shader type when possible"
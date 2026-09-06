from . import ProductWarning, ProductNotice

class InvalidDSONFilesIssue(ProductWarning):
	title = 'Invalid DSON file(s) in Content directory'
	reference = 'http://docs.daz3d.com/doku.php/public/dson_spec/start'
	description = "Content directory contains invalid DSON file(s)"

class SourceFileReferencesIssue(ProductNotice):
	title = 'Source file reference(s) in DSON file(s)'
	description = "Path to source file included in DSON file(s)"

class AssetIDMismatchFilesIssue(ProductNotice):
	title = 'Asset ID mismatch(es) in DSON file(s)'
	description = "Asset ID in DSON file does not match filename"

class DuplicateIDsInFilesIssue(ProductWarning):
	title = 'Duplicate ID(s) in file(s)'
	description = "An ID may only be defined once per file"

class RootNodeWithNonStandardOrientationInFilesIssue(ProductNotice):
	title = 'Root node with non standard orientation in file(s)'
	description = ("Using non standard orientation on root nodes can be confusing when not intentional. "
		           "It often occurs unintentionally when importing objects from FBX.")

class GeometryInDUFFilesIssue(ProductWarning):
	title = 'Geometry in DSON User File(s) (*.duf)'
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/packaging_genesis_morph_products/start'
	description = "Geometry should be saved as Support Assets, to prevent being resaved in user's Scene file"

class UVSetInDUFFilesIssue(ProductWarning):
	title = 'UV Set(s) in DSON User File(s) (*.duf)'
	reference = 'http://docs.daz3d.com/doku.php/public/publishing/uv_update_replace/start'
	description = ("UV sets should be saved as Support Assets, to prevent being resaved in user's Scene file. If this item is also listed "
	               "as having a Geometry in DSON User File(s) issue, solving that issue should also solve this issue.")

class MorphInDUFFilesIssue(ProductWarning):
	title = 'Morph(s) in DSON User File(s) (*.duf)'
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/saving_morphs/start#custom_or_dialed_morphs'
	description = "Morphs should be saved as Support Assets, to prevent being resaved in user's Scene file"

class ShaderInDUFFilesIssue(ProductWarning):
	title = 'Custom Shader(s) in DSON User File(s) (*.duf)'
	description = "Custom Shaders should be saved as Support Assets, to prevent being resaved in user's Scene file"

class FavoriteInMaterialInDUFFilesIssue(ProductWarning):
	title = 'Favorite(s) in Materials(s) in DSON User File(s) (*.duf)'
	description = "Favorites should not be set in distributed files"

class FavoriteInNodePropertyInDUFFilesIssue(ProductWarning):
	title = 'Favorite(s) in Node Properties(s) in DSON User File(s) (*.duf)'
	description = "Favorites should not be set in distributed files"

class NormalMapInNonNormalMapChannelInDUFFilesIssue(ProductWarning):
	title = 'Possible Normal Map(s) in Non-Normal Map channel(s) in DSON User File(s) (*.duf)'
	description = ("Normal Maps should only be used in Normal Map channels. "
	               "This is heuristically determined, and may have incorrect results.")

class NonNormalMapInNormalMapChannelInDUFFilesIssue(ProductWarning):
	title = 'Possible Non-normal Map(s) in Normal Map channel(s) in DSON User File(s) (*.duf)'
	description = ("Only Normal Maps should be used in Normal Map channels. "
	               "This is heuristically determined, and may have incorrect results.")

class TextureMapSavedInLossyFormatIssue(ProductWarning):
	title = 'Texture Map(s) saved in lossy format'
	description = "Texture maps should be in a lossless format to prevent banding and other artifacts."

class TextureMapSavedWithInsufficientBitDepthIssue(ProductWarning):
	title = 'Texture Map(s) saved with insufficient bit depth'
	description = "Normal and displacement texture maps should be in a 16+bit format to prevent banding and other artifacts."

class TextureMapSavedWithTooManyChannelsIssue(ProductWarning):
	title = 'Texture Map(s) saved with too many channels'
	description = "Bump and displacement texture maps should be grayscale and contain only one channel of data."

class ActiveMorphsInDSFFilesIssue(ProductWarning):
	title = 'Active Morph(s) in DSON Support File(s) (*.dsf)'
	description = "Morphs should be set to 0 or False when saved as Support Assets. Use Presets to set active values."

class MorphLoaderGroupInDSFFilesIssue(ProductWarning):
	title = 'Morph(s) in "Morphs/Morph Loader" property group in DSON Support File(s) (*.dsf)'
	description = ("Morphs should be reassigned from the 'Morphs/Morph Loader' property group to an appropriate "
	               "group for filtering.")

class TonemapperOptionsInDUFFilesIssue(ProductWarning):
	title = 'Tonemapper Options unexpectedly included in DSON User File(s) (*.duf)'
	description = "Tonemapper Options should only be included in Scene and Render Settings files"

class EnvironmentOptionsInDUFFilesIssue(ProductWarning):
	title = 'Environment Options unexpectedly included in DSON User File(s) (*.duf)'
	description = "Environment Options should only be included in Scene and Render Settings files"

class HiddenParameterNotInHiddenCategoryInFilesIssue(ProductWarning):
	title = 'Hidden parameter(s) not in hidden category in DSON file(s)'
	description = "Hidden parameters should be in a hidden category"

class NonHiddenParameterInHiddenCategoryInFilesIssue(ProductWarning):
	title = 'Non hidden parameter(s) in hidden category in DSON file(s)'
	description = "All parameters in a hidden category should be hidden"

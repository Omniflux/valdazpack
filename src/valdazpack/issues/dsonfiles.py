from . import ProductWarning, ProductNotice

class InvalidDSONFilesIssue(ProductWarning):
	title = 'Invalid DSON file(s) in Content directory'
	reference = 'http://docs.daz3d.com/doku.php/public/dson_spec/start'
	description = "Content directory contains invalid DSON file"

class AssetIDMismatchFilesIssue(ProductNotice):
	title = 'Asset ID mismatch(es) in DSON file(s)'
	description = "Asset ID in DSON file does not match filename"

class DuplicateIDsInFilesIssue(ProductWarning):
	title = 'Duplicate ID(s) in file(s)'
	description = "An ID may only be defined once per file"

class DuplicateFormulasInMorphsIssue(ProductWarning):
	title = 'Duplicate formula(s) in morph(s)'
	description = "Each formula target may only occur once per morph"

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

class ActiveMorphsInDSFFilesIssue(ProductWarning):
	title = 'Active Morph(s) in DSON Support File(s) (*.dsf)'
	description = "Morphs should be set to 0 or False when saved as Support Assets. Use Presets to set active values."

class MorphLoaderGroupInDSFFilesIssue(ProductWarning):
	title = 'Morph(s) in "Morphs/Morph Loader" property group in DSON Support File(s) (*.dsf)'
	description = ("Morphs should be reassigned from the 'Morphs/Morph Loader' property group to an appropriate "
	               "group for filtering.")
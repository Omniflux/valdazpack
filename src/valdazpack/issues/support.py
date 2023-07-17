from . import ProductWarning

class MissingMetadataFilesIssue(ProductWarning):
	title = 'Missing Metadata file(s)'
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/adding_metadata/start'
	description = "Product should provide a metadata file"

class SubdirectoriesInRuntimeSupportIssue(ProductWarning):
	title = 'Unexpected subdirector(y|ies) in Runtime/Support'
	description = "Runtime/Support should not contain subdirectories"

class UnexpectedFilesInRuntimeSupportIssue(ProductWarning):
	title = 'Unexpected file(s) in Runtime/Support'
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/referenceguide/interface/panes/smart_content/products_page/results_view/'
	description = "Files in Runtime/Support should have the same stem as the DSX file providing metadata"

class MissingMetadataIconFilesIssue(ProductWarning):
	title = 'Missing Metadata Icon file(s)'
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/referenceguide/interface/panes/smart_content/products_page/results_view/'
	description = "Product should provide an icon with metadata"

class MissingMetadataScriptFilesIssue(ProductWarning):
	title = 'Missing Metadata Script file(s)'
	description = "Product should provide a default script with metadata"

class RedundantMetadataIconFilesIssue(ProductWarning):
	title = 'Redundant Metadata Icon file(s)'
	reference = 'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/change_log_4_9_4_122#4_9_4_31'
	description = "Metadata Icon files should not be provided in multiple formats"

class UndersizedMetadataIconFilesIssue(ProductWarning):
	title = 'Undersized Metadata Icon file(s)'
	reference = [
		'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/userguide/creating_content/packaging/tutorials/adding_metadata/start',
		'http://docs.daz3d.com/doku.php/public/software/dazstudio/4/referenceguide/interface/panes/smart_content/products_page/results_view/start']
	description = "Metadata Icon files should be 114x148 pixels or larger"
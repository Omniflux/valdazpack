from .validationdata import ValidationData
from ..rules.datadirectory import ValidateDataDirectory
from ..rules.dsonfiles import ValidateDSONFiles
from ..rules.metadatafiles import ValidateMetadataFiles
from ..rules.package import ValidatePackages
from ..rules.packagemanifest import ValidatePackageManifests
from ..rules.packagesupplementfile import ValidateSupplementFiles
from ..rules.contentdirectory import ValidateContentDirectory
from ..rules.runtimedirectory import ValidateRuntimeDirectory
from ..rules.runtimelibrariesdirectory import ValidateRuntimeLibrariesDirectory
from ..rules.runtimegeometriesdirectory import ValidateRuntimeGeometriesDirectory
from ..rules.runtimesupportdirectory import ValidateRuntimeSupportDirectory
from ..rules.zipfile import ValidateZipFiles

def validate(data: ValidationData) -> None:
	rules = [
		ValidateZipFiles,
		ValidatePackages,
		ValidatePackageManifests,
		ValidateSupplementFiles,
		ValidateRuntimeSupportDirectory,
		ValidateRuntimeDirectory,
		ValidateRuntimeGeometriesDirectory,
		ValidateRuntimeLibrariesDirectory,
		ValidateDSONFiles,
		ValidateDataDirectory,	# data.dependency_files, data.postload_files must be populated by ValidateDSONFiles, etc. before this step
		ValidateContentDirectory,	# data.vendor_paths, data.referenced_files, data.missing_referenced_files must be populated by ValidateRuntimeDirectory, ValidateDataDirectory, ValidateDSONFiles, etc. before this step
		ValidateMetadataFiles,	# data.shader_users must be populated by ValidateDSONFiles, etc. before this step
	]

	for r in rules:
		r(data)
from pytest_mock import MockerFixture

from fs.wrapcifs import WrapCaseInsensitive
from pathlib import Path

from valdazpack.validator import ValidationData, validate
from valdazpack.issues.contentdirectory import (
	CaseInsensitivePathCollision,
	FilesInRootOfContentDirectoryIssue,
	ExcessContentDirectoryIssue,
	EmptyDirectoriesIssue,
	GratuitousFilesIssue,
	EmptyFilesIssue,
	InvalidDJLFilesIssue,
	UnnecessaryThumbnailsForDJLIssue,
	UncommonDirectoryInRootOfContentDirectoryIssue,
	FilesInVendorDazDirectoryIssue,
	FilesReferenceNonexistentFilesIssue,
	FilesReferenceAbsolutePathsIssue,
	LegacyFilesIssue,
	UnreferencedFilesInTexturesDirectoryIssue
)

from .conftest import mockExistsWithoutFile

def test_CaseInsensitivePathCollision(validatorINVALID: ValidationData):
	assert any(isinstance(x, CaseInsensitivePathCollision) for x in validatorINVALID.issues.product)

def test_FilesInRootOfContentDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesInRootOfContentDirectoryIssue) for x in validatorINVALID.issues.product)

def test_ExcessContentDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, ExcessContentDirectoryIssue) for x in validatorINVALID.issues.product)

def test_EmptyDirectoriesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, EmptyDirectoriesIssue) for x in validatorINVALID.issues.product)

def test_GratuitousFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, GratuitousFilesIssue) for x in validatorINVALID.issues.product)

def test_EmptyFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, EmptyFilesIssue) for x in validatorINVALID.issues.product)

def test_FilesInVendorDazDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesInVendorDazDirectoryIssue) for x in validatorINVALID.issues.product)

def test_InvalidDJLFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, InvalidDJLFilesIssue) for x in validatorINVALID.issues.product)

def test_UnnecessaryThumbnailsForDJLIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UnnecessaryThumbnailsForDJLIssue) for x in validatorINVALID.issues.product)

def test_UnnecessaryThumbnailsForDJLNonIssue(dimzipfileINVALID: Path, mocker: MockerFixture):
	v = ValidationData([dimzipfileINVALID])
	mocker.patch('fs.wrapcifs.WrapCaseInsensitive.exists', side_effect=mockExistsWithoutFile(WrapCaseInsensitive, 'invalid.png'), autospec=True)
	validate(v)

	assert not any(isinstance(x, UnnecessaryThumbnailsForDJLIssue) for x in v.issues.product)

def test_UncommonDirectoryInRootOfContentDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UncommonDirectoryInRootOfContentDirectoryIssue) for x in validatorINVALID.issues.product)

def test_FilesInVendorDazDirectoryNonIssue(validatorINVALIDdazOriginal: ValidationData):
	assert not any(isinstance(x, FilesInVendorDazDirectoryIssue) for x in validatorINVALIDdazOriginal.issues.product)

def test_FilesReferenceNonexistentFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesReferenceNonexistentFilesIssue) for x in validatorINVALID.issues.product)

def test_FilesReferenceAbsolutePathsIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, FilesReferenceAbsolutePathsIssue) for x in validatorINVALID.issues.product)

def test_LegacyFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, LegacyFilesIssue) for x in validatorINVALID.issues.product)

def test_UnreferencedFilesInTexturesDirectoryIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UnreferencedFilesInTexturesDirectoryIssue) for x in validatorINVALID.issues.product)
from pytest_mock import MockerFixture

from pathlib import Path

from valdazpack.validator import ValidationData, validate
from valdazpack.issues.support import (
	MissingMetadataFilesIssue,
	SubdirectoriesInRuntimeSupportIssue,
	UnexpectedFilesInRuntimeSupportIssue,
	MissingMetadataIconFilesIssue,
	MissingMetadataScriptFilesIssue,
	RedundantMetadataIconFilesIssue,
	UndersizedMetadataIconFilesIssue
)

from .conftest import mockWalkFilesWithoutFiles

def test_MissingMetadataFilesIssue(dimzipfileCUSTOM: Path, mocker: MockerFixture):
	v = ValidationData([dimzipfileCUSTOM])
	mocker.patch('fs.walk.BoundWalker', side_effect=mockWalkFilesWithoutFiles(['Runtime/Support/LOCAL_USER_Valid_Test_Product.dsx']), autospec=True)
	validate(v)

	assert any(isinstance(x, MissingMetadataFilesIssue) for x in v.issues.product)

def test_SubdirectoriesInRuntimeSupportIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, SubdirectoriesInRuntimeSupportIssue) for x in validatorINVALID.issues.product)

def test_UnexpectedFilesInRuntimeSupportIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UnexpectedFilesInRuntimeSupportIssue) for x in validatorINVALID.issues.product)

def test_MissingMetadataIconFilesIssue(dimzipfileCUSTOM: Path, mocker: MockerFixture):
	v = ValidationData([dimzipfileCUSTOM])
	mocker.patch('fs.walk.BoundWalker', side_effect=mockWalkFilesWithoutFiles(['Runtime/Support/LOCAL_USER_Valid_Test_Product.jpg', 'Runtime/Support/LOCAL_USER_Valid_Test_Product.png']), autospec=True)
	validate(v)

	assert any(isinstance(x, MissingMetadataIconFilesIssue) for x in v.issues.product)

def test_MissingMetadataScriptFilesIssue(dimzipfileCUSTOM: Path, mocker: MockerFixture):
	v = ValidationData([dimzipfileCUSTOM])
	mocker.patch('fs.walk.BoundWalker', side_effect=mockWalkFilesWithoutFiles(['Runtime/Support/LOCAL_USER_Valid_Test_Product.dsa']), autospec=True)
	validate(v)

	assert any(isinstance(x, MissingMetadataScriptFilesIssue) for x in v.issues.product)

def test_RedundantMetadataIconFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, RedundantMetadataIconFilesIssue) for x in validatorINVALID.issues.product)

def test_UndersizedMetadataIconFilesIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, UndersizedMetadataIconFilesIssue) for x in validatorINVALID.issues.product)
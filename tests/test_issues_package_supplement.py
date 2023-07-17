from pytest_mock import MockerFixture

from fs.zipfs import ReadZipFS
from pathlib import Path

from valdazpack.validator import ValidationData, validate
from valdazpack.issues.supplementfile import (
	MissingPackageSupplementIssue,
	InvalidPackageSupplementIssue,
	EmbeddedPackageSupplementElementIssue,
	MismatchedPackageSupplementProductNameIssue,
	IncorrectPackageSupplementProductStoreIDXIssue
)

from .conftest import mockOpenBinWithoutFile

def test_MissingPackageSupplementIssue(dimzipfileCUSTOM: Path, mocker: MockerFixture):
	v = ValidationData([dimzipfileCUSTOM])
	mocker.patch('fs.zipfs.ReadZipFS.openbin', side_effect=mockOpenBinWithoutFile(ReadZipFS, 'Supplement.dsx'), autospec=True)
	validate(v)

	assert any(isinstance(x, MissingPackageSupplementIssue) for x in v.issues.package)

def test_InvalidPackageSupplementIssue(validatorINVALIDdsx: ValidationData):
	assert any(isinstance(x, InvalidPackageSupplementIssue) for x in validatorINVALIDdsx.issues.package)

def test_EmbeddedPackageSupplementElementIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, EmbeddedPackageSupplementElementIssue) for x in validatorINVALID.issues.package)

def test_MismatchedPackageSupplementProductNameIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, MismatchedPackageSupplementProductNameIssue) for x in validatorINVALID.issues.package)

def test_IncorrectPackageSupplementProductStoreIDXIssue(validatorINVALID: ValidationData):
	assert any(isinstance(x, IncorrectPackageSupplementProductStoreIDXIssue) for x in validatorINVALID.issues.package)
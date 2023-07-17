from fs.osfs import OSFS
from pathlib import Path

from valdazpack.validator import ValidationData, validate
from valdazpack.issues.package import (
	PackageNameIssue,
	CustomPackageNameIssue,
	StandardPackageNameIssue
)

from .conftest import createZipFromData

def test_PackageNameIssue(osFS: OSFS):
	dimzip = createZipFromData(osFS, 'valid', '00013176-02_ValidTestProduct')

	v = ValidationData([dimzip])
	validate(v)
	assert any(isinstance(x, PackageNameIssue) for x in v.issues.package)

	v = ValidationData([dimzip], daz=True)
	validate(v)
	assert any(isinstance(x, PackageNameIssue) for x in v.issues.package)

def test_StandardPackageNameIssue(osFS: OSFS):
	dimzip = createZipFromData(osFS, 'valid', 'IM00013176-02_ValidTestProduct')

	v = ValidationData([dimzip])
	validate(v)
	assert not v.daz and any(isinstance(x, StandardPackageNameIssue) for x in v.issues.package)

	v = ValidationData([dimzip], daz=True)
	validate(v)
	assert v.daz and not any(isinstance(x, StandardPackageNameIssue) for x in v.issues.package)

def test_CustomPackageNameIssue(dimzipfileCUSTOM: Path):
	v = ValidationData([dimzipfileCUSTOM])
	validate(v)
	assert not v.daz and not any(isinstance(x, CustomPackageNameIssue) for x in v.issues.package)

	v = ValidationData([dimzipfileCUSTOM], daz=True)
	validate(v)
	assert v.daz and any(isinstance(x, CustomPackageNameIssue) for x in v.issues.package)
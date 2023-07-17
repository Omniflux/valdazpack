import pytest

from fs.osfs import OSFS
from pathlib import Path
from zipfile import ZipFile

from valdazpack.validator import ValidationData, validate
from valdazpack.issues.zipfile import PathCollisionsInZipFile

@pytest.mark.filterwarnings("ignore:Duplicate name")
def test_MultipleFilesWithSameName(osFS: OSFS):
	zipfile = osFS.getsyspath('') + 'duplicate_entries.zip'
	zip = ZipFile(zipfile , 'w')
	zip.writestr('test', '')
	zip.writestr('test', '')
	zip.close()

	v = ValidationData([Path(zipfile)])
	validate(v)
	assert any(isinstance(x, PathCollisionsInZipFile) for x in v.issues.package)
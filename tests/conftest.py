import pytest

from fs.memoryfs import MemoryFS
from pathlib import Path
from typing import Any

from fs.base import FS
from fs.errors import ResourceNotFound
from fs.osfs import OSFS
from fs.walk import BoundWalker
from fs.zipfs import WriteZipFS

from valdazpack.validator import ValidationData, validate

def createZipFromData(osFS: OSFS, srcname: str, zipname: str | None = None):
	zipFilename = f'{zipname if zipname else srcname}.zip'
	if not osFS.exists(zipFilename):
		with osFS.openbin(zipFilename, 'w') as file:
			WriteZipFS(file, temp_fs=OSFS(f'tests/data/{srcname}'))

	return (Path(osFS.root_path, zipFilename))

def mockExistsWithoutFile(fs: type[FS], filepath: str):
	fs_exists = fs.exists
	def exists(self: FS, path: str, *args: Any, **kwargs: Any):
		if path == filepath:
			return False
		return fs_exists(self, path, *args, **kwargs)

	return exists

def mockOpenBinWithoutFile(fs: type[FS], filepath: str):
	fs_openbin = fs.openbin
	def openbin(self: FS, path: str, *args: Any, **kwargs: Any):
		if path == filepath:
			raise ResourceNotFound(path)
		return fs_openbin(self, path, *args, **kwargs)

	return openbin

def mockWalkFilesWithoutFiles(filepath: list[str]):
	fs_boundwalker = BoundWalker
	def boundwalker(*args: Any, **kwargs: Any):
		def _without_files(*args: Any, **kwargs: Any):
			for f in bw_files(*args, **kwargs):
				if f not in filepath:
					yield f

		bw = fs_boundwalker(*args, **kwargs)
		bw_files = bw.files
		bw.files = _without_files
		return bw

	return boundwalker

@pytest.fixture(scope='package')
def osFS(tmp_path_factory: pytest.TempPathFactory):
	return OSFS(tmp_path_factory.mktemp('data').as_posix())

@pytest.fixture(scope="package")
def zipfile(osFS: OSFS):
	return createZipFromData(osFS, 'zip')

@pytest.fixture(scope="package")
def dimzipfileCUSTOM(osFS: OSFS):
	return createZipFromData(osFS, 'valid', 'CUSTOM00013176-02_ValidTestProduct')

@pytest.fixture(scope="package")
def dimzipfileINVALID(osFS: OSFS):
	return createZipFromData(osFS, 'invalid', 'CUSTOM00013176-02_InvalidTestProduct')

@pytest.fixture(scope="package")
def dimzipfileINVALIDdsx(osFS: OSFS):
	return createZipFromData(osFS, 'invalid-dsx', 'CUSTOM00013176-02_InvalidManifestAndSupplement')

@pytest.fixture(scope="package")
def validatorINVALID(osFS: OSFS, dimzipfileINVALID: Path):
	v = ValidationData([dimzipfileINVALID])

	m = MemoryFS()
	m.create('readme.txt')
	v.product_fs_unwrapped.add_fs('collision', m)

	validate(v)

	return v

@pytest.fixture(scope="package")
def validatorINVALIDPoser(osFS: OSFS, dimzipfileINVALID: Path):
	v = ValidationData([dimzipfileINVALID], poser=True)
	validate(v)

	return v

@pytest.fixture(scope="package")
def validatorINVALIDdazOriginal(osFS: OSFS, dimzipfileINVALID: Path):
	v = ValidationData([dimzipfileINVALID], daz_original=True)
	validate(v)

	return v

@pytest.fixture(scope="package")
def validatorINVALIDdsx(osFS: OSFS, dimzipfileINVALIDdsx: Path):
	v = ValidationData([dimzipfileINVALIDdsx])
	validate(v)

	return v
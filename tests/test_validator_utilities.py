import gzip

from pytest_mock import MockerFixture

from fs.memoryfs import MemoryFS
from pathlib import Path

from valdazpack.validator import ValidationData
from valdazpack.validator.utilities import (
	alpha_numeric,
	checkDirectoryHasSelfAsChild,
	checkImageDir, checkTypo,
	checkVendorDirsOnly,
	decompressDSON,
	thumbnailsFor,
	trackDependencyIfExists
)
from valdazpack.validator.resources import (
	read_datafile_bytes,
	read_list_from
)

#_create_merged_fs
#_get_unwrapped_fs

def test_alpha_numeric():
	assert alpha_numeric("A B C 123 !@#_-") == 'ABC123'

def test_checkDirectoryHasSelfAsChild(dimzipfileINVALID: Path):
	v = ValidationData([dimzipfileINVALID])
	assert checkDirectoryHasSelfAsChild(v.product_fs, 'Runtime')
	assert not checkDirectoryHasSelfAsChild(v.product_fs, 'Runtime/Support')

def test_checkVendorDirsOnly(dimzipfileINVALID: Path):
	v = ValidationData([dimzipfileINVALID])
	assert checkVendorDirsOnly(v, 'Runtime/Textures') == ['Image.jpg', 'Image.bmp']
	assert v.vendor_paths == {'DAZ 3D': {'Runtime/Textures/DAZ 3D'}, 'Textures': {'Runtime/Textures/Textures'}}

def test_checkImageDir(dimzipfileINVALID: Path):
	v = ValidationData([dimzipfileINVALID])
	assert checkImageDir(v.product_fs, 'Runtime/Textures', set(['.png'])) == (
		['Runtime/Textures/DAZ 3D/ReadMe.txt'],
		['Runtime/Textures/Image.jpg', 'Runtime/Textures/Image.bmp'],
		['Runtime/Textures/Image.bmp'],
		{'Runtime/Textures/Image.jpg': 'image/png'}
	)

def test_checkTypo():
	assert checkTypo('Enviroment', ['Environment', 'Shader Presets']) == ['Environment']

def test_decompressDSON():
	fs = MemoryFS()
	with fs.openbin('test', 'w') as file:
		file.write(b'test')

	with fs.openbin('test', 'r') as file:
		with decompressDSON(file) as f:
			assert f.read() == b'test'

	with fs.openbin('testgz', 'w') as file:
		with gzip.open(file, 'wb') as f:
			f.write(b'testgz')

	with fs.openbin('testgz', 'r') as file:
		with decompressDSON(file) as f:
			assert f.read() == b'testgz'

def test_thumbnailsFor(dimzipfileINVALID: Path):
	v = ValidationData([dimzipfileINVALID])
	assert thumbnailsFor(v.product_fs, 'Invalid.djl') == (['Invalid.png'], [])
	
def test_trackDependencyIfExists(dimzipfileINVALID: Path):
	v = ValidationData([dimzipfileINVALID])
	assert trackDependencyIfExists(v, 'GoodLink.djl', 'Somefile.duf')
	assert not trackDependencyIfExists(v, 'NonexistantLink.djl', 'Somefile.duf')
	assert v.referenced_files == {'GoodLink.djl': set(['Somefile.duf'])}
	
def test_read_datafile_bytes(mocker: MockerFixture):
	mocker.patch('valdazpack.validator.resources.resources.files', return_value=Path('tests'))
	assert read_datafile_bytes('list.txt') == b'# Test list file\r\nABC\r\n123 #DEF\r\n\r\nGHI#JKL    #456'

def test_read_list_from(mocker: MockerFixture):
	mocker.patch('valdazpack.validator.resources.resources.files', return_value=Path('tests'))
	assert list(read_list_from('list.txt')) == ['ABC', '123', 'GHI#JKL']
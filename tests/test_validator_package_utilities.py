from pathlib import Path
from uuid import UUID

from valdazpack.validator import ValidationData
from valdazpack.validator.package import PackageType

def test_package(dimzipfileCUSTOM: Path, dimzipfileINVALID: Path):
	v = ValidationData([dimzipfileCUSTOM])

	assert v.packages[0].path == dimzipfileCUSTOM
	assert v.packages[0].parsed == { 'prefix': 'CUSTOM', 'sku': '00013176', 'id': '02', 'name': 'ValidTestProduct' }
	assert v.packages[0].type == PackageType.CUSTOM
	assert v.packages[0].product_store_idx == '77732743000013176-02'
	assert v.packages[0].product_file_guid == UUID('30b46b76-ef1c-df6c-c0ad-f7a53b627778')

	assert ValidationData([dimzipfileINVALID]).packages[0] < v.packages[0]
import re

from enum import Enum
from hashlib import md5
from pathlib import Path
from typing import cast, Self, TypedDict
from uuid import UUID

from fs.dimzipfs import DIMZipFS

from .resources import read_list_from

class PackageType(Enum):
	"""Whether package is a standard or custom package."""

	STANDARD = 0
	CUSTOM = 1

class ParsedPackageFilename(TypedDict):
	"""Data extracted from package filename."""

	prefix: str
	sku: str
	id: str | None
	name: str

class Package:
	"""Data for a package.

	Arguments:
		package (DIMZipFS): `DIMZipFS` pyfilesystem2 filesystem
	"""

	def __init__(self, package: DIMZipFS) -> None:
		path = package.delegate_fs()._file  # pyright: ignore[reportPrivateUsage]
		if not isinstance(path, str):
			raise ValueError

		self.path = Path(path)
		self.root_fs = package.delegate_fs()
		self.parsed: ParsedPackageFilename | None = None
		self.type: PackageType | None = None
		self.product_name: str | None = None
		self.product_store_idx: str | None = None
		self.product_file_guid = self._calculateProductFileGUID()
		self.readme: bool = False

		if self.path and (matches := re.match(r'^(?P<prefix>[A-Z][0-9A-Z]{0,6})(?=\d{8})(?P<sku>\d{8})(-(?P<id>\d{2}))?_(?P<name>[0-9A-Za-z]+)\.zip$', self.path.name)):
			self.parsed = cast(ParsedPackageFilename, matches.groupdict())

		if self.parsed:
			self.type = PackageType(self.parsed['prefix'] not in read_list_from('daz/reserved_package_prefixes.txt'))

			if self.type == PackageType.STANDARD:
				self.product_store_idx = f"{self.parsed['sku'].lstrip('0')}"
			else:
				self.product_store_idx = f"{str(int(self.parsed['prefix'], 36))}{self.parsed['sku']}"
			
			if self.parsed['id']:
				self.product_store_idx += f"-{self.parsed['id']}"

	def __lt__(self, other: Self) -> bool:
		return self.path.name < other.path.name

	def _calculateProductFileGUID(self) -> UUID:
		"""Calculate `ProductFileGUID` used in DIM generated `Supplement.dsx` stored outside of product zip."""

		hash = md5()

		with open(self.path, 'rb') as file:
			while chunk := file.read(hash.digest_size * hash.block_size * 8):
				hash.update(chunk)

		return UUID(bytes = hash.digest())
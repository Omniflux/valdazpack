from pathlib import Path
from typing import cast, Type, TypeVar

from fs.base import FS
from fs.dimzipfs import DIMZipFS
from fs.errors import CreateFailed
from fs.multifs import MultiFS
from fs.opener import open_fs
from fs.opener.errors import OpenerError
from fs.opener.parse import parse_fs_url
from fs.path import relpath
from fs.wrapcifs import WrapCaseInsensitive
from fs.zipfs import ReadZipFS

from .issues import PackageNotice, PackageWarning, ProductNotice, ProductWarning
from .package import Package

class ValidationData:
	"""Stores data on what to validate and data discovered during validation.

	Arguments:
		product_path (list[pathlib.Path]): A list of files or directories making up the product to validate
		dependencies_paths (list[pathlib.Path]): A list of files or directories the product may reference
		                                         but that are not part of the product to validate
		daz (bool): Validate as if this is a product distributed by Daz Productions, Inc
		daz_original (bool): Validate as if this is a product produced by Daz Productions, Inc
		poser (bool): Validate using rules for Poser content (experimental)
		dson_schema (bool): Validate DSON schema (experimental)
		verbose (bool): Enable verbose output
	"""

	class Issues:
		"""Stores issues discovered during validaiton."""

		def __init__(self) -> None:
			self.package: list[PackageNotice | PackageWarning] = []
			self.product: list[ProductNotice | ProductWarning] = []

	class MetaData:
		"""Stores metadata information discovered during validation."""

		def __init__(self) -> None:
			self.products: list[str] = []
			self.artists: set[str] = set()
			self.stores: set[str] = set()

	def __init__(self, product_paths: list[Path], dependencies_paths: list[Path] | None = None, daz: bool = False, daz_original: bool = False, poser: bool = False, dson_schema: bool = False, verbose: bool = False) -> None:
		self.product_paths = product_paths
		self.dependency_paths = dependencies_paths
		self.poser = poser
		self.daz = daz or daz_original
		self.daz_original = daz_original
		self.dson_schema = dson_schema
		self.verbose = verbose

		self.product_fs_unwrapped = _create_merged_fs(product_paths)
		self.product_fs = WrapCaseInsensitive(self.product_fs_unwrapped)
		self.filesystem_unwrapped = _create_merged_fs((dependencies_paths or []) + product_paths)
		self.filesystem = WrapCaseInsensitive(self.filesystem_unwrapped)
		
		self.packages = [Package(dfs) for fs in self.product_fs_unwrapped.iterate_fs() if (dfs := _get_unwrapped_fs(fs[1], DIMZipFS))]
		self.zips = [zfs for fs in self.product_fs_unwrapped.iterate_fs() if (zfs := _get_unwrapped_fs(fs[1], ReadZipFS))]

		self.issues = self.Issues()
		self.metadata = self.MetaData()
		self.contributors: dict[str, dict[str, set[str]]] = {}

		self.vendor_paths: dict[str, set[str]] = {}
		self.dependency_files: dict[str, dict[str, set[str]]] = {}
		self.referenced_files: dict[str, set[str]] = {}
		self.missing_referenced_files: dict[str, set[str]] = {}
		self.shader_users: dict[str, set[str]] = {}
		self.postload_files: set[str] = set()


def _create_merged_fs(filesystems: list[Path]) -> MultiFS:
	def _path_to_fs(path: Path) -> FS:
		for f in [f'dimzip://{path.as_posix()}', f'zip://{path.as_posix()}', f'osfs://{path.as_posix()}']:
			try:
				if isinstance(fs := open_fs(f), DIMZipFS):
					if fs.isdir('Content'):
						fs = fs.opendir('Content')  # pyright: ignore[reportUnknownMemberType]
					else:
						raise ValueError(f'DIM ZIP does not have Content: {path}')
				elif isinstance(fs, ReadZipFS):
					if subpath := cast(str | None, parse_fs_url(f).path):  # pyright: ignore[reportUnknownMemberType]
						fs = fs.opendir(relpath(subpath.lstrip('\\')))  # pyright: ignore[reportUnknownMemberType]
				return fs
			except (CreateFailed, OpenerError):
				continue

		raise ValueError(f'Not a ZIP file or directory: {path}')

	fs = MultiFS()
	for f in filesystems:
		fs.add_fs(f.as_posix(), _path_to_fs(f))

	return fs

T = TypeVar('T', bound=FS)
def _get_unwrapped_fs(fs: FS, fs_type: Type[T]) -> T | None:
	if isinstance(fs, fs_type):
		return fs
	else:
		try:
			return _get_unwrapped_fs(fs.delegate_fs(), fs_type)  # pyright: ignore[reportGeneralTypeIssues, reportUnknownArgumentType, reportUnknownMemberType]
		except AttributeError:
			pass
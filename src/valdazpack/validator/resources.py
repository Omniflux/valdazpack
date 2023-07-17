from importlib import resources
from typing import Generator

def read_datafile_bytes(path: str) -> bytes:
	"""Get resource data file from package as bytes."""

	resource = resources.files(__name__.split('.', 1)[0]) / 'data' / path
	return resource.read_bytes()

def read_list_from(path: str) -> Generator[str, None, None]:
	"""Get resource data file from package as text."""

	resource = resources.files(__name__.split('.', 1)[0]) / 'data' / path
	with resource.open() as file:
		for line in file:
			line = line.split(' #')[0].strip()
			if line and not line.startswith('#'):
				yield line
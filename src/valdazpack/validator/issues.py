from abc import ABC
from collections.abc import Iterable

Detail = str | Exception | Iterable['Detail'] | tuple[str, 'Detail']

class ValidationIssue(ABC):
	"""Abstract base class for recording issues discovered during validation.

	Subclasses must set title and description.
	Subclasses may set reference.

	Arguments:
		detail (str | Iterable[str]): details of issue discovered
	"""

	type: str
	title: str
	description: str
	reference: str | list[str] = ''

	def __init__(self, detail: Detail | None = None) -> None:
		self.detail = detail

	def __str__(self) -> str:
		return f"{self.title}{f': {self.detail}' if self.detail else ''}\n{self.description}\n{self.reference}"

class ValidationNotice(ValidationIssue):
	"""Notice level issue."""

	type = 'NOTICE'

	def __str__ (self) -> str:
		return f'{type}: ' + super().__str__()

class ValidationWarning(ValidationIssue):
	"""Warning level issue."""

	type = 'WARNING'

	def __str__ (self) -> str:
		return f'{type}: ' + super().__str__()

class PackageNotice(ValidationNotice):
	"""Notice level package issue."""
	pass

class PackageWarning(ValidationWarning):
	"""Warning level package issue."""
	pass

class ProductNotice(ValidationNotice):
	"""Notice level product issue."""
	pass

class ProductWarning(ValidationWarning):
	"""Warning level product issue."""
	pass
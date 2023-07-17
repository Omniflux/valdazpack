from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Concatenate, ParamSpec, TypeVar

from .issues import PackageNotice, PackageWarning, ProductNotice, ProductWarning
from .validationdata import ValidationData

P = ParamSpec('P')
T = TypeVar('T')
R = TypeVar('R', bound='Ruleset')

def rule(func: Callable[Concatenate[R, P], T]) -> Callable[Concatenate[R, P], T]:
	"""Decorator to print rule name."""

	@wraps(func)
	def wrapper(self: R, *args: P.args, **kwargs: P.kwargs) -> T:
		if self.data.verbose:
			if len(args):
				print(func.__qualname__, [*args])
			else:
				print(func.__qualname__)
		return func(self, *args, **kwargs)

	return wrapper

class Ruleset(ABC):
	"""Abstract base class for validation rules.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def __init__(self, data: ValidationData) -> None:
		self.data = data
		self._validate()

	@abstractmethod
	def _validate(self) -> None:
		if self.data.verbose:
			print (self.__class__.__qualname__)

class PackageRuleset(Ruleset):
	"""Abstract base class for package validation rules.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def _addIssue(self, issue: PackageNotice | PackageWarning) -> None:
		"""Add issue to validation data."""

		self.data.issues.package.append(issue)

class ProductRuleset(Ruleset):
	"""Abstract base class for product validation rules.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def _addIssue(self, issue: ProductNotice | ProductWarning) -> None:
		"""Add issue to validation data."""

		self.data.issues.product.append(issue)
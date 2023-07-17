from collections import defaultdict
from os.path import normpath
from zipfile import ZipFile

from ..issues import zipfile as issues
from ..validator.ruleset import Ruleset, rule

class ValidateZipFiles(Ruleset):
	"""Perform zip file validation of product.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()

		self.collisions: dict[str, list[list[str]]] = {}
		for zip in self.data.zips:
			self._checkPathCollisions(zip._zip)  # pyright: ignore[reportPrivateUsage]

		if self.collisions:
			self.data.issues.package.append(issues.PathCollisionsInZipFile(self.collisions))

	@rule
	def _checkPathCollisions(self, zip: ZipFile) -> None:
		"""Check product zip file for path collisions.

		A ZIP archive may contain `a/b`, `a/b`, and `a\\b`, and still be valid
		but this will not extract in a useful way with most tools.
		"""

		path_count: dict[str, list[str]] = defaultdict(list)
		for entry in zip.namelist():
			path_count[normpath(entry)].append(entry)
		
		if path_collisions := [entries for entries in path_count.values() if len(entries) > 1]:
			self.collisions[zip.filename or 'Unknown'] = path_collisions
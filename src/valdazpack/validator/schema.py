import json
import jsonschema

from pathlib import Path
from typing import cast, Any, BinaryIO

from fs.iotools import RawWrapper
from lxml import etree

from .resources import read_datafile_bytes

class SchemaCheckedXML():
	"""XML Schema validator

	Arguments:
		xml_file (pathlib.Path | typing.BinaryIO): XML file to validate
		schema (str): Schema name to validate against

	Raises:
		`lxml.etree.DocumentInvalid`
		`FileNotFoundError`
		...
	"""

	cache: dict[str, etree.XMLSchema] = {}

	def __init__(self, xml_file: Path | BinaryIO, schema: str) -> None:
		if not schema in self.cache:
			xmlschema = etree.XMLSchema(etree.fromstring(read_datafile_bytes(f'schemas/{schema}')))
			self.cache[schema] = xmlschema
		else:
			xmlschema = self.cache[schema]

		base_url = xml_file.name if isinstance(xml_file, (BinaryIO, RawWrapper)) else None
		self.tree = etree.parse(xml_file, base_url = base_url)

		xmlschema.assertValid(self.tree)

class SchemaCheckedJSON():
	"""JSON Schema validator

	Arguments:
		json_file (pathlib.Path | typing.BinaryIO): JSON file to validate
		schema (str): Schema name to validate against

	Raises:
		`json.JSONDecodeError`
		`jsonschema.exceptions.ValidationError`
		`jsonschema.exceptions.SchemaError`
		`FileNotFoundError`
		...
	"""

	cache: dict[str, jsonschema.Validator] = {}
	data: dict[str, Any]

	def __init__(self, json_file: Path | BinaryIO, schema: str) -> None:
		if not schema in self.cache:
			schema_data: dict[str, Any] = json.loads(read_datafile_bytes(f'schemas/{schema}'))
			validator = cast(jsonschema.Validator, jsonschema.validators.validator_for(schema_data))  # pyright: ignore[reportGeneralTypeIssues, reportUnknownMemberType]
			validator.check_schema(schema_data)
			self.cache[schema] = validator(schema_data)  # pyright: ignore[reportGeneralTypeIssues, reportUnknownArgumentType]

		validator = self.cache[schema]

		if isinstance(json_file, Path):
			with open(json_file, 'r') as file:
				self.data = json.load(file)
		else:
			self.data = json.load(json_file)

		validator.validate(self.data)
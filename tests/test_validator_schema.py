import pytest

from jsonschema import ValidationError
from pathlib import Path
from lxml.etree import DocumentInvalid

from valdazpack.validator.schema import SchemaCheckedJSON, SchemaCheckedXML

def test_invalid_djl():
	with pytest.raises(ValidationError):
		SchemaCheckedJSON(Path('tests/data/invalid/Content/Invalid.djl'), 'djl.schema.json')

def test_invalid_dsx():
	with pytest.raises(DocumentInvalid):
		SchemaCheckedXML(Path('tests/data/invalid-dsx/Supplement.dsx'), 'Supplement.xsd')

def test_valid_dsx():
	SchemaCheckedXML(Path('tests/data/valid/Supplement.dsx'), 'Supplement.xsd')
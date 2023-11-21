import json
import re

from jsonpath_ng.ext import parse

from typing import Any
from urllib.parse import urlparse, unquote
from warnings import warn

from ..issues import dsonfiles as issues
from ..validator.resources import read_list_from
from ..validator.ruleset import ProductRuleset, rule
from ..validator.schema import SchemaCheckedJSON
from ..validator.utilities import decompressDSON, trackDependencyIfExists

class ValidateDSONFiles(ProductRuleset):
	"""Perform validation of DSON files.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	dson: dict[str, Any]

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()

		# Cache these
		self.ext_file_parsers = [ ({'0': False, '1': True}[(x := line.split(maxsplit=1))[0]], parse(x[1])) for line in read_list_from('daz/dson_external_file_references.txt') ]
		self.geometry_parser = parse('$.geometry_library[*].id')
		self.uvs_parser = parse('$.uv_set_library[*].id')
		self.morphs_parser = parse('$.modifier_library[*].id')
		self.material_daz_brick_parser = parse('$.material_library[?(@.extra[*].type == "studio/material/daz_brick")].id')
		self.asset_type_parser = parse('$.asset_info.type')
		self.preset_shader_parser = parse('$.scene.materials[*].extra[*].type')
		self.preset_shader_count = parse('$.scene.materials[*].extra[*].`len`')
		self.active_morph_parser = parse('$.modifier_library[?(@.channel.value != 0 & @.channel.value != 0)].channel')
		self.probable_path = re.compile(r'\b(data|runtime)\/', re.IGNORECASE)

		self.invalid_dson_files: dict[str, Exception] = {}
		self.asset_id_mismatch_files: dict[str, str] = {}
		self.geometry_in_duf_files: dict[str, list[str]] = {}
		self.uvs_in_duf_files: dict[str, list[str]] = {}
		self.morphs_in_duf_files: dict[str, list[str]] = {}
		self.materials_in_duf_files: dict[str, list[str]] = {}
		self.active_morphs_in_dsf_files: dict[str, list[tuple[str, str]]] = {}
		for filename in self.data.product_fs.walk.files(filter=['*.dsf', '*.duf']):  # pyright: ignore[reportUnknownMemberType]
			dson: dict[str, Any] | None = None

			if self.data.dson_schema:
				with decompressDSON(self.data.product_fs.openbin(filename)) as file:
					try:
						dson = SchemaCheckedJSON(file, 'dson.schema.json').data
					except Exception as e:
						self.invalid_dson_files[filename] = e

			if not dson:
				with decompressDSON(self.data.product_fs.openbin(filename)) as file:
					try:
						dson = json.load(file)
						if not isinstance(dson, dict):
							raise TypeError('Object expected')
					except Exception as e:
						self.invalid_dson_files[filename] = e
	
			if dson:
				self.dson = dson
				self.asset_type: str = getattr(next(iter(self.asset_type_parser.find(dson)), None), 'value', '')

				self._getContributors()
				self._checkAssetID(filename)
				self._checkDSONFileReferences(filename)

				if filename.lower().endswith('.dsf'):
					self._checkActiveMorphsInDSF(filename)

				elif filename.lower().endswith('.duf'):
					self._getShaderTypeInDUF(filename)
					self._checkSupportAssetsInDUF(filename)

		if self.invalid_dson_files:
			self._addIssue(issues.InvalidDSONFilesIssue(self.invalid_dson_files))

		if self.asset_id_mismatch_files:
			self._addIssue(issues.AssetIDMismatchFilesIssue(self.asset_id_mismatch_files))

		if self.geometry_in_duf_files:
			self._addIssue(issues.GeometryInDUFFilesIssue(self.geometry_in_duf_files))

		if self.uvs_in_duf_files:
			self._addIssue(issues.UVSetInDUFFilesIssue(self.uvs_in_duf_files))

		if self.morphs_in_duf_files:
			self._addIssue(issues.MorphInDUFFilesIssue(self.morphs_in_duf_files))

		if self.materials_in_duf_files:
			self._addIssue(issues.ShaderInDUFFilesIssue(self.materials_in_duf_files))

		if self.active_morphs_in_dsf_files:
			self._addIssue(issues.ActiveMorphsInDSFFilesIssue(self.active_morphs_in_dsf_files))

	@rule
	def _getContributors(self) -> None:
		"""Get contributors."""

		try:
			contributor: dict[str, str] = self.dson['asset_info']['contributor']
			author_data = self.data.contributors.setdefault(contributor.get('author', ''), {})
			author_data.setdefault('Email', set()).add(contributor.get('email', ''))
			author_data.setdefault('Website', set()).add(contributor.get('website', ''))
		except Exception:
			pass

	@rule
	def _checkAssetID(self, filename: str) -> None:
		"""Check asset ID."""

		try:
			asset_id = unquote(self.dson['asset_info']['id'])
		except Exception:
			asset_id = ''

		if not filename.lower().endswith(asset_id.lower()):
			self.asset_id_mismatch_files[filename] = asset_id

	@rule
	def _checkDSONFileReferences(self, filename: str) -> None:
		"""Check DSON file references."""

		# TODO: this is slow. Try JMESPath? dpath? multithread? ... something...
		url_references: set[str] = set()
		for encoded, parser in self.ext_file_parsers:
			for v in parser.find(self.dson):
				value = v.value
				if isinstance(value, str):
					if encoded:
						if '://' in value:
							path = unquote(urlparse(value).path.split(':', 1)[-1])
						else:
							path = unquote(urlparse(value.split(':', 1)[-1]).path)

						if ' ' in value:
							warn(f'Possible unquoted attribute marked as quoted: {filename}: {str(v.full_path)}, value: {value}')
						if not path and self.probable_path.search(value):
							warn(f'Possible misparse of path: {filename}: {str(v.full_path)}, value: {value}')
					else:
						path = value

						if '%20' in value:
							warn(f'Possible quoted attribute marked as unquoted: {filename}: {str(v.full_path)}, value: {value}')

					url_references.add(path)

					if str(v.path) in ['AssetFile', 'PresetFile']:
						self.data.postload_files.add(path)

		for file in url_references - {''}:
			if not trackDependencyIfExists(self.data, file, filename):
				self.data.missing_referenced_files.setdefault(file, set()).add(filename)

	@rule
	def _getShaderTypeInDUF(self, filename: str) -> None:
		"""Get shader types in DUF."""

#		if self.asset_type in ['preset_material', 'preset_shader', 'preset_hierarchical_material']:
		shaderCount = sum([v.value for v in self.preset_shader_count.find(self.dson)])
		shaderList: list[str] = [v.value for v in self.preset_shader_parser.find(self.dson)]
		shaders: set[str] = set()

		if shaderCount == 0 or shaderCount < len(shaderList) :
			shaders.add('studio/material/daz_shader')
		shaders.update(shaderList)
		shaders.discard('studio_material_channels')

		if shaders:
			self.data.shader_users[filename] = shaders

	@rule
	def _checkSupportAssetsInDUF(self, filename: str) -> None:
		"""Check DUF file for data better saved in DSF."""

		geometry: list[str] = [v.value for v in self.geometry_parser.find(self.dson)]
		uvs: list[str] = [v.value for v in self.uvs_parser.find(self.dson)]
		morphs: list[str] = [v.value for v in self.morphs_parser.find(self.dson)]
		materials: list[str] = [v.value for v in self.material_daz_brick_parser.find(self.dson)]

		if geometry:
			self.geometry_in_duf_files[filename] = geometry
		if uvs:
			self.uvs_in_duf_files[filename] = uvs
		if morphs:
			self.morphs_in_duf_files[filename] = morphs
		if materials:
			self.materials_in_duf_files[filename] = materials

	@rule
	def _checkActiveMorphsInDSF(self, filename: str) -> None:
		"""Check for active morphs in DSF."""

		for channel in self.active_morph_parser.find(self.dson):
			self.active_morphs_in_dsf_files.setdefault(filename, []).append((channel.value['label'], channel.value['value']))
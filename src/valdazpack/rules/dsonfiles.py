import json
import jsonpath
import re

from collections import defaultdict
from typing import Any, cast
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
		self.ext_file_parsers = [ ({'0': False, '1': True}[(x := line.split(maxsplit=1))[0]], jsonpath.compile(x[1])) for line in read_list_from('daz/dson_external_file_references.txt') ]
		self.geometry_parser = jsonpath.compile('$.geometry_library[?!@.extra[?@.type == "studio/geometry/shell"]].id')
		self.uvs_parser = jsonpath.compile('$.uv_set_library[*].id')
		self.morphs_data_parser = jsonpath.compile('$.modifier_library[?@.morph || @.skin].id')
		self.id_parser = jsonpath.compile('$.scene.*[*].id | $.*[*].id')
		self.material_daz_brick_parser = jsonpath.compile('$.material_library[?@.extra[?@.type == "studio/material/daz_brick"]].id')
		self.asset_type_parser = jsonpath.compile('$.asset_info.type')
		self.preset_shader_parser = jsonpath.compile('$.scene.materials[*].extra[?startswith(@.type, "studio/material/")].type')
		self.preset_old_shader_parser = jsonpath.compile('$.scene.materials[*].extra[?!startswith(@.type, "studio/material/")].type')
		self.favorites_materials_parser = jsonpath.compile('$.scene.materials[*].extra[?@.type == "studio_material_channels"].favorites')
		self.favorites_node_properties_parser = jsonpath.compile('$.scene.nodes[*].extra[?@.type == "studio_node_channels"].favorites')
		self.active_morph_parser = jsonpath.compile('$.modifier_library[?@.channel.value && @.channel.value != 0].channel')
		self.morph_loader_group_parser = jsonpath.compile('$.modifier_library[?@.group == "/Morphs/Morph Loader"].channel.label')
		self.tonemapper_options_parser = jsonpath.compile('$.scene.nodes[*].extra[?@.type == "studio/node/tone_mapper"]')
		self.environment_options_parser = jsonpath.compile('$.scene.nodes[*].extra[?@.type == "studio/node/environment"]')
		self.probable_path = re.compile(r'\b(data|runtime)\/', re.IGNORECASE)

		# TODO Add check for simulation data in non scene files

		self.invalid_dson_files: dict[str, Exception] = {}
		self.asset_id_mismatch_files: dict[str, str] = {}
		self.duplicate_ids_in_files: dict[str, list[str]] = {}
		self.geometry_in_duf_files: dict[str, list[str]] = {}
		self.uvs_in_duf_files: dict[str, list[str]] = {}
		self.morphs_in_duf_files: dict[str, list[str]] = {}
		self.materials_in_duf_files: dict[str, list[str]] = {}
		self.favorites_in_materials_in_duf_files: dict[str, dict[str, list[str]]] = {}
		self.favorites_in_node_properties_in_duf_files: dict[str, dict[str, list[str]]] = {}
		self.active_morphs_in_dsf_files: dict[str, list[tuple[str, str]]] = {}
		self.morph_loader_group_in_dsf_files: dict[str, list[str]] = {}
		self.tonemapper_options_in_duf_files: dict[str, str] = {}
		self.environment_options_in_duf_files: dict[str, str] = {}
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
				self.asset_type = cast(str, next(iter(self.asset_type_parser.findall(dson))) or '')

				self._getContributors()
				self._checkAssetID(filename)
				self._checkDSONFileReferences(filename)
				self._checkDuplicateIdsInFiles(filename)

				if filename.lower().endswith('.dsf'):
					self._checkActiveMorphsInDSF(filename)
					self._checkMorphLoaderGroupInDSF(filename)

				elif filename.lower().endswith('.duf'):
					self._getShaderTypeInDUF(filename)
					self._checkFavoritesInMaterialsInDUF(filename)
					self._checkFavoritesInNodePropertiesInDUF(filename)
					self._checkSupportAssetsInDUF(filename)
					self._checkTonemapperOptionsInDUF(filename)
					self._checkEnvironmentOptionsInDUF(filename)

		if self.invalid_dson_files:
			self._addIssue(issues.InvalidDSONFilesIssue(self.invalid_dson_files))

		if self.asset_id_mismatch_files:
			self._addIssue(issues.AssetIDMismatchFilesIssue(self.asset_id_mismatch_files))

		if self.duplicate_ids_in_files:
			self._addIssue(issues.DuplicateIDsInFilesIssue(self.duplicate_ids_in_files))

		if self.geometry_in_duf_files:
			self._addIssue(issues.GeometryInDUFFilesIssue(self.geometry_in_duf_files))

		if self.uvs_in_duf_files:
			self._addIssue(issues.UVSetInDUFFilesIssue(self.uvs_in_duf_files))

		if self.morphs_in_duf_files:
			self._addIssue(issues.MorphInDUFFilesIssue(self.morphs_in_duf_files))

		if self.materials_in_duf_files:
			self._addIssue(issues.ShaderInDUFFilesIssue(self.materials_in_duf_files))

		if self.favorites_in_materials_in_duf_files:
			self._addIssue(issues.FavoriteInMaterialInDUFFilesIssue(self.favorites_in_materials_in_duf_files))

		if self.favorites_in_node_properties_in_duf_files:
			self._addIssue(issues.FavoriteInNodePropertyInDUFFilesIssue(self.favorites_in_node_properties_in_duf_files))

		if self.active_morphs_in_dsf_files:
			self._addIssue(issues.ActiveMorphsInDSFFilesIssue(self.active_morphs_in_dsf_files))

		if self.morph_loader_group_in_dsf_files:
			self._addIssue(issues.MorphLoaderGroupInDSFFilesIssue(self.morph_loader_group_in_dsf_files))

		if self.tonemapper_options_in_duf_files:
			self._addIssue(issues.TonemapperOptionsInDUFFilesIssue(self.tonemapper_options_in_duf_files))

		if self.environment_options_in_duf_files:
			self._addIssue(issues.EnvironmentOptionsInDUFFilesIssue(self.environment_options_in_duf_files))

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

		if not filename.lower() == asset_id.lower():
			self.asset_id_mismatch_files[filename] = asset_id

	@rule
	def _checkDSONFileReferences(self, filename: str) -> None:
		"""Check DSON file references."""

		# TODO: this is slow. Try JMESPath? dpath? multithread? ... something...
		url_references: set[str] = set()
		for encoded, parser in self.ext_file_parsers:
			for v in parser.finditer(self.dson):
				if isinstance(v.value, str):
					if encoded:
						value = v.value
						if '://' in value:
							path = unquote(urlparse(value).path.split(':', 1)[-1])
						else:
							# Work around double forward slash being interpreted as netloc by urlparse
							leading_slash_count = len(re.split("[^/]", value, 1)[0])
							value = value.lstrip('/')
							path = '/' * leading_slash_count + unquote(urlparse(value.split(':', 1)[-1]).path)

						if ' ' in value:
							warn(f'Possible unquoted attribute marked as quoted: {filename}: {str(v.path)}, value: {value}')
						if not path and self.probable_path.search(value):
							warn(f'Possible misparse of path: {filename}: {str(v.path)}, value: {value}')
					else:
						path = v.value

						if '%20' in v.value:
							warn(f'Possible quoted attribute marked as unquoted: {filename}: {str(v.path)}, value: {v.value}')

					url_references.add(path)

					if str(object=v.path) in ['AssetFile', 'PresetFile']:
						self.data.postload_files.add(path.lstrip('/'))

		for file in url_references - {''}:
			if file.startswith('//') or not trackDependencyIfExists(self.data, file, filename):
				self.data.missing_referenced_files.setdefault(file, set()).add(filename)

	@rule
	def _checkDuplicateIdsInFiles(self, filename: str) -> None:
		"""Check for duplicate IDs in files."""

		id_counts: dict[str, int] = defaultdict(int)
		for id in cast(list[str], self.id_parser.findall(self.dson)):
			id_counts[id] += 1

		for id in (k for k, v in id_counts.items() if v > 1):
			self.duplicate_ids_in_files.setdefault(filename, []).append(id)

	@rule
	def _getShaderTypeInDUF(self, filename: str) -> None:
		"""Get shader types in DUF."""

#		if self.asset_type in ['preset_material', 'preset_shader', 'preset_hierarchical_material']:
		shaders: set[str] = set()
		if self.preset_old_shader_parser.findall(self.dson):
			shaders.add('studio/material/daz_shader')
		shaders.update(cast(list[str], self.preset_shader_parser.findall(self.dson)))
		shaders.discard('studio_material_channels')

		if shaders:
			self.data.shader_users[filename] = shaders

	@rule
	def _checkFavoritesInMaterialsInDUF(self, filename: str) -> None:
		"""Check for Favorites saved in Materials."""

		for favorites in self.favorites_materials_parser.finditer(self.dson):
			self.favorites_in_materials_in_duf_files.setdefault(filename, {})[favorites.parent.parent.parent.value['id']] = cast(list[str], favorites.value)  # pyright: ignore[reportIndexIssue, reportOptionalMemberAccess]

	@rule
	def _checkFavoritesInNodePropertiesInDUF(self, filename: str) -> None:
		"""Check for Favorites saved in Node Properties."""

		for favorites in self.favorites_node_properties_parser.finditer(self.dson):
			self.favorites_in_node_properties_in_duf_files.setdefault(filename, {})[favorites.parent.parent.parent.value['id']] = cast(list[str], favorites.value)  # pyright: ignore[reportIndexIssue, reportOptionalMemberAccess]

	@rule
	def _checkSupportAssetsInDUF(self, filename: str) -> None:
		"""Check DUF file for data better saved in DSF."""

		if x := cast(list[str], self.geometry_parser.findall(self.dson)):
			self.geometry_in_duf_files[filename] = x

		if x := cast(list[str], self.uvs_parser.findall(self.dson)):
			self.uvs_in_duf_files[filename] = x

		if x := cast(list[str], self.morphs_data_parser.findall(self.dson)):
			self.morphs_in_duf_files[filename] = x

		if x := cast(list[str], self.material_daz_brick_parser.findall(self.dson)):
			self.materials_in_duf_files[filename] = x

	@rule
	def _checkActiveMorphsInDSF(self, filename: str) -> None:
		"""Check for active morphs in DSF."""

		if x := [(x['label'], x['value']) for x in cast(list[dict[str, Any]], self.active_morph_parser.findall(self.dson))]:
			self.active_morphs_in_dsf_files[filename] = x

	@rule
	def _checkMorphLoaderGroupInDSF(self, filename: str) -> None:
		"""Check for Morph Loader path in DSF."""

		if x := cast(list[str], self.morph_loader_group_parser.findall(self.dson)):
			self.morph_loader_group_in_dsf_files[filename] = x

	@rule
	def _checkTonemapperOptionsInDUF(self, filename: str) -> None:
		"""Check for Morph Loader path in DSF."""

		if cast(list[str], self.tonemapper_options_parser.findall(self.dson)):
			if self.asset_type not in ['scene']:
				self.tonemapper_options_in_duf_files[filename] = self.asset_type

	@rule
	def _checkEnvironmentOptionsInDUF(self, filename: str) -> None:
		"""Check for Morph Loader path in DSF."""

		if cast(list[str], self.environment_options_parser.findall(self.dson)):
			if self.asset_type not in ['scene']:
				self.environment_options_in_duf_files[filename] = self.asset_type

import re

from lxml import etree
from lxml.etree import DocumentInvalid
#from warnings import warn

from ..issues import metadatafile as issues
from ..validator.resources import read_list_from
from ..validator.ruleset import ProductRuleset, rule
from ..validator.schema import SchemaCheckedXML
from ..validator.utilities import alpha_numeric

_SUPPORT_DIR = 'Runtime/Support'

class ValidateMetadataFiles(ProductRuleset):
	"""Perform metadata file validation of product.

	Arguments:
		data (ValidationData): validation data of product to validate.
	"""

	def _validate(self) -> None:
		"""Perform validation."""

		super()._validate()
		if self.data.product_fs.isdir(_SUPPORT_DIR):
			self.listed_assets: list[str] = []
			self.invalid_metadata_files: dict[str, Exception] = {}
			self.metadata_filenames_mismatches: dict[str, list[str]] = {}
			self.product_name_mismatches: list[str] = []
			self.multiple_stores: dict[str, set[str]] = {}
			self.store_not_daz: dict[str, set[str]] = {}
			self.store_is_daz: list[str] = []
			self.store_not_local: dict[str, set[str]] = {}
			self.missing_product_token: dict[str, list[str]] = {}
			self.missing_artists: dict[str, list[str]] = {}
			self.unexpected_assets: dict[str, list[str]] = {}
			self.unexpected_support_assets: dict[str, list[str]] = {}
			self.bad_support_asset_file_ref: dict[str, list[str]] = {}
			self.missing_content_types: dict[str, list[str]] = {}
			self.deprecated_content_types: dict[str, dict[str, str]] = {}
			self.missing_audiences: dict[str, list[str]] = {}
			self.non_standard_audiences: dict[str, dict[str, str]] = {}
			self.missing_categories: dict[str, list[str]] = {}
			self.duplicate_categories_used: dict[str, dict[str, set[str]]] = {}
			self.parent_categories_used: dict[str, dict[str, list[str]]] = {}
			self.special_categories_used: dict[str, dict[str, list[str]]] = {}
			self.deprecated_categories_used: dict[str, dict[str, list[str]]] = {}
			self.user_categories_used: dict[str, dict[str, list[str]]] = {}
			self.missing_compatibilities: dict[str, list[str]] = {}
			self.missing_compatibility_base: dict[str, list[str]] = {}
			self.missing_tags: dict[str, list[str]] = {}
			self.has_description: dict[str, list[str]] = {}
			self.has_userwords: dict[str, dict[str, list[str]]] = {}
			self.wrong_shader_types: dict[str, list[tuple[str, str, str]]] = {}
			self.nonspecific_shader_types: dict[str, list[tuple[str, str]]] = {}

			for self.metadata_file in self.data.product_fs.filterdir(_SUPPORT_DIR, files=['*.dsx']):
				filename = self.metadata_file.make_path(_SUPPORT_DIR)
				try:
					self.metadata = SchemaCheckedXML(self.data.product_fs.openbin(filename), 'Metadata.xsd').tree
				except DocumentInvalid as e:
					self.invalid_metadata_files[self.metadata_file.name] = e
					# Does not match Schema, but is valid XML, so attempt to use it anyway
					self.metadata = etree.parse(self.data.product_fs.openbin(filename), base_url = filename)
				except Exception as e:
					self.invalid_metadata_files[self.metadata_file.name] = e
					continue

				self._getPackageProductsFromMetadata()
				self._checkMetadataFilename()
				self._checkStoresInMetadata()
				self._checkProductTokenInMetadata()
				self._checkArtistsInMetadata()
				self._checkAssetsInMetadata()
				self._checkAssetsContentType()
				self._checkAssetsAudience()
				self._checkAssetsCategories()
				self._checkAssetsCompatibilities()
				self._checkAssetsCompatibilityBase()
				self._checkAssetsObjectCompatibility()
				self._checkAssetsHaveTags()
				self._checkAssetsHaveDescriptions()
				self._checkAssetsHaveUserwords()

			self._checkPackageProductInMetadata()
			self._checkUnlistedAssets()

			if self.invalid_metadata_files:
				self._addIssue(issues.InvalidProductMetadataIssue(self.invalid_metadata_files))

			if self.metadata_filenames_mismatches:
				self._addIssue(issues.MetadataFilenameIssue(self.metadata_filenames_mismatches))

			if self.product_name_mismatches:
				self._addIssue(issues.PackageProductNotMetadataProductIssue(self.product_name_mismatches))

			if self.multiple_stores:
				self._addIssue(issues.MetadataFileContainsMultipleStoreIDsIssue(self.multiple_stores))

			if self.store_not_daz:
				self._addIssue(issues.MetadataStoreIDIsNotDAZ3DIssue(self.store_not_daz))

			if self.store_is_daz:
				self._addIssue(issues.MetadataStoreIDIsDAZ3DIssue(self.store_is_daz))

			if self.store_not_local:
				self._addIssue(issues.MetadataStoreIDIsNotLocalUserIssue(self.store_not_local))

			if self.missing_product_token:
				self._addIssue(issues.MetadataMissingProductTokenIssue(self.missing_product_token))

			if self.missing_artists:
				self._addIssue(issues.MetadataMissingArtistIssue(self.missing_artists))

			if self.unexpected_assets:
				self._addIssue(issues.MetadataUnexpectedAssetsIssue(self.unexpected_assets))

			if self.unexpected_support_assets:
				self._addIssue(issues.MetadataUnexpectedSupportAssetsIssue(self.unexpected_support_assets))

			if self.bad_support_asset_file_ref:
				self._addIssue(issues.MetadataInvalidSupportAssetFileRefIssue(self.bad_support_asset_file_ref))

			if self.missing_content_types:
				self._addIssue(issues.MetadataMissingContentTypeIssue(self.missing_content_types))

			if self.deprecated_content_types:
				self._addIssue(issues.MetadataDeprecatedContentTypeIssue(self.deprecated_content_types))

			if self.wrong_shader_types:
				self._addIssue(issues.MetadataWrongShaderTypeIssue(self.wrong_shader_types))

			if self.nonspecific_shader_types:
				self._addIssue(issues.MetadataNonspecificShaderTypeIssue(self.nonspecific_shader_types))

			if self.missing_audiences:
				self._addIssue(issues.MetadataMissingAudienceIssue(self.missing_audiences))

			if self.non_standard_audiences:
				self._addIssue(issues.MetadataNonStandardAudienceIssue(self.non_standard_audiences))

			if self.missing_categories:
				self._addIssue(issues.MetadataMissingCategoriesIssue(self.missing_categories))

			if self.duplicate_categories_used:
				self._addIssue(issues.MetadataDuplicateCategoriesUsedIssue(self.duplicate_categories_used))

			if self.parent_categories_used:
				self._addIssue(issues.MetadataParentCategoriesUsedIssue(self.parent_categories_used))

			if self.special_categories_used:
				self._addIssue(issues.MetadataSpecialCategoriesUsedIssue(self.special_categories_used))

			if self.deprecated_categories_used:
				self._addIssue(issues.MetadataDeprecatedCategoriesIssue(self.deprecated_categories_used))

			if self.user_categories_used:
				self._addIssue(issues.MetadataUserCategoriesUsedIssue(self.user_categories_used))

			if self.missing_compatibilities:
				self._addIssue(issues.MetadataMissingCompatibilitiesIssue(self.missing_compatibilities))

			if self.missing_compatibility_base:
				self._addIssue(issues.MetadataMissingCompatibilityBaseIssue(self.missing_compatibility_base))

			if self.missing_tags:
				self._addIssue(issues.MetadataMissingTagsIssue(self.missing_tags))

			if self.has_description:
				self._addIssue(issues.MetadataHasDescriptionIssue(self.has_description))

			if self.has_userwords:
				self._addIssue(issues.MetadataHasUserwordsIssue(self.has_userwords))

	@rule
	def _getPackageProductsFromMetadata(self) -> None:
		"""Get package product names from metadata.

		Updates `data.metadata.products` with found products.
		"""

		self.data.metadata.products.extend([e.attrib['VALUE'] for e in self.metadata.xpath("/ContentDBInstall/Products/Product")])

	@rule
	def _checkMetadataFilename(self) -> None:
		"""Check metadata filename matches name auto generated by Daz Studio."""

		# NOTE: This is a guess and may need to be expanded with additional characters
		REPLACE_METADATA_FILENAME_CHARACTERS = r'[\\/*?:"<>|!. ]'

		expected_metadata_filenames: list[str] = []
		for e in self.metadata.xpath("/ContentDBInstall/Products/Product"):
			storeID = e.xpath('StoreID')[0].attrib['VALUE']
			token = eToken[0].attrib['VALUE'] if (eToken := e.xpath('ProductToken')) else None
			name = e.attrib['VALUE']
			metadata_filename_base = f"{storeID}_{f'{token}_' if token else ''}{name}"
			expected_metadata_filenames.append(re.sub(REPLACE_METADATA_FILENAME_CHARACTERS, '_', metadata_filename_base) + '.dsx')

		if self.metadata_file.name not in expected_metadata_filenames:
			self.metadata_filenames_mismatches[self.metadata_file.name] = expected_metadata_filenames

	@rule
	def _checkStoresInMetadata(self) -> None:
		"""Check stores listed in metadata.

		- Only one unique store listed
		- Store is `DAZ 3D` for products distributed by DAZ
		- Store is NOT `DAZ 3D` for products not distributed by DAZ
		- Store is one of [`DAZ 3D`, `LOCAL USER`, ``]
		This is a NOTICE, not a WARNING as the store will be automatically updated
		to `LOCAL USER` if the store is not already in the users database.

		Updates `data.metadata.stores` with found stores.
		"""

		if len(stores := {e.attrib['VALUE'] for e in self.metadata.xpath("/ContentDBInstall/Products/Product/StoreID")}) > 1:
			self.multiple_stores[self.metadata_file.name] = stores

		self.data.metadata.stores.update(stores)

		if self.data.daz:
			if stores != {'DAZ 3D'}:
				self.store_not_daz[self.metadata_file.name] = stores
		else:
			if 'DAZ 3D' in stores:
				self.store_is_daz.append(self.metadata_file.name)
			if not stores.issubset(defaultStores := {'DAZ 3D', 'LOCAL USER', ''}):
				self.store_not_local[self.metadata_file.name] = stores - defaultStores

	@rule
	def _checkProductTokenInMetadata(self) -> None:
		"""Check product token listed in metadata."""

		if missing_product_tokens := [e.attrib['VALUE'] for e in self.metadata.xpath("/ContentDBInstall/Products/Product[not (StoreID[@VALUE='LOCAL USER']) and not(ProductToken)]")]:
			self.missing_product_token[self.metadata_file.name] = missing_product_tokens

	@rule
	def _checkArtistsInMetadata(self) -> None:
		"""Check artists listed in metadata.

		Updates `data.metadata.artists` with found artists.
		"""

		if missing_artists := [e.attrib['VALUE'] for e in self.metadata.xpath("/ContentDBInstall/Products/Product[not (Artists/Artist)]")]:
			self.missing_artists[self.metadata_file.name] = missing_artists

		self.data.metadata.artists.update({e.attrib['VALUE'] for e in self.metadata.xpath("/ContentDBInstall/Products/Product/Artists/Artist")})

	@rule
	def _checkAssetsInMetadata(self) -> None:
		"""Check assets and support assets listed in metadata."""

		assets = [e.attrib['VALUE'].lstrip('/') for e in self.metadata.xpath("/ContentDBInstall/Products/Product/Assets/Asset")]
		if unexpected_assets := [f for f in assets if not self.data.product_fs.exists(f)]:
			self.unexpected_assets[self.metadata_file.name] = unexpected_assets
		self.listed_assets.extend(assets)

		support_assets = [e.attrib['VALUE'].lstrip('/') for e in self.metadata.xpath("/ContentDBInstall/Products/Product/SupportAssets/SupportAsset")]
		if unexpected_support_assets := [f for f in support_assets if not self.data.product_fs.exists(f)]:
			self.unexpected_support_assets[self.metadata_file.name] = unexpected_support_assets
		self.listed_assets.extend(support_assets)

		support_asset_files = [e.attrib['VALUE'].lstrip('/') for e in self.metadata.xpath("/ContentDBInstall/Products/Product/SupportAssets")]
		if bad_support_asset_file_ref := [f for f in support_asset_files if not self.metadata_file.make_path(_SUPPORT_DIR) == f]:
			self.bad_support_asset_file_ref[self.metadata_file.name] = bad_support_asset_file_ref

	@rule
	def _checkAssetsContentType(self) -> None:
		"""Check asset content type listed in metadata."""

		deprecated_content_type_list = [content_type.lower() for content_type in read_list_from('daz/deprecated_content_types.txt')]
		shader_users_key_lc = {k.lstrip('/').lower(): k for k in self.data.shader_users.keys()}

		# TODO: Expand this type to name map
		shader_map = (('studio/material/daz_shader', 'RSL'), ('studio/material/uber_iray', 'MDL'), ('mt5', 'MT5'), ('mc6', 'MC6'))

		deprecated_content_types: dict[str, str] = {}
		missing_content_types: list[str] = []
		wrong_shader_types: list[tuple[str, str, str]] = []
		nonspecific_shader_types: list[tuple[str, str,]] = []
		for e in self.metadata.xpath("/ContentDBInstall/Products/Product/Assets/Asset"):
			asset = e.attrib['VALUE']
			asset_lc = asset.lower()
			element = e.xpath("ContentType")
			if content_type := element[0].attrib['VALUE'] if len(element) else None:
				if content_type.lower() in deprecated_content_type_list:
					deprecated_content_types[asset] = content_type

				content_type_parts = content_type.split('/')
				if len(content_type_parts) > 1 and content_type_parts[0] == 'Preset' and content_type_parts[1] in ['Materials', 'Shader'] and asset_lc in shader_users_key_lc:
					shaders = self.data.shader_users[shader_users_key_lc[asset_lc]]
#					found_shader = False

					for shader_type, shader_name in shader_map:
						if shaders == {shader_type}:
#							found_shader = True
							if not content_type_parts[-1] == shader_name:
								if len(content_type_parts) == 2 or content_type_parts[-1] == 'Hierarchical':
									nonspecific_shader_types.append((asset, shader_name))
								else:
									wrong_shader_types.append((asset, content_type_parts[-1], shader_name))

#					if not found_shader:
#						warn(f'Unhandled shader: {shaders}')

				# TODO: Validate type better

			else:
				missing_content_types.append(e.attrib['VALUE'])

		if deprecated_content_types:
			self.deprecated_content_types[self.metadata_file.name] = deprecated_content_types

		if missing_content_types:
			self.missing_content_types[self.metadata_file.name] = missing_content_types

		if wrong_shader_types:
			self.wrong_shader_types[self.metadata_file.name] = wrong_shader_types

		if nonspecific_shader_types:
			self.nonspecific_shader_types[self.metadata_file.name] = nonspecific_shader_types

	@rule
	def _checkAssetsAudience(self) -> None:
		"""Check asset audiences listed in metadata."""

		missing_audience: list[str] = []
		non_standard_audience: dict[str, str] = {}
		for e in self.metadata.xpath("/ContentDBInstall/Products/Product/Assets/Asset"):
			element = e.xpath("Audience")
			if audience := element[0].attrib['VALUE'] if len(element) else None:
				if audience not in read_list_from('daz/audiences.txt'):
					non_standard_audience[e.attrib['VALUE']] = audience
			else:
				missing_audience.append(e.attrib['VALUE'])

		if missing_audience:
			self.missing_audiences[self.metadata_file.name] = missing_audience

		if non_standard_audience:
			self.non_standard_audiences[self.metadata_file.name] = non_standard_audience

	@rule
	def _checkAssetsCategories(self) -> None:
		"""Check asset categories listed in metadata."""

		special_categories_list = tuple('/' + category.lower().strip('/') + '/' for category in read_list_from('daz/special_categories.txt'))
		deprecated_categories_list = tuple('/' + category.lower().strip('/') + '/' for category in read_list_from('daz/deprecated_categories.txt'))

		missing_categories: list[str] = []
		duplicate_categories_used: dict[str, set[str]] = {}
		parent_categories_used: dict[str, list[str]] = {}
		special_categories_used: dict[str, list[str]] = {}
		deprecated_categories_used: dict[str, list[str]] = {}
		user_categories_used: dict[str, list[str]] = {}
		for e in self.metadata.xpath("/ContentDBInstall/Products/Product/Assets/Asset"):
			categories: list[str]
			if categories := [element.attrib['VALUE'] for element in e.xpath("Categories/Category")]:
				categories.sort()
				duplicate_categories: set[str] = set()
				parent_categories: list[str] = []
				special_categories: list[str] = []
				user_categories: list[str] = []
				deprecated_categories: list[str] = []
				for i in range(category_count := len(categories)):
					category_lc = '/' + categories[i].lower().strip('/') + '/'

					if (next_index := i + 1) < category_count:
						next_category_lc = '/' + categories[next_index].lower().strip('/') + '/'

						if next_category_lc == category_lc:
							duplicate_categories.add(categories[i])
						elif next_category_lc.startswith(category_lc):
							parent_categories.append(categories[i])

					if category_lc.startswith(special_categories_list):
						special_categories.append(categories[i])

					if category_lc.startswith(deprecated_categories_list):
						deprecated_categories.append(categories[i])

					if not category_lc.startswith('/default/'):
						user_categories.append(categories[i])

					# TODO: Validate categories better

				if duplicate_categories:
					duplicate_categories_used[e.attrib['VALUE']] = duplicate_categories

				if parent_categories:
					parent_categories_used[e.attrib['VALUE']] = parent_categories

				if special_categories:
					special_categories_used[e.attrib['VALUE']] = special_categories

				if deprecated_categories:
					deprecated_categories_used[e.attrib['VALUE']] = deprecated_categories

				if user_categories:
					user_categories_used[e.attrib['VALUE']] = user_categories

			else:
				missing_categories.append(e.attrib['VALUE'])

		if missing_categories:
			self.missing_categories[self.metadata_file.name] = missing_categories

		if duplicate_categories_used:
			self.duplicate_categories_used[self.metadata_file.name] = duplicate_categories_used

		if parent_categories_used:
			self.parent_categories_used[self.metadata_file.name] = parent_categories_used

		if special_categories_used:
			self.special_categories_used[self.metadata_file.name] = special_categories_used

		if deprecated_categories_used:
			self.deprecated_categories_used[self.metadata_file.name] = deprecated_categories_used

		if user_categories_used:
			self.user_categories_used[self.metadata_file.name] = user_categories_used

	@rule
	def _checkAssetsCompatibilities(self) -> None:
		"""Check asset compatibilites listed in metadata."""

		missing_compatibilities: list[str] = []
		for e in self.metadata.xpath("/ContentDBInstall/Products/Product/Assets/Asset"):
			if compatibilities := [element.attrib['VALUE'] for element in e.xpath("Compatibilities/Compatibility")]:
				compatibilities = compatibilities # TODO: Validate compatibilities
			else:
				pass # TODO: Only some types need compatibilities listed
				#missing_compatibilities.append (e.attrib['VALUE'])

		if missing_compatibilities:
			self.missing_compatibilities[self.metadata_file.name] = missing_compatibilities

	@rule
	def _checkAssetsCompatibilityBase(self) -> None:
		"""Check asset compatibility bases listed in metadata."""

		missing_compatibility_base: list[str] = []
		for element in self.metadata.xpath("/ContentDBInstall/Products/Product/Assets/Asset/CompatibilityBase"):
			if compatibility_base := element[0].attrib['VALUE'] if len(element) else None:
				compatibility_base = compatibility_base # TODO: Validate compatibility base
			else:
				pass # TODO: Only some types need compatibility base listed
				#missing_compatibility_base.append (e.attrib['VALUE'])

		if missing_compatibility_base:
			self.missing_compatibility_base[self.metadata_file.name] = missing_compatibility_base

	@rule
	def _checkAssetsObjectCompatibility(self) -> None:
		"""Check asset object compatibility listed in metadata."""

		#missing_object_compatibilities: list[str] = []
		#for e in metadata.xpath("/ContentDBInstall/Products/Product/ObjectCompatibilities/ObjectCompatibility"):
		#	pass # TODO: Validate ObjectCompatibilities

		# TODO: issue if value is #blah and not /blah/blah#blah

	@rule
	def _checkAssetsHaveTags(self) -> None:
		"""Check if assets listed in metadata have tags."""

		missing_tags: list[str] = []
		for e in self.metadata.xpath("/ContentDBInstall/Products/Product/Assets/Asset"):
			if tags := [element.attrib['VALUE'] for element in e.xpath("Tags/Tag")]:
				tags = tags # TODO: Validate tags
			else:
				missing_tags.append(e.attrib['VALUE'])

		if missing_tags:
			self.missing_tags[self.metadata_file.name] = missing_tags

	@rule
	def _checkAssetsHaveDescriptions(self) -> None:
		"""Check if assets listed in metadata have descriptions."""

		if has_description := [e.attrib['VALUE'] for e in self.metadata.xpath("/ContentDBInstall/Products/Product/Assets/Asset[Description[string-length(text()) > 0]]")]:
			self.has_description[self.metadata_file.name] = has_description

	@rule
	def _checkAssetsHaveUserwords(self) -> None:
		"""Check if assets listed in metadata have userwords."""

		for asset in [e.attrib['VALUE'] for e in self.metadata.xpath("/ContentDBInstall/Products/Product/Assets/Asset[Userwords/Userword[string-length(@VALUE) > 0]]")]:
			self.has_userwords.setdefault(self.metadata_file.name, {})[asset] = [e.attrib['VALUE'] for e in self.metadata.xpath(f"/ContentDBInstall/Products/Product/Assets/Asset[@VALUE = '{asset}']/Userwords/Userword[string-length(@VALUE) > 0]")]

	@rule
	def _checkPackageProductInMetadata(self) -> None:
		"""Check package product name is a product listed in metadata."""

		strippedNames = [alpha_numeric(product) for product in self.data.metadata.products]

		for package in self.data.packages:
			if not package.product_name in self.data.metadata.products and not (package.parsed and not package.parsed['name'] in strippedNames):
				self.product_name_mismatches.append(package.product_name or (package.parsed['name'] if package.parsed else ''))

	@rule
	def _checkUnlistedAssets(self) -> None:
		"""Check for unlisted assets."""

		support_dir_lc = _SUPPORT_DIR.lower()
		assets_lc = [asset.lower() for asset in self.listed_assets]

		if unlisted_assets := [file for file in self.data.product_fs.walk.files() if not (f := file.lstrip('/').lower()).startswith(support_dir_lc) and not f in assets_lc]:  # pyright: ignore[reportUnknownMemberType]
			self._addIssue(issues.MetadataUnlistedAssetsIssue(unlisted_assets))
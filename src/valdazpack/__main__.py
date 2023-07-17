import sys

from argparse import ArgumentParser, ArgumentTypeError, FileType
from fs.errors import ResourceNotFound
from fs.opener import open_fs
from fs.opener.parse import parse_fs_url
from fs.path import relpath
from jinja2 import Environment, FileSystemLoader, PackageLoader, Template, select_autoescape
from jinja2.exceptions import TemplateError
from pathlib import Path
from pprint import PrettyPrinter
from typing import Any

from .validator import ValidationData, validate

class PrettyPrinterWithoutStringWrapping(PrettyPrinter):
	"""PrettyPrinter without string wrapping."""

	def __init__(self, *args: Any) -> None:
		super().__init__(*args)
		self._dispatch[str.__repr__] = self._pprint_str  # pyright: ignore[reportGeneralTypeIssues, reportUnknownMemberType]

	def _pprint_str(self, _self: PrettyPrinter, *args: Any) -> None:
		width = self._width
		self._width = sys.maxsize
		try:
			super()._pprint_str(*args)  # pyright: ignore[reportGeneralTypeIssues, reportUnknownMemberType]
		finally:
			self._width = width

def _content_location(path: str) -> Path:
	"""Clean up error messages for paths passed on commandline."""

	try:
		return Path(path).resolve(True)
	except FileNotFoundError as e:
		url = f'zip://{path}'
		try:
			parsed_url = parse_fs_url(url)
			fs = open_fs(url)
			fs.opendir(relpath((parsed_url.path or '').lstrip('\\')))  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
		except ResourceNotFound as e:
			raise ArgumentTypeError(f'{parsed_url.path} not found in {parsed_url.resource}')  # pyright: ignore[reportUnboundVariable, reportUnknownMemberType]
		except:
			raise ArgumentTypeError(e)
		else:
			return Path(path)
	except Exception as e:
		raise ArgumentTypeError(e)

def _jinja_user_template(template_filepath: str) -> Template:
	"""Load user specified Jinja template."""

	filepath = Path(template_filepath)
	if not filepath.exists():
		raise ArgumentTypeError(f"Template not found: {template_filepath}")

	jinja_env = Environment(loader=FileSystemLoader(searchpath=filepath.parent), auto_reload=False)
	jinja_env.filters['pformat'] = PrettyPrinterWithoutStringWrapping().pformat  # pyright: ignore[reportGeneralTypeIssues, reportUnknownMemberType]

	try:
		return jinja_env.get_template(filepath.name)
	except TemplateError as e:
		raise ArgumentTypeError(repr(e))
	except Exception as e:
		raise ArgumentTypeError(e)

def _main() -> None:
	parser = ArgumentParser(description = 'Validate DAZ Studio Product', epilog = 'For non-DIM ZIP files, a subdirectory may be specified as the content root by appending !<subdirectory> to the filename: "example.zip!My Library"')
	parser.add_argument('product_path', type = _content_location, nargs = '+', help = 'DIM Packages, ZIP files, or Content Directories to validate')
	parser.add_argument('-d', '--dependencies', type = _content_location, nargs = '+', help = 'additional DIM Packages, ZIP files, or Content Directories which are not validated but which the validated product depends on')

	parser.add_argument('-D', '--daz', action = 'store_true', help = 'enable validation rules for products distributed by Daz Productions, Inc')
	parser.add_argument('-O', '--daz-original', action = 'store_true', help = 'enable validation rules for products produced by Daz Productions, Inc')

	parser.add_argument('-p', '--poser', action = 'store_true', help = 'enable validation rules for included Poser content (experimental)')
	parser.add_argument('-s', '--dson-schema', action = 'store_true', help = 'enable DSON schema checking (experimental)')

	template_parser = parser.add_mutually_exclusive_group()
	template_parser.add_argument('-H', '--html', action = 'store_true', help = 'generate HTML report')
	template_parser.add_argument('-T', '--template', type = _jinja_user_template, help = 'generate report using Jinja template')

	parser.add_argument('-o', '--output', type = FileType('w', encoding='utf-8'), default=sys.stdout, help = 'write report to file')
	parser.add_argument('-v', '--verbose', action = 'store_true', help = 'enable verbose output')

	args = parser.parse_args()

	# Prepare report template
	if args.template:
		template = args.template
	else:
		jinja_env = Environment(loader=PackageLoader(__package__, "data/templates",), autoescape=select_autoescape(['html.jinja']), auto_reload=False)
		jinja_env.filters['pformat'] = PrettyPrinterWithoutStringWrapping().pformat  # pyright: ignore[reportGeneralTypeIssues, reportUnknownMemberType]
		template = jinja_env.get_template("report.html.jinja" if args.html else "report.txt.jinja")

	# Validate
	data = ValidationData(args.product_path, args.dependencies, args.daz, args.daz_original, args.poser, args.dson_schema, args.verbose)
	validate(data)

	args.output.write(template.render(data=data))

def _profile() -> None:  # pyright: ignore[reportUnusedFunction]
	import cProfile, pstats
	profiler = cProfile.Profile()
	profiler.enable()
	_main()
	profiler.disable()
	pstats.Stats(profiler).dump_stats('stats.profiler')
 
if __name__ == '__main__':
	_profile()
	# _main()
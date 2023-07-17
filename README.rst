valdazpack
==========

``valdazpack`` is a DAZ Studio content validator.

Supported Python versions
-------------------------

- Python 3.11

Usage
-----

``valdazpack [-h] [-d <DEPENDENCIES ...>] [-D] [-O] [-p] [-s] [-H | -T TEMPLATE] [-o OUTPUT] [-v] product_path [product_path ...]``

positional arguments:
  product_path          DIM Packages, ZIP files, or Content Directories to validate

options:
  -h, --help            show this help message and exit
  -d <DEPENDENCIES ...>, --dependencies <DEPENDENCIES ...>
                        additional DIM Packages, ZIP files, or Content Directories which are not validated but which the validated product depends on
  -D, --daz             enable validation rules for products distributed by Daz Productions, Inc
  -O, --daz-original    enable validation rules for products produced by Daz Productions, Inc
  -H, --html            generate HTML report
  -T TEMPLATE, --template TEMPLATE
                        generate report using Jinja template
  -o OUTPUT, --output OUTPUT
                        write report to file
  -v, --verbose         enable verbose output

For non-DIM ZIP files, a subdirectory may be specified as the content root by appending ``!<subdirectory>`` to the filename: ``example.zip!My Library``

.. code:: 

    E:\> valdazpack --dependencies "C:\Users\Username\Documents\MDL" --html --output report.html OMNFLUX00000001-01_NVIDIAvMaterials170ShaderPresets.zip

    E:\> valdazpack --dependencies "D:\InstallManager\Downloads\IM00042071-02_Genesis8MaleStarterEssentials.zip" --html --output report.html "D:\My Custom G8M Character"

    E:\> valdazpack --daz-original --html --output report.html "D:\InstallManager\Downloads\IM00042071-02_Genesis8MaleStarterEssentials.zip"

    E:\> valdazpack --html --output report.html "example.zip!My Library"

License
-------

This module is published under the MIT license.
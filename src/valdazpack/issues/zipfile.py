from . import PackageWarning

# NOTE: Using PackageWarning for plain ZIP archives....
class PathCollisionsInZipFile(PackageWarning):
	title = 'Path Collision(s) in ZIP file'
	description = "Path collisions found in ZIP file"
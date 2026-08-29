class ValDazPackError(Exception):
	"""Base exception for ValDazPack errors."""
	pass
    
class NoDIMContentError(ValDazPackError):
	"""Raised when path cannot be treated as DIM content."""
	pass

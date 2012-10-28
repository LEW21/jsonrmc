"""Simple Python library implementing the JSON-RMC (remote method call) interface.
"""

from .server import exposed, call, handle

try:
	from .server import launch
except:
	pass

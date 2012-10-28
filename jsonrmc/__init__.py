"""Simple Python library implementing the JSON-RMC (remote method call) interface.

Server-side design rationale is strongly influenced by CherryPy.

Sample server-side usage::

	from jsonrmc import exposed

	class Math:
		@exposed
		@staticmethod
		def sum(x, y):
			return x + y

		@exposed
		def triple(self, x):
			return 3 * x

	root = {}
	root["math"] = Math()

	# Somewhere inside your network handling routines:
	from jsonrmc import handle
	# ...
	result = handle(root, jsondata)
	# ...

	# Now let's assume a client sent a request:
	# {"id": 1, "resource": "/math", "method": "triple", "params": [10]}

	# When jsonrmc.handle is called for root, response is ready:
	# {"id": 1, "result": 30}

"""

from .server import exposed, call, handle

try:
	from .server import launch
except:
	pass

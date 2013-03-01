"""JSON-RMC server library / reserve.jsons app.

Design rationale is strongly influenced by CherryPy.

Sample usage::

	from jsonrmc.server import exposed

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
	from jsonrmc.server import handle
	# ...
	result = handle(root, jsondata)
	# ...

	# Now let's assume a client sent a request:
	# {"id": 1, "resource": "/math", "method": "triple", "params": [10]}

	# When jsonrmc.handle is called for root, response is ready:
	# {"id": 1, "result": 30}

"""

def exposed(handler):
	"""Makes the method or resource accessible remotely.

	It's a cleaner way of saying: method.exposed = True
	"""

	handler.exposed = True
	return handler

def call(root, resource, method, params, **kwargs):
	"""Traverses the tree (starting from the ``root`` object) and tries to execute the appropriate method."""

	# Split the resource
	submodules = resource.strip("/").split("/")

	# Iterate over the exposed children
	current = root

	for sm in [x for x in submodules if x]:
		try:
			current = current[sm]
		except BaseException:
			raise NameError("Resource not found: " + resource + "!")

	try:
		func = getattr(current, method)
		if not method.exposed:
			raise AttributeError
	except BaseException:
		raise NameError("No such method: " + method + "!")

	# Execute
	return func(*params)

def CallHandler(tree):
	"""jsonrmc.server app traversing given tree and executing selected method"""
	return lambda **kwargs: call(tree, **kwargs)

def Handler(app):
	"""reserve.jsons app implementing jsonrmc protocol

	Supports subapplications of form::

		app(resource, method, params)

	If the subapplication is not a callable, it's wrapped in the CallHandler.
	"""
	if not callable(app):
		app = CallHandler(app)

	def handle(obj):
		"""
		Reads the provided JSON-RMC object and passes its content to the subapplication.
		Wraps and returns return value of / exception thrown by the subapplication according to the JSON-RMC protocol.

		Warning: this function does not encode/decode JSON, it operates on its decoded form.
		"""

		response = {}

		try:
			response["id"] = obj["id"]
		except:
			pass

		try:
			# Check if JSON-RMC is correct
			if not "resource" in obj or not "method" in obj:
				raise ValueError("Incorrect JSON-RMC! resource and method are required!")

			if not "params" in obj:
				obj["params"] = []
			elif not type(obj["params"]) is list:
				raise ValueError("Incorrect JSON-RMC! params must be a list!")

			response["result"] = app(**obj)
		except BaseException as e:
			response["error"] = str(e)

		return response

	return handle

try:
	from reserve import find_app

	def launch(args):
		return Handler(find_app(args, 'jsonrmc handler.', 'jsonrmc app or root'))
except:
	pass

import json

def handle(app, data):
	obj = json.loads(data)
	result = Handler(app)(obj)
	return json.dumps(result)

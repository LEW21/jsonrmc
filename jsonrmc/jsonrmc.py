import json

def exposed(handler):
	"""
	@exposed makes the method or resource accessible remotely. It's a cleaner way of saying: method.exposed = True
	"""
	
	handler.exposed = True
	return handler

def call(root, resource, method, params, **kwargs):
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

def handle(app, data):
	"""
	handle() processes the JSON-RMC data and tries to execute the appropriate handlers pinned to your root object.
	Normally handle() will return a ready JSON-RMC response containing the execution result.
	However a bad thing can happen: provided data is not correct JSON - in such case ValueError is thrown.
	"""

	if not callable(app):
		app = lambda **kwargs: call(app, **kwargs)

	obj = json.loads(data)

	response = {}

	try:
		response["id"] = obj["id"]
	except:
		pass

	try:
		# Check if JSON and JSON-RMC are correct
		if not "resource" in obj or not "method" in obj:
			raise ValueError("Incorrect JSON-RMC! resource and method are required!")

		if not "params" in obj:
			obj["params"] = []
		elif not type(obj["params"]) is list:
			raise ValueError("Incorrect JSON-RMC! params must be a list!")

		response["result"] = app(**obj)
	except BaseException as e:
		response["error"] = str(e)
	
	# Encode and return
	return json.dumps(response)

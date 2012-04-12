import json

class Node(object):
	"""
	A node of a jsonrmc tree. Object passed to the handle() function must be an instance of Node or of a descendant class.
	"""

	def __setitem__(self, key, value):
		self._resources[key] = value

	def __getitem__(self, key):
		return self._resources[key]
	
	_resources = {}

def exposed(handler):
	"""
	@exposed makes the method or resource accessible remotely. It's a cleaner way of saying: method.exposed = True
	"""
	
	handler.exposed = True
	return handler

def parse(data):
	"""
	parse() processes JSON-RMC data and returns a python dictionary.
	"""
	
	# Check if JSON and JSON-RMC are correct
	obj = json.loads(data)
	
	if not "id" in obj or not "resource" in obj or not "method" in obj:
		raise ValueError("Incorrect JSON-RMC! id, resource and method are required!")
	
	if not "params" in obj:
		obj["params"] = []
	elif not type(obj["params"]) is list:
		raise ValueError("Incorrect JSON-RMC! params must be a list!")
	
	return obj

# Methods executed before and after calling. They take parsed JSON-RMC dictionary as a parameter.
beforeCall = afterCall = lambda parsedObj: None

def handle(root, data):
	"""
	handle() processes the JSON-RMC data and tries to execute the appropriate handlers pinned to your root object.
	Normally handle() will return a ready JSON-RMC response containing the execution result.
	However a bad thing can happen: provided data is not correct JSON or JSON-RMC - in such case ValueError is thrown.
	"""
	
	obj = parse(data)

	result = error = None
	
	try:
		# Split the resource
		submodules = obj["resource"].strip("/").split("/")
	
		# Iterate over the exposed children
		current = root
		
		for sm in [x for x in submodules if x]:
			try:
				current = current[sm]
			except BaseException:
				raise NameError("Resource not found: " + obj["resource"] + "!")
		
		try:
			method = getattr(current, obj["method"])
			if not method.exposed:
				raise AttributeError
		except BaseException:
			raise NameError("No such method: " + obj["method"] + "!")
		
		# Execute
		beforeCall(obj)
		result = method(*obj["params"])
		afterCall(obj)
	except BaseException as e:
		error = str(e)
	
	# Encode and return
	return json.dumps({"id": obj["id"], "result" if not error else "error": result if not error else error})

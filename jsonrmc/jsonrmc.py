import json

class Root(object):
	"""
	The root of a jsonrmc tree. Object passed to the handle() function must be an instance of Root or of a descendant class.
	"""

	def __setitem__(self, key, value):
		self._resources[key] = value

	def __getitem__(self, key):
		return self._resources[key]
	
	_resources = {}
	exposed = True

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
			if not sm in current or not hasattr(current[sm], "exposed") or not current[sm].exposed:
				raise NameError("Resource not found: " + obj["resource"] + "!")
		
			current = current[sm]
		
		# Is the method out there and is it exposed?
		if not hasattr(current, obj["method"]):
			raise NameError("No such method: " + obj["method"] + "!")
		
		if not hasattr(getattr(current, obj["method"]), "exposed") or not getattr(current, obj["method"]).exposed:
			raise NameError("No such method: " + obj["method"] + "!")
		
		# Execute
		result = getattr(current, obj["method"])(*obj["params"])
	except BaseException as e:
		error = str(e)
	
	# Encode and return
	return json.dumps({"id": obj["id"], "result" if result is not None else "error": result if result is not None else error})

import json

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
			if not hasattr(current, sm) or not hasattr(getattr(current, sm), "exposed") or not getattr(current, sm).exposed:
				raise NameError("Resource not found: " + obj["resource"] + "!")
		
			current = getattr(current, sm)
		
		# Is the method out there and is it exposed?
		if not hasattr(current, obj["method"]):
			raise NameError("No such method: " + obj["method"] + "!")
		
		if not hasattr(getattr(current, obj["method"]), "exposed") or not getattr(current, obj["method"]).exposed:
			raise NameError("No such method: " + obj["method"] + "!")
		
		# Execute
		try:
			result = getattr(current, obj["method"])(*obj["params"])
		except BaseException as e:
			error = str(e)
	except NameError as e:
		error = str(e)
	
	# Encode and return
	return json.dumps({"id": obj["id"], "result" if result is not None else "error": result if result is not None else error})

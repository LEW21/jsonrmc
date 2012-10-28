from reserve.jsons import Stream

class Connection:
	def __init__(socket):
		self.stream = Stream(socket)

	def call(**kwargs):
		try:
			self.stream.write(kwargs)
			response = self.stream.read()
		except:
			raise IOError("Connection error.")

		try:
			return response['result']
		except KeyError:
			raise Exception(response['error'])

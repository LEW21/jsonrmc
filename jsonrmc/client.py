"""JSON-RMC client library.

Usage::

	from socket import socket
	from jsonrmc.client import Connection

	with socket() as s:
		s.connect(("localhost", 6000))
		with s.makefile('rw') as stream:
			rmc = Connection(stream)
			rmc.call("/my/object", "method", ["param1", 2])

"""

from reserve.jsons import Stream

class Connection:
	def __init__(socket):
		self.stream = Stream(socket)

	def call(resource, method, params):
		message = {"resource": resource, "method": method, "params": params}
		try:
			self.stream.write(message)
			response = self.stream.read()
		except:
			raise IOError("Connection error.")

		try:
			return response['result']
		except KeyError:
			raise Exception(response['error'])

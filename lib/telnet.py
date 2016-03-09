import socket, select, string, sys

class Telnet():

	def __init__(self, ip, port, timeout=5):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.settimeout(timeout)
		try:
			self.s.connect((ip,port))
		except:
			print 'unable to connect'

	def write(self, msg):
		self.s.send(msg)
		return self.read()

	def read(self, buf=4096):
		return self.s.recv(buf)
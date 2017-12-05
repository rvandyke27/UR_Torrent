
import socket
from threading import Thread


class Listen(Thread):

	def __init__(self, client):
		Thread.__init__(self)
		self.client = client

	def run(self):

		while True:

			conn, address = self.client.listening_socket.accept()
			buf = conn.recv(1024)
			print(buf)
			if len(buf) > 0:
				
				conn.send((bytearray(map(ord, "HERE IS YOUR PIECE"))))

			conn.close()
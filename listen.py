
import socket
from threading import Thread


class Listen(Thread):

	def __init__(self, client):
		Thread.__init__(self)
		self.client = client

	def run(self):

		while True:
			try:
				conn, address = self.client.listening_socket.accept()
				buf = conn.recv(1024)
				print(buf)
				if len(buf) > 0:
					
					conn.send((bytearray(map(ord, "HERE IS YOUR PIECE"))))

			except Exception as exc: 
				print(str(exc))
				conn.close()
				break

			except KeyboardInterrupt:
				print("closing")
				conn.close()
				break
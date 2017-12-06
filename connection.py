import socket
from threading import Thread
import time
import atexit

class Connection(Thread):

	def __init__(self, client_leecher, ip_addr, port, peer_bitfield):
		Thread.__init__(self)
		atexit.register(self.exit_handler)
		self.client = client_leecher
		self.peer_ip_addr = ip_addr
		self.peer_port = port
		self.peer_id = bytes(20)
		self.am_choking = 1
		self.am_interested = 0
		self.peer_choking = 1
		self.peer_interested = 0
		self.peer_bitfield = peer_bitfield
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.sock.connect((socket.gethostbyname(self.peer_ip_addr), self.peer_port))
		self.client.connection_list.append(self)

	def run(self):
		while True:
	#	while not self.client.bitfield.all(True):
			#check choking/interested conditions
			time.sleep(1)
			try:

				self.sock.send(bytearray(map(ord, "Piece request")))
				print("Asking  ", self.peer_ip_addr, "on port ", self.peer_port)
				response = self.sock.recv(16384)
				print("Got reply ", response)

			except Exception as exc: 
				print(str(exc))
				self.sock.close()
				break

			except KeyboardInterrupt:
				print("closing")
				self.sock.close()
				break

	def exit_handler(self):
		print("Connection closing")
		self.sock.close()

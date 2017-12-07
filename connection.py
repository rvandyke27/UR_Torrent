import socket
from threading import Thread
import time
import struct
import atexit

from bitstring import BitArray

import hashlib


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
		#self.client.connection_list.append(self)

		print(self.peer_bitfield)

	def run(self):
		print("Running")
		print(self.client.bitfield.bin)
		while True:
			try:
				message = self.sock.recv(65549)

				if message:
					#check messsage type
					message_prefix = message[0:4]
					message_id = message[4]
					#default block size = piece size = 65536
					if message_id == 7:
						print("Piece Message Received")
						#piece message
						index = message[5:9]
						begin = message[9:13]
						piece = message[13:]
						#check info hash
						int_index = struct.unpack('>i', index)[0]
						print(int_index)
						piece_hash = hashlib.sha1(piece).hexdigest()
						print(piece_hash)
						print(self.client.metainfo.get_piece_hash(int_index))
						if (piece_hash == self.client.metainfo.get_piece_hash(int_index)):
							print("Piece hash verified")
							#save piece
							temp_filename = "temp-" + str(int_index) + self.client.filename
							print(temp_filename)
							fout = open(temp_filename, 'w+b')
							if(piece):
								fout.write(piece)
								#update bitfield
								self.client.bitfield.set(True, int_index)
								print(self.client.bitfield.bin)
							fout.close()
							self.client.downloaded+=1
						else:
							print("Invalid Piece")
					elif message_id == 0:
						#choke
						self.peer_choking == 1
					elif message_id == 1:
						#unchoke
						self.peer_choking == 0
					elif message_id == 2:
						self.peer_interested == 1
					elif message_id == 3:
						self.peer_interested = 0
					elif message_id == 4:
						#have message
						print("Have Message")
					elif message_id == 5 :
						print("Bitfield message")
						#bitfield message
						#check that bitfield is correct length
						if len(message) == 5 + self.client.metainfo.num_pieces:
							for k in range(self.client.metainfo.num_pieces):
								#print(message[5+k])
								if message[5+k]== 1:
									self.peer_bitfield.set(True,k)
								else:
									self.peer_bitfield.set(False, k)
							print(self.peer_bitfield.bin)
						else:
							print("Incorrect length of bitfield")
					elif message_id == 6:
						index = message[5:9]
						begin = message[9:13]
						length = message[13:17]
						#request message
						print("Request Message")
					elif message_id == 8:
						#cancel message
						print("Cancel Message")
						index = message[5:9]
						begin = message[9:13]
						length = message[13:17]
					else:
						print("Invalid Message")

			except Exception as exc: 
				print(str(exc))
				self.sock.close()
				break

			except KeyboardInterrupt:
				print("closing")
				self.sock.close()
				break

	def has_piece(self, index):
		if self.peer_bitfield.bin[index] == '1':
			return True
		else:
			return False

	def exit_handler(self):
		print("Connection closing")
		self.sock.close()



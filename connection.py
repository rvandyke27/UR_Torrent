import socket
from threading import Thread
import time
import struct
import atexit
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
		self.client.connection_list.append(self)

	def run(self):
		while True:
	#	while not self.client.bitfield.all(True):
			#check choking/interested conditions
			time.sleep(.1)
			for i in range(self.client.metainfo.num_pieces):
				print(i)
				piece_request = bytearray(14)
				piece_request[0:4] = struct.pack('>i', int(13))
				piece_request[4] = 6
				piece_request[5:9] = struct.pack('>i', int(i))
				piece_request[9:13] = struct.pack('>i', int(0))
				if i < self.client.metainfo.num_pieces-1:
					piece_request[13:17] = struct.pack('>i', int(self.client.metainfo.piece_length))
				else:
					print("Last Piece")
					file_size = self.client.metainfo.file_length
					last_piece_size = file_size % self.client.metainfo.num_pieces
					print(last_piece_size)
					piece_request[13:17] = struct.pack('>i', int(last_piece_size))
				try:
					print("Sending piece request: ", piece_request)
					self.sock.send(piece_request)
					print("Asking  ", self.peer_ip_addr, "on port ", self.peer_port)
					message = self.sock.recv(65549)
					print("Got reply ")

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
						int_index = int.from_bytes(index, byteorder='big')
						print(int_index)
						piece_hash = hashlib.sha1(piece).hexdigest()
						print(piece_hash)
						print(self.client.metainfo.get_piece_hash(int_index))
						if (piece_hash == self.client.metainfo.get_piece_hash(int_index)):
							#save piece
							temp_filename = "temp-" + str(int.from_bytes(index, byteorder='big')) + self.client.filename
							print(temp_filename)
							fout = open(temp_filename, 'w+b')
							if(piece):
								fout.write(piece)
								#update bitfield
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
						#bitfield message
						#check that bitfield is correct length
						self.peer_bitfield = message[5:6+len(self.peer_bitfield)]
						print(self.peer_bitfield)
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
			else:
				self.client.reassemble_file()
				break

	def exit_handler(self):
		print("Connection closing")
		self.sock.close()


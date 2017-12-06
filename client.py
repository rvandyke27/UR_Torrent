import urllib.parse
from bencodepy import decode_from_file, decode
from listen import Listen
import hashlib
import connection
import struct
import os
import os.path
import socket
from metainfo import Metainfo
import re
from bitstring import BitArray
from connection import Connection
import threading
import time
import codecs
import atexit
import struct

class Client:

	def __init__(self, ip_addr, port, filename):
		print("thing")
		atexit.register(self.exit_handler)

		#list of peers (and connection info) that this client is connected to
		self.connection_list = list()
		self.listen_list = list()
		self.metainfo = Metainfo(filename)
		self.filename = filename
		self.ip_addr = ip_addr
		self.port = port
		self.peer_id = os.urandom(20)
		self.info_hash = self.metainfo.info_hash
		self.uploaded = 0
		self.downloaded = 0
		#if client has file, set left to 0 and bitfield to full

		self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.tracker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.tracker_socket.connect((socket.gethostbyname('localhost'), 6969))
		self.bitfield = BitArray(self.metainfo.num_pieces)
		if(self.check_for_file()):
			self.bitfield.set(True)
			self.left = 0		

		else:
			self.bitfield.set(False)
			self.left = self.metainfo.file_length
		self.send_GET_request(0)
		
		self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.listening_socket.bind((socket.gethostbyname(self.ip_addr), self.port))
		self.listening_socket.listen(5) 

		# while True:
		# 	(opentracker_socket, opentracker_addr) = self.socket.accept()
		# 	response = socket.recv(4096)
		# 	print(response)



		tracker_response = self.tracker_socket.recv(1024)
		print("Response: ", tracker_response)
		status = re.split(" ", str(tracker_response)[2:-1])
		if(status[1] != "200"):
			print("ERROR")

		else:
			print("parsing tracker response...")
			self.response = tracker_response
			self.handle_tracker_response()



		#listen for handshakes
		i = 0
		while True:

			i = i + 1

			try:
				peer_connection, address = self.listening_socket.accept()
				print(i)
				buf = peer_connection.recv(1024)
				print("maybe receive stuff")
				#print(len(buf))
				#if message is handshake
				
				if buf[0]==18 and buf[1:19] == b'URTorrent protocol' and buf[19:27] == b'\x00\x00\x00\x00\x00\x00\x00\x00' and buf[27:47] == self.info_hash.digest():
				#if len(buf) > 0 and "URTorrent" in str(buf):
					#ip = connection_socket.getsockname()[0]
					#port = connection_socket.getsockname()[1]
					#connection_socket.close()
					print("Received valid handshake", buf)

					peer_connection.send(self.generate_handshake_msg())

					#split off thread to listen for piece requests on this socket
					peer_connection.settimeout(120)
					threading.Thread(target = self.listen_to_peer, args = (peer_connection, address)).start()
					#listen = Listen(self)
					#listen.start()
					#self.listen_list[0].start()

			except Exception as exc:
				print(str(exc))
				peer_connection.close()
				break
			except KeyboardInterrupt:
				print("Closing")
				peer_connection.close()
				break


			#if message is request for piece
		#	elif len(buf) > 0:
		#		print("Got request: ", buf)
		#		connection_socket.send(bytearray(map(ord, "HELLO FRIEND")))
		#		print("Sent reply to ", address)
			
	#		peer_connection.close()
			
	

	def check_for_file(self):
		if os.path.exists(self.filename):
			print("FILE EXISTS")
			#piece length 65536
			#file size 4641991

			#split file into temporary chunks
			f = open(self.filename, "rb")
			for i in range(self.metainfo.num_pieces-2):
				temp_filename = "temp-" + str(i) + self.filename
				fout = open(temp_filename, 'w+b')
				b = f.read(65536)
				if(b):
					fout.write(b)

			temp_filename = "temp-" + str(self.metainfo.num_pieces-1) + self.filename
			fout = open(temp_filename, 'w+b')
			while True:
				b = f.read(1)
				if(b):
					fout.write(b)
				else:
					break

			return True

		else:
			print("FILE DOESN'T EXIST")
			return False

		#if file is in local directory start running in seeder state
		#else if file is not in local directory run in leecher state

	def send_GET_request(self, event):
		get_request = bytearray(map(ord, "GET /announce?info_hash="))
		get_request.extend(map(ord, urllib.parse.quote_plus(self.metainfo.info_hash.digest())))
		get_request.extend(map(ord, "&peer_id="))
		get_request.extend(map(ord, urllib.parse.quote_plus(self.peer_id)))
		get_request.extend(map(ord, "&port="))
		get_request.extend(bytes(str(self.port), "ascii"))
		#ignore key
		get_request.extend(map(ord, "&uploaded="))
		get_request.extend(bytes(str(self.uploaded), "ascii"))
		get_request.extend(map(ord, "&downloaded"))
		get_request.extend(bytes(str(self.downloaded), "ascii"))
		get_request.extend(map(ord, "&left"))
		get_request.extend(bytes(str(self.left), "ascii"))
		get_request.extend(map(ord, "&compact=1"))
		if event==0:
			get_request.extend(map(ord, "&event=started HTTP/1.1\r\n\r\n"))
		elif event==1:
			get_request.extend(map(ord, "&event=completed HTTP 1.1\r\n\r\n"))
		elif event==2:
			get_request.extend(map(ord, "&event=stopped HTTP/1.1\r\n\r\n"))
		else:
			get_request.extend(map(ord, " HTTP/1.1\r\n\r\n"))
		print("GET request: ", get_request)

		#send HTTP request to tracker

		self.tracker_socket.send(get_request)

		return get_request

	def handle_tracker_response(self):
		print("Raw Response: ", self.response)
		#decoded_response = self.response.decode('utf-8') 
		#print("Decoded Response: ", decoded_response)
		split_decoded = self.response.split(b'\r\n\r\n')
		response_dict = decode(split_decoded[1])
		print("Tracker response: ", response_dict)

		#check for failure reason
		if b'failure reason' in response_dict:
			print(response_dict[b'failure reason'].decode('utf-8'))

		else:
			self.interval = response_dict[b'interval']
			#self.tracker_id = response_dict[b'tracker id']
			self.complete = response_dict[b'complete']
			self.incomplete = response_dict[b'incomplete']


			#parse list of peers
			peerlist = list()
			unparsed_peers = response_dict[b'peers']
			print(unparsed_peers)

			#add peers to list of tuples (IP, port)
			for x in range(len(unparsed_peers)//6):
				ip = socket.inet_ntoa(unparsed_peers[x*6:x*6+4])
				port = int.from_bytes(unparsed_peers[x*6+4:x*6+6], byteorder='big')
				#print("Reading peer ", ip, port)
				peerlist.append((ip, port))

			print(peerlist);
			self.peer_list = peerlist

			#for each peer in peer list, check if connected
			for (IP, port) in self.peer_list:
				#print(self.ip_addr, IP, self.ip_addr != IP)
				#print(self.port, port, self.port != port)
				if (IP != self.ip_addr) or (port != self.port):
					for connection in self.connection_list:
						if (IP == connection.peer_ip_addr) and (port == connection.peer_port):
							break
					else:
						#if not connected, initiate handshake with peer
						print("Connect to peer ", IP, port)
						self.initiate_handshaking(IP, port)


	def initiate_handshaking(self, IP, port):
		handshake_message = self.generate_handshake_msg()
	#	new_connection = Connection(self, IP, port, BitArray(self.metainfo.num_pieces).set(False))
		# temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# temp_socket.connect((socket.gethostbyname(IP), port))
		# ip = temp_socket.getsockname()[0]
		# port = temp
		new_connection = Connection(self, IP, port, BitArray(self.metainfo.num_pieces).set(False))
		#send start of handshake
	#	temp_socket.send(handshake_message)
		new_connection.sock.send(handshake_message)
		print("Handshake initiated ", handshake_message)

		#just try to read hello message for now
	#	handshake_response = temp_socket.recv(1024)
		handshake_response = new_connection.sock.recv(1024)

		#if handshake response is valid, save connection

		if handshake_response[0]==18 and handshake_response[1:19] == b'URTorrent protocol' and handshake_response[19:27] == b'\x00\x00\x00\x00\x00\x00\x00\x00' and handshake_response[27:47] == self.info_hash.digest():			
			new_connection.peer_id = handshake_response[47:68]
			print("Received valid handshake response ", handshake_response)
			self.connection_list.append(new_connection)
			new_connection.start()

			#listen for bitfield?


		# new_connection, address = self.listening_socket.accept()
		# buf = new_connection.sock.recv(1024)
		# if len(buf) > 0:
		# 	print("Received handshake response", buf)
			#check if handshake is valid/good
			#split off thread to listen for piece requests on this socket	

		#listen for bitfield?

	def listen_to_peer(self, peer, address):
		while True:
			try:
				message = peer.recv(1024)
				if message:
					print("received message")
					#check messsage type
					message_prefix = struct.unpack('>i', message[0:4])[0]
					print("Message Prefix = ", message_prefix)
					print(message_prefix==13)
					message_id = message[4]
					print("Message ID = ", message_id)
					print(message_id == 6)
					if message_prefix == 1:
						if message_id == 0:
							#choke
							self.peer_choking == 1
						elif message_id == 1:
							#unchoke
							self.peer_choking == 0
						elif message_id == 2:
							self.peer_interested == 1
						elif message_id == 3:
							self.peer_interested = 0
						else:
							print("Invalid Message")
					elif message_prefix == 5:
						#have message
						print("Have Message")
					elif message_prefix == 1 + len(self.peer_bitfield):
						if message_id == 5:
							#bitfield message
							#check that bitfield is correct length
							self.peer_bitfield = message[5:6+len(self.peer_bitfield)]
							print(self.peer_bitfield)
					elif message_prefix == 13:
						print("Request message received")
						index = message[5:9]
						begin = message[9:13]
						length = message[13:17]
						if message_id == 6:
							#request message
							#check that peer is not choked
							#send requested chunk
							length_prefix = 9 + 65536
							piece_payload = bytearray(b'\x07')
							piece_payload.extend(index)
							piece_payload.extend(begin)
							filename = "temp-" + str(int.from_bytes(index, byteorder='big')) + self.metainfo.filename
							f = open(filename, 'rb')
							b = bytearray()
							b = f.read(65536)
							if not b:
								while True:
									k = f.read(1)
									if k:
										b.extend(k)
									else:
										break

							piece_payload.extend(b)
							piece_message = bytearray(struct.pack('>i',len(piece_payload)))
							piece_message.extend(piece_payload)
							print("Piece Message: ", piece_message)
							peer.send(piece_message)
					
						elif message_id == 8:
							#cancel message
							print("Cancel Message")
						else:
							print("Invalid Message")
					#default block size is 16384
					elif message_prefix == 9 + 16384:
						if message_id == 7:
							#piece message
							index = message[5:9]
							begin = message[9:13]
							piece = message[13:16397]
							#save piece
						else:
							print("Invalid Message")
					else:
						print("Invalid Message")

					time.sleep(1)
				else:
					print("No data received")
					time.sleep(1)
			except:
				print("Except")
				return False

	def next_piece(self):
		#find random rarest missing pieces
		#return index of piece
		return 0


	def request_piece(self, index):

		#find peers that client is interested in that are not choking client
		#request desired piece of file
		#while file not complete
			#i = next_piece()
			#request_piece(i)
		return 0

	#generate handshake message 
	def generate_handshake_msg(self):
		handshake = bytearray(b'\x12')
		handshake.extend(map(ord, "URTorrent protocol"))
		handshake.extend(bytearray(8))
		handshake.extend(self.metainfo.info_hash.digest())
		handshake.extend(self.peer_id)
		#print("Handshake message: ", handshake)
		return handshake

	def exit_handler(self):
		self.send_GET_request(2)
		print("Client closing")
		self.tracker_socket.close()
		self.listening_socket.close()
		print("Cleaning up temporary files")
		for fl in os.listdir():
			if "temp" in fl:
				os.remove(fl)
		print("Quitting...")







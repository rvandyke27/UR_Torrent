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
import pickle
from threading import Thread
from random import randint
import struct

class Client:


	def __init__(self, ip_addr, port, filename):

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


		listening_thread = threading.Thread(target = self.listen_for_handshake)
		listening_thread.daemon = True
		listening_thread.start()

	def leech(self):
		while True:
			time.sleep(.2)
			if self.bitfield.all(True):
				print(self.bitfield.all(True))
				break
			#determine which piece to look for
			index = self.next_piece()
			#see who on peer list has the piece
			for connection in self.connection_list:
				if connection.has_piece(index):
					#request the piece from the peer
					print("Requesting piece ", str(index), " from ", connection.peer_port )
					self.request_piece(index, connection)
					break
		#stop when bitfield is full
		print("done")
		self.reassemble_file()
		return
		#close connections but keep listening

	
	def send_have_message(self, index):
		print("TODO")
		return


	def check_for_file(self):
		if os.path.exists(self.filename):
			print("FILE EXISTS")
			#piece length 65536
			#file size 4641991

			#split file into temporary chunks
			f = open(self.filename, "rb")
			for i in range(self.metainfo.num_pieces-1):
				temp_filename = "temp-" + str(i) + self.filename
				fout = open(temp_filename, 'wb')
				b = bytearray()
				b = f.read(self.metainfo.piece_length)
				if(b):
					fout.write(b)
				piece_hash = hashlib.sha1()
				piece_hash.update(b)
				#print(i)
				#print(piece_hash.hexdigest())
				#print(self.metainfo.get_piece_hash(i))


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

			requesting_thread = threading.Thread(target = self.leech)
			requesting_thread.daemon = True
			requesting_thread.start()

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
						handshake_thread = threading.Thread(target = self.initiate_handshaking, args = (IP, port))
						handshake_thread.daemon = True
						handshake_thread.start()

						handshake_thread.join()


	def initiate_handshaking(self, IP, port):
		handshake_message = self.generate_handshake_msg()
		new_connection = Connection(self, IP, port, BitArray(self.metainfo.num_pieces))
		#send start of handshake
		new_connection.sock.send(handshake_message)
		print("Handshake initiated ", handshake_message)
		handshake_response = new_connection.sock.recv(1024)

		#if handshake response is valid, save connection
		if handshake_response[0]==18 and handshake_response[1:19] == b'URTorrent protocol' and handshake_response[19:27] == b'\x00\x00\x00\x00\x00\x00\x00\x00' and handshake_response[27:47] == self.info_hash.digest():			
			new_connection.peer_id = handshake_response[47:68]
			print("Received valid handshake response ", handshake_response)
			self.connection_list.append(new_connection)

			new_connection.start()

	def listen_to_peer(self, peer, address):
		while True:
			try:
				message = peer.recv(1024)
				if message:
					print("received message")
					#check messsage type
					message_prefix = struct.unpack('>i', message[0:4])[0]
					print("Message Prefix = ", message_prefix)
					message_id = message[4]
					print("Message ID = ", message_id)
					if message_id == 6:
						print("Request message received")
						index = message[5:9]
						begin = message[9:13]
						length = message[13:17]
						#request message
						#check that peer is not choked
						#send requested chunk
						length_prefix = 9 + 65536
						piece_payload = bytearray(b'\x07')
						piece_payload.extend(index)
						piece_payload.extend(begin)
						print("Sending piece Message: ", piece_payload)
						int_index = struct.unpack('>i', index)[0]
						filename = "temp-" + str(int_index) + self.metainfo.filename
						f = open(filename, 'rb')
						b = bytearray()
						if int_index < self.metainfo.num_pieces-1:
							b = f.read(65536)
						else:
							b = f.read(self.metainfo.file_length % self.metainfo.piece_length)
							#print("Last piece data: ", b)

						piece_payload.extend(b)
						piece_message = bytearray(struct.pack('>i',len(piece_payload)))
						piece_message.extend(piece_payload)
						peer.send(piece_message)
						self.uploaded+=1
					
					elif message_id == 8:
							#cancel message
							print("Cancel Message")
					elif message_id == 4:
						#have message
						print("Have Message")
						#self.bitfield.bin[]
					elif message_id == 5:
						#bitfield message
						#check that bitfield is correct length
						if(len(self.bitfield.bin) == len(message[5:])):
							print("Received bitfield of ", message[5:])
						#self.peer_bitfield.bin = message[5:6+len(self.peer_bitfield)]
						#print(self.peer_bitfield)
					#default block size is 16384
					elif message_id == 7:
						#piece message
						index = message[5:9]
						begin = message[9:13]
						piece = message[13:]
						#save piece	
					else:
						print("Invalid Message")

					time.sleep(.1)
				else:
					print("No data received")
					time.sleep(1)
			except Exception as e:
				print(e)
				return False

	def next_piece(self):
		#find missing piece
		print("Choose piece")
		while True:
			j = randint(0, self.metainfo.num_pieces-1)
			if self.bitfield.bin[j] == '0':
				print("Chose next piece index = ", j)
				return j
		else:
			return 0


	def request_piece(self, index, peer_connection):
		piece_request = bytearray(18)
		piece_request[0:4] = struct.pack('>i', int(13))
		piece_request[4] = 6
		piece_request[5:9] = struct.pack('>i', int(index))
		piece_request[9:13] = struct.pack('>i', int(0))
		if index < self.metainfo.num_pieces-1:
			piece_request[13:17] = struct.pack('>i', int(self.metainfo.piece_length))
		else:
			print("Last Piece")
			file_size = self.metainfo.file_length
			last_piece_size = file_size % self.metainfo.num_pieces
			#print(last_piece_size)
			piece_request[13:17] = struct.pack('>i', int(last_piece_size))

		print("Sending piece request: ", piece_request)
		peer_connection.sock.send(piece_request)
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

	def reassemble_file(self):
		print("Reassembling File...")
		f = open(self.filename, 'ab')

		for i in range(self.metainfo.num_pieces):
			piece_filename = "temp-" + str(i) + self.filename
			piece = open(piece_filename, 'rb')
			b = bytearray()
			b = piece.read(65536)
			if not b:
				while True:
					k = piece.read(1)
					if k:
						b.extend(k)
					else:
						break

			f.write(b)

		#for fl in os.listdir():
		#	if "temp" in fl:
		#		os.remove(fl)

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



	def listen_for_handshake(self):

		#listen for handshakes
		i = 0
		while True:

			i = i + 1

			try:
				peer_connection, address = self.listening_socket.accept()
				print(i)
				buf = peer_connection.recv(1024)
				#print(len(buf))
				#if message is handshake
				
				if buf[0]==18 and buf[1:19] == b'URTorrent protocol' and buf[19:27] == b'\x00\x00\x00\x00\x00\x00\x00\x00' and buf[27:47] == self.info_hash.digest():
				#if len(buf) > 0 and "URTorrent" in str(buf):
					#ip = connection_socket.getsockname()[0]
					#port = connection_socket.getsockname()[1]
					#connection_socket.close()
					print("Received valid handshake", buf)
					#self.listen_list.append()

					new_listener = (peer_connection.getsockname()[0], address)

					self.listen_list.append(new_listener)
					#print(self.listen_list[0])
					peer_connection.send(self.generate_handshake_msg())

					time.sleep(.1)

					#send bitfield message
					bitfield_message = bytearray(1+self.metainfo.num_pieces)
					bitfield_message[0:4] = struct.pack('>i', int(1+self.metainfo.num_pieces))
					bitfield_message[4] = 5
					bitfield_message[5:] = self.bitfield
					print("Sending bitfield message: ", bitfield_message)
					peer_connection.send(bitfield_message)

					#split off thread to listen for piece requests on this socket
					peer_connection.settimeout(120)
					listen_thread = threading.Thread(target = self.listen_to_peer, args = (peer_connection, address))
					listen_thread.daemon = True

					listen_thread.start()

				#	listen_thread.join()
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



	


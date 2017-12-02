
import urllib.parse
from bencodepy import decode_from_file, decode
import hashlib
import connection
import struct
import os
import os.path
import socket
from metainfo import Metainfo
import re
from bitstring import BitArray

class Client:

	def __init__(self, ip_addr, port, filename):

		#list of peers (and connection info) that this client is connected to
		self.connection_list = []
		self.metainfo = Metainfo(filename)
		self.filename = filename
		self.ip_addr = ip_addr
		self.port = port
		self.peer_id = os.urandom(20)
		self.info_hash = self.metainfo.info_hash
		self.uploaded = 0
		self.downloaded = 0
		#if client has file, set left to 0 and bitfield to full
		self.left = self.metainfo.file_length

		self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.tracker_socket.connect((socket.gethostbyname('localhost'), 6969))
		self.bitfield = BitArray(self.metainfo.num_pieces)
		if(self.check_for_file()):
			self.bitfield.set(True)
		else:
			self.bitfield.set(False)
		self.send_GET_request(0)
		
		#from metainfo file
		# self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# self.socket.bind((socket.gethostbyname(self.ip_addr), self.port))
		# self.socket.listen(30) #placeholder, can listen to up to 30 peers right now
		# self.check_for_file()
		# self.send_GET_request_test()

		# while True:
		# 	(opentracker_socket, opentracker_addr) = self.socket.accept()
		# 	response = socket.recv(4096)
		# 	print(response)



		self.response = self.tracker_socket.recv(2048)
		status = re.split(" ", self.response.decode('utf-8'))
		print(self.response)
		if(status[1] != "200"):
			print("ERROR")

		else:
			print("parse content")
			
			parsed = self.response.decode('utf-8') 
			print(parsed)
			split_parsed = parsed.split('\r\n\r\n')
			print(split_parsed)
			response_dict = decode(split_parsed[1].encode('utf-8'))
			print(response_dict)

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

				#add peers to list of tuples (IP, port)
				for x in range(len(unparsed_peers)//6):
					peerlist.append((unparsed_peers[x*6:x*6+4], unparsed_peers[x*6+4:x*6+6]))

				print(peerlist);
				self.peer_list = peerlist

	def check_for_file(self):
		if os.path.exists(self.filename):
			print("FILE EXISTS")
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
		print(get_request)

		#send HTTP request to tracker

		self.tracker_socket.send(get_request)
	#	tracker_response = self.tracker_socket.recv(1024)
	#	print(tracker_response)

		return get_request

	# def send_GET_request_test(self):
		# get_request = b"GET /announce?info_hash=_tWL%26%BD%C4%BDsEn%FD%7E1%2CJ3%40s%1B&peer_id=M3-4-2--5ffd511f4079&port=6881&key=585b8345&uploaded=0&downloaded=0&left=0&compact=1&event=started HTTP/1.1"

		# self.socket.connect(('localhost', 6969))
		# self.socket.send(get_request)
		# print(get_request)
		# tempsocket.close()



	def next_piece(self):
		#find rarest missing pieces
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
		handshake = bytearray(b'\x18')
		handshake.extend(map(ord, "URTorrent protocol"))
		handshake.extend(bytearray(8))
		handshake.extend(metainfo.info_hash.digest())
		handshake.extend(map(ord, peer_id))
		print(handshake)
		print(len(handshake))
		return



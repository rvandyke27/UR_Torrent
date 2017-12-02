
import urllib.parse
from bencodepy import decode_from_file, decode
import hashlib
import connection
import struct
import os
import socket
from metainfo import Metainfo
import socket
import re

class Client:

	def __init__(self, ip_addr, port, filename):

		#list of peers (and connection info) that this client is connected to
		self.connection_list = []
		self.metainfo = Metainfo(filename)
		self.ip_addr = ip_addr
		self.port = port
		self.peer_id = os.urandom(20)
		self.info_hash = self.metainfo.info_hash
		self.uploaded = 0
		self.downloaded = 0
		#if client has file, set left to 0
		self.left = self.metainfo.file_length

		self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.tracker_socket.connect((socket.gethostbyname('localhost'), 6969))

		self.check_for_file()
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



		self.response = self.tracker_socket.recv(1024)
		status = re.split(" ", str(self.response))
		print(self.response)
		if(status[1] != "200"):
			print("ERROR")

		else:
			print("parse content")
			test = b"d8:completei0e10:downloadedi0e10:incompletei1e8:intervali1869e12:min intervali934e5:peers6:'e"
			print("test")
			# mydata = b'd8:completei0e10:downloadedi0e10e' 
			# my_ordred_dict = decode(mydata) 
			# print(my_ordred_dict) 
			# parsed = re.split(r"[\r\n]+", str(self.response)) #might need to change to "\r\n" when using real response
			parsed = str(self.response).split("\\r\\n\\r\\n") 
			parsed_fixed = parsed[1][:-1] + 'e'
			print(parsed_fixed)
			#decoded_response = decode(parsed_fixed.encode())
			print(parsed[1])
			print(parsed_fixed)	
			print(decode(test))		
			#print(decoded_response)

		#message = read/parse response from socket 
		#from tracker reply to GET request
		#self.peer_list = {} from response
		#self.interval = interval part of response
		#self.tracker_id = tracker_id from resposne
		#self.complete = ...

	def check_for_file(self):
		return 0
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
		get_request.extend(map(ord, "&compact=1&event="))
		if event==0:
			get_request.extend(map(ord, "started HTTP/1.1\r\n\r\n"))
		elif event==1:
			get_request.extend(map(ord, "completed HTTP 1.1\r\n\r\n"))
		elif event==2:
			get_request.extend(map(ord, "stopped HTTP/1.1\r\n\r\n"))
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



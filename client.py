
import urllib.parse
from bencoding import *
from bencodepy import decode_from_file, decode
import hashlib
import connection
import struct
import os

from metainfo import Metainfo

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
		self.left = metainfo.file_length

		self.check_for_file()
		self.send_GET_request()
		
		#from metainfo file

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

	def send_GET_request(self):
		get_request = bytearray("GET /announce?info_hash=")
		get_request.extend(urllib.parse.quote_plus(metainfo.info_hash.digest.encode('utf-8')))
		get_request.extend("&peer_id=")
		get_request.extend(urllib.parse.quote_plus(self.peer_id.encode('utf-8')))
		get_request.extend("&port=")
		get_request.extend(self.port)
		#get tracker information dictionary from metainfo file
		#info_hash, peer_id, port, uploaded, downloaed, left, compact, event, 
		#send HTTP request to tracker	
		return 0

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




import hashlib
import math
from bencodepy import decode_from_file, decode
from collections import OrderedDict
import json

class Metainfo:

	def __init__(self, filename):

		self.metainfo_file_path = "UR.mp3.torrent".encode('utf-8')
		self.decoded_metainfo = decode_from_file(self.metainfo_file_path)
	
		self.info_dict = self.decoded_metainfo[b'info']
	
		self.info_hash = hashlib.sha1()
		for key in self.info_dict.keys():
			self.info_hash.update(key)

		for value in self.info_dict.values():
			self.info_hash.update(bytearray(value))

		self.announce = self.decoded_metainfo[b'announce'].decode('utf-8')
		self.filename = filename
		self.piece_length = self.info_dict[b'piece length']
		self.file_length = self.info_dict[b'length']
		self.pieces = self.info_dict[b'pieces']
		self.num_pieces = math.ceil(self.info_dict[b'length']/self.info_dict[b"piece length"])

		self.print()

	def print(self):
		print("metainfo file:  " + "UR.mp3.torrent")
		print("info hash    :  " + str(self.info_hash.hexdigest()))
		print("filename    :  " + self.filename)
		print("piece length:  " + str(self.info_dict[b"piece length"]))
		print("file size:  " + str(self.info_dict[b"length"]))
		print("announce URL:  " + str(self.decoded_metainfo[b"announce"])[1:])
		print("pieces' hashes:  ")
		for i in range(0, self.num_pieces):
			print(str(i) + " " + self.info_dict[b"pieces"][i*20:i*20+20].hex())

	def get_piece_hash(self, index):
		return self.info_dict[b'pieces'][index*20:index*20+20].hex()


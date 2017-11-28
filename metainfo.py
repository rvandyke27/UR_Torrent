
import hashlib
from client import Client
import math
from bencodepy import decode_from_file, decode
from collections import OrderedDict
import json

class Metainfo:

	def __init__(self, announce, info, length, name, piece_length, pieces):

		metainfo_file_path = "UR.mp3.torrent".encode('utf-8')
		decoded_metainfo = decode_from_file(metainfo_file_path)
	
		info_dict = decoded_metainfo[b'info']
	
		info_hash = hashlib.sha1()
		for key in info_dict.keys():
			info_hash.update(key)

		for value in info_dict.values():
			info_hash.update(bytearray(value))
import hashlib
from client import Client
import math
from bencodepy import decode_from_file, decode
from collections import OrderedDict
import json

#generate handshake message
#handshake: (pstrlen)(pstr)(reserved)(info_hash)(peer_id) 
def handshake( peer_id, info_hash ):
	return 0
	#peer_id comes from tracker



def main():

	client = Client('127.0.0.1', 9999, 'UR.mp3')
	#parse metainfo file
	metainfo_file_path = "UR.mp3.torrent".encode('utf-8')
	decoded_metainfo = decode_from_file(metainfo_file_path)
	
	info_dict = decoded_metainfo[b'info']
	
	info_hash = hashlib.sha1()
	for key in info_dict.keys():
		info_hash.update(key)
		print("Key: " + str(key) + '\n')

	for value in info_dict.values():
		info_hash.update(bytearray(value))
		print("val: " + str(value) + '\n')

	print(info_hash)

	#Contact tracker and get list of peers

	#initiate handshaking with peers

	#download/upload chunks according to peer wire protocol
		#maintain state information for each connection with remote peer
		#should include bidirectional status
		#use status info to determine whether a chunk should be downloaded or uploaded
		#rarest first with randomization

	#message flow
		#choke, unchoke, interested, not interested

		#have

		#bitfield
			#sent after handshaking before any other messages
			#client should drop connection if bitfield is wrong length

		#request

		#piece

		#cancel (can be ignored)

	#implement commands

	def print_metainfo():
		print("IP/port    :  " + str(client.ip_addr) + "/" + str(client.port) )
		print("ID        :  " + "someplaceholderstuff")
		print("metainfo file:  " + "UR.mp3.torrent")
		print("info hash    :  " + str(info_hash.hexdigest()))
		print("filename    :  " + "UR.mp3")
		print("piece length:  " + str(info_dict[b"piece length"]))
		print("file size:  " + str(info_dict[b"length"]))
		print("announce URL:  " + str(decoded_metainfo[b"announce"]))
		print("pieces' hashes:  ")
		num_pieces = math.ceil(info_dict[b"length"]/info_dict[b"piece length"])
		print(num_pieces)
		print("other")
	#	for i in range(0, num_pieces):
	#		print(info_dict[b"pieces"][i:i+20+1].hexdigest())
		

	

	while True:
		command = input()
		#metainfo
		if(command == "metainfo"):
			print_metainfo()
		#announce

		#trackerinfo

		#show

		#status

	#status

if __name__=="__main__":
	main()

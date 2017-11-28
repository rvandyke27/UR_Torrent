import hashlib
import client
from bencodepy import decode_from_file, decode
from collections import OrderedDict
import json

#generate handshake message
#handshake: (pstrlen)(pstr)(reserved)(info_hash)(peer_id) 
def handshake( peer_id, info_hash ):
	return
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
		print(key)

	for value in info_dict.values():
		info_hash.update(bytearray(value))
		print(value)

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
		print("IP/port    : " + client.ip_addr + "/" + client.port)

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

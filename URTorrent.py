import hashlib
from client import Client
from metainfo import Metainfo
import math
from bencodepy import decode_from_file, decode
from collections import OrderedDict
import json


def main():

	#parse metainfo file
	# metainfo_file_path = "UR.mp3.torrent".encode('utf-8')
	# decoded_metainfo = decode_from_file(metainfo_file_path)
	
	# info_dict = decoded_metainfo[b'info']
	
	# info_hash = hashlib.sha1()
	# for key in info_dict.keys():
	# 	info_hash.update(key)

	# for value in info_dict.values():
	# 	info_hash.update(bytearray(value))


	# print(info_hash.hexdigest())

	#Determine if leecher or seeder

	#Contact tracker and get list of peers

	#Create client
	client = Client('127.0.0.1', 9999, 'UR.mp3')

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

	while True:
		command = input("URTorrent>")
		#metainfo
		if(command == "metainfo"):
			print("IP/port    :  " + str(client.ip_addr) + "/" + str(client.port))
			print("ID        :  " + str(client.peer_id.hex()))
			client.metainfo.print()
		#announce
		if(command == "announce"):
			client.send_GET_request(-1)
			#print status line of response
			#print tracker info

		#trackerinfo
		if(command == "trackerinfo"):

		#show

		#status
		if(command == "status"):
			print("Downloaded | Uploaded | Left    | My bit field \n---------------------------------------------------")
			print('{:11}|{:10}|{:6}|{19}'.format(client.downloaded, client.uploaded, client.left, client.bitfield))


	#status

if __name__=="__main__":
	main()
import sys
sys.path.insert(0, '/Users/aviwebberman/Desktop/GitHub/final_project')
import hashlib
from client import Client
from metainfo import Metainfo
import math
from bencodepy import decode_from_file, decode
from collections import OrderedDict
import json
import re
import socket
from bitstring import BitArray


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
			client.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client.tracker_socket.connect((socket.gethostbyname('localhost'), 6969))
			client.send_GET_request(-1)
			client.response = client.tracker_socket.recv(1024)
			status_line = str(client.response).split('\\r\\n')
			print("Tracker responded: " + status_line[0][2:])
			#print status line of response
			#print tracker info
			client.tracker_socket.close()

		#trackerinfo
		if(command == "trackerinfo"):
			print("trackerinfo")
		#show

		#status
		if(command == "status"):
			print("Downloaded | Uploaded | Left    | My bit field \n---------------------------------------------------")
			#print('{:11}|{:10}|{:6}|{19}'.format(client.downloaded, client.uploaded, client.left, client.bitfield))
			print(str(client.downloaded) + "	" + str(client.uploaded) + "	" + str(client.left) + "	" + str(client.bitfield.bin))
			#print(client.downloaded)
			#print(client.uploaded)
			#print(client.left)
			#print(client.bitfield)
	#status

if __name__=="__main__":
	main()
import hashlib
import sys
import os
up1 = os.path.abspath('..') 
sys.path.insert(0, up1)
from client import Client
from metainfo import Metainfo
import math
from bencodepy import decode_from_file, decode
from collections import OrderedDict
import re
import socket



def main():

	#Create client

	client = Client('127.0.0.1', int(sys.argv[1]), str(sys.argv[2]))


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
			print_tracker_info(client)
			client.tracker_socket.close()

		#trackerinfo
		if(command == "trackerinfo"):
			print_tracker_info(client)
		#show

		#status
		if(command == "status"):
			print("Downloaded | Uploaded | Left    | My bit field \n---------------------------------------------------")
			#print('{:11}|{:10}|{:6}|{19}'.format(client.downloaded, client.uploaded, client.left, client.bitfield))
			print(str(client.downloaded) + "	" + str(client.uploaded) + "	" + str(client.left) + "	" + client.bitfield.bin)
			

def print_tracker_info(client):
	print("complete  |  downloaded  |  incomplete  |  interval  |  \n---------------------------------------------------")
	print(str(client.complete), "       |", str(client.downloaded), "         |", str(client.incomplete), "      |", str(client.interval), "      |")
	print("---------------------------------------------------\nPeer List (self included):")
	print("     IP            |  Port")
	print("     ----------------------------")
	peer_list = client.peer_list
	for (IP, port) in peer_list:
		print("     ", IP, "    |  ", port)

if __name__=="__main__":
	main()

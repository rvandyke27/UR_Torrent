import hashlib

from bencodepy import decode_from_file, decode
from collections import OrderedDict
import json

#generate handshake message
#handshake: (pstrlen)(pstr)(reserved)(info_hash)(peer_id) 
def handshake( peer_id ):
	return
	#info_hash = hashlib.sha1(info_dict.items)
	#info_key comes from metainfo file
	#peer_id comes from tracker

def main():
	#parse metainfo file
	metainfo_file_path = "UR.mp3.torrent".encode('utf-8')
	decoded_metainfo = decode_from_file(metainfo_file_path)
	#print("Decoded metainfo file\n")
	#print(decoded_metainfo)
	info_dict = decoded_metainfo[b'info']
	#print("info dictionary\n")
	#print(info_dict)
	


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
		#metainfo

		#announce

		#trackerinfo

		#show

		#status

	#status

if __name__=="__main__":
	main()

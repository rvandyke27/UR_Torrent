import hashlib
from bencodepy import decode_from_file

def main():
	#parse metainfo file
	metainfo_file_path = "\UR.torrent"
	decoded_metainfo = decode_from_file(metainfo_file_path)
	print(decoded_metainfo)
	
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

if__name__=="__main__":
	main()

#generate handshake message
#handshake: (pstrlen)(pstr)(reserved)(info_hash)(peer_id) 
def handshake( peer_id ):
	info_hash = hashlib.sha1(info_key);
	#info_key comes from metainfo file
	#peer_id comes from tracker
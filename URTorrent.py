#Contact tracker and get list of peers


#initiate handshaking with peers
#handshake: (pstrlen)(pstr)(reserved)(info_hash)(peer_id) 
#info_key comes from metainfo file
info_hash = hashlib.sha1(info_key);
#peer_id comes from tracke

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
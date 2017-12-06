import urllib.parse
from bencodepy import decode_from_file, decode
from listen import Listen
import hashlib
import connection
import struct
import os
import os.path
import socket
from metainfo import Metainfo
import re
from bitstring import BitArray
from connection import Connection
import threading
import time

class Client:

    def __init__(self, ip_addr, port, filename):

        #list of peers (and connection info) that this client is connected to
        self.connection_list = list()
        self.listen_list = list()
        self.metainfo = Metainfo(filename)
        self.filename = filename
        self.ip_addr = ip_addr
        self.port = port
        self.peer_id = os.urandom(20)
        self.info_hash = self.metainfo.info_hash
        self.uploaded = 0
        self.downloaded = 0
        #if client has file, set left to 0 and bitfield to full

        self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tracker_socket.connect((socket.gethostbyname('localhost'), 6969))
        self.bitfield = BitArray(self.metainfo.num_pieces)
        if(self.check_for_file()):
            self.bitfield.set(True)
            self.left = 0        

        else:
            self.bitfield.set(False)
            self.left = self.metainfo.file_length
        self.send_GET_request(0)
        
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listening_socket.bind((socket.gethostbyname(self.ip_addr), self.port))
        self.listening_socket.listen(5) 

        # while True:
        #     (opentracker_socket, opentracker_addr) = self.socket.accept()
        #     response = socket.recv(4096)
        #     print(response)



        tracker_response = self.tracker_socket.recv(2048)
        print(tracker_response)
        status = re.split(" ", tracker_response.decode('utf-8'))
        if(status[1] != "200"):
            print("ERROR")

        else:
            print("parsing tracker response...")
            self.response = tracker_response
            self.handle_tracker_response()



        #listen for handshakes
        i = 0
        while True:

            i = i + 1


            peer_connection, address = self.listening_socket.accept()
            print(i)
            buf = peer_connection.recv(1024)
            print("maybe receive stuff")
            #print(len(buf))
            #if message is handshake
            
            if buf[0]==18 and buf[1:19] == b'URTorrent protocol' and buf[19:27] == b'\x00\x00\x00\x00\x00\x00\x00\x00' and buf[27:47] == self.info_hash.digest():
            #if len(buf) > 0 and "URTorrent" in str(buf):
                #ip = connection_socket.getsockname()[0]
                #port = connection_socket.getsockname()[1]
                #connection_socket.close()
                print("Received valid handshake", buf)

                peer_connection.send(self.generate_handshake_msg())

                #split off thread to listen for piece requests on this socket
                peer_connection.settimeout(120)
                threading.Thread(target = self.listen_to_peer, args = (peer_connection, address)).start()
                #listen = Listen(self)
                #listen.start()
                #self.listen_list[0].start()


            #if message is request for piece
        #    elif len(buf) > 0:
        #        print("Got request: ", buf)
        #        connection_socket.send(bytearray(map(ord, "HELLO FRIEND")))
        #        print("Sent reply to ", address)
            
    #        peer_connection.close()
            
    

    def check_for_file(self):
        if os.path.exists(self.filename):
            print("FILE EXISTS")
            return True

        else:
            print("FILE DOESN'T EXIST")
            return False

        #if file is in local directory start running in seeder state
        #else if file is not in local directory run in leecher state

    def send_GET_request(self, event):
        get_request = bytearray(map(ord, "GET /announce?info_hash="))
        get_request.extend(map(ord, urllib.parse.quote_plus(self.metainfo.info_hash.digest())))
        get_request.extend(map(ord, "&peer_id="))
        get_request.extend(map(ord, urllib.parse.quote_plus(self.peer_id)))
        get_request.extend(map(ord, "&port="))
        get_request.extend(bytes(str(self.port), "ascii"))
        #ignore key
        get_request.extend(map(ord, "&uploaded="))
        get_request.extend(bytes(str(self.uploaded), "ascii"))
        get_request.extend(map(ord, "&downloaded"))
        get_request.extend(bytes(str(self.downloaded), "ascii"))
        get_request.extend(map(ord, "&left"))
        get_request.extend(bytes(str(self.left), "ascii"))
        get_request.extend(map(ord, "&compact=1"))
        if event==0:
            get_request.extend(map(ord, "&event=started HTTP/1.1\r\n\r\n"))
        elif event==1:
            get_request.extend(map(ord, "&event=completed HTTP 1.1\r\n\r\n"))
        elif event==2:
            get_request.extend(map(ord, "&event=stopped HTTP/1.1\r\n\r\n"))
        else:
            get_request.extend(map(ord, " HTTP/1.1\r\n\r\n"))
        print("GET request: ", get_request)

        #send HTTP request to tracker

        self.tracker_socket.send(get_request)

        return get_request

    def handle_tracker_response(self):
        decoded_response = self.response.decode('utf-8') 
        split_decoded = decoded_response.split('\r\n\r\n')
        response_dict = decode(split_decoded[1].encode('utf-8'))
        print("Tracker response: ", response_dict)

        #check for failure reason
        if b'failure reason' in response_dict:
            print(response_dict[b'failure reason'].decode('utf-8'))

        else:
            self.interval = response_dict[b'interval']
            #self.tracker_id = response_dict[b'tracker id']
            self.complete = response_dict[b'complete']
            self.incomplete = response_dict[b'incomplete']


            #parse list of peers
            peerlist = list()
            unparsed_peers = response_dict[b'peers']

            #add peers to list of tuples (IP, port)
            for x in range(len(unparsed_peers)//6):
                ip = socket.inet_ntoa(unparsed_peers[x*6:x*6+4])
                port = int.from_bytes(unparsed_peers[x*6+4:x*6+6], byteorder='big')
                #print("Reading peer ", ip, port)
                peerlist.append((ip, port))

            print(peerlist);
            self.peer_list = peerlist

            #for each peer in peer list, check if connected
            for (IP, port) in self.peer_list:
                #print(self.ip_addr, IP, self.ip_addr != IP)
                #print(self.port, port, self.port != port)
                if (IP != self.ip_addr) or (port != self.port):
                    for connection in self.connection_list:
                        if (IP == connection.peer_ip_addr) and (port == connection.peer_port):
                            break
                    else:
                        #if not connected, initiate handshake with peer
                        print("Connect to peer ", IP, port)
                        self.initiate_handshaking(IP, port)


    def initiate_handshaking(self, IP, port):
        handshake_message = self.generate_handshake_msg()
    #    new_connection = Connection(self, IP, port, BitArray(self.metainfo.num_pieces).set(False))
        # temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # temp_socket.connect((socket.gethostbyname(IP), port))
        # ip = temp_socket.getsockname()[0]
        # port = temp
        new_connection = Connection(self, IP, port, BitArray(self.metainfo.num_pieces).set(False))
        #send start of handshake
    #    temp_socket.send(handshake_message)
        new_connection.sock.send(handshake_message)
        print("Handshake initiated ", handshake_message)

        #just try to read hello message for now
    #    handshake_response = temp_socket.recv(1024)
        handshake_response = new_connection.sock.recv(1024)

        #if handshake response is valid, save connection

        if handshake_response[0]==18 and handshake_response[1:19] == b'URTorrent protocol' and handshake_response[19:27] == b'\x00\x00\x00\x00\x00\x00\x00\x00' and handshake_response[27:47] == self.info_hash.digest():            
            new_connection.peer_id = handshake_response[47:68]
            print("Received valid handshake response ", handshake_response)
            self.connection_list.append(new_connection)
            new_connection.start()

            #listen for bitfield?


        # new_connection, address = self.listening_socket.accept()
        # buf = new_connection.sock.recv(1024)
        # if len(buf) > 0:
        #     print("Received handshake response", buf)
            #check if handshake is valid/good
            #split off thread to listen for piece requests on this socket    

        #listen for bitfield?




    def listen_to_peer(self, peer, address):
        while True:
            try:
                data = peer.recv(1024)
                if data:
                    print("received data")
                    peer.send(b'Hello')
                    time.sleep(1)
                else:
                    print("Client Disconnected")
            except:
                peer.close()
                return False

    def next_piece(self):
        #find random rarest missing pieces
        #return index of piece
        return 0


    def request_piece(self, index):

        #find peers that client is interested in that are not choking client
        #request desired piece of file
        #while file not complete
            #i = next_piece()
            #request_piece(i)
        return 0

    #generate handshake message 
    def generate_handshake_msg(self):
        handshake = bytearray(b'\x12')
        handshake.extend(map(ord, "URTorrent protocol"))
        handshake.extend(bytearray(8))
        handshake.extend(self.metainfo.info_hash.digest())
        handshake.extend(self.peer_id)
        #print("Handshake message: ", handshake)
        return handshake
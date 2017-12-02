
class Connection:

	def __init__(self, ip_addr, port, peer_bitfield):

		self.peer_ip_addr = peer_ip_addr
		self.peer_port = peer_port
		self.am_choking = 1
		self.am_interesting = 0
		self.peer_choking = 1
		self.peer_interested = 0
		self.peer_bitfield = peer_bitfield
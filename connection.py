
class Connection:

	def __init__(self, ip_addr, port, am_choking, am_interested):

		self.ip_addr = ip_addr
		self.port = port
		self.am_choking = am_choking
		self.am_interesting = am_interested
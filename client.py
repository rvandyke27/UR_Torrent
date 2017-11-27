


class Client:


	def __init__(self, client_list, peer_id, ip_addr, port, am_choking, am_interested,filename):

			self.peer_id = peer_id
			self.connection = Connection(ip_addr, port, am_choking, am_interested)

			self.check_for_file(filename)
			self.send_GET_request()


	def check_for_file(filename):
		#if file is in local directory start running in seeder state
		#else if file is not in local directory run in leecher state

	def send_GET_request():

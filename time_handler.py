import ntplib
from time import ctime

class TimeHandler:
	def __init__(self, ntp_server='pool.ntp.org'):
		self.ntp_server = ntp_server
		self.client = ntplib.NTPClient()

	def get_current_time(self):
		try:
			response = self.client.request(self.ntp_server)
			return ctime(response.tx_time)
		except Exception as e:
			print(f"Failed to get time from NTP server: {e}")
			return None

	def get_time_offset(self):
		try:
			response = self.client.request(self.ntp_server)
			return response.offset
		except Exception as e:
			print(f"Failed to get time offset from NTP server: {e}")
			return None

from beverage import Beverage
from open_ai import fetch_image
from time_handler import TimeHandler

class Tea(Beverage):
	def __init__(self, id):
		super().__init__(id)
		self.time_handler = TimeHandler()

	def brew(self):
		print('Brewing tea...')

	def generate_image(self):
		if self.image_data is not None:
			return self.image_data
		self.image_data = fetch_image(f"""
Freshly brewed tea in server room, additions: {', '.join(self.additions)}
""")
		return self.image_data

	def get_temperature(self):
		if self.status == Beverage.State.READY and self.serve_time is not None:
			elapsed_time = self.time_handler.get_current_time() - self.serve_time
			if elapsed_time < Beverage.COOLTIME:
				self.temperature = 20 + (Beverage.COOLTIME - elapsed_time) / Beverage.COOLTIME * 80
			else:
				self.temperature = 20
		return self.temperature
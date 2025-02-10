from enum import Enum
import time
from alcohol import Alcohol
from time_handler import TimeHandler

class Beverage:
	COOLTIME = 20 * 60  # 20 minutes

	class State(Enum):
		NOT_READY = 0
		READY = 1

		def __str__(self):
			return self.name.replace("_", " ").title()

	def __init__(self, id, additions=None):
		self.id = id

		self.status = Beverage.State.NOT_READY
		self.temperature = 20
		self.additions = additions or []
		
		self.serve_time = None
		self.serve_temperature = None

		self.image_data = None
		self.time_handler = TimeHandler()

	def brew(self):
		raise NotImplementedError("This method should be implemented by the inheriting class")

	def get_temperature(self):
		if self.serve_time is not None:
			return self.temperature
		elapsed_time = self.time_handler.get_current_time() - self.serve_time
		if elapsed_time < Beverage.COOLTIME:
			self.temperature = 20 + (Beverage.COOLTIME - elapsed_time) / Beverage.COOLTIME * 80
		else:
			self.temperature = 20
	
	def get_alcohol_percentage(self):
		alcohol_additions = [addition.percentage for addition in self.additions if isinstance(addition, Alcohol)]
		if not alcohol_additions:
			return 0
		return sum(alcohol_additions) / len(alcohol_additions)
	
	def get_serving_time(self):
		return self.serve_time
	
	def generate_image(self):
		raise NotImplementedError("This method should be implemented by the inheriting class")
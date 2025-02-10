import time
import uuid
from enum import Enum
from beverage import Beverage
from tea import Tea
from coffee import Coffee
from milk import Milk
from syrup import Syrup
from alcohol import Alcohol
from spice import Spice
from sweetener import Sweetener
from typing import List, Optional
from open_ai import fetch_image

class Brewer:
	class State(Enum):
		NOT_STARTED = 0
		IN_PROGRESS = 1
		DONE = 2

		def __str__(self):
			return self.name.replace("_", " ").title()

	VALID_ADDITIONS = (
		*Milk.__subclasses__(),
		*Syrup.__subclasses__(),
		*Alcohol.__subclasses__(),
		*Spice.__subclasses__(),
		*Sweetener.__subclasses__(),
	)

	def __init__(self, brewing_seconds: int, additions: Optional[List[str]] = None):
		self.id = str(uuid.uuid4())
		self.state = Brewer.State.NOT_STARTED

		self.brewing_seconds = brewing_seconds
		self.additions = additions or []
		self.time_left_seconds = brewing_seconds

		self.result = None
		self.image_data = None

	def brew(self, serviceRegister):
		raise NotImplementedError("This method should be implemented by the inheriting class")
	
	def get_temperature(self):
		raise NotImplementedError("This method should be implemented by the inheriting class")
	
	def generate_image(self):
		raise NotImplementedError("This method should be implemented by the inheriting class")

	def get_time_left(self) -> int:
		return self.time_left_seconds
	
	def create_addition_class(self, addition_type: str, addition_value: str) -> List:
		ret = []
		count = int(addition_value)
		if count < 0:
			return ret
		for cls in Brewer.VALID_ADDITIONS:
			if addition_type == cls.__name__:
				for _ in range(count):
					ret.append(cls())
				break
		return ret

class CoffeeBrewer(Brewer):
	IDEAL_BREWING_TEMPERATURE = 90
	BREWING_TIME = 5

	def __init__(self, brewing_time: int, additions: Optional[List[str]] = None):
		super().__init__(brewing_time, additions)

	def brew(self, serviceRegister):
		self.state = Brewer.State.IN_PROGRESS

		self.result = Coffee(self.id)
		self.result.status = Beverage.State.NOT_READY
		self.result.temperature = 20 

		for i in range(self.brewing_seconds):
			time.sleep(1)
			self.result.temperature += (
				CoffeeBrewer.IDEAL_BREWING_TEMPERATURE - self.result.temperature
			) / self.brewing_seconds
			self.time_left_seconds -= 1

		self.result.status = Beverage.State.READY
		self.result.temperature = CoffeeBrewer.IDEAL_BREWING_TEMPERATURE

		for addition in self.additions:
			addition_type, addition_value = addition.split(":", 1)
			addition_class = self.create_addition_class(addition_type, addition_value)
			self.result.additions.extend(addition_class)

		self.state = Brewer.State.DONE
		serviceRegister.on_brewed(self, self.result)

	def get_temperature(self) -> int:
		return self.result.get_temperature()
	
	def generate_image(self):
		if self.image_data is not None:
			return self.image_data
		self.image_data = fetch_image(f"""
Coffee brewing machine in server room, brewing coffee with {self.brewing_seconds} seconds,
additions: {', '.join(self.additions)}
""")
		return self.image_data

class TeaBrewer(Brewer):
	IDEAL_BREWING_TEMPERATURE = 85
	BREWING_TIME = 3

	def __init__(self, brewing_time: int, additions: Optional[List[str]] = None):
		super().__init__(brewing_time, additions)

	def brew(self, serviceRegister):
		self.state = Brewer.State.IN_PROGRESS

		self.result = Tea(self.id)
		self.result.status = Beverage.State.NOT_READY
		self.result.temperature = 20 

		for i in range(self.brewing_seconds):
			time.sleep(1)
			self.result.temperature += (
				TeaBrewer.IDEAL_BREWING_TEMPERATURE - self.result.temperature
			) / self.brewing_seconds

		self.result.status = Beverage.State.READY
		self.result.temperature = TeaBrewer.IDEAL_BREWING_TEMPERATURE

		for addition in self.additions:
			addition_type, addition_value = addition.split(":", 1)
			addition_class = self.create_addition_class(addition_type, addition_value)
			self.result.additions.extend(addition_class)

		self.state = Brewer.State.DONE
		serviceRegister.on_brewed(self, self.result)

	def get_temperature(self) -> int:
		return self.result.get_temperature()
	
	def generate_image(self):
		if self.image_data is not None:
			return self.image_data
		self.image_data = fetch_image(f"""
Tea brewing machine in server room, brewing tea with {self.brewing_seconds} seconds,
additions: {', '.join(self.additions)}
""")
		return self.image_data
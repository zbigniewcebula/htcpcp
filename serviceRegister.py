import threading
import time
from typing import List, Optional
from brewing import Brewer
from milk import Milk
from beverage import Beverage

class ServiceRegister:
	def __init__(self):
		self.brewers: List[Brewer] = []
		self.pouring_list: List[Beverage] = []
		self.milk_poured_list: List[Beverage] = []
		self.done_list: List[Beverage] = []

	def register_brewer(self, brewer: Brewer):
		self.brewers.append(brewer)

	def on_brewed(self, brewer: Brewer, beverage: Beverage):
		self.brewers.remove(brewer)
		
		milk_additions = [addition for addition in beverage.additions if isinstance(addition, Milk)]
		if len(milk_additions) > 0:
			pouring_threads = []
			for addition in milk_additions:
				self.milk_poured_list.append(beverage)
				pour_thread = threading.Thread(target=addition.pour)
				pour_thread.start()
				pouring_threads.append(pour_thread)
			for pour_thread in pouring_threads:
				pour_thread.join()
			self.milk_poured_list.remove(beverage)
		self.on_finished(beverage)

	def is_milk_poured(self, beverage: Beverage) -> bool:
		return beverage in self.milk_poured_list

	def on_finished(self, beverage: Beverage):
		self.done_list.append(beverage)
		
		beverage.serve_time = time.time()
		beverage.serve_temperature = beverage.temperature

		beverage.status = Beverage.State.READY

	def get_brewer_by_id(self, brewer_id: str) -> Optional[Brewer]:
		for brewer in self.brewers:
			if brewer.id == brewer_id:
				return brewer
		return None

	def get_beverage_by_id(self, beverage_id: str) -> Optional[Beverage]:
		for beverage in self.done_list:
			if beverage.id == beverage_id:
				return beverage
		return None
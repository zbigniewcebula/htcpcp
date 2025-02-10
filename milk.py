from xml.etree.ElementTree import Element
from addition import Addition

class Milk(Addition):
	def __init__(self):
		super().__init__()
		self.volume = 0.0 # in mililiters
		self.pouring = False

	def pour(self):
		self.pouring = True
		while self.pouring:
			self.volume += 1.0

	def stop_pouring(self):
		self.pouring = False
	
	def to_dict(self):
		return {
			'name': self.__class__.__name__,
			'volume': self.volume
		}
	
	def to_xml(self):
		elem = super().to_xml()
		elem.set('volume', str(self.volume))
		return elem

class Cream(Milk):
	def __init__(self):
		super().__init__()

		self.fat = 0.5

class HalfAndHalf(Milk):
	def __init__(self):
		super().__init__()

		self.fat = 0.3

class WholeMilk(Milk):
	def __init__(self):
		super().__init__()

		self.fat = 0.4

class PartSkim(Milk):
	def __init__(self):
		super().__init__()

		self.fat = 0.2

class Skim(Milk):
	def __init__(self):
		super().__init__()

		self.fat = 0.1

class NonDairy(Milk):
	def __init__(self):
		super().__init__()

		self.fat = 0.0

class SoyMilk(NonDairy):
	def __init__(self):
		super().__init__()

class AlmondMilk(NonDairy):
	def __init__(self):
		super().__init__()
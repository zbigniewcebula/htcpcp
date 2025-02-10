from addition import Addition

class Alcohol(Addition):
	def __init__(self):
		super().__init__()
		self.percentage = self.get_percentage()

	def get_percentage(self):
		raise NotImplementedError("This method should be implemented by the inheriting class")
	
	def to_dict(self):
		ret = super().to_dict()
		ret['percentage'] = self.percentage
		return ret
	
	def to_xml(self):
		elem = super().to_xml()
		elem.set('percentage', str(self.percentage))
		return elem

class Whisky(Alcohol):
	def __init__(self):
		super().__init__()

	def get_percentage(self):
		return 40  # Percentage for Whisky

class Rum(Alcohol):
	def __init__(self):
		super().__init__()

	def get_percentage(self):
		return 37.5  # Percentage for Rum

class Kahlua(Alcohol):
	def __init__(self):
		super().__init__()

	def get_percentage(self):
		return 20  # Percentage for Kahlua

class Aquavit(Alcohol):
	def __init__(self):
		super().__init__()

	def get_percentage(self):
		return 40  # Percentage for Aquavit

class Vodka(Alcohol):
	def __init__(self):
		super().__init__()

	def get_percentage(self):
		return 40  # Percentage for Vodka
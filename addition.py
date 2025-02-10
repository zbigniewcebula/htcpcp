from xml.etree.ElementTree import Element


class Addition:
	def __init__(self):
		pass

	def to_dict(self):
		return {
			'name': self.__class__.__name__
		}
	
	def to_xml(self):
		elem = Element('addition')
		elem.set('name', self.__class__.__name__)
		return elem
import re
import json
from xml.etree.ElementTree import Element, tostring
from serviceRegister import ServiceRegister
from milk import Milk

class MilkHandler:
	def __init__(self, serviceRegister: ServiceRegister, protocolHandler):
		self.serviceRegister = serviceRegister
		self.path = protocolHandler.path
		self.send_response = protocolHandler.send_response
		self.send_header = protocolHandler.send_header
		self.end_headers = protocolHandler.end_headers
		self.wfile = protocolHandler.wfile

	def handle(self):
		if self.path.endswith('/json'):
			self.handle_json()
		else:
			self.handle_plain()

	def handle_plain(self):
		ready_for_milk_beverages = len(self.serviceRegister.milk_poured_list)
		if ready_for_milk_beverages == 0:
			self.send_response(418)
			self.send_header('Content-type', 'text/plain')
			self.send_header('Safe', 'yes')
			self.end_headers()
			self.wfile.write("I'm a teapot".encode())
			return False
		match = re.match(r'^/milk/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})$', self.path)
		if match:
			beverage_id = match.group(1)
			beverage = self.serviceRegister.get_beverage_by_id(beverage_id)
			if beverage:
				self.send_response(200)
				response = f"Beverage with id {beverage.id}\n"
				response += f"Time left: {beverage.get_time_left()}\n"
				response += f"Status: {beverage.status}\n"
				response += f"Additions: {', '.join([addition.to_dict() for addition in beverage.additions])}\n"
				response += f"Temperature: {beverage.get_temperature()}\n"
				#how many milk additions are ready to say WHEN
				milk_additions = [addition for addition in beverage.additions if isinstance(addition, Milk)]
				if len(milk_additions) > 0:
					response += f"Milk: Ready to say WHEN: {len(milk_additions)}\n"
					#milk volume already poured
					response += f"Milk ml poured already: {sum(addition.volume for addition in milk_additions)}\n"
				else:
					response += "Milk: None\n"
			else:
				self.send_response(404)
				response = "I'm a teapot"
			self.end_headers()
			self.send_header('Content-type', 'text/plain')
			self.send_header('Safe', 'yes')
			self.wfile.write(response.encode())
			return True
		match = re.match(r'^/milk$', self.path)
		if match:
			countOfBeverages = len(self.serviceRegister.milk_poured_list)
			if countOfBeverages == 0:
				self.send_response(418)
				self.send_header('Content-type', 'text/plain')
				self.send_header('Safe', 'yes')
				self.end_headers()
				self.wfile.write("I'm a teapot".encode())
				return
			elif countOfBeverages == 1:
				self.send_header('Content-type', 'text/plain')
				self.send_header('Safe', 'yes')
				self.end_headers()
				self.wfile.write("1 beverage is ready to say WHEN while milk is pouring".encode())
			else:
				self.send_header('Content-type', 'text/plain')
				self.send_header('Safe', 'yes')
				self.end_headers()
				self.wfile.write(f"{countOfBeverages} beverages are ready to say WHEN while milk is pouring".encode())
			return True

		self.send_response(404)
		self.send_header('Content-type', 'text/plain')
		self.send_header('Safe', 'yes')
		self.end_headers()
		self.wfile.write("I'm a teapot".encode())
		return False

	def handle_json(self):
		match = re.match(r'^/milk/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})/json$', self.path)
		if match:
			beverage_id = match.group(1)
			beverage = self.serviceRegister.get_beverage_by_id(beverage_id)
			if beverage:
				self.send_response(200)
				milk_additions = [addition for addition in beverage.additions if isinstance(addition, Milk)]
				response = {
					'beverage_id': beverage.id,
					'type': beverage.__class__.__name__,
					'time_left': beverage.get_time_left(),
					'status': beverage.status,
					'additions': [addition.to_dict() for addition in beverage.additions],
					'temperature': beverage.get_temperature(),
					'milk_additions': len(milk_additions),
					'milk_volume': sum(addition.volume for addition in milk_additions)
				}
			else:
				self.send_response(404)
				response = {'message': "I'm a teapot"}
			self.end_headers()
			self.send_header('Content-type', 'application/json')
			self.send_header('Safe', 'yes')
			self.wfile.write(json.dumps(response).encode())
			return True
		match = re.match(r'^/milk/json$', self.path)
		if match:
			countOfBeverages = len(self.serviceRegister.milk_poured_list)
			self.send_response(200)
			self.send_header('Content-type', 'application/json')
			self.send_header('Safe', 'yes')
			self.end_headers()
			self.wfile.write(json.dumps({'ready_for_milk': countOfBeverages}).encode())
			return True

		self.send_response(404)
		self.send_header('Content-type', 'application/json')
		self.send_header('Safe', 'yes')
		self.end_headers()
		self.wfile.write(json.dumps({'message': "I'm a teapot"}).encode())
		return False

	def handle_xml(self):
		root = Element('milk_beverages')
		for beverage in self.serviceRegister.milk_poured_list:
			beverage_elem = Element('beverage')
			beverage_elem.set('id', beverage.id)
			beverage_elem.set('type', beverage.__class__.__name__)
			beverage_elem.set('time_left', str(beverage.get_time_left()))
			beverage_elem.set('status', beverage.status.name)
			beverage_elem.set('temperature', str(beverage.get_temperature()))
			additions_elem = Element('additions')
			for addition in beverage.additions:
				addition_elem = Element('addition')
				addition_elem.set('name', addition.__class__.__name__)
				addition_elem.append(addition.to_xml())
				additions_elem.append(addition_elem)
			beverage_elem.append(additions_elem)
			root.append(beverage_elem)
		return tostring(root)

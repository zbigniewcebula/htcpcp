import re
import json
from xml.etree.ElementTree import Element, tostring
from serviceRegister import ServiceRegister

class CheckHandler:
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
		elif self.path.endswith('/image'):
			self.handle_image()
		else:
			self.handle_plain()

	def handle_plain(self):
		ready_beverages = len(self.serviceRegister.done_list)
		if ready_beverages == 0:
			self.send_response(418)
			self.send_header('Content-type', 'text/plain')
			self.send_header('Safe', 'yes')
			self.end_headers()
			self.wfile.write("I'm a teapot".encode())
			return False
		match = re.match(r'^/check/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})$', self.path)
		if match:
			beverage_id = match.group(1)
			beverage = self.serviceRegister.get_beverage_by_id(beverage_id)
			if beverage:
				self.send_response(200)
				response = f"Beverage with id {beverage.id}\n"
				timestamp = beverage.get_serving_time()
				response += f"Served at: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
				response += f"Status: {str(beverage.status)}\n"
				response += f"Additions: {', '.join([addition.to_dict() for addition in beverage.additions])}\n"
				response += f"Temperature: {beverage.get_temperature()}\n"
				response += f"Image: /check/{beverage.id}/image\n"
			else:
				self.send_response(404)
				response = "I'm a teapot"
			self.end_headers()
			self.send_header('Content-type', 'text/plain')
			self.send_header('Safe', 'yes')
			self.wfile.write(response.encode())
			return True
		match = re.match(r'^/check$', self.path)
		if match:
			countOfBeverages = len(self.serviceRegister.done_list)
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
				self.wfile.write("1 beverage is ready".encode())
			else:
				self.send_header('Content-type', 'text/plain')
				self.send_header('Safe', 'yes')
				self.end_headers()
				self.wfile.write(f"{countOfBeverages} beverages are ready".encode())
			return True

		self.send_response(404)
		self.send_header('Content-type', 'text/plain')
		self.send_header('Safe', 'yes')
		self.end_headers()
		self.wfile.write("I'm a teapot".encode())
		return False

	def handle_json(self):
		match = re.match(r'^/check/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})/json$', self.path)
		if match:
			beverage_id = match.group(1)
			beverage = self.serviceRegister.get_beverage_by_id(beverage_id)
			if beverage:
				self.send_response(200)
				response = {
					'beverage_id': beverage.id,
					'type': beverage.__class__.__name__,
					'serving_time': beverage.get_serving_time(),
					'status': str(beverage.status),
					'additions': [addition.to_dict() for addition in beverage.additions],
					'temperature': beverage.get_temperature(),
					'image': f"/check/{beverage.id}/image"
				}
			else:
				self.send_response(404)
				response = {'message': "I'm a teapot"}
			self.end_headers()
			self.send_header('Content-type', 'application/json')
			self.send_header('Safe', 'yes')
			self.wfile.write(json.dumps(response).encode())
			return True
		match = re.match(r'^/check/json$', self.path)
		if match:
			countOfBeverages = len(self.serviceRegister.done_list)
			self.send_response(200)
			self.send_header('Content-type', 'application/json')
			self.send_header('Safe', 'yes')
			self.end_headers()
			self.wfile.write(json.dumps({'ready_to_gather': countOfBeverages}).encode())
			return True

		self.send_response(404)
		self.send_header('Content-type', 'application/json')
		self.send_header('Safe', 'yes')
		self.end_headers()
		self.wfile.write(json.dumps({'message': "I'm a teapot"}).encode())
		return False
	
	def handle_image(self):
		match = re.match(r'^/check/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})/image$', self.path)
		if match:
			beverage_id = match.group(1)
			beverage = self.serviceRegister.get_beverage_by_id(beverage_id)
			if beverage:
				self.send_response(200)
				self.send_header('Content-type', 'image/png')
				self.send_header('Safe', 'yes')
				self.end_headers()
				
				if beverage.image_data is None:
					beverage.generate_image()
				self.wfile.write(beverage.image_data)

	def handle_xml(self):
		root = Element('beverages')
		for beverage in self.serviceRegister.done_list:
			beverage_elem = Element('beverage')
			beverage_elem.set('id', beverage.id)
			beverage_elem.set('type', beverage.__class__.__name__)
			beverage_elem.set('serving_time', str(beverage.get_serving_time()))
			beverage_elem.set('status', str(beverage.status))
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

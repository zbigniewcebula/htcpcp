import re
import json
from serviceRegister import ServiceRegister
from xml.etree.ElementTree import Element, tostring

class BrewerHandler:
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
		match = re.match(r'^/brewer/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})$', self.path)
		if match:
			brewer_id = match.group(1)
			brewer = self.serviceRegister.get_brewer_by_id(brewer_id)
			if brewer:
				self.send_response(200)
				response = f"Brewer with id {brewer.id}\n"
				response += f"Time left: {brewer.get_time_left()}\n"
				response += f"Status: {brewer.status}\n"
				response += f"Additions: {', '.join([addition.to_dict() for addition in brewer.additions])}\n"
				response += f"Temperature: {brewer.get_temperature()}\n"
				response += f"Image: /brewer/{brewer.id}/image\n"
			else:
				self.send_response(404)
				response = "I'm a teapot"
			self.end_headers()
			self.send_header('Content-type', 'text/plain')
			self.send_header('Safe', 'yes')
			self.wfile.write(response.encode())
			return True
		match = re.match(r'^/brewer$', self.path)
		if match:
			countOfBrewers = len(self.serviceRegister.brewers)
			if countOfBrewers == 0:
				self.send_response(418)
				self.send_header('Content-type', 'text/plain')
				self.send_header('Safe', 'yes')
				self.end_headers()
				self.wfile.write("I'm a teapot".encode())
				return
			elif countOfBrewers == 1:
				self.send_header('Content-type', 'text/plain')
				self.send_header('Safe', 'yes')
				self.end_headers()
				self.wfile.write("Currently preparing 1 beverage".encode())
			else:
				self.send_header('Content-type', 'text/plain')
				self.send_header('Safe', 'yes')
				self.end_headers()
				self.wfile.write(f"Currently preparing {countOfBrewers} beverages".encode())
			return True

		self.send_response(404)
		self.send_header('Content-type', 'text/plain')
		self.send_header('Safe', 'yes')
		self.end_headers()
		self.wfile.write("I'm a teapot".encode())
		return False

	def handle_json(self):
		match = re.match(r'^/brewer/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})/json$', self.path)
		if match:
			brewer_id = match.group(1)
			brewer = self.serviceRegister.get_brewer_by_id(brewer_id)
			if brewer:
				self.send_response(200)
				response = {
					'brewer_id': brewer.id,
					'type': brewer.__class__.__name__,
					'time_left': brewer.get_time_left(),
					'status': brewer.status,
					'additions': [addition.to_dict() for addition in brewer.additions],
					'temperature': brewer.get_temperature(),
					'image': f"/brewer/{brewer.id}/image"
				}
			else:
				self.send_response(404)
				response = {'message': "I'm a teapot"}
			self.end_headers()
			self.send_header('Content-type', 'application/json')
			self.send_header('Safe', 'yes')
			self.wfile.write(json.dumps(response).encode())
			return True
		match = re.match(r'^/brewer/json$', self.path)
		if match:
			countOfBrewers = len(self.serviceRegister.brewers)
			self.send_response(200)
			self.send_header('Content-type', 'application/json')
			self.send_header('Safe', 'yes')
			self.end_headers()
			self.wfile.write(json.dumps({'count': countOfBrewers}).encode())
			return True

		self.send_response(404)
		self.send_header('Content-type', 'application/json')
		self.send_header('Safe', 'yes')
		self.end_headers()
		self.wfile.write(json.dumps({'message': "I'm a teapot"}).encode())
		return False

	def handle_image(self):
		match = re.match(r'^/brewer/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})/image$', self.path)
		if match:
			brewer_id = match.group(1)
			brewer = self.serviceRegister.get_brewer_by_id(brewer_id)
			if brewer:
				self.send_response(200)
				self.send_header('Content-type', 'image/png')
				self.send_header('Safe', 'yes')
				self.end_headers()
				
				#if there is no image file at local server dir, executre generate_image method
				if brewer.image_data is None:
					brewer.generate_image()
				self.wfile.write(brewer.image_data)

	def handle_xml(self):
		root = Element('brewers')
		for brewer in self.serviceRegister.brewers:
			brewer_elem = Element('brewer')
			brewer_elem.set('id', brewer.id)
			brewer_elem.set('type', brewer.__class__.__name__)
			brewer_elem.set('time_left', str(brewer.get_time_left()))
			brewer_elem.set('status', str(brewer.status))
			brewer_elem.set('temperature', str(brewer.get_temperature()))
			additions_elem = Element('additions')
			for addition in brewer.additions:
				additions_elem.append(addition.to_xml())
			brewer_elem.append(additions_elem)
			root.append(brewer_elem)
		return tostring(root)

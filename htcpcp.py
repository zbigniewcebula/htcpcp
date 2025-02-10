from functools import reduce
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import urllib.parse
from typing import List, Optional
import argparse

from serviceRegister import ServiceRegister
from brewing import TeaBrewer, CoffeeBrewer, Brewer
from milk import Milk
from handlers.BrewerHandler import BrewerHandler
from handlers.CheckHandler import CheckHandler
from handlers.MilkHandler import MilkHandler
from handlers.GatherHandler import GatherHandler
from time_handler import TimeHandler

serviceRegister = ServiceRegister()
timeHandler = TimeHandler()

class HTCPCPHandler(BaseHTTPRequestHandler):
	def do_OPTIONS(self):
		self.send_response(200)
		self.send_header('Allow', 'OPTIONS, GET, POST, PROPFIND, WHEN, BREW')
		self.send_header('Content-type', 'text/plain')
		self.end_headers()
		self.wfile.write(b'Allowed methods: OPTIONS, GET, POST, PROPFIND, WHEN, BREW')

	def do_BREW(self):
		content_types = ['application/coffee-pot-command', 'application/tea-pot-command', 'message/coffeepot', 'message/teapot']
		if args.coffee_only:
			content_types = [content_type for content_type in content_types if 'coffee' not in content_type]
		if args.tea_only:
			content_types = [content_type for content_type in content_types if 'tea' not in content_type]
		
		content_type = self.headers.get('Content-Type')
		if content_type not in content_types:
			self.send_response(415)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
			self.wfile.write(b'Unsupported Media Type, please read: https://datatracker.ietf.org/doc/html/rfc2324\n')
			return

		accept_additions = self.headers.get('Accept-Additions')
		additions = self.parse_accept_additions(accept_additions)

		if not self.validate_additions(additions):
			self.send_response(406)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
			self.wfile.write(b'Invalid additions specified\n')
			return

		header = None
		if "coffee" in content_type:
			brewing = CoffeeBrewer(CoffeeBrewer.BREWING_TIME, additions)
			header = 'message/coffeepot'
		else:
			brewing = TeaBrewer(TeaBrewer.BREWING_TIME, additions)
			header = 'message/teapot'

		threading.Thread(target=brewing.brew, args=(serviceRegister,)).start()
		
		self.send_response(200)
		self.send_header('Content-type', header)
		self.send_header('Safe', 'conditionally-safe')
		self.end_headers()
		if self.path == "/json":
			self.wfile.write(json.dumps({'start': brewing.id}).encode())
		else:
			self.wfile.write(f"start {brewing.id}".encode())

	def parse_accept_additions(self, accept_additions: Optional[str]) -> List[str]:
		if not accept_additions:
			return []
		return [addition.strip() for addition in accept_additions.split(',')]

	def validate_additions(self, additions: List[str]) -> bool:
		for addition in additions:
			addition_type, _ = addition.split(":", 1)
			if not any(addition_type == cls.__name__ for cls in Brewer.VALID_ADDITIONS):
				return False
		return True

	def do_GET(self):
		if self.path.startswith('/brewer'):
			handler = BrewerHandler(serviceRegister, self)
			handler.handle()
			return
		elif self.path.startswith('/check'):
			handler = CheckHandler(serviceRegister, self)
			handler.handle()
			return
		elif self.path.startswith('/milk'):
			handler = MilkHandler(serviceRegister, self)
			handler.handle()
			return
		elif self.path.startswith('/gather'):
			handler = GatherHandler(serviceRegister, self)
			handler.handle()
			return
		
		self.send_response(418)
		self.send_header('Content-type', 'text/plain')
		self.send_header('Safe', 'yes')
		self.end_headers()
		self.wfile.write(b'I\'m a teapot')

	def do_POST(self):
		self.do_BREW()

	def do_PROPFIND(self):
		header = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n'
		if self.path.startswith('/brewer'):
			handler = BrewerHandler(serviceRegister, self)
			self.send_response(207)
			self.send_header('Content-type', 'application/xml')
			self.end_headers()
			self.wfile.write(header.encode() + handler.handle_xml())
			return
		elif self.path.startswith('/fetch'):
			handler = CheckHandler(serviceRegister, self)
			self.send_response(207)
			self.send_header('Content-type', 'application/xml')
			self.end_headers()
			self.wfile.write(header.encode() + handler.handle_xml())
			return
		elif self.path.startswith('/milk'):
			handler = MilkHandler(serviceRegister, self)
			self.send_response(207)
			self.send_header('Content-type', 'application/xml')
			self.end_headers()
			self.wfile.write(header.encode() + handler.handle_xml())
			return
		
		self.send_response(418)
		self.send_header('Content-type', 'application/xml')
		self.end_headers()
		self.wfile.write((header + '<status>I\'m a teapot</status>').encode())

	def do_WHEN(self):
		for beverage in serviceRegister.milk_poured_list:
			milk_additions = [addition for addition in beverage.additions if isinstance(addition, Milk)]
			if len(milk_additions) > 0:
				for addition in milk_additions:
					if serviceRegister.is_milk_poured(beverage):
						addition.stop_pouring()

				self.send_response(200)
				self.send_header('Content-type', 'text/plain')
				self.send_header('Safe', 'conditionally-safe')
				self.end_headers()
				self.wfile.write(b'stop')
				return

		self.send_response(404)
		self.send_header('Content-type', 'text/plain')
		self.send_header('Safe', 'conditionally-safe')
		self.end_headers()
		self.wfile.write(b'No coffee or tea with milk additions in brewing process\n')

	def parse_uri(self, uri: str):
		parsed_uri = urllib.parse.urlparse(uri)
		scheme = parsed_uri.scheme
		host = parsed_uri.hostname
		path = parsed_uri.path
		query = urllib.parse.parse_qs(parsed_uri.query)

		return scheme, host, path, query

def run(server_class=HTTPServer, handler_class=HTCPCPHandler, host='localhost', port=8080):
	server_address = (host, port)
	httpd = server_class(server_address, handler_class)
	print(f'Starting HTCPCP server on {host}:{port}...')
	httpd.serve_forever()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='HTCPCP Server')
	parser.add_argument('--port', '-p', type=int, default=8080, help='Port to run the server on')
	parser.add_argument('--host', '-ip', type=str, default='localhost', help='Host to run the server on')
	parser.add_argument('--coffee-only', '-co', action='store_true', help='Enable coffee only mode')
	parser.add_argument('--tea-only', '-to', action='store_true', help='Enable tea only mode')
	args = parser.parse_args()

	run(host=args.host, port=args.port)
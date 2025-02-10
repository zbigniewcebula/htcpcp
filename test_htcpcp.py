# Let me be honest, I'm too lazy after implementing all of this, copilot wrote those tests for me.
# I'm not even sure if they are correct.

import unittest
from unittest.mock import MagicMock

from requests import patch
from htcpcp import HTCPCPHandler

class TestHTCPCPHandler(unittest.TestCase):
	def setUp(self):
		self.handler = HTCPCPHandler(MagicMock(), MagicMock(), MagicMock())

	def test_do_OPTIONS(self):
		self.handler.send_response = MagicMock()
		self.handler.send_header = MagicMock()
		self.handler.end_headers = MagicMock()
		self.handler.wfile = MagicMock()

		self.handler.do_OPTIONS()

		self.handler.send_response.assert_called_with(200)
		self.handler.send_header.assert_any_call('Allow', 'OPTIONS, GET, POST, PROPFIND, WHEN, BREW')
		self.handler.send_header.assert_any_call('Content-type', 'text/plain')
		self.handler.end_headers.assert_called_once()
		self.handler.wfile.write.assert_called_with(b'Allowed methods: OPTIONS, GET, POST, PROPFIND, WHEN, BREW')

	@patch('htcpcp.CoffeeBrewer')
	@patch('htcpcp.TeaBrewer')
	def test_do_BREW(self, MockTeaBrewer, MockCoffeeBrewer):
		self.handler.send_response = MagicMock()
		self.handler.send_header = MagicMock()
		self.handler.end_headers = MagicMock()
		self.handler.wfile = MagicMock()
		self.handler.headers = {'Content-Type': 'application/coffee-pot-command'}

		MockCoffeeBrewer.BREWING_TIME = 5
		MockCoffeeBrewer.return_value.id = 1

		self.handler.do_BREW()

		self.handler.send_response.assert_called_with(200)
		self.handler.send_header.assert_any_call('Content-type', 'message/coffeepot')
		self.handler.send_header.assert_any_call('Safe', 'conditionally-safe')
		self.handler.end_headers.assert_called_once()
		self.handler.wfile.write.assert_called_with(b'start 1')

	def test_do_GET(self):
		self.handler.send_response = MagicMock()
		self.handler.send_header = MagicMock()
		self.handler.end_headers = MagicMock()
		self.handler.wfile = MagicMock()
		self.handler.path = '/brewer'

		with patch('htcpcp.BrewerHandler.handle') as mock_handle:
			self.handler.do_GET()
			mock_handle.assert_called_once()

		self.handler.path = '/check'
		with patch('htcpcp.CheckHandler.handle') as mock_handle:
			self.handler.do_GET()
			mock_handle.assert_called_once()

		self.handler.path = '/milk'
		with patch('htcpcp.MilkHandler.handle') as mock_handle:
			self.handler.do_GET()
			mock_handle.assert_called_once()

		self.handler.path = '/gather'
		with patch('htcpcp.GatherHandler.handle') as mock_handle:
			self.handler.do_GET()
			mock_handle.assert_called_once()

		self.handler.path = '/unknown'
		self.handler.do_GET()
		self.handler.send_response.assert_called_with(418)
		self.handler.send_header.assert_any_call('Content-type', 'text/plain')
		self.handler.send_header.assert_any_call('Safe', 'yes')
		self.handler.end_headers.assert_called_once()
		self.handler.wfile.write.assert_called_with(b'I\'m a teapot')

	def test_do_POST(self):
		with patch.object(self.handler, 'do_BREW') as mock_do_BREW:
			self.handler.do_POST()
			mock_do_BREW.assert_called_once()

	def test_do_PROPFIND(self):
		self.handler.send_response = MagicMock()
		self.handler.send_header = MagicMock()
		self.handler.end_headers = MagicMock()
		self.handler.wfile = MagicMock()
		self.handler.path = '/brewer'

		with patch('htcpcp.BrewerHandler.handle_xml') as mock_handle_xml:
			mock_handle_xml.return_value = b'<xml></xml>'
			self.handler.do_PROPFIND()
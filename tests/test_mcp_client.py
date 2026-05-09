import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import requests

# Ensure we can import mcp_client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mcp_client

class TestMcpClient(unittest.TestCase):

    @patch('mcp_client.requests.get')
    def test_get_happy_path(self, mock_get):
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "data": "test_data"}
        mock_get.return_value = mock_response

        # Call function
        result = mcp_client._get("/test-endpoint", {"param1": "value1"})

        # Assertions
        mock_get.assert_called_once_with(f"{mcp_client.SERVER}/test-endpoint", params={"param1": "value1"}, timeout=60)
        self.assertEqual(result, {"status": "success", "data": "test_data"})

    @patch('mcp_client.requests.get')
    def test_get_exception(self, mock_get):
        # Setup mock to raise an exception
        mock_get.side_effect = Exception("Connection Refused")

        # Call function
        result = mcp_client._get("/test-endpoint")

        # Assertions
        mock_get.assert_called_once_with(f"{mcp_client.SERVER}/test-endpoint", params=None, timeout=60)
        self.assertEqual(result, {"status": "error", "message": "Connection Refused"})

    @patch('mcp_client.requests.get')
    def test_get_timeout(self, mock_get):
        # Setup mock to raise a Timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Read timed out")

        # Call function
        result = mcp_client._get("/test-endpoint")

        # Assertions
        mock_get.assert_called_once_with(f"{mcp_client.SERVER}/test-endpoint", params=None, timeout=60)
        self.assertEqual(result, {"status": "error", "message": "Read timed out"})

if __name__ == '__main__':
    unittest.main()

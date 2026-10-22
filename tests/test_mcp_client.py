import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mcp_client

class TestMcpClientGet(unittest.TestCase):
    @patch('mcp_client.requests.get')
    def test_get_success_with_params(self, mock_get):
        """Test _get handles a successful response correctly with params."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok", "data": "test"}
        mock_get.return_value = mock_response

        result = mcp_client._get("test", params={"param": "1"})

        mock_get.assert_called_once_with(f"{mcp_client.BASE_URL}/test", params={"param": "1"}, timeout=30)
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, {"status": "ok", "data": "test"})

    @patch('mcp_client.requests.get')
    def test_get_success_without_params(self, mock_get):
        """Test _get handles a successful response correctly without params."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response

        result = mcp_client._get("test")

        mock_get.assert_called_once_with(f"{mcp_client.BASE_URL}/test", params=None, timeout=30)
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, {"status": "ok"})

    @patch('mcp_client.requests.get')
    def test_get_exception(self, mock_get):
        """Test _get catches exceptions and returns the expected error dictionary."""
        mock_get.side_effect = Exception("Test connection error")

        result = mcp_client._get("test")

        mock_get.assert_called_once_with(f"{mcp_client.BASE_URL}/test", params=None, timeout=30)
        self.assertEqual(result, {"status": "error", "message": "Test connection error"})

if __name__ == '__main__':
    unittest.main()

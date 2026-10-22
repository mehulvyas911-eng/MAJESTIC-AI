import unittest
from unittest.mock import patch
import mcp_client

class TestMCPClient(unittest.TestCase):
    @patch('mcp_client._get')
    def test_process_status_success(self, mock_get):
        mock_get.return_value = {"status": "success", "pid": 42}
        result = mcp_client.process_status(42)
        mock_get.assert_called_once_with("/processes/42")
        self.assertEqual(result, {"status": "success", "pid": 42})

    @patch('mcp_client._get')
    def test_process_status_error(self, mock_get):
        mock_get.return_value = {"status": "error", "message": "Not found"}
        result = mcp_client.process_status(999)
        mock_get.assert_called_once_with("/processes/999")
        self.assertEqual(result, {"status": "error", "message": "Not found"})

if __name__ == '__main__':
    unittest.main()

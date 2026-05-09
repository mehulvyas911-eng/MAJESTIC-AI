import unittest
from unittest.mock import patch
import mcp_client

class TestMCPClient(unittest.TestCase):

    @patch('mcp_client._get')
    def test_list_processes_success(self, mock_get):
        """Test successful retrieval of processes."""
        mock_response = {"status": "success", "data": [{"pid": 1234, "status": "running"}]}
        mock_get.return_value = mock_response

        result = mcp_client.list_processes()

        self.assertEqual(result, mock_response)
        mock_get.assert_called_once_with("sys/processes")

    @patch('mcp_client._get')
    def test_list_processes_error(self, mock_get):
        """Test error propagation when listing processes fails."""
        mock_response = {"status": "error", "message": "Connection refused"}
        mock_get.return_value = mock_response

        result = mcp_client.list_processes()

        self.assertEqual(result, mock_response)
        mock_get.assert_called_once_with("sys/processes")

if __name__ == '__main__':
    unittest.main()

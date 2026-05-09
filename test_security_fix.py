import unittest
from unittest.mock import patch, MagicMock
import shlex
import sys

# Mocking Flask and other dependencies to avoid side effects during import
mock_flask_app = MagicMock()
# Ensure decorators return the original function
mock_flask_app.post = lambda x, **kwargs: (lambda f: f)
mock_flask_app.get = lambda x, **kwargs: (lambda f: f)
mock_flask_app.delete = lambda x, **kwargs: (lambda f: f)

flask_mock = MagicMock()
flask_mock.Flask = MagicMock(return_value=mock_flask_app)

sys.modules['flask'] = flask_mock
sys.modules['flask_cors'] = MagicMock()
sys.modules['visual_engine'] = MagicMock()
sys.modules['cache_engine'] = MagicMock()
sys.modules['error_engine'] = MagicMock()
sys.modules['agents'] = MagicMock()
sys.modules['browser_agent'] = MagicMock()

# Import server after mocking
import server

class TestSecurityFix(unittest.TestCase):

    def setUp(self):
        # Reset cache for each test to ensure run_cmd actually calls subprocess
        server.cache = MagicMock()
        server.cache.get.return_value = None

    def test_run_cmd_safe(self):
        with patch('server.subprocess.run') as mock_run:
            # Setup mock
            mock_run.return_value = MagicMock(stdout="hello\n", stderr="", returncode=0)

            # Test command without injection
            server.run_cmd("echo hello")
            # Verify it was called with list and shell=False
            self.assertTrue(mock_run.called)
            args, kwargs = mock_run.call_args
            self.assertEqual(args[0], ['echo', 'hello'])
            self.assertEqual(kwargs['shell'], False)

            # Test command with injection attempt
            server.run_cmd("echo hello; id")
            args, kwargs = mock_run.call_args
            # shlex.split("echo hello; id") -> ['echo', 'hello;', 'id']
            self.assertEqual(args[0], ['echo', 'hello;', 'id'])
            self.assertEqual(kwargs['shell'], False)

    def test_execute_stream_safe(self):
        # Patch subprocess.Popen IN THE server MODULE
        with patch('server.subprocess.Popen') as mock_popen, \
             patch('server.threading.Thread') as mock_thread:
            # Setup mock
            mock_popen.return_value = MagicMock(pid=123)
            server.request = MagicMock()
            server.request.json = {"command": "echo hello; id"}

            # Call execute_stream
            server.execute_stream()

            # Verify Popen was called with split command and shell=False
            self.assertTrue(mock_popen.called)
            args, kwargs = mock_popen.call_args
            self.assertEqual(args[0], ['echo', 'hello;', 'id'])
            self.assertEqual(kwargs['shell'], False)

if __name__ == '__main__':
    unittest.main()

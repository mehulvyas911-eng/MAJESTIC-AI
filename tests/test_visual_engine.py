import unittest
from visual_engine import ansi, fg256, bg256

class TestVisualEngine(unittest.TestCase):
    def test_ansi(self):
        self.assertEqual(ansi(0), "\033[0m")
        self.assertEqual(ansi(1), "\033[1m")
        self.assertEqual(ansi("31"), "\033[31m")

    def test_fg256(self):
        self.assertEqual(fg256(0), "\033[38;5;0m")
        self.assertEqual(fg256(160), "\033[38;5;160m")
        self.assertEqual(fg256(255), "\033[38;5;255m")

    def test_bg256(self):
        self.assertEqual(bg256(0), "\033[48;5;0m")
        self.assertEqual(bg256(52), "\033[48;5;52m")
        self.assertEqual(bg256(255), "\033[48;5;255m")

if __name__ == "__main__":
    unittest.main()

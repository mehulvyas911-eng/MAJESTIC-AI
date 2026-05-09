import unittest
from visual_engine import ansi, fg256, bg256, RESET, BOLD

class TestVisualEngineANSI(unittest.TestCase):

    def test_ansi_formatting(self):
        # Happy path tests
        self.assertEqual(ansi(1), "\033[1m")
        self.assertEqual(ansi("1"), "\033[1m")
        self.assertEqual(ansi(31), "\033[31m")
        self.assertEqual(ansi(0), "\033[0m")

        # Edge cases and unusual inputs (functions just use f-string)
        self.assertEqual(ansi(-1), "\033[-1m")
        self.assertEqual(ansi(999), "\033[999m")
        self.assertEqual(ansi(1.5), "\033[1.5m")
        self.assertEqual(ansi(""), "\033[m")

    def test_fg256_formatting(self):
        # Happy path tests
        self.assertEqual(fg256(160), "\033[38;5;160m")
        self.assertEqual(fg256("124"), "\033[38;5;124m")
        self.assertEqual(fg256(0), "\033[38;5;0m")
        self.assertEqual(fg256(255), "\033[38;5;255m")

        # Edge cases and unusual inputs
        self.assertEqual(fg256(-10), "\033[38;5;-10m")
        self.assertEqual(fg256(999), "\033[38;5;999m")
        self.assertEqual(fg256(3.14), "\033[38;5;3.14m")

    def test_bg256_formatting(self):
        # Happy path tests
        self.assertEqual(bg256(52), "\033[48;5;52m")
        self.assertEqual(bg256("232"), "\033[48;5;232m")
        self.assertEqual(bg256(0), "\033[48;5;0m")
        self.assertEqual(bg256(255), "\033[48;5;255m")

        # Edge cases and unusual inputs
        self.assertEqual(bg256(-5), "\033[48;5;-5m")
        self.assertEqual(bg256(1000), "\033[48;5;1000m")
        self.assertEqual(bg256(2.71), "\033[48;5;2.71m")

    def test_constants(self):
        self.assertEqual(RESET, "\033[0m")
        self.assertEqual(BOLD, "\033[1m")

if __name__ == '__main__':
    unittest.main()

import unittest
from visual_engine import progress_bar, bg256, RESET, BOLD, GRAY

class TestVisualEngine(unittest.TestCase):
    def test_progress_bar_zero(self):
        result = progress_bar(0.0)
        expected_filled = 0
        expected_empty = 40
        bar = bg256(196) + " " * expected_filled + RESET + bg256(236) + " " * expected_empty + RESET
        expected_str = f"[{bar}] {BOLD}  0.0%{RESET} {GRAY}{RESET}"
        self.assertEqual(result, expected_str)

    def test_progress_bar_half(self):
        result = progress_bar(0.5)
        expected_filled = 20
        expected_empty = 20
        bar = bg256(196) + " " * expected_filled + RESET + bg256(236) + " " * expected_empty + RESET
        expected_str = f"[{bar}] {BOLD} 50.0%{RESET} {GRAY}{RESET}"
        self.assertEqual(result, expected_str)

    def test_progress_bar_full(self):
        result = progress_bar(1.0)
        expected_filled = 40
        expected_empty = 0
        bar = bg256(196) + " " * expected_filled + RESET + bg256(236) + " " * expected_empty + RESET
        expected_str = f"[{bar}] {BOLD}100.0%{RESET} {GRAY}{RESET}"
        self.assertEqual(result, expected_str)

    def test_progress_bar_custom_width_and_label(self):
        result = progress_bar(0.5, width=10, label="Downloading")
        expected_filled = 5
        expected_empty = 5
        bar = bg256(196) + " " * expected_filled + RESET + bg256(236) + " " * expected_empty + RESET
        expected_str = f"[{bar}] {BOLD} 50.0%{RESET} {GRAY}Downloading{RESET}"
        self.assertEqual(result, expected_str)

    def test_progress_bar_clamp_values(self):
        # Value below 0.0 should clamp to 0.0
        result_neg = progress_bar(-0.5)
        self.assertEqual(result_neg, progress_bar(0.0))

        # Value above 1.0 should clamp to 1.0
        result_over = progress_bar(1.5)
        self.assertEqual(result_over, progress_bar(1.0))

if __name__ == '__main__':
    unittest.main()

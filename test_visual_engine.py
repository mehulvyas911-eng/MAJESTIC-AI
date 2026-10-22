import unittest
from visual_engine import tabular, BLOOD_RED, RESET

class TestVisualEngineTabular(unittest.TestCase):

    def test_tabular_empty(self):
        # Empty headers or empty rows should return empty string
        self.assertEqual(tabular([], []), "")
        self.assertEqual(tabular(["A"], []), "")
        self.assertEqual(tabular([], [["A"]]), "")

    def test_tabular_happy_path(self):
        headers = ["ID", "Name", "Score"]
        rows = [
            ["1", "Alice", "95"],
            ["2", "Bob", "80"]
        ]
        result = tabular(headers, rows)

        # Verify basic structure
        self.assertIn("ID", result)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("95", result)
        self.assertIn("80", result)
        self.assertTrue(result.startswith(BLOOD_RED + "┌"))
        self.assertTrue(result.endswith("┘" + RESET))

    def test_tabular_mixed_types(self):
        headers = ["ID", "Score"]
        rows = [
            [1, 95.5],
            [2, 80]
        ]
        result = tabular(headers, rows)

        self.assertIn("1", result)
        self.assertIn("95.5", result)
        self.assertIn("2", result)
        self.assertIn("80", result)

    def test_tabular_varying_widths(self):
        headers = ["Short"]
        rows = [
            ["Very Long Row Item"],
            ["X"]
        ]
        result = tabular(headers, rows)

        # The width should accommodate the longest item ("Very Long Row Item" is 18 chars)
        self.assertIn("Very Long Row Item", result)

        # Verify the borders have correct length based on width
        # width = 18. separator is '─'*(width+2) = 20 dashes
        self.assertIn("─"*20, result)

if __name__ == '__main__':
    unittest.main()

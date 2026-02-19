"""Tests for reporter.py."""

import csv
import os
import sys
import tempfile
import unittest

# Ensure the project root is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import reporter


# ---------------------------------------------------------------------------
# reporter.py
# ---------------------------------------------------------------------------

class TestWriteCsv(unittest.TestCase):
    """Tests for reporter.write_csv()."""

    def test_writes_header_and_rows(self):
        """write_csv produces the correct header and data rows in a temp file."""
        rows = [
            ("https://example.com/page", "https://example.com/", "200"),
            ("https://example.com/gone", "https://example.com/", "404"),
        ]

        with tempfile.NamedTemporaryFile(
            mode="r", suffix=".csv", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name

        try:
            reporter.write_csv(rows, tmp_path)
            with open(tmp_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                all_rows = list(reader)

            self.assertEqual(all_rows[0], ["link", "referrer", "http_status_code"])
            self.assertEqual(all_rows[1], list(rows[0]))
            self.assertEqual(all_rows[2], list(rows[1]))
            self.assertEqual(len(all_rows), 3)
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)

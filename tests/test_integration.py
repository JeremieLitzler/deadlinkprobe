"""Live integration tests against the sample website."""

import csv
import os
import subprocess
import sys
import tempfile
import unittest

# Ensure the project root is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CHECKER_PATH = os.path.join(PROJECT_ROOT, "checker.py")

# ---------------------------------------------------------------------------
# Integration test — live network
# ---------------------------------------------------------------------------

SAMPLE_SITE = "https://deadlinkchecker-sample-website.netlify.app"


class TestIntegration(unittest.TestCase):
    """Live integration test against the sample website.

    Requires network access. Uses a temporary output file.
    """

    @classmethod
    def setUpClass(cls):
        """Run the checker once and store results for all integration tests."""
        cls.tmp_output = tempfile.NamedTemporaryFile(
            suffix=".csv", delete=False
        ).name

        result = subprocess.run(
            [
                sys.executable,
                CHECKER_PATH,
                SAMPLE_SITE,
                "--output", cls.tmp_output,
                "--workers", "5",
                "--timeout", "15",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        cls.exit_code = result.returncode
        cls.stdout = result.stdout
        cls.stderr = result.stderr

        cls.csv_rows = []
        if os.path.exists(cls.tmp_output):
            with open(cls.tmp_output, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cls.csv_rows = list(reader)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.tmp_output):
            os.unlink(cls.tmp_output)

    def test_exit_code_is_zero(self):
        """The checker exits with code 0 on a successful run."""
        self.assertEqual(
            self.exit_code, 0,
            msg=f"Non-zero exit.\nSTDOUT: {self.stdout}\nSTDERR: {self.stderr}",
        )

    def test_csv_has_correct_header(self):
        """The output CSV contains the expected header row."""
        with open(self.tmp_output, newline="", encoding="utf-8") as f:
            first_line = f.readline().strip()
        self.assertEqual(first_line, "link,referrer,http_status_code")

    def test_contains_404_status(self):
        """At least one row has http_status_code of 404."""
        statuses = [row["http_status_code"] for row in self.csv_rows]
        self.assertIn("404", statuses, msg=f"No 404 found. Rows: {self.csv_rows}")

    def test_contains_200_status(self):
        """At least one row has http_status_code of 200."""
        statuses = [row["http_status_code"] for row in self.csv_rows]
        self.assertIn("200", statuses, msg=f"No 200 found. Rows: {self.csv_rows}")

    def test_about_page_is_404(self):
        """The /about/ page appears in results with status 404."""
        about_url = f"{SAMPLE_SITE}/about/"
        matching = [
            row for row in self.csv_rows
            if row["link"] == about_url and row["http_status_code"] == "404"
        ]
        self.assertTrue(
            len(matching) >= 1,
            msg=f"Expected {about_url!r} with status 404. Rows: {self.csv_rows}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

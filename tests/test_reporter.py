"""Tests for reporter.py."""

import csv
import os
import sys
import tempfile
import unittest

# Ensure src/ is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

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


class TestWriteMarkdownSummary(unittest.TestCase):
    """Tests for reporter.write_markdown_summary()."""

    TIMESTAMP = "2026-02-24T14-05-32"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _write_and_read(self, results):
        """Call write_markdown_summary into a temp file and return its lines."""
        with tempfile.NamedTemporaryFile(
            mode="r", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            reporter.write_markdown_summary(results, tmp_path, self.TIMESTAMP)
            with open(tmp_path, encoding="utf-8") as f:
                return f.readlines(), tmp_path
        finally:
            # cleanup is handled by each test via finally blocks; return path
            pass

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_file_is_created(self):
        """write_markdown_summary creates the output file at the given path."""
        with tempfile.NamedTemporaryFile(
            mode="r", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            reporter.write_markdown_summary([], tmp_path, self.TIMESTAMP)
            self.assertTrue(os.path.exists(tmp_path))
        finally:
            os.unlink(tmp_path)

    def test_first_non_empty_line_is_heading(self):
        """The first non-empty line is '## <timestamp>'."""
        with tempfile.NamedTemporaryFile(
            mode="r", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            reporter.write_markdown_summary([], tmp_path, self.TIMESTAMP)
            with open(tmp_path, encoding="utf-8") as f:
                lines = f.readlines()
            non_empty = [ln.rstrip("\n") for ln in lines if ln.strip()]
            self.assertEqual(non_empty[0], f"## {self.TIMESTAMP}")
        finally:
            os.unlink(tmp_path)

    def test_table_header_row_present(self):
        """The table header row '| URL | Referrer | HTTP Status |' is present."""
        with tempfile.NamedTemporaryFile(
            mode="r", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            reporter.write_markdown_summary([], tmp_path, self.TIMESTAMP)
            with open(tmp_path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("| URL | Referrer | HTTP Status |", content)
        finally:
            os.unlink(tmp_path)

    def test_non_200_rows_appear_in_table_body(self):
        """Rows with status 404, 500, and ERROR:URLError appear in the table body."""
        results = [
            ("https://example.com/gone", "https://example.com/", "404"),
            ("https://example.com/error", "https://example.com/", "500"),
            ("https://example.com/net", "https://example.com/", "ERROR:URLError"),
        ]
        with tempfile.NamedTemporaryFile(
            mode="r", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            reporter.write_markdown_summary(results, tmp_path, self.TIMESTAMP)
            with open(tmp_path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("https://example.com/gone", content)
            self.assertIn("404", content)
            self.assertIn("https://example.com/error", content)
            self.assertIn("500", content)
            self.assertIn("https://example.com/net", content)
            self.assertIn("ERROR:URLError", content)
        finally:
            os.unlink(tmp_path)

    def test_200_rows_do_not_appear_in_table_body(self):
        """Rows with status 200 are excluded from the table body."""
        results = [
            ("https://example.com/ok", "https://example.com/", "200"),
            ("https://example.com/gone", "https://example.com/", "404"),
        ]
        with tempfile.NamedTemporaryFile(
            mode="r", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            reporter.write_markdown_summary(results, tmp_path, self.TIMESTAMP)
            with open(tmp_path, encoding="utf-8") as f:
                lines = f.readlines()
            # Data rows are lines containing '|' that come after the separator row
            separator_idx = next(
                i for i, ln in enumerate(lines) if ln.startswith("|---|")
            )
            data_lines = [ln for ln in lines[separator_idx + 1:] if ln.strip()]
            # None of the data rows should reference the 200 URL
            for ln in data_lines:
                self.assertNotIn("https://example.com/ok", ln)
        finally:
            os.unlink(tmp_path)

    def test_all_200_results_produce_empty_table_body(self):
        """When every result is 200, the table body contains no data rows."""
        results = [
            ("https://example.com/a", "https://example.com/", "200"),
            ("https://example.com/b", "https://example.com/", "200"),
        ]
        with tempfile.NamedTemporaryFile(
            mode="r", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            reporter.write_markdown_summary(results, tmp_path, self.TIMESTAMP)
            with open(tmp_path, encoding="utf-8") as f:
                lines = f.readlines()
            # Header and separator must be present
            content = "".join(lines)
            self.assertIn("| URL | Referrer | HTTP Status |", content)
            self.assertIn("|---|---|---|", content)
            # No data rows after the separator
            separator_idx = next(
                i for i, ln in enumerate(lines) if ln.startswith("|---|")
            )
            data_lines = [ln for ln in lines[separator_idx + 1:] if ln.strip()]
            self.assertEqual(data_lines, [])
        finally:
            os.unlink(tmp_path)

    def test_empty_results_writes_heading_and_empty_table(self):
        """An empty results list still produces the heading and empty table."""
        with tempfile.NamedTemporaryFile(
            mode="r", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
        try:
            reporter.write_markdown_summary([], tmp_path, self.TIMESTAMP)
            with open(tmp_path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn(f"## {self.TIMESTAMP}", content)
            self.assertIn("| URL | Referrer | HTTP Status |", content)
            self.assertIn("|---|---|---|", content)
            # No data rows
            lines = content.splitlines()
            separator_idx = next(i for i, ln in enumerate(lines) if ln.startswith("|---|"))
            data_lines = [ln for ln in lines[separator_idx + 1:] if ln.strip()]
            self.assertEqual(data_lines, [])
        finally:
            os.unlink(tmp_path)

    def test_oserror_on_unwritable_path_causes_systemexit_1(self):
        """An OSError when opening the output path causes SystemExit with code 1."""
        bad_path = os.path.join(
            tempfile.gettempdir(), "nonexistent_dir_xyz", "README.md"
        )
        with self.assertRaises(SystemExit) as ctx:
            reporter.write_markdown_summary([], bad_path, self.TIMESTAMP)
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

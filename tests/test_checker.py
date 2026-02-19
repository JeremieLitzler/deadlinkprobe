"""Test suite for the dead link checker tool.

Covers: normaliser, parser, fetcher (mocked), reporter, checker CLI, and
one live integration test against the sample website.
"""

import csv
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

# Ensure the project root is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import normaliser
import parser as link_parser
import fetcher
import reporter


# ---------------------------------------------------------------------------
# normaliser.py
# ---------------------------------------------------------------------------

class TestNormalise(unittest.TestCase):
    """Tests for normaliser.normalise()."""

    def test_strips_fragment_from_absolute_url(self):
        """Fragment portion is removed from an already-absolute URL."""
        result = normaliser.normalise(
            "https://example.com/page#section",
            "https://example.com/",
        )
        self.assertEqual(result, "https://example.com/page")

    def test_resolves_root_relative_href(self):
        """Root-relative href is resolved against the base host."""
        result = normaliser.normalise(
            "/about",
            "https://example.com/home",
        )
        self.assertEqual(result, "https://example.com/about")

    def test_resolves_protocol_relative_href(self):
        """Protocol-relative href inherits the scheme from base."""
        result = normaliser.normalise(
            "//cdn.example.com/x.js",
            "https://example.com/",
        )
        self.assertEqual(result, "https://cdn.example.com/x.js")

    def test_resolves_relative_path_href(self):
        """Relative path href is resolved against the full base URL."""
        result = normaliser.normalise(
            "../other",
            "https://example.com/a/b/",
        )
        self.assertEqual(result, "https://example.com/a/other")

    def test_returns_none_for_mailto(self):
        """mailto: scheme returns None."""
        result = normaliser.normalise(
            "mailto:user@example.com",
            "https://example.com/",
        )
        self.assertIsNone(result)

    def test_returns_none_for_javascript(self):
        """javascript: scheme returns None."""
        result = normaliser.normalise(
            "javascript:void(0)",
            "https://example.com/",
        )
        self.assertIsNone(result)

    def test_is_internal_same_host(self):
        """is_internal returns True for same scheme and host."""
        self.assertTrue(
            normaliser.is_internal(
                "https://example.com/page",
                "https://example.com/",
            )
        )

    def test_is_internal_different_host(self):
        """is_internal returns False for a different host."""
        self.assertFalse(
            normaliser.is_internal(
                "https://other.com/page",
                "https://example.com/",
            )
        )


# ---------------------------------------------------------------------------
# parser.py
# ---------------------------------------------------------------------------

class TestExtractLinks(unittest.TestCase):
    """Tests for link_parser.extract_links()."""

    def test_returns_hrefs_from_anchor_tags(self):
        """href values from <a> tags are returned."""
        html = '<html><body><a href="/page1">One</a><a href="/page2">Two</a></body></html>'
        result = link_parser.extract_links(html)
        self.assertIn("/page1", result)
        self.assertIn("/page2", result)
        self.assertEqual(len(result), 2)

    def test_ignores_non_anchor_tags(self):
        """href values on non-<a> tags are not returned."""
        html = '<html><body><img href="/image.png"><link href="/style.css"></body></html>'
        result = link_parser.extract_links(html)
        self.assertEqual(result, [])

    def test_empty_html_returns_empty_list(self):
        """Empty string input yields an empty list."""
        result = link_parser.extract_links("")
        self.assertEqual(result, [])

    def test_skips_empty_href_values(self):
        """An <a> tag with an empty href is not included in the output."""
        html = '<a href="">empty</a><a href="/valid">valid</a>'
        result = link_parser.extract_links(html)
        self.assertNotIn("", result)
        self.assertIn("/valid", result)


# ---------------------------------------------------------------------------
# fetcher.py — unit tests with mocks
# ---------------------------------------------------------------------------

class TestCheckUrl(unittest.TestCase):
    """Unit tests for fetcher.check_url() using unittest.mock."""

    def _make_mock_response(self, status: int):
        """Return a MagicMock that behaves like a urllib response object."""
        response = MagicMock()
        response.status = status
        response.__enter__ = lambda s: s
        response.__exit__ = MagicMock(return_value=False)
        return response

    @patch("fetcher.urllib.request.build_opener")
    def test_returns_200_on_success(self, mock_build_opener):
        """check_url returns '200' when HEAD succeeds with status 200."""
        mock_opener = MagicMock()
        mock_opener.open.return_value = self._make_mock_response(200)
        mock_build_opener.return_value = mock_opener

        result = fetcher.check_url("https://example.com/", 10, "test-agent")
        self.assertEqual(result, "200")

    @patch("fetcher.urllib.request.build_opener")
    def test_returns_301_on_redirect(self, mock_build_opener):
        """check_url returns '301' when the no-redirect handler raises HTTPError."""
        mock_opener = MagicMock()
        mock_opener.open.side_effect = urllib.error.HTTPError(
            "https://example.com/", 301, "Moved Permanently", {}, None
        )
        mock_build_opener.return_value = mock_opener

        result = fetcher.check_url("https://example.com/", 10, "test-agent")
        self.assertEqual(result, "301")

    @patch("fetcher.urllib.request.build_opener")
    def test_returns_error_on_url_error(self, mock_build_opener):
        """check_url returns 'ERROR:URLError' when a URLError is raised."""
        mock_opener = MagicMock()
        mock_opener.open.side_effect = urllib.error.URLError("Network unreachable")
        mock_build_opener.return_value = mock_opener

        result = fetcher.check_url("https://example.com/", 10, "test-agent")
        self.assertEqual(result, "ERROR:URLError")

    @patch("fetcher.urllib.request.build_opener")
    def test_retries_get_on_405(self, mock_build_opener):
        """check_url retries with GET when HEAD returns 405 and returns the GET result."""
        mock_opener = MagicMock()
        mock_get_response = self._make_mock_response(200)

        call_count = [0]

        def side_effect(request, timeout):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call is HEAD — raise 405
                raise urllib.error.HTTPError(
                    request.get_full_url(), 405, "Method Not Allowed", {}, None
                )
            # Second call is GET — succeed
            return mock_get_response

        mock_opener.open.side_effect = side_effect
        mock_build_opener.return_value = mock_opener

        result = fetcher.check_url("https://example.com/", 10, "test-agent")
        self.assertEqual(result, "200")
        self.assertEqual(call_count[0], 2)


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


# ---------------------------------------------------------------------------
# checker.py CLI tests (subprocess)
# ---------------------------------------------------------------------------

CHECKER_PATH = os.path.join(PROJECT_ROOT, "checker.py")


class TestCheckerCLI(unittest.TestCase):
    """Tests for the checker.py CLI entry point."""

    def test_no_args_exits_nonzero(self):
        """Running checker.py with no arguments exits with a non-zero code."""
        result = subprocess.run(
            [sys.executable, CHECKER_PATH],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_help_exits_zero(self):
        """Running checker.py --help exits with code 0."""
        result = subprocess.run(
            [sys.executable, CHECKER_PATH, "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)

    def test_invalid_url_scheme_exits_nonzero(self):
        """Running checker.py with a non-http/https URL exits non-zero."""
        result = subprocess.run(
            [sys.executable, CHECKER_PATH, "invalid-url"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)


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

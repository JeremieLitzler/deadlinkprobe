"""Tests for checker.py CLI entry point."""

import io
import os
import subprocess
import sys
import threading
import unittest
from unittest.mock import MagicMock, patch

# Ensure src/ is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import crawler
import fetcher

CHECKER_PATH = os.path.join(SRC_DIR, "checker.py")


# ---------------------------------------------------------------------------
# checker.py CLI tests (subprocess)
# ---------------------------------------------------------------------------

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
# CR-3: DISCOVERED output tests (crawler.py unit tests)
# ---------------------------------------------------------------------------

class TestCrawlerDiscoveredOutput(unittest.TestCase):
    """Tests that crawler.crawl() prints DISCOVERED lines to stdout."""

    def _make_fetch_html(self, pages: dict):
        """Return a fetch_html side-effect that serves pages from a dict."""
        def fetch_html(url, timeout, user_agent):
            return pages.get(url)
        return fetch_html

    @patch("crawler.fetch_html")
    def test_discovered_printed_for_start_url(self, mock_fetch_html):
        """DISCOVERED is printed for the start URL itself before any fetching."""
        mock_fetch_html.return_value = None  # no HTML, single URL only

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            result = crawler.crawl("https://example.com/", 10, "test-agent")

        output = buf.getvalue()
        self.assertIn("DISCOVERED https://example.com/\n", output)
        self.assertEqual(len(result), 1)

    @patch("crawler.fetch_html")
    def test_discovered_printed_for_each_found_link(self, mock_fetch_html):
        """DISCOVERED is printed for every subsequently found URL."""
        start = "https://example.com/"
        page_html = (
            '<a href="/about">About</a>'
            '<a href="https://external.com/">Ext</a>'
        )

        def side_effect(url, timeout, user_agent):
            if url == start:
                return page_html
            return None

        mock_fetch_html.side_effect = side_effect

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            result = crawler.crawl(start, 10, "test-agent")

        output = buf.getvalue()
        lines = output.strip().splitlines()

        self.assertIn("DISCOVERED https://example.com/", lines)
        self.assertIn("DISCOVERED https://example.com/about", lines)
        self.assertIn("DISCOVERED https://external.com/", lines)
        # Three links discovered total: start, /about, external
        self.assertEqual(len(result), 3)

    @patch("crawler.fetch_html")
    def test_discovered_count_matches_results(self, mock_fetch_html):
        """Number of DISCOVERED lines equals the number of entries in results."""
        start = "https://example.com/"
        page_html = '<a href="/page1">P1</a><a href="/page2">P2</a>'

        def side_effect(url, timeout, user_agent):
            if url == start:
                return page_html
            return None

        mock_fetch_html.side_effect = side_effect

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            result = crawler.crawl(start, 10, "test-agent")

        discovered_lines = [
            ln for ln in buf.getvalue().splitlines()
            if ln.startswith("DISCOVERED ")
        ]
        self.assertEqual(len(discovered_lines), len(result))

    def test_no_discovered_when_start_url_invalid(self):
        """No DISCOVERED line is printed when start_url normalisation returns None."""
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            result = crawler.crawl("mailto:user@example.com", 10, "test-agent")

        output = buf.getvalue()
        self.assertEqual(output, "")
        self.assertEqual(result, [])

    @patch("crawler.fetch_html")
    def test_duplicate_links_not_discovered_twice(self, mock_fetch_html):
        """The same URL linked from multiple pages produces only one DISCOVERED line."""
        start = "https://example.com/"
        # Both /page1 and /page2 link to /shared
        pages = {
            start: '<a href="/page1">P1</a><a href="/page2">P2</a>',
            "https://example.com/page1": '<a href="/shared">S</a>',
            "https://example.com/page2": '<a href="/shared">S</a>',
        }

        mock_fetch_html.side_effect = self._make_fetch_html(pages)

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            result = crawler.crawl(start, 10, "test-agent")

        discovered_lines = [
            ln for ln in buf.getvalue().splitlines()
            if ln.startswith("DISCOVERED ")
        ]
        # start, /page1, /page2, /shared — /shared must appear exactly once
        shared_lines = [ln for ln in discovered_lines if ln.endswith("/shared")]
        self.assertEqual(len(shared_lines), 1)
        # Total unique URLs
        self.assertEqual(len(discovered_lines), len(result))


# ---------------------------------------------------------------------------
# CR-3: CHECKED output tests (checker.py unit tests)
# ---------------------------------------------------------------------------

class TestCheckerCheckedOutput(unittest.TestCase):
    """Tests that checker.py prints CHECKED lines with correct format."""

    def _run_checker_with_mocks(self, link_pairs, statuses, workers=2):
        """
        Run checker.main() with mocked crawler.crawl and fetcher.check_url.

        link_pairs: list of (link, referrer) returned by crawl
        statuses:   dict mapping link -> status string returned by check_url
        Returns the captured stdout as a string.
        """
        import checker
        import tempfile

        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()

        argv = [
            "checker.py",
            "https://example.com/",
            "--output", tmp.name,
            "--workers", str(workers),
        ]

        def mock_check_url(link, timeout, user_agent):
            return statuses.get(link, "200")

        buf = io.StringIO()
        with patch("sys.argv", argv), \
             patch("crawler.crawl", return_value=link_pairs), \
             patch("fetcher.check_url", side_effect=mock_check_url), \
             patch("sys.stdout", buf):
            checker.main()

        os.unlink(tmp.name)
        return buf.getvalue()

    def test_checked_line_printed_for_each_link(self):
        """A CHECKED line is printed for every link in the results."""
        link_pairs = [
            ("https://example.com/", ""),
            ("https://example.com/about", "https://example.com/"),
        ]
        statuses = {
            "https://example.com/": "200",
            "https://example.com/about": "404",
        }

        output = self._run_checker_with_mocks(link_pairs, statuses)
        checked_lines = [ln for ln in output.splitlines() if ln.startswith("CHECKED ")]

        self.assertEqual(len(checked_lines), 2)

    def test_checked_line_format_with_status_code(self):
        """CHECKED lines follow the format 'CHECKED <url> <status>'."""
        link_pairs = [("https://example.com/page", "https://example.com/")]
        statuses = {"https://example.com/page": "301"}

        output = self._run_checker_with_mocks(link_pairs, statuses)
        checked_lines = [ln for ln in output.splitlines() if ln.startswith("CHECKED ")]

        self.assertEqual(len(checked_lines), 1)
        self.assertEqual(checked_lines[0], "CHECKED https://example.com/page 301")

    def test_checked_line_format_with_error_status(self):
        """CHECKED lines include ERROR:<ExceptionClassName> statuses verbatim."""
        link_pairs = [("https://example.com/broken", "https://example.com/")]
        statuses = {"https://example.com/broken": "ERROR:URLError"}

        output = self._run_checker_with_mocks(link_pairs, statuses)
        checked_lines = [ln for ln in output.splitlines() if ln.startswith("CHECKED ")]

        self.assertEqual(len(checked_lines), 1)
        self.assertEqual(checked_lines[0], "CHECKED https://example.com/broken ERROR:URLError")

    def test_no_checked_lines_when_no_links(self):
        """No CHECKED lines are printed when crawl returns an empty list."""
        output = self._run_checker_with_mocks([], {})
        checked_lines = [ln for ln in output.splitlines() if ln.startswith("CHECKED ")]
        self.assertEqual(checked_lines, [])

    def test_summary_line_present_after_checked_lines(self):
        """The final summary line appears after all CHECKED lines."""
        link_pairs = [("https://example.com/", "")]
        statuses = {"https://example.com/": "200"}

        output = self._run_checker_with_mocks(link_pairs, statuses)
        lines = [ln for ln in output.splitlines() if ln.strip()]

        # Last non-empty line must be the summary
        self.assertTrue(lines[-1].startswith("Checked "))
        self.assertIn("Results written to", lines[-1])


# ---------------------------------------------------------------------------
# CR-3: Thread safety test — no interleaved CHECKED output
# ---------------------------------------------------------------------------

class TestCheckerThreadSafety(unittest.TestCase):
    """Tests that CHECKED print calls are not interleaved under concurrency."""

    def test_checked_lines_are_not_interleaved(self):
        """Each CHECKED line is complete and correctly formatted under 10 workers."""
        import checker
        import tempfile

        n_links = 20
        link_pairs = [
            (f"https://example.com/page{i}", "https://example.com/")
            for i in range(n_links)
        ]
        statuses = {link: "200" for link, _ in link_pairs}

        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()

        argv = [
            "checker.py",
            "https://example.com/",
            "--output", tmp.name,
            "--workers", "10",
        ]

        # Introduce a small sleep in check_url to encourage concurrent completion.
        import time

        def slow_check_url(link, timeout, user_agent):
            time.sleep(0.01)
            return statuses.get(link, "200")

        buf = io.StringIO()
        with patch("sys.argv", argv), \
             patch("crawler.crawl", return_value=link_pairs), \
             patch("fetcher.check_url", side_effect=slow_check_url), \
             patch("sys.stdout", buf):
            checker.main()

        os.unlink(tmp.name)

        checked_lines = [
            ln for ln in buf.getvalue().splitlines()
            if ln.startswith("CHECKED ")
        ]

        # Every line must match the exact format: CHECKED <url> <status>
        import re
        pattern = re.compile(r"^CHECKED https://example\.com/page\d+ 200$")
        for line in checked_lines:
            self.assertRegex(line, pattern, msg=f"Malformed CHECKED line: {line!r}")

        # Every link must have been checked exactly once.
        self.assertEqual(len(checked_lines), n_links)

        # No duplicate URLs in the output.
        checked_urls = [ln.split()[1] for ln in checked_lines]
        self.assertEqual(len(checked_urls), len(set(checked_urls)))


if __name__ == "__main__":
    unittest.main(verbosity=2)

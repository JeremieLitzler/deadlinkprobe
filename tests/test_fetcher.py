"""Tests for fetcher.py."""

import os
import sys
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

# Ensure src/ is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import fetcher


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


if __name__ == "__main__":
    unittest.main(verbosity=2)

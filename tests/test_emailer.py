"""Tests for emailer.py."""

import io
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure src/ is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import emailer


# ---------------------------------------------------------------------------
# _build_email_rows
# ---------------------------------------------------------------------------

class TestBuildEmailRows(unittest.TestCase):
    """Tests for emailer._build_email_rows()."""

    def test_returns_empty_string_for_empty_list(self):
        """An empty list returns an empty string."""
        result = emailer._build_email_rows([])
        self.assertEqual(result, "")

    def test_single_row_contains_link_referrer_status(self):
        """A single result row contains link, referrer, and status in <td> elements."""
        rows = emailer._build_email_rows([
            ("https://example.com/gone", "https://example.com/", "404"),
        ])
        self.assertIn("https://example.com/gone", rows)
        self.assertIn("https://example.com/", rows)
        self.assertIn("404", rows)
        self.assertIn("<tr>", rows)
        self.assertIn("</tr>", rows)
        self.assertIn("<td>", rows)

    def test_multiple_rows_joined_by_newline(self):
        """Multiple result rows are joined by newlines."""
        results = [
            ("https://example.com/a", "https://example.com/", "404"),
            ("https://example.com/b", "https://example.com/", "500"),
        ]
        rows = emailer._build_email_rows(results)
        lines = rows.splitlines()
        self.assertEqual(len(lines), 2)

    def test_html_special_chars_are_escaped(self):
        """HTML special characters in link/referrer/status are escaped."""
        results = [
            ('<script>alert("xss")</script>', "https://example.com/", "200"),
        ]
        rows = emailer._build_email_rows(results)
        self.assertNotIn("<script>", rows)
        self.assertIn("&lt;script&gt;", rows)


# ---------------------------------------------------------------------------
# _build_email_html
# ---------------------------------------------------------------------------

class TestBuildEmailHtml(unittest.TestCase):
    """Tests for emailer._build_email_html()."""

    def _build(self, website="example.com", timestamp="2026-02-24T14-05-32",
               total_links=10, non_200_results=None, excluded_summary=None):
        if non_200_results is None:
            non_200_results = []
        if excluded_summary is None:
            excluded_summary = {}
        return emailer._build_email_html(website, timestamp, total_links, non_200_results, excluded_summary)

    def test_contains_website(self):
        """Output contains the website name."""
        html = self._build(website="example.com")
        self.assertIn("example.com", html)

    def test_contains_timestamp(self):
        """Output contains the scan timestamp."""
        html = self._build(timestamp="2026-02-24T14-05-32")
        self.assertIn("2026-02-24T14-05-32", html)

    def test_contains_total_links_count(self):
        """Output contains the total links checked count."""
        html = self._build(total_links=42)
        self.assertIn("42", html)

    def test_contains_non_200_count(self):
        """Output contains the count of non-200 results."""
        results = [
            ("https://example.com/a", "https://example.com/", "404"),
            ("https://example.com/b", "https://example.com/", "500"),
        ]
        html = self._build(non_200_results=results)
        self.assertIn("2", html)

    def test_no_table_when_no_non_200_results(self):
        """No <table> element is present when non_200_results is empty."""
        html = self._build(non_200_results=[])
        self.assertNotIn("<table>", html)

    def test_table_present_when_non_200_results_exist(self):
        """A <table> is present when non_200_results is non-empty."""
        results = [("https://example.com/gone", "https://example.com/", "404")]
        html = self._build(non_200_results=results)
        self.assertIn("<table>", html)
        self.assertIn("</table>", html)

    def test_table_contains_thead_and_tbody(self):
        """Table contains <thead> and <tbody> elements."""
        results = [("https://example.com/gone", "https://example.com/", "404")]
        html = self._build(non_200_results=results)
        self.assertIn("<thead>", html)
        self.assertIn("<tbody>", html)

    def test_website_html_special_chars_escaped(self):
        """HTML special chars in website name are escaped."""
        html = self._build(website='<b>evil</b>')
        self.assertNotIn("<b>evil</b>", html)
        self.assertIn("&lt;b&gt;evil&lt;/b&gt;", html)


# ---------------------------------------------------------------------------
# _send_via_resend
# ---------------------------------------------------------------------------

class TestSendViaResend(unittest.TestCase):
    """Tests for emailer._send_via_resend()."""

    def _call(self, side_effect=None):
        """Call _send_via_resend with resend.Emails.send mocked."""
        with patch("resend.Emails.send") as mock_send:
            if side_effect is not None:
                mock_send.side_effect = side_effect
            emailer._send_via_resend(
                notify_email="user@example.com",
                from_address="noreply@example.com",
                subject="Test subject",
                body="<p>Test body</p>",
            )
            return mock_send

    def test_prints_notification_sent_on_success(self):
        """'Notification sent.' is printed to stdout when SDK call succeeds."""
        buf = io.StringIO()
        with patch("resend.Emails.send"), patch("sys.stdout", buf):
            emailer._send_via_resend(
                "user@example.com", "from@example.com", "subj", "body"
            )
        self.assertIn("Notification sent.", buf.getvalue())

    def test_warns_to_stderr_on_exception(self):
        """Any Exception from the SDK causes a warning to stderr."""
        buf = io.StringIO()
        with patch("resend.Emails.send", side_effect=Exception("API error")), \
             patch("sys.stderr", buf):
            emailer._send_via_resend(
                "user@example.com", "from@example.com", "subj", "body"
            )
        self.assertIn("Warning", buf.getvalue())
        self.assertIn("API error", buf.getvalue())

    def test_sdk_called_with_correct_params(self):
        """resend.Emails.send is called with the expected params dict."""
        captured = {}

        def fake_send(params):
            captured["params"] = params

        with patch("resend.Emails.send", side_effect=fake_send):
            emailer._send_via_resend(
                notify_email="dest@example.com",
                from_address="sender@example.com",
                subject="My subject",
                body="<p>body</p>",
            )

        params = captured.get("params", {})
        self.assertEqual(params.get("from"), "sender@example.com")
        self.assertEqual(params.get("to"), ["dest@example.com"])
        self.assertEqual(params.get("subject"), "My subject")
        self.assertEqual(params.get("html"), "<p>body</p>")

    def test_exception_does_not_propagate(self):
        """An Exception raised by the SDK is caught; _send_via_resend returns normally."""
        with patch("resend.Emails.send", side_effect=RuntimeError("boom")), \
             patch("sys.stderr"):
            # Must not raise
            emailer._send_via_resend(
                "user@example.com", "from@example.com", "subj", "body"
            )


# ---------------------------------------------------------------------------
# send_email_notification
# ---------------------------------------------------------------------------

class TestSendEmailNotification(unittest.TestCase):
    """Tests for emailer.send_email_notification()."""

    _RESULTS = [
        ("https://example.com/", "", "200"),
        ("https://example.com/gone", "https://example.com/", "404"),
    ]

    def _call_with_env(self, api_key, from_address, filtered_results=None, excluded_summary=None, notify_email="user@example.com"):
        """Patch module-level env-var constants and call send_email_notification."""
        if filtered_results is None:
            filtered_results = [r for r in self._RESULTS if r[2] != "200"]
        if excluded_summary is None:
            excluded_summary = {}
        with patch.object(emailer, "_RESEND_API_KEY", api_key), \
             patch.object(emailer, "_RESEND_FROM_ADDRESS", from_address):
            emailer.send_email_notification(
                filtered_results=filtered_results,
                excluded_summary=excluded_summary,
                website="example.com",
                timestamp="2026-02-24T14-05-32",
                total_links=len(self._RESULTS),
                notify_email=notify_email,
            )

    # --- missing env vars ---

    def test_warns_and_returns_when_api_key_missing(self):
        """When _RESEND_API_KEY is None a warning is printed and no SDK call is made."""
        stderr_buf = io.StringIO()
        with patch("resend.Emails.send") as mock_send, \
             patch("sys.stderr", stderr_buf):
            self._call_with_env(api_key=None, from_address="from@example.com")
        mock_send.assert_not_called()
        self.assertIn("RESEND_API_KEY", stderr_buf.getvalue())

    def test_warns_and_returns_when_from_address_missing(self):
        """When _RESEND_FROM_ADDRESS is None a warning is printed and no SDK call is made."""
        stderr_buf = io.StringIO()
        with patch("resend.Emails.send") as mock_send, \
             patch("sys.stderr", stderr_buf):
            self._call_with_env(api_key="key", from_address=None)
        mock_send.assert_not_called()
        self.assertIn("RESEND_FROM_ADDRESS", stderr_buf.getvalue())

    def test_warns_for_api_key_not_from_address_when_both_missing(self):
        """When both env vars are absent the warning mentions RESEND_API_KEY (checked first)."""
        stderr_buf = io.StringIO()
        with patch("resend.Emails.send"), \
             patch("sys.stderr", stderr_buf):
            self._call_with_env(api_key=None, from_address=None)
        # Only the first missing-var warning is emitted (early return)
        self.assertIn("RESEND_API_KEY", stderr_buf.getvalue())
        self.assertNotIn("RESEND_FROM_ADDRESS", stderr_buf.getvalue())

    # --- filters non-200 results ---

    def test_filtered_results_passed_to_build_email_html(self):
        """The filtered_results list is passed verbatim to _build_email_html."""
        captured = {}

        def fake_build_html(website, timestamp, total_links, filtered_results, excluded_summary):
            captured["filtered_results"] = filtered_results
            return "<p>body</p>"

        filtered = [r for r in self._RESULTS if r[2] != "200"]
        with patch.object(emailer, "_RESEND_API_KEY", "key"), \
             patch.object(emailer, "_RESEND_FROM_ADDRESS", "from@example.com"), \
             patch("emailer._build_email_html", side_effect=fake_build_html), \
             patch("emailer._send_via_resend"):
            emailer.send_email_notification(
                filtered_results=filtered,
                excluded_summary={},
                website="example.com",
                timestamp="2026-02-24T14-05-32",
                total_links=len(self._RESULTS),
                notify_email="user@example.com",
            )

        rows = captured["filtered_results"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], "404")

    # --- subject line ---

    def test_subject_contains_website_and_count(self):
        """Email subject contains the website and filtered result count."""
        captured = {}

        def fake_send(notify_email, from_address, subject, body):
            captured["subject"] = subject

        filtered = [r for r in self._RESULTS if r[2] != "200"]
        with patch.object(emailer, "_RESEND_API_KEY", "key"), \
             patch.object(emailer, "_RESEND_FROM_ADDRESS", "from@example.com"), \
             patch("emailer._send_via_resend", side_effect=fake_send):
            emailer.send_email_notification(
                filtered_results=filtered,
                excluded_summary={},
                website="example.com",
                timestamp="2026-02-24T14-05-32",
                total_links=len(self._RESULTS),
                notify_email="user@example.com",
            )

        subject = captured.get("subject", "")
        self.assertIn("example.com", subject)
        self.assertIn("1", subject)
        self.assertIn("result(s) matching filter", subject)

    # --- delegates to _send_via_resend ---

    def test_send_via_resend_called_with_correct_args(self):
        """_send_via_resend receives from_address and notify_email from env-var constants."""
        captured = {}

        def fake_send(notify_email, from_address, subject, body):
            captured["from_address"] = from_address
            captured["notify_email"] = notify_email

        with patch.object(emailer, "_RESEND_API_KEY", "real-key"), \
             patch.object(emailer, "_RESEND_FROM_ADDRESS", "real-from@example.com"), \
             patch("emailer._send_via_resend", side_effect=fake_send):
            emailer.send_email_notification(
                filtered_results=[],
                excluded_summary={},
                website="example.com",
                timestamp="2026-02-24T14-05-32",
                total_links=0,
                notify_email="dest@example.com",
            )

        self.assertEqual(captured["from_address"], "real-from@example.com")
        self.assertEqual(captured["notify_email"], "dest@example.com")

    def test_resend_api_key_set_before_send(self):
        """resend.api_key is set to the value of _RESEND_API_KEY before calling _send_via_resend."""
        import resend as resend_module
        captured = {}

        def fake_send(notify_email, from_address, subject, body):
            captured["api_key_at_send_time"] = resend_module.api_key

        with patch.object(emailer, "_RESEND_API_KEY", "test-api-key"), \
             patch.object(emailer, "_RESEND_FROM_ADDRESS", "from@example.com"), \
             patch("emailer._send_via_resend", side_effect=fake_send):
            emailer.send_email_notification(
                filtered_results=[],
                excluded_summary={},
                website="example.com",
                timestamp="2026-02-24T14-05-32",
                total_links=0,
                notify_email="user@example.com",
            )

        self.assertEqual(captured.get("api_key_at_send_time"), "test-api-key")

    # --- all-200 results ---

    def test_empty_filtered_results_sends_email_with_zero_count(self):
        """When filtered_results is empty, subject shows 0 result(s) matching filter."""
        captured = {}

        def fake_send(notify_email, from_address, subject, body):
            captured["subject"] = subject

        with patch.object(emailer, "_RESEND_API_KEY", "key"), \
             patch.object(emailer, "_RESEND_FROM_ADDRESS", "from@example.com"), \
             patch("emailer._send_via_resend", side_effect=fake_send):
            emailer.send_email_notification(
                filtered_results=[],
                excluded_summary={"200": 2},
                website="example.com",
                timestamp="2026-02-24T14-05-32",
                total_links=2,
                notify_email="user@example.com",
            )

        subject = captured.get("subject", "")
        self.assertIn("0", subject)
        self.assertIn("result(s) matching filter", subject)


if __name__ == "__main__":
    unittest.main(verbosity=2)

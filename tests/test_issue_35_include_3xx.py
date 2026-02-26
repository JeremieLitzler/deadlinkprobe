"""Tests for issue #35 — --include-3xx-status-code flag.

Covers:
1. Default (flag absent): 3xx rows excluded from email, CSV unaffected.
2. Flag present: 3xx rows included in email.
3. Flag absent + only 3xx non-200 results: email table empty, count = 0.
4. ERROR:* strings always appear regardless of flag.
5. Subject-line count matches rendered row count in both flag states.
6. All-200 scan: email table empty regardless of flag.
7. _is_3xx helper boundary conditions.
8. argument_parser: --include-3xx-status-code flag defaults and stores correctly.
"""

import os
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import emailer
import argument_parser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ENV_PATCHES = dict(
    _RESEND_API_KEY="test-api-key",
    _RESEND_FROM_ADDRESS="from@example.com",
)

_MIXED_RESULTS = [
    ("https://example.com/", "", "200"),
    ("https://example.com/redirect", "https://example.com/", "301"),
    ("https://example.com/moved", "https://example.com/", "302"),
    ("https://example.com/gone", "https://example.com/", "404"),
    ("https://example.com/error", "https://example.com/", "500"),
    ("https://example.com/broken", "https://example.com/", "ERROR:ConnectionError"),
]


def _call_send(results, include_3xx=False):
    """Call send_email_notification with mocked env-vars; return captured subject and non_200_results."""
    captured = {}

    def fake_build_html(website, timestamp, total_links, non_200_results):
        captured["non_200_results"] = non_200_results
        return "<p>body</p>"

    def fake_send_via_resend(notify_email, from_address, subject, body):
        captured["subject"] = subject

    with patch.object(emailer, "_RESEND_API_KEY", _ENV_PATCHES["_RESEND_API_KEY"]), \
         patch.object(emailer, "_RESEND_FROM_ADDRESS", _ENV_PATCHES["_RESEND_FROM_ADDRESS"]), \
         patch("emailer._build_email_html", side_effect=fake_build_html), \
         patch("emailer._send_via_resend", side_effect=fake_send_via_resend):
        emailer.send_email_notification(
            results=results,
            website="example.com",
            timestamp="2026-02-26T13-00-00",
            total_links=len(results),
            notify_email="user@example.com",
            include_3xx=include_3xx,
        )
    return captured


# ---------------------------------------------------------------------------
# Test Case 1: Default behaviour (flag absent) — 3xx excluded from email
# ---------------------------------------------------------------------------

class TestDefaultExcludes3xx(unittest.TestCase):
    """With include_3xx=False (default) 3xx rows must not appear in email."""

    def setUp(self):
        self.captured = _call_send(_MIXED_RESULTS, include_3xx=False)
        self.non_200 = self.captured["non_200_results"]

    def test_3xx_rows_absent_from_non_200_results(self):
        """301 and 302 rows must not be in non_200_results when flag is absent."""
        statuses = [row[2] for row in self.non_200]
        self.assertNotIn("301", statuses)
        self.assertNotIn("302", statuses)

    def test_404_and_500_rows_present(self):
        """404 and 500 rows must still appear in non_200_results."""
        statuses = [row[2] for row in self.non_200]
        self.assertIn("404", statuses)
        self.assertIn("500", statuses)

    def test_200_row_absent(self):
        """200 row is never included in non_200_results."""
        statuses = [row[2] for row in self.non_200]
        self.assertNotIn("200", statuses)

    def test_subject_count_excludes_3xx(self):
        """Subject-line count equals the number of non-3xx, non-200 rows (including errors)."""
        # 404, 500, ERROR:ConnectionError = 3 rows
        subject = self.captured["subject"]
        self.assertIn("3 non-200 result(s)", subject)

    def test_subject_count_matches_row_count(self):
        """Subject count matches len(non_200_results)."""
        subject = self.captured["subject"]
        expected = str(len(self.non_200))
        self.assertIn(expected + " non-200 result(s)", subject)


# ---------------------------------------------------------------------------
# Test Case 2: Flag present — 3xx included in email
# ---------------------------------------------------------------------------

class TestFlagPresentIncludes3xx(unittest.TestCase):
    """With include_3xx=True all non-200 rows (including 3xx) must appear."""

    def setUp(self):
        self.captured = _call_send(_MIXED_RESULTS, include_3xx=True)
        self.non_200 = self.captured["non_200_results"]

    def test_3xx_rows_present_in_non_200_results(self):
        """301 and 302 rows must be in non_200_results when flag is present."""
        statuses = [row[2] for row in self.non_200]
        self.assertIn("301", statuses)
        self.assertIn("302", statuses)

    def test_404_500_and_error_rows_present(self):
        """404, 500, and ERROR rows must also be present."""
        statuses = [row[2] for row in self.non_200]
        self.assertIn("404", statuses)
        self.assertIn("500", statuses)
        self.assertIn("ERROR:ConnectionError", statuses)

    def test_200_row_still_absent(self):
        """200 row is never in non_200_results even when flag is present."""
        statuses = [row[2] for row in self.non_200]
        self.assertNotIn("200", statuses)

    def test_subject_count_includes_3xx(self):
        """Subject-line count is 5 (301, 302, 404, 500, ERROR) when flag present."""
        subject = self.captured["subject"]
        self.assertIn("5 non-200 result(s)", subject)

    def test_subject_count_matches_row_count(self):
        """Subject count matches len(non_200_results)."""
        subject = self.captured["subject"]
        expected = str(len(self.non_200))
        self.assertIn(expected + " non-200 result(s)", subject)


# ---------------------------------------------------------------------------
# Test Case 3: Flag absent + only 3xx non-200 results => email table empty
# ---------------------------------------------------------------------------

class TestOnly3xxResultsFlagAbsent(unittest.TestCase):
    """When all non-200 results are 3xx and flag is absent, table is empty, count = 0."""

    _ONLY_3XX = [
        ("https://example.com/", "", "200"),
        ("https://example.com/a", "https://example.com/", "301"),
        ("https://example.com/b", "https://example.com/", "302"),
        ("https://example.com/c", "https://example.com/", "307"),
    ]

    def setUp(self):
        self.captured = _call_send(self._ONLY_3XX, include_3xx=False)
        self.non_200 = self.captured["non_200_results"]

    def test_non_200_results_is_empty(self):
        """non_200_results list is empty when only 3xx statuses exist and flag absent."""
        self.assertEqual(self.non_200, [])

    def test_subject_count_is_zero(self):
        """Subject-line count is 0 when only 3xx results exist and flag absent."""
        subject = self.captured["subject"]
        self.assertIn("0 non-200 result(s)", subject)

    def test_subject_count_matches_row_count(self):
        """Subject count matches len(non_200_results) = 0."""
        subject = self.captured["subject"]
        self.assertIn("0 non-200 result(s)", subject)
        self.assertEqual(len(self.non_200), 0)


# ---------------------------------------------------------------------------
# Test Case 4: ERROR:* strings always appear regardless of flag
# ---------------------------------------------------------------------------

class TestErrorRowsAlwaysIncluded(unittest.TestCase):
    """ERROR:* statuses must appear in email regardless of include_3xx flag."""

    _ERROR_RESULTS = [
        ("https://example.com/", "", "200"),
        ("https://example.com/a", "https://example.com/", "301"),
        ("https://example.com/b", "https://example.com/", "ERROR:ConnectionError"),
        ("https://example.com/c", "https://example.com/", "ERROR:Timeout"),
    ]

    def test_error_rows_present_flag_absent(self):
        """ERROR:* rows present in non_200_results when include_3xx=False."""
        captured = _call_send(self._ERROR_RESULTS, include_3xx=False)
        statuses = [row[2] for row in captured["non_200_results"]]
        self.assertIn("ERROR:ConnectionError", statuses)
        self.assertIn("ERROR:Timeout", statuses)

    def test_error_rows_present_flag_present(self):
        """ERROR:* rows present in non_200_results when include_3xx=True."""
        captured = _call_send(self._ERROR_RESULTS, include_3xx=True)
        statuses = [row[2] for row in captured["non_200_results"]]
        self.assertIn("ERROR:ConnectionError", statuses)
        self.assertIn("ERROR:Timeout", statuses)

    def test_3xx_excluded_but_errors_included_flag_absent(self):
        """301 excluded but ERROR rows remain when flag absent."""
        captured = _call_send(self._ERROR_RESULTS, include_3xx=False)
        statuses = [row[2] for row in captured["non_200_results"]]
        self.assertNotIn("301", statuses)
        self.assertIn("ERROR:ConnectionError", statuses)

    def test_only_error_results_flag_absent(self):
        """When only ERROR rows and 200 exist with flag absent, count equals error count."""
        results = [
            ("https://example.com/", "", "200"),
            ("https://example.com/a", "https://example.com/", "ERROR:ConnectionError"),
        ]
        captured = _call_send(results, include_3xx=False)
        self.assertEqual(len(captured["non_200_results"]), 1)
        self.assertIn("1 non-200 result(s)", captured["subject"])


# ---------------------------------------------------------------------------
# Test Case 5: Subject-line count matches rendered row count (both states)
# ---------------------------------------------------------------------------

class TestSubjectCountMatchesRowCount(unittest.TestCase):
    """Subject-line count must always equal the number of rows that will be rendered."""

    def _subject_count_matches(self, results, include_3xx):
        captured = _call_send(results, include_3xx=include_3xx)
        expected_count = len(captured["non_200_results"])
        expected_str = "{} non-200 result(s)".format(expected_count)
        self.assertIn(expected_str, captured["subject"])
        return expected_count

    def test_flag_absent_mixed_results(self):
        """Count in subject matches non_200_results length with flag absent."""
        count = self._subject_count_matches(_MIXED_RESULTS, include_3xx=False)
        # 404 + 500 + ERROR = 3
        self.assertEqual(count, 3)

    def test_flag_present_mixed_results(self):
        """Count in subject matches non_200_results length with flag present."""
        count = self._subject_count_matches(_MIXED_RESULTS, include_3xx=True)
        # 301 + 302 + 404 + 500 + ERROR = 5
        self.assertEqual(count, 5)

    def test_flag_absent_all_3xx(self):
        """Count is 0 and matches subject when all non-200s are 3xx, flag absent."""
        results = [
            ("https://example.com/", "", "200"),
            ("https://example.com/r", "https://example.com/", "301"),
        ]
        count = self._subject_count_matches(results, include_3xx=False)
        self.assertEqual(count, 0)

    def test_flag_present_one_3xx(self):
        """Count is 1 when one 3xx result, flag present."""
        results = [
            ("https://example.com/", "", "200"),
            ("https://example.com/r", "https://example.com/", "301"),
        ]
        count = self._subject_count_matches(results, include_3xx=True)
        self.assertEqual(count, 1)


# ---------------------------------------------------------------------------
# Test Case 6: All-200 scan — email table empty regardless of flag
# ---------------------------------------------------------------------------

class TestAll200Results(unittest.TestCase):
    """When every link returns 200, non_200_results is empty under both flag states."""

    _ALL_200 = [
        ("https://example.com/", "", "200"),
        ("https://example.com/about", "https://example.com/", "200"),
        ("https://example.com/contact", "https://example.com/", "200"),
    ]

    def test_empty_table_flag_absent(self):
        """non_200_results is empty with all-200 scan and flag absent."""
        captured = _call_send(self._ALL_200, include_3xx=False)
        self.assertEqual(captured["non_200_results"], [])

    def test_empty_table_flag_present(self):
        """non_200_results is empty with all-200 scan and flag present."""
        captured = _call_send(self._ALL_200, include_3xx=True)
        self.assertEqual(captured["non_200_results"], [])

    def test_subject_count_zero_flag_absent(self):
        """Subject shows 0 non-200 result(s) with all-200 scan, flag absent."""
        captured = _call_send(self._ALL_200, include_3xx=False)
        self.assertIn("0 non-200 result(s)", captured["subject"])

    def test_subject_count_zero_flag_present(self):
        """Subject shows 0 non-200 result(s) with all-200 scan, flag present."""
        captured = _call_send(self._ALL_200, include_3xx=True)
        self.assertIn("0 non-200 result(s)", captured["subject"])


# ---------------------------------------------------------------------------
# Test Case 7: _is_3xx helper boundary conditions
# ---------------------------------------------------------------------------

class TestIs3xx(unittest.TestCase):
    """Unit tests for emailer._is_3xx()."""

    def test_300_is_3xx(self):
        self.assertTrue(emailer._is_3xx("300"))

    def test_301_is_3xx(self):
        self.assertTrue(emailer._is_3xx("301"))

    def test_302_is_3xx(self):
        self.assertTrue(emailer._is_3xx("302"))

    def test_307_is_3xx(self):
        self.assertTrue(emailer._is_3xx("307"))

    def test_308_is_3xx(self):
        self.assertTrue(emailer._is_3xx("308"))

    def test_399_is_3xx(self):
        self.assertTrue(emailer._is_3xx("399"))

    def test_200_is_not_3xx(self):
        self.assertFalse(emailer._is_3xx("200"))

    def test_400_is_not_3xx(self):
        self.assertFalse(emailer._is_3xx("400"))

    def test_404_is_not_3xx(self):
        self.assertFalse(emailer._is_3xx("404"))

    def test_500_is_not_3xx(self):
        self.assertFalse(emailer._is_3xx("500"))

    def test_error_string_is_not_3xx(self):
        self.assertFalse(emailer._is_3xx("ERROR:ConnectionError"))

    def test_error_timeout_is_not_3xx(self):
        self.assertFalse(emailer._is_3xx("ERROR:Timeout"))

    def test_short_string_is_not_3xx(self):
        self.assertFalse(emailer._is_3xx("3"))

    def test_long_string_is_not_3xx(self):
        self.assertFalse(emailer._is_3xx("3000"))

    def test_non_digit_3xx_like_is_not_3xx(self):
        """'3xx' is not a valid 3-char all-digit string starting with 3."""
        self.assertFalse(emailer._is_3xx("3xx"))

    def test_empty_string_is_not_3xx(self):
        self.assertFalse(emailer._is_3xx(""))


# ---------------------------------------------------------------------------
# Test Case 8: argument_parser --include-3xx-status-code flag
# ---------------------------------------------------------------------------

class TestArgumentParserInclude3xxFlag(unittest.TestCase):
    """Tests for the --include-3xx-status-code CLI flag in argument_parser."""

    def _parse(self, argv):
        return argument_parser.build_arg_parser().parse_args(argv)

    def test_include_3xx_status_code_default_is_false(self):
        """--include-3xx-status-code defaults to False when omitted."""
        args = self._parse(["https://example.com/"])
        self.assertFalse(args.include_3xx_status_code)

    def test_include_3xx_status_code_flag_sets_true(self):
        """--include-3xx-status-code sets attribute to True when provided."""
        args = self._parse(["https://example.com/", "--include-3xx-status-code"])
        self.assertTrue(args.include_3xx_status_code)

    def test_include_3xx_status_code_is_bool(self):
        """include_3xx_status_code is a boolean value."""
        args = self._parse(["https://example.com/"])
        self.assertIsInstance(args.include_3xx_status_code, bool)

    def test_include_3xx_flag_independent_of_notify_email(self):
        """--include-3xx-status-code can be set with or without --notify-email."""
        args_with = self._parse([
            "https://example.com/",
            "--notify-email", "user@example.com",
            "--include-3xx-status-code",
        ])
        args_without = self._parse([
            "https://example.com/",
            "--include-3xx-status-code",
        ])
        self.assertTrue(args_with.include_3xx_status_code)
        self.assertTrue(args_without.include_3xx_status_code)

    def test_include_3xx_false_when_notify_email_also_absent(self):
        """When neither flag is provided both default to False/None."""
        args = self._parse(["https://example.com/"])
        self.assertFalse(args.include_3xx_status_code)
        self.assertIsNone(args.notify_email)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Tests for --include-3xx-status-code deprecation and --keep-status-codes filter.

Covers:
1. Default filter (404,500): 3xx rows excluded from output.
2. include_3xx_compat=True: 3xx rows included in output.
3. Only 3xx non-200 results with default filter: table empty, count = 0.
4. ERROR:* strings always appear regardless of filter.
5. Subject-line count matches rendered row count.
6. All-200 scan: table empty when filter is 404,500.
7. _is_3xx helper boundary conditions.
8. argument_parser: --include-3xx-status-code flag defaults and stores correctly.
9. checker._build_filter: deprecation warning and backward-compat logic.
"""

import io
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
import status_filter as sf


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


def _call_send(results, include_3xx_compat=False, filter_codes="404,500"):
    """Build a StatusFilter, apply it to results, call send_email_notification."""
    filter_obj = sf.build_filter(filter_codes, include_3xx_compat)
    filtered = [r for r in results if filter_obj.matches(r[2])]
    excluded = filter_obj.excluded_summary(results)

    captured = {}

    def fake_build_html(website, timestamp, total_links, filtered_results, excluded_summary):
        captured["non_200_results"] = filtered_results
        captured["excluded_summary"] = excluded_summary
        return "<p>body</p>"

    def fake_send_via_resend(notify_email, from_address, subject, body):
        captured["subject"] = subject

    with patch.object(emailer, "_RESEND_API_KEY", _ENV_PATCHES["_RESEND_API_KEY"]), \
         patch.object(emailer, "_RESEND_FROM_ADDRESS", _ENV_PATCHES["_RESEND_FROM_ADDRESS"]), \
         patch("emailer._build_email_html", side_effect=fake_build_html), \
         patch("emailer._send_via_resend", side_effect=fake_send_via_resend):
        emailer.send_email_notification(
            filtered_results=filtered,
            excluded_summary=excluded,
            website="example.com",
            timestamp="2026-02-26T13-00-00",
            total_links=len(results),
            notify_email="user@example.com",
        )
    return captured


# ---------------------------------------------------------------------------
# Test Case 1: Default filter (404,500) — 3xx excluded
# ---------------------------------------------------------------------------

class TestDefaultFilterExcludes3xx(unittest.TestCase):
    """With default filter (404,500) 3xx rows must not appear in output."""

    def setUp(self):
        self.captured = _call_send(_MIXED_RESULTS, include_3xx_compat=False)
        self.non_200 = self.captured["non_200_results"]

    def test_3xx_rows_absent_from_filtered_results(self):
        """301 and 302 rows must not be in filtered results with default filter."""
        statuses = [row[2] for row in self.non_200]
        self.assertNotIn("301", statuses)
        self.assertNotIn("302", statuses)

    def test_404_and_500_rows_present(self):
        """404 and 500 rows must appear in filtered results."""
        statuses = [row[2] for row in self.non_200]
        self.assertIn("404", statuses)
        self.assertIn("500", statuses)

    def test_200_row_absent(self):
        """200 row is not in filtered results (not in default filter 404,500)."""
        statuses = [row[2] for row in self.non_200]
        self.assertNotIn("200", statuses)

    def test_subject_count_excludes_3xx(self):
        """Subject count equals the number of matching rows (404, 500, ERROR = 3)."""
        subject = self.captured["subject"]
        self.assertIn("3 result(s) matching filter", subject)

    def test_subject_count_matches_row_count(self):
        """Subject count matches len(non_200_results)."""
        subject = self.captured["subject"]
        expected = str(len(self.non_200))
        self.assertIn(expected + " result(s) matching filter", subject)

    def test_3xx_rows_appear_in_excluded_summary(self):
        """301 and 302 are counted in excluded_summary."""
        excluded = self.captured["excluded_summary"]
        self.assertIn("301", excluded)
        self.assertIn("302", excluded)


# ---------------------------------------------------------------------------
# Test Case 2: include_3xx_compat=True — 3xx included
# ---------------------------------------------------------------------------

class TestInclude3xxCompatIncludes3xx(unittest.TestCase):
    """With include_3xx_compat=True all 3xx codes appear alongside 404/500."""

    def setUp(self):
        self.captured = _call_send(_MIXED_RESULTS, include_3xx_compat=True)
        self.non_200 = self.captured["non_200_results"]

    def test_3xx_rows_present_in_filtered_results(self):
        """301 and 302 rows must be in filtered results when 3xx compat is active."""
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
        """200 row is never in filtered results even with 3xx compat."""
        statuses = [row[2] for row in self.non_200]
        self.assertNotIn("200", statuses)

    def test_subject_count_includes_3xx(self):
        """Subject count is 5 (301, 302, 404, 500, ERROR) with 3xx compat."""
        subject = self.captured["subject"]
        self.assertIn("5 result(s) matching filter", subject)

    def test_subject_count_matches_row_count(self):
        """Subject count matches len(non_200_results)."""
        subject = self.captured["subject"]
        expected = str(len(self.non_200))
        self.assertIn(expected + " result(s) matching filter", subject)


# ---------------------------------------------------------------------------
# Test Case 3: Default filter + only 3xx => table empty, count = 0
# ---------------------------------------------------------------------------

class TestOnly3xxResultsDefaultFilter(unittest.TestCase):
    """When all non-200 results are 3xx and default filter (404,500) is active, table empty."""

    _ONLY_3XX = [
        ("https://example.com/", "", "200"),
        ("https://example.com/a", "https://example.com/", "301"),
        ("https://example.com/b", "https://example.com/", "302"),
        ("https://example.com/c", "https://example.com/", "307"),
    ]

    def setUp(self):
        self.captured = _call_send(self._ONLY_3XX, include_3xx_compat=False)
        self.non_200 = self.captured["non_200_results"]

    def test_filtered_results_is_empty(self):
        """filtered_results is empty when only 3xx statuses exist and default filter used."""
        self.assertEqual(self.non_200, [])

    def test_subject_count_is_zero(self):
        """Subject count is 0."""
        subject = self.captured["subject"]
        self.assertIn("0 result(s) matching filter", subject)

    def test_3xx_appear_in_excluded_summary(self):
        """3xx codes appear in excluded_summary with correct counts."""
        excluded = self.captured["excluded_summary"]
        self.assertIn("301", excluded)
        self.assertIn("302", excluded)
        self.assertIn("307", excluded)


# ---------------------------------------------------------------------------
# Test Case 4: ERROR:* strings always appear regardless of filter
# ---------------------------------------------------------------------------

class TestErrorRowsAlwaysIncluded(unittest.TestCase):
    """ERROR:* statuses must appear in filtered results regardless of filter."""

    _ERROR_RESULTS = [
        ("https://example.com/", "", "200"),
        ("https://example.com/a", "https://example.com/", "301"),
        ("https://example.com/b", "https://example.com/", "ERROR:ConnectionError"),
        ("https://example.com/c", "https://example.com/", "ERROR:Timeout"),
    ]

    def test_error_rows_present_with_default_filter(self):
        """ERROR:* rows present with default filter (404,500)."""
        captured = _call_send(self._ERROR_RESULTS, include_3xx_compat=False)
        statuses = [row[2] for row in captured["non_200_results"]]
        self.assertIn("ERROR:ConnectionError", statuses)
        self.assertIn("ERROR:Timeout", statuses)

    def test_error_rows_present_with_3xx_compat(self):
        """ERROR:* rows present with 3xx compat active."""
        captured = _call_send(self._ERROR_RESULTS, include_3xx_compat=True)
        statuses = [row[2] for row in captured["non_200_results"]]
        self.assertIn("ERROR:ConnectionError", statuses)
        self.assertIn("ERROR:Timeout", statuses)

    def test_3xx_excluded_but_errors_included_default_filter(self):
        """301 excluded but ERROR rows remain with default filter."""
        captured = _call_send(self._ERROR_RESULTS, include_3xx_compat=False)
        statuses = [row[2] for row in captured["non_200_results"]]
        self.assertNotIn("301", statuses)
        self.assertIn("ERROR:ConnectionError", statuses)

    def test_only_error_results_with_default_filter(self):
        """When only ERROR rows and 200 exist, count equals error count."""
        results = [
            ("https://example.com/", "", "200"),
            ("https://example.com/a", "https://example.com/", "ERROR:ConnectionError"),
        ]
        captured = _call_send(results, include_3xx_compat=False)
        self.assertEqual(len(captured["non_200_results"]), 1)
        self.assertIn("1 result(s) matching filter", captured["subject"])


# ---------------------------------------------------------------------------
# Test Case 5: Subject count matches rendered row count
# ---------------------------------------------------------------------------

class TestSubjectCountMatchesRowCount(unittest.TestCase):
    """Subject count must always equal the number of rows rendered."""

    def _subject_count_matches(self, results, include_3xx_compat):
        captured = _call_send(results, include_3xx_compat=include_3xx_compat)
        expected_count = len(captured["non_200_results"])
        expected_str = "{} result(s) matching filter".format(expected_count)
        self.assertIn(expected_str, captured["subject"])
        return expected_count

    def test_default_filter_mixed_results(self):
        """Count in subject matches filtered count: 404 + 500 + ERROR = 3."""
        count = self._subject_count_matches(_MIXED_RESULTS, include_3xx_compat=False)
        self.assertEqual(count, 3)

    def test_3xx_compat_mixed_results(self):
        """Count in subject matches filtered count: 301 + 302 + 404 + 500 + ERROR = 5."""
        count = self._subject_count_matches(_MIXED_RESULTS, include_3xx_compat=True)
        self.assertEqual(count, 5)

    def test_default_filter_all_3xx(self):
        """Count is 0 when all non-200s are 3xx and default filter used."""
        results = [
            ("https://example.com/", "", "200"),
            ("https://example.com/r", "https://example.com/", "301"),
        ]
        count = self._subject_count_matches(results, include_3xx_compat=False)
        self.assertEqual(count, 0)

    def test_3xx_compat_one_3xx(self):
        """Count is 1 when one 3xx result and 3xx compat active."""
        results = [
            ("https://example.com/", "", "200"),
            ("https://example.com/r", "https://example.com/", "301"),
        ]
        count = self._subject_count_matches(results, include_3xx_compat=True)
        self.assertEqual(count, 1)


# ---------------------------------------------------------------------------
# Test Case 6: All-200 scan — table empty with default filter
# ---------------------------------------------------------------------------

class TestAll200Results(unittest.TestCase):
    """When every link returns 200, filtered results is empty under default filter."""

    _ALL_200 = [
        ("https://example.com/", "", "200"),
        ("https://example.com/about", "https://example.com/", "200"),
        ("https://example.com/contact", "https://example.com/", "200"),
    ]

    def test_empty_table_default_filter(self):
        """filtered_results is empty with all-200 scan and default filter."""
        captured = _call_send(self._ALL_200, include_3xx_compat=False)
        self.assertEqual(captured["non_200_results"], [])

    def test_empty_table_3xx_compat(self):
        """filtered_results is empty with all-200 scan and 3xx compat (200 not in filter)."""
        captured = _call_send(self._ALL_200, include_3xx_compat=True)
        self.assertEqual(captured["non_200_results"], [])

    def test_subject_count_zero_default_filter(self):
        """Subject shows 0 result(s) matching filter with all-200 scan."""
        captured = _call_send(self._ALL_200, include_3xx_compat=False)
        self.assertIn("0 result(s) matching filter", captured["subject"])

    def test_all_200_appear_in_excluded_summary(self):
        """200 codes appear in excluded_summary."""
        captured = _call_send(self._ALL_200, include_3xx_compat=False)
        excluded = captured["excluded_summary"]
        self.assertIn("200", excluded)
        self.assertEqual(excluded["200"], 3)


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
        self.assertFalse(emailer._is_3xx("3xx"))

    def test_empty_string_is_not_3xx(self):
        self.assertFalse(emailer._is_3xx(""))


# ---------------------------------------------------------------------------
# Test Case 8: argument_parser --include-3xx-status-code flag
# ---------------------------------------------------------------------------

class TestArgumentParserInclude3xxFlag(unittest.TestCase):
    """Tests for the deprecated --include-3xx-status-code CLI flag."""

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

    def test_deprecated_help_text_contains_deprecated_marker(self):
        """Help text for --include-3xx-status-code mentions DEPRECATED."""
        import io as _io
        buf = _io.StringIO()
        try:
            argument_parser.build_arg_parser().parse_args(["--help"])
        except SystemExit:
            pass
        # Check the help action output via format_help
        help_text = argument_parser.build_arg_parser().format_help()
        self.assertIn("DEPRECATED", help_text)


# ---------------------------------------------------------------------------
# Test Case 9: checker._build_filter deprecation warning and backward compat
# ---------------------------------------------------------------------------

class TestBuildFilterDeprecation(unittest.TestCase):
    """Tests for checker._build_filter() deprecation warning and flag interaction."""

    def _make_args(self, keep_status_codes=None, include_3xx_status_code=False):
        import types
        args = types.SimpleNamespace()
        args.keep_status_codes = keep_status_codes
        args.include_3xx_status_code = include_3xx_status_code
        return args

    def test_deprecated_flag_emits_warning_to_stderr(self):
        """When --include-3xx-status-code is set, a deprecation warning is printed to stderr."""
        import checker
        buf = io.StringIO()
        args = self._make_args(include_3xx_status_code=True)
        with patch("sys.stderr", buf):
            checker._build_filter(args)
        self.assertIn("deprecated", buf.getvalue())
        self.assertIn("--keep-status-codes", buf.getvalue())

    def test_no_warning_when_deprecated_flag_absent(self):
        """No deprecation warning when --include-3xx-status-code is not set."""
        import checker
        buf = io.StringIO()
        args = self._make_args(include_3xx_status_code=False)
        with patch("sys.stderr", buf):
            checker._build_filter(args)
        self.assertEqual(buf.getvalue(), "")

    def test_deprecated_flag_alone_includes_3xx_in_filter(self):
        """When old flag is used without --keep-status-codes, 3xx codes pass through filter."""
        import checker
        args = self._make_args(include_3xx_status_code=True, keep_status_codes=None)
        with patch("sys.stderr"):
            filter_obj = checker._build_filter(args)
        self.assertTrue(filter_obj.matches("301"))
        self.assertTrue(filter_obj.matches("302"))
        self.assertTrue(filter_obj.matches("404"))

    def test_new_flag_wins_over_deprecated_when_both_provided(self):
        """When both flags are provided, --keep-status-codes wins; 3xx are NOT auto-included."""
        import checker
        args = self._make_args(include_3xx_status_code=True, keep_status_codes="404")
        with patch("sys.stderr"):
            filter_obj = checker._build_filter(args)
        self.assertTrue(filter_obj.matches("404"))
        self.assertFalse(filter_obj.matches("301"))

    def test_default_filter_matches_404_and_500(self):
        """Default filter (no flags) matches 404 and 500."""
        import checker
        args = self._make_args()
        filter_obj = checker._build_filter(args)
        self.assertTrue(filter_obj.matches("404"))
        self.assertTrue(filter_obj.matches("500"))

    def test_default_filter_excludes_200_and_3xx(self):
        """Default filter excludes 200 and 3xx codes."""
        import checker
        args = self._make_args()
        filter_obj = checker._build_filter(args)
        self.assertFalse(filter_obj.matches("200"))
        self.assertFalse(filter_obj.matches("301"))

    def test_default_filter_passes_error_rows(self):
        """Default filter always passes ERROR:* rows."""
        import checker
        args = self._make_args()
        filter_obj = checker._build_filter(args)
        self.assertTrue(filter_obj.matches("ERROR:URLError"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

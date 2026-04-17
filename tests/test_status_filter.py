"""Tests for status_filter.py."""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import status_filter as sf


# ---------------------------------------------------------------------------
# _is_3xx
# ---------------------------------------------------------------------------

class TestIs3xx(unittest.TestCase):
    """Unit tests for status_filter._is_3xx()."""

    def test_300_through_399_are_3xx(self):
        for code in ("300", "301", "302", "307", "308", "399"):
            self.assertTrue(sf._is_3xx(code), f"{code} should be 3xx")

    def test_200_is_not_3xx(self):
        self.assertFalse(sf._is_3xx("200"))

    def test_400_is_not_3xx(self):
        self.assertFalse(sf._is_3xx("400"))

    def test_error_string_is_not_3xx(self):
        self.assertFalse(sf._is_3xx("ERROR:Timeout"))

    def test_short_string_is_not_3xx(self):
        self.assertFalse(sf._is_3xx("3"))

    def test_long_string_is_not_3xx(self):
        self.assertFalse(sf._is_3xx("3000"))

    def test_empty_string_is_not_3xx(self):
        self.assertFalse(sf._is_3xx(""))

    def test_non_digit_starting_with_3_is_not_3xx(self):
        self.assertFalse(sf._is_3xx("3xx"))


# ---------------------------------------------------------------------------
# StatusFilter.matches
# ---------------------------------------------------------------------------

class TestStatusFilterMatches(unittest.TestCase):
    """Tests for StatusFilter.matches()."""

    def _filter(self, codes_raw, include_3xx_compat=False):
        return sf.build_filter(codes_raw, include_3xx_compat)

    def test_code_in_filter_matches(self):
        """A status code in the filter set matches."""
        filter_obj = self._filter("404,500")
        self.assertTrue(filter_obj.matches("404"))
        self.assertTrue(filter_obj.matches("500"))

    def test_code_not_in_filter_does_not_match(self):
        """A status code absent from the filter set does not match."""
        filter_obj = self._filter("404,500")
        self.assertFalse(filter_obj.matches("200"))
        self.assertFalse(filter_obj.matches("301"))

    def test_error_rows_always_match(self):
        """ERROR:* rows always match regardless of filter."""
        filter_obj = self._filter("404,500")
        self.assertTrue(filter_obj.matches("ERROR:URLError"))
        self.assertTrue(filter_obj.matches("ERROR:ConnectionError"))
        self.assertTrue(filter_obj.matches("ERROR:Timeout"))

    def test_empty_filter_matches_everything(self):
        """An empty filter (no codes) matches every status."""
        filter_obj = self._filter("")
        self.assertTrue(filter_obj.matches("200"))
        self.assertTrue(filter_obj.matches("301"))
        self.assertTrue(filter_obj.matches("404"))
        self.assertTrue(filter_obj.matches("ERROR:URLError"))

    def test_include_3xx_compat_matches_3xx_codes(self):
        """With include_3xx_compat=True, 3xx codes match even if not in the explicit set."""
        filter_obj = self._filter("404,500", include_3xx_compat=True)
        self.assertTrue(filter_obj.matches("301"))
        self.assertTrue(filter_obj.matches("302"))
        self.assertTrue(filter_obj.matches("307"))

    def test_include_3xx_compat_still_excludes_200(self):
        """With include_3xx_compat=True, 200 still does not match (not 3xx, not in set)."""
        filter_obj = self._filter("404,500", include_3xx_compat=True)
        self.assertFalse(filter_obj.matches("200"))

    def test_whitespace_stripped_from_codes(self):
        """build_filter strips whitespace around comma-separated codes."""
        filter_obj = self._filter("404 , 500 , 403")
        self.assertTrue(filter_obj.matches("404"))
        self.assertTrue(filter_obj.matches("403"))

    def test_single_code_filter(self):
        """A filter with a single code only matches that code (and ERROR:*)."""
        filter_obj = self._filter("404")
        self.assertTrue(filter_obj.matches("404"))
        self.assertFalse(filter_obj.matches("500"))
        self.assertTrue(filter_obj.matches("ERROR:URLError"))


# ---------------------------------------------------------------------------
# StatusFilter.excluded_summary
# ---------------------------------------------------------------------------

class TestStatusFilterExcludedSummary(unittest.TestCase):
    """Tests for StatusFilter.excluded_summary()."""

    _RESULTS = [
        ("https://example.com/", "", "200"),
        ("https://example.com/r", "https://example.com/", "301"),
        ("https://example.com/g", "https://example.com/", "404"),
        ("https://example.com/e", "https://example.com/", "500"),
        ("https://example.com/b", "https://example.com/", "ERROR:URLError"),
    ]

    def test_excluded_codes_counted_correctly(self):
        """Codes not matching the filter appear in excluded_summary with correct counts."""
        filter_obj = sf.build_filter("404,500")
        excluded = filter_obj.excluded_summary(self._RESULTS)
        self.assertIn("200", excluded)
        self.assertEqual(excluded["200"], 1)
        self.assertIn("301", excluded)
        self.assertEqual(excluded["301"], 1)

    def test_matching_codes_not_in_excluded_summary(self):
        """Codes matching the filter do not appear in excluded_summary."""
        filter_obj = sf.build_filter("404,500")
        excluded = filter_obj.excluded_summary(self._RESULTS)
        self.assertNotIn("404", excluded)
        self.assertNotIn("500", excluded)
        self.assertNotIn("ERROR:URLError", excluded)

    def test_empty_results_returns_empty_summary(self):
        """An empty results list produces an empty excluded_summary."""
        filter_obj = sf.build_filter("404,500")
        self.assertEqual(filter_obj.excluded_summary([]), {})

    def test_all_matching_returns_empty_summary(self):
        """When all results match the filter, excluded_summary is empty."""
        filter_obj = sf.build_filter("404,500")
        results = [
            ("https://example.com/a", "", "404"),
            ("https://example.com/b", "", "500"),
            ("https://example.com/c", "", "ERROR:URLError"),
        ]
        self.assertEqual(filter_obj.excluded_summary(results), {})

    def test_multiple_occurrences_summed(self):
        """Multiple rows with the same excluded code sum to a single entry."""
        filter_obj = sf.build_filter("404")
        results = [
            ("https://example.com/a", "", "200"),
            ("https://example.com/b", "", "200"),
            ("https://example.com/c", "", "200"),
        ]
        excluded = filter_obj.excluded_summary(results)
        self.assertEqual(excluded.get("200"), 3)

    def test_empty_filter_produces_empty_summary(self):
        """With an empty filter (no filtering), excluded_summary is always empty."""
        filter_obj = sf.build_filter("")
        excluded = filter_obj.excluded_summary(self._RESULTS)
        self.assertEqual(excluded, {})


# ---------------------------------------------------------------------------
# build_filter factory
# ---------------------------------------------------------------------------

class TestBuildFilter(unittest.TestCase):
    """Tests for status_filter.build_filter()."""

    def test_default_codes_parsed_correctly(self):
        """'404,500' builds a filter matching 404 and 500."""
        filter_obj = sf.build_filter("404,500")
        self.assertTrue(filter_obj.matches("404"))
        self.assertTrue(filter_obj.matches("500"))
        self.assertFalse(filter_obj.matches("200"))

    def test_empty_string_builds_no_filter(self):
        """An empty string builds a filter that matches everything."""
        filter_obj = sf.build_filter("")
        self.assertTrue(filter_obj.matches("200"))
        self.assertTrue(filter_obj.matches("404"))

    def test_include_3xx_compat_false_by_default(self):
        """include_3xx_compat defaults to False."""
        filter_obj = sf.build_filter("404,500")
        self.assertFalse(filter_obj.matches("301"))

    def test_include_3xx_compat_true_includes_3xx(self):
        """include_3xx_compat=True makes 3xx codes match."""
        filter_obj = sf.build_filter("404,500", include_3xx_compat=True)
        self.assertTrue(filter_obj.matches("301"))

    def test_custom_codes(self):
        """Custom code list is respected."""
        filter_obj = sf.build_filter("403,404,500")
        self.assertTrue(filter_obj.matches("403"))
        self.assertFalse(filter_obj.matches("200"))

    def test_codes_with_spaces_stripped(self):
        """Spaces around commas are stripped."""
        filter_obj = sf.build_filter(" 404 , 500 ")
        self.assertTrue(filter_obj.matches("404"))
        self.assertTrue(filter_obj.matches("500"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

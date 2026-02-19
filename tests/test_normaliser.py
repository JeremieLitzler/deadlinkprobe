"""Tests for normaliser.py."""

import os
import sys
import unittest

# Ensure the project root is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import normaliser


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


if __name__ == "__main__":
    unittest.main(verbosity=2)

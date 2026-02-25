"""Tests for web_parser.py."""

import os
import sys
import unittest

# Ensure src/ is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import web_parser as link_parser


# ---------------------------------------------------------------------------
# web_parser.py
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


if __name__ == "__main__":
    unittest.main(verbosity=2)

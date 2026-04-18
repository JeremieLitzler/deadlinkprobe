"""Tests for argument_parser.py."""

import os
import sys
import unittest

# Ensure src/ is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import argument_parser


class TestBuildArgParser(unittest.TestCase):
    """Tests for argument_parser.build_arg_parser()."""

    def _parse(self, argv):
        """Parse argv using the real parser and return the Namespace."""
        return argument_parser.build_arg_parser().parse_args(argv)

    # --- positional ---

    def test_start_url_is_required(self):
        """Omitting start_url raises SystemExit (argparse exits on missing required arg)."""
        with self.assertRaises(SystemExit):
            argument_parser.build_arg_parser().parse_args([])

    def test_start_url_stored(self):
        """start_url positional argument is stored on the namespace."""
        args = self._parse(["https://example.com/"])
        self.assertEqual(args.start_url, "https://example.com/")

    # --- --output / -o ---

    def test_output_default_is_none(self):
        """--output defaults to None when omitted."""
        args = self._parse(["https://example.com/"])
        self.assertIsNone(args.output)

    def test_output_long_flag(self):
        """--output stores the provided path."""
        args = self._parse(["https://example.com/", "--output", "out.csv"])
        self.assertEqual(args.output, "out.csv")

    def test_output_short_flag(self):
        """-o is an alias for --output."""
        args = self._parse(["https://example.com/", "-o", "results.csv"])
        self.assertEqual(args.output, "results.csv")

    # --- --workers / -w ---

    def test_workers_default(self):
        """--workers defaults to 10."""
        args = self._parse(["https://example.com/"])
        self.assertEqual(args.workers, 10)

    def test_workers_long_flag(self):
        """--workers stores the given integer."""
        args = self._parse(["https://example.com/", "--workers", "5"])
        self.assertEqual(args.workers, 5)

    def test_workers_short_flag(self):
        """-w is an alias for --workers."""
        args = self._parse(["https://example.com/", "-w", "3"])
        self.assertEqual(args.workers, 3)

    def test_workers_is_int(self):
        """--workers value is stored as an int, not a string."""
        args = self._parse(["https://example.com/", "--workers", "7"])
        self.assertIsInstance(args.workers, int)

    # --- --timeout / -t ---

    def test_timeout_default(self):
        """--timeout defaults to 10."""
        args = self._parse(["https://example.com/"])
        self.assertEqual(args.timeout, 10)

    def test_timeout_long_flag(self):
        """--timeout stores the given integer."""
        args = self._parse(["https://example.com/", "--timeout", "30"])
        self.assertEqual(args.timeout, 30)

    def test_timeout_short_flag(self):
        """-t is an alias for --timeout."""
        args = self._parse(["https://example.com/", "-t", "15"])
        self.assertEqual(args.timeout, 15)

    def test_timeout_is_int(self):
        """--timeout value is stored as an int."""
        args = self._parse(["https://example.com/", "--timeout", "20"])
        self.assertIsInstance(args.timeout, int)

    # --- --user-agent ---

    def test_user_agent_default(self):
        """--user-agent defaults to 'linkprobe/1.0'."""
        args = self._parse(["https://example.com/"])
        self.assertEqual(args.user_agent, "linkprobe/1.0")

    def test_user_agent_custom(self):
        """--user-agent stores the provided string."""
        args = self._parse(["https://example.com/", "--user-agent", "mybot/2.0"])
        self.assertEqual(args.user_agent, "mybot/2.0")

    # --- --notify-email ---

    def test_notify_email_default_is_none(self):
        """--notify-email defaults to None when omitted."""
        args = self._parse(["https://example.com/"])
        self.assertIsNone(args.notify_email)

    def test_notify_email_stores_address(self):
        """--notify-email stores the provided email address."""
        args = self._parse(["https://example.com/", "--notify-email", "user@example.com"])
        self.assertEqual(args.notify_email, "user@example.com")

    # --- --keep-status-codes ---

    def test_keep_status_codes_default_is_none(self):
        """--keep-status-codes defaults to None when omitted."""
        args = self._parse(["https://example.com/"])
        self.assertIsNone(args.keep_status_codes)

    def test_keep_status_codes_stores_value(self):
        """--keep-status-codes stores the provided string."""
        args = self._parse(["https://example.com/", "--keep-status-codes", "404,500,403"])
        self.assertEqual(args.keep_status_codes, "404,500,403")

    def test_keep_status_codes_accepts_single_code(self):
        """--keep-status-codes accepts a single status code."""
        args = self._parse(["https://example.com/", "--keep-status-codes", "404"])
        self.assertEqual(args.keep_status_codes, "404")

    def test_keep_status_codes_accepts_empty_string(self):
        """--keep-status-codes accepts an empty string (means no filter)."""
        args = self._parse(["https://example.com/", "--keep-status-codes", ""])
        self.assertEqual(args.keep_status_codes, "")

    def test_keep_status_codes_is_string(self):
        """--keep-status-codes stores value as a string."""
        args = self._parse(["https://example.com/", "--keep-status-codes", "404,500"])
        self.assertIsInstance(args.keep_status_codes, str)


if __name__ == "__main__":
    unittest.main(verbosity=2)

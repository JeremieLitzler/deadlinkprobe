"""Tests for checker.py CLI entry point."""

import os
import subprocess
import sys
import unittest

# Ensure the project root is on sys.path so the modules can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CHECKER_PATH = os.path.join(PROJECT_ROOT, "checker.py")


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


if __name__ == "__main__":
    unittest.main(verbosity=2)

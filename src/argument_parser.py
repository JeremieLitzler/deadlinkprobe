"""CLI argument parser for the dead link checker."""

import argparse


def build_arg_parser() -> argparse.ArgumentParser:
    """Return the configured ArgumentParser for the dead link checker CLI."""
    parser = argparse.ArgumentParser(
        description="Check a website for dead links.",
    )
    parser.add_argument("start_url", help="The URL to begin crawling from.")
    parser.add_argument(
        "--output", "-o",
        default=None,
        help=(
            "Path to the output CSV file. When omitted, results are written to "
            "scans/[WEBSITE]/[TIMESTAMP]/results.csv and a README.md summary is also produced."
        ),
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=10,
        help="Number of threads in the ThreadPoolExecutor. (default: 10)",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=10,
        help="Per-request timeout in seconds. (default: 10)",
    )
    parser.add_argument(
        "--user-agent",
        default="deadlinkchecker/1.0",
        help="User-Agent header sent with every request. (default: deadlinkchecker/1.0)",
    )
    parser.add_argument(
        "--notify-email",
        default=None,
        metavar="ADDRESS",
        help=(
            "Recipient email address for a post-scan notification via the Resend API. "
            "Requires RESEND_API_KEY and RESEND_FROM_ADDRESS environment variables."
        ),
    )
    return parser

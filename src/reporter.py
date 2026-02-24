"""CSV and Markdown output writing."""

import csv
import sys


def write_csv(results: list[tuple[str, str, str]], output_path: str) -> None:
    """Write results to a CSV file at `output_path`.

    Parameters
    ----------
    results:
        List of (link, referrer, http_status_code) tuples, already sorted.
    output_path:
        File path for the output CSV.

    Prints an error to stderr and exits with code 1 if the file cannot be opened.
    """
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["link", "referrer", "http_status_code"])
            writer.writerows(results)
    except OSError as e:
        print(f"Error: cannot write to '{output_path}': {e}", file=sys.stderr)
        sys.exit(1)


def write_markdown_summary(
    results: list[tuple[str, str, str]],
    output_path: str,
    timestamp: str,
) -> None:
    """Write a Markdown summary of non-200 results to `output_path`.

    Parameters
    ----------
    results:
        List of (link, referrer, http_status_code) tuples, already sorted.
    output_path:
        Full file path where the README.md should be written.
    timestamp:
        The scan timestamp string (e.g. "2026-02-24T14-05-32").

    Prints an error to stderr and exits with code 1 if the file cannot be opened.
    """
    non_200 = [row for row in results if row[2] != "200"]
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"## {timestamp}\n\n")
            f.write("| URL | Referrer | HTTP Status |\n")
            f.write("|---|---|---|\n")
            for link, referrer, status in non_200:
                f.write(f"| {link} | {referrer} | {status} |\n")
    except OSError as e:
        print(f"Error: cannot write to '{output_path}': {e}", file=sys.stderr)
        sys.exit(1)

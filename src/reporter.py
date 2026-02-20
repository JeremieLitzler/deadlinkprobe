"""CSV output writing."""

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

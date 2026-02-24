"""Dead link checker — entry point and CLI argument parsing."""

import argparse
import concurrent.futures
import datetime
import os
import sys
import threading
import urllib.parse

import crawler
import fetcher
import reporter


def main() -> None:
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

    args = parser.parse_args()

    scan_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

    parsed = urllib.parse.urlparse(args.start_url)
    if parsed.scheme not in ("http", "https"):
        print(
            f"Error: start_url must use http or https scheme, got: '{args.start_url}'",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.workers < 1:
        print("Error: --workers must be >= 1.", file=sys.stderr)
        sys.exit(1)

    if args.timeout < 1:
        print("Error: --timeout must be >= 1.", file=sys.stderr)
        sys.exit(1)

    link_pairs = crawler.crawl(args.start_url, args.timeout, args.user_agent)

    results: list[tuple[str, str, str]] = []
    print_lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_pair = {
            executor.submit(fetcher.check_url, link, args.timeout, args.user_agent): (link, referrer)
            for link, referrer in link_pairs
        }
        for future in concurrent.futures.as_completed(future_to_pair):
            link, referrer = future_to_pair[future]
            status = future.result()
            results.append((link, referrer, status))
            with print_lock:
                print(f"CHECKED {link} {status}")

    results.sort(key=lambda row: (row[1], row[0]))

    if args.output is not None:
        # Legacy mode: flat CSV only, no README.md
        csv_path = args.output
        md_path = None
    else:
        # Scan-folder mode
        website = parsed.netloc.replace(":", "_")
        scan_dir = os.path.join("scans", website, scan_timestamp)
        os.makedirs(scan_dir, exist_ok=True)
        csv_path = os.path.join(scan_dir, "results.csv")
        md_path = os.path.join(scan_dir, "README.md")

    reporter.write_csv(results, csv_path)

    if md_path is not None:
        reporter.write_markdown_summary(results, md_path, scan_timestamp)

    print(f"Checked {len(results)} links. Results written to {csv_path}.")


if __name__ == "__main__":
    main()

"""Dead link checker — entry point and CLI argument parsing."""

import argparse
import concurrent.futures
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
        default="results.csv",
        help="Path to the output CSV file. (default: results.csv)",
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

    reporter.write_csv(results, args.output)

    print(f"Checked {len(results)} links. Results written to {args.output}.")


if __name__ == "__main__":
    main()

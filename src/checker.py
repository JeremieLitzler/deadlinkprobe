"""Dead link checker — entry point and CLI argument parsing."""

import concurrent.futures
import datetime
import os
import sys
import threading
import urllib.parse

import argument_parser
import crawler
import emailer
import fetcher
import reporter


def _maybe_send_notification(
    args,
    results: list[tuple[str, str, str]],
    website: str,
    scan_timestamp: str,
) -> None:
    if args.notify_email is None:
        return
    emailer.send_email_notification(
        results,
        website,
        scan_timestamp,
        len(results),
        args.notify_email,
        args.include_3xx_status_code,
    )


def main() -> None:
    args = argument_parser.build_arg_parser().parse_args()

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

    _maybe_send_notification(args, results, parsed.netloc, scan_timestamp)


if __name__ == "__main__":
    main()

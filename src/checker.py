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
import status_filter as status_filter_module


def _build_filter(args) -> status_filter_module.StatusFilter:
    include_3xx_compat = False
    if args.include_3xx_status_code:
        print(
            "Warning: --include-3xx-status-code is deprecated; use --keep-status-codes instead.",
            file=sys.stderr,
        )
        if args.keep_status_codes is None:
            include_3xx_compat = True
    codes_raw = args.keep_status_codes if args.keep_status_codes is not None else "404,500"
    return status_filter_module.build_filter(codes_raw, include_3xx_compat)


def _maybe_send_notification(
    args,
    filtered_results: list,
    excluded_summary: dict,
    total_links: int,
    website: str,
    scan_timestamp: str,
) -> None:
    if args.notify_email is None:
        return
    emailer.send_email_notification(
        filtered_results,
        excluded_summary,
        website,
        scan_timestamp,
        total_links,
        args.notify_email,
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

    result_filter = _build_filter(args)
    filtered = [r for r in results if result_filter.matches(r[2])]
    excluded = result_filter.excluded_summary(results)

    if args.output is not None:
        csv_path = args.output
        md_path = None
    else:
        website = parsed.netloc.replace(":", "_")
        scan_dir = os.path.join("scans", website, scan_timestamp)
        os.makedirs(scan_dir, exist_ok=True)
        csv_path = os.path.join(scan_dir, "results.csv")
        md_path = os.path.join(scan_dir, "README.md")

    reporter.write_csv(filtered, csv_path)

    if md_path is not None:
        reporter.write_markdown_summary(filtered, md_path, scan_timestamp)

    print(f"Checked {len(results)} links. Results written to {csv_path}.")

    _maybe_send_notification(args, filtered, excluded, len(results), parsed.netloc, scan_timestamp)


if __name__ == "__main__":
    main()

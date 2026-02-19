# Code Ready

## Files Created

- `normaliser.py` — URL normalisation: resolves relative URLs against a base, strips fragments, filters non-http/https schemes, and determines internal vs external links.
- `parser.py` — HTML link extraction: subclasses `html.parser.HTMLParser` to collect all non-empty `href` values from `<a>` tags; returns empty list on parse failure.
- `fetcher.py` — HTTP request layer: `check_url` issues HEAD (GET fallback on 405) without following redirects, recording 3xx as-is and network errors as `ERROR:<ExceptionClassName>`; `fetch_html` follows redirects and returns decoded HTML body or None for non-HTML content.
- `crawler.py` — BFS crawl engine: traverses internal pages breadth-first using a queue and visited set, collecting `(link, referrer)` pairs for every discovered URL (internal and external) without recursing into external links.
- `reporter.py` — CSV writer: writes `link,referrer,http_status_code` rows with header to the specified output path; exits with code 1 on file write failure.
- `checker.py` — CLI entry point: parses arguments, validates inputs, orchestrates the crawl and parallel status-check phase via `ThreadPoolExecutor`, sorts results by `(referrer, link)`, and writes the CSV output.

status: ready

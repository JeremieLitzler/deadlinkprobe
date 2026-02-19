## 2026-02-19

Build the dead link checker CLI tool in **Python** as described in CLAUDE.md and README.md.

Given a starting URL:

1. Crawl all internal links recursively until all are discovered.
2. Collect external links but do not recurse into them.
3. Check all discovered links for their HTTP status code.
4. Output results as CSV: `link, referrer, http_status_code`.
5. Use parallel requests for performance.

Language: Python 3. Prefer stdlib only (urllib, concurrent.futures, html.parser). Third-party libraries only if strictly necessary.

## 2026-02-19 — Change request

- Split test file into several file, one per code file and one for the integration tests.

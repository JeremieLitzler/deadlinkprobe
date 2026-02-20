# Dead Link Checker — Technical Specification

## Goal and Scope

Build a CLI tool in Python 3 that, given a starting URL:

1. Crawls all internal links recursively using BFS (Breadth-First Search, https://en.wikipedia.org/wiki/Breadth-first_search) until all reachable internal pages are discovered.
2. Collects external links encountered during the crawl but does not recurse into them.
3. Issues HTTP status checks against every discovered link (both internal and external).
4. Writes results to a CSV file: `link,referrer,http_status_code`, sorted by referrer then link, with header always present.
5. Uses parallel HTTP requests for performance.

Scope is limited to HTTP and HTTPS schemes. No authentication, no JavaScript rendering, no cookie handling, no robots.txt compliance (unless explicitly requested later).

## Language and Dependencies

- **Python 3.9+**
- **Standard library only**: `urllib.request`, `urllib.parse`, `urllib.error`, `concurrent.futures`, `html.parser`, `csv`, `argparse`, `collections`, `sys`, `os`
- No third-party libraries.

## Repository File Layout

### Files to Create

```
deadlinkchecker/
├── checker.py          # Entry point + CLI argument parsing
├── crawler.py          # BFS crawl logic; produces link/referrer pairs
├── fetcher.py          # HTTP HEAD/GET requests; returns status or error string
├── parser.py           # HTML link extraction using html.parser
├── normaliser.py       # URL normalisation (resolve, strip fragments, filter schemes)
└── reporter.py         # CSV writing
```

### Files to Modify

- `README.md` — update Usage section once CLI is stable (handled by versioning/docs agent, not coder).

## CLI Interface

### Entry Point

```
python checker.py <start_url> [options]
```

The tool is invoked directly. No `setup.py` or `pip install` is required at this stage.

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `start_url` | positional str | Yes | — | The URL to begin crawling from. |
| `--output` / `-o` | str | No | `results.csv` | Path to the output CSV file. |
| `--workers` / `-w` | int | No | `10` | Number of threads in the ThreadPoolExecutor. |
| `--timeout` / `-t` | int | No | `10` | Per-request timeout in seconds. |
| `--user-agent` | str | No | `deadlinkchecker/1.0` | User-Agent header sent with every request. |

### Example

```bash
python checker.py https://example.com --output report.csv --workers 20 --timeout 15
```

## Module Specifications

### `normaliser.py`

Responsible for all URL manipulation. No I/O.

#### `normalise(url: str, base: str) -> str | None`

Resolves `url` relative to `base`, then applies all normalisation rules. Returns the normalised absolute URL string, or `None` if the URL must be filtered out.

Rules applied in order:

1. Strip leading/trailing whitespace from `url`.
2. Use `urllib.parse.urljoin(base, url)` to resolve relative URLs. This handles:
   - Root-relative paths (`/about` -> `https://example.com/about`)
   - Protocol-relative URLs (`//cdn.example.com/x` -> `https://cdn.example.com/x`, inheriting the scheme of `base`)
   - Relative paths (`../page` resolved against `base`)
3. Parse the result with `urllib.parse.urlparse`.
4. Scheme filter: If the scheme is not `http` or `https`, return `None`. This filters out `mailto:`, `javascript:`, `tel:`, `ftp:`, and any other non-HTTP schemes.
5. Fragment stripping: Reconstruct the URL without the fragment component. Use `urllib.parse.urlunparse` with `fragment=''`.
6. Return the normalised URL string.

#### `is_internal(url: str, base_url: str) -> bool`

Returns `True` if `url` shares the same scheme and netloc (host + port) as `base_url`.

Implementation:

```python
def is_internal(url: str, base_url: str) -> bool:
    parsed_url = urllib.parse.urlparse(url)
    parsed_base = urllib.parse.urlparse(base_url)
    return parsed_url.scheme == parsed_base.scheme and parsed_url.netloc == parsed_base.netloc
```

### `parser.py`

Extracts all href values from `<a>` tags in an HTML document.

#### Class `LinkExtractor(html.parser.HTMLParser)`

Subclass of `html.parser.HTMLParser`.

Attributes:
- `links: list[str]` — accumulated raw href values.

Method `handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None`:
- If `tag == 'a'`, iterate over `attrs`.
- For each `(name, value)` pair where `name == 'href'` and `value` is not `None` and not empty string, append `value` to `self.links`.

#### `extract_links(html_content: str) -> list[str]`

Instantiates `LinkExtractor`, calls `feed(html_content)`, returns `extractor.links`. Wraps the call in a try/except to catch `html.parser.HTMLParseError`; returns an empty list on parse failure.

### `fetcher.py`

Performs HTTP requests. No crawling logic here.

#### `check_url(url: str, timeout: int, user_agent: str) -> str`

Returns the HTTP status code as a string (e.g. `"200"`, `"404"`) or an error string of the form `"ERROR:<ExceptionClassName>"`.

Algorithm:

1. Build a `urllib.request.Request` with `method='HEAD'`, setting the `User-Agent` header.
2. Set `urllib.request.urlopen` with `timeout=timeout`.
3. Do not follow redirects: Install a custom `urllib.request.HTTPRedirectHandler` subclass that raises `urllib.error.HTTPError` immediately on any redirect (3xx), preserving the original status code.
4. Call `urlopen(request)`. On success, return `str(response.status)`.
5. On `urllib.error.HTTPError`: if `e.code == 405`, retry once using `method='GET'` with the same no-redirect handler. Return `str(response.status)` on success of the retry, or `str(e.code)` if the GET also raises `HTTPError`.
6. On `urllib.error.URLError`: return `"ERROR:URLError"`.
7. On `TimeoutError` or `socket.timeout`: return `"ERROR:TimeoutError"`.
8. On any other `Exception`: return `f"ERROR:{type(e).__name__}"`.

No-redirect handler implementation:

```python
class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)
```

Use `urllib.request.build_opener(NoRedirectHandler())` to create the opener.

#### `fetch_html(url: str, timeout: int, user_agent: str) -> str | None`

Fetches the full response body for an internal page (used during crawling to extract links).

1. Build a `urllib.request.Request` with `method='GET'`, setting the `User-Agent` header.
2. Use a standard opener (with default redirect handling) to follow redirects so crawling can discover pages served via redirect.
3. Check `Content-Type` header; if it does not contain `text/html`, return `None`.
4. Read and decode the response body. Use the charset from the `Content-Type` header if present, otherwise fall back to `utf-8` with `errors='replace'`.
5. On any exception, return `None`.

### `crawler.py`

Implements the BFS (Breadth-First Search, https://en.wikipedia.org/wiki/Breadth-first_search) crawl. Produces the complete set of `(link, referrer)` pairs to be status-checked.

#### `crawl(start_url: str, timeout: int, user_agent: str) -> list[tuple[str, str]]`

Returns a list of `(link, referrer)` tuples representing every link that needs a status check. The `start_url` itself is included with referrer set to `""` (empty string).

Algorithm:

```
queue        = deque([start_url])
visited      = set()               # internal URLs already enqueued or fetched
results      = []                  # (link, referrer) pairs
visited.add(normalise(start_url, start_url))
results.append((normalised_start_url, ""))

while queue is not empty:
    current_url = queue.popleft()
    html = fetch_html(current_url, timeout, user_agent)
    if html is None:
        continue
    raw_links = extract_links(html)
    for raw in raw_links:
        norm = normalise(raw, current_url)
        if norm is None:
            continue                          # filtered scheme
        if norm in visited:
            continue                          # already queued or checked
        results.append((norm, current_url))
        if is_internal(norm, start_url):
            visited.add(norm)
            queue.append(norm)
        else:
            visited.add(norm)                 # do not re-add external links
            # do NOT enqueue external links
```

Notes:
- `visited` tracks both internal and external URLs to prevent the same external link from appearing more than once in results even if linked from multiple pages.
- The `start_url` itself is normalised before being placed into `visited` and `results`.
- BFS order ensures pages closer to the root are crawled before deeper pages.

### `reporter.py`

Writes the final CSV output.

#### `write_csv(results: list[tuple[str, str, str]], output_path: str) -> None`

Parameters:
- `results`: list of `(link, referrer, http_status_code)` tuples, already sorted.
- `output_path`: file path for the output CSV.

Behaviour:
- Opens `output_path` in write mode with `newline=''` and `encoding='utf-8'`.
- Uses `csv.writer` with default dialect.
- Writes header row: `link,referrer,http_status_code`.
- Writes all result rows.
- If the file cannot be opened (e.g. permission error), prints an error message to `stderr` and exits with code 1.

### `checker.py`

Entry point. Orchestrates all modules.

#### `main() -> None`

Algorithm:

1. Parse CLI arguments using `argparse`.
2. Validate `start_url`: must parse as `http` or `https` scheme; if not, print error to `stderr` and exit with code 1.
3. Call `crawler.crawl(start_url, timeout, user_agent)` -> `link_pairs: list[tuple[str, str]]`.
4. Use `concurrent.futures.ThreadPoolExecutor(max_workers=workers)` to dispatch `fetcher.check_url(link, timeout, user_agent)` for each `(link, referrer)` in `link_pairs`.
5. Collect futures using `as_completed` or `executor.map`. Associate each result with its `(link, referrer)` pair.
6. Build `results: list[tuple[str, str, str]]` as `(link, referrer, status)` for each pair.
7. Sort `results` by `(referrer, link)` — both ascending, with empty-string referrer sorting before any URL (Python default string sort satisfies this).
8. Call `reporter.write_csv(results, output_path)`.
9. Print a summary line to `stdout`: `Checked {n} links. Results written to {output_path}.`

Thread safety note: `crawler.crawl` runs single-threaded (BFS). Parallelism applies only to the status-check phase (`check_url` calls). This avoids shared-state complexity in the crawler.

## URL Normalisation — Detailed Rules

| Input | Base | Result |
|---|---|---|
| `https://example.com/page#section` | any | `https://example.com/page` |
| `/about` | `https://example.com/home` | `https://example.com/about` |
| `//cdn.example.com/x.js` | `https://example.com/` | `https://cdn.example.com/x.js` |
| `../other` | `https://example.com/a/b/` | `https://example.com/a/other` |
| `mailto:x@y.com` | any | `None` (filtered) |
| `javascript:void(0)` | any | `None` (filtered) |
| `tel:+123` | any | `None` (filtered) |
| `https://example.com/page?q=1` | any | `https://example.com/page?q=1` (query preserved) |

## Error Handling

| Scenario | Behaviour |
|---|---|
| `start_url` not http/https | Print error to stderr, exit code 1 |
| `fetch_html` network failure during crawl | Return `None`; skip page silently |
| `check_url` network failure | Record `ERROR:<ExceptionClassName>` as status |
| `check_url` HTTP 3xx | Record the 3xx status code as-is (no follow) |
| `check_url` HTTP 405 on HEAD | Retry with GET; record result of GET |
| HTML parse failure | Return empty link list; log nothing |
| Output file not writable | Print error to stderr, exit code 1 |
| Worker count < 1 | Validate `>= 1` manually, exit code 1 if invalid |
| Timeout < 1 | Validate `>= 1` manually, exit code 1 if invalid |

## Edge Cases

- Self-referencing links (`href=""`): `urljoin(base, "")` returns `base`; it will be in `visited` already and thus skipped.
- Duplicate links on the same page: The `visited` set deduplicates across all pages; a link seen twice on one page is only added once.
- `start_url` with trailing slash vs without: Treat as distinct URLs — do not normalise trailing slashes beyond what `urljoin` produces naturally. The crawler will visit each form only once due to the `visited` set.
- `start_url` is a redirect: `fetch_html` follows redirects, so the actual content page is parsed. The start URL itself is still recorded in `results` with its true HTTP status from `check_url` (which does not follow redirects).
- Non-HTML internal pages (PDF, image, etc.): `fetch_html` returns `None` on non-`text/html` Content-Type; the page is recorded in results with its real HTTP status but no links are extracted from it.
- Very large pages: `fetch_html` reads the full response body. No size cap is specified; this is acceptable for v1.
- Relative URL with no path (e.g. `?query=1`): `urljoin` resolves correctly against the base page.
- Ports in URLs: `urlparse.netloc` includes the port; `is_internal` compares the full netloc so `example.com` and `example.com:8080` are treated as different hosts.
- Case sensitivity of scheme/host: `urllib.parse` lowercases scheme and host automatically; no extra normalisation needed.

## Expected Output Example

From the sample site `https://deadlinkchecker-sample-website.netlify.app`:

```csv
link,referrer,http_status_code
https://deadlinkchecker-sample-website.netlify.app/about/,https://deadlinkchecker-sample-website.netlify.app/,404
https://deadlinkchecker-sample-website.netlify.app/blog,https://deadlinkchecker-sample-website.netlify.app/,200
https://deadlinkchecker-sample-website.netlify.app/contact,https://deadlinkchecker-sample-website.netlify.app/,200
https://iamjeremie.me/,https://deadlinkchecker-sample-website.netlify.app/contact,200
https://iamjeremie.me/doesnt-exist,https://deadlinkchecker-sample-website.netlify.app/contact,404
```

Note: the start URL itself (`https://deadlinkchecker-sample-website.netlify.app/`) does not appear in the output because its referrer is `""` and none of the other crawled pages link back to it as a new discovery. If the start URL is discovered as a link from another page before being placed into `visited`, it will appear with the appropriate referrer. The first insertion always uses `""` as referrer.

## Summary of Key Design Decisions

1. Single-threaded BFS crawl, parallel status checks: Separates crawl graph traversal (which requires sequential state management) from HTTP status checking (which is embarrassingly parallel).
2. HEAD first, GET fallback on 405: Minimises bandwidth while maintaining compatibility with servers that reject HEAD.
3. No redirect following in `check_url`: Exposes the true HTTP status of each URL as found, not the final destination. This is the specified behaviour.
4. Redirect following in `fetch_html`: Allows the crawler to discover links from pages that respond with a redirect, avoiding incomplete crawls.
5. Fragment stripping: Prevents `page#section1` and `page#section2` from being treated as separate URLs.
6. Empty-string referrer for start URL: Provides a consistent sentinel that sorts before all other referrers in the output.

## Change Requests

### CR-2: Split `tests/test_checker.py` into per-module test files

**Motivation:** A single monolithic test file mixes concerns from six modules plus integration. Splitting into one file per source module and one integration file improves isolation, discoverability, and parallel test execution.

**File deleted:** `tests/test_checker.py`

**Files created:**

| New file | Contains (class names from the original file) |
|---|---|
| `tests/test_normaliser.py` | `TestNormalise` |
| `tests/test_parser.py` | `TestExtractLinks` |
| `tests/test_fetcher.py` | `TestCheckUrl` |
| `tests/test_reporter.py` | `TestWriteCsv` |
| `tests/test_checker_cli.py` | `TestCheckerCLI` |
| `tests/test_integration.py` | `TestIntegration` |

Each new file must:
- Include the `PROJECT_ROOT` / `sys.path` bootstrap block identical to the original.
- Import only the module(s) it tests.
- End with the `if __name__ == "__main__": unittest.main(verbosity=2)` guard.

### CR-3: Add terminal feedback during execution

**Motivation:** The tool currently produces no output while it runs, making it appear hung on large sites. Live progress output lets users see activity as URLs are discovered and checked.

**Scope:** Two distinct events must be printed to stdout during execution:

1. **URL discovered** — emitted by `crawler.crawl()` each time a new URL is added to `results` (both internal and external).
2. **URL checked** — emitted by `checker.py` each time a `check_url` future completes.

**Files to modify:**

| File | Change |
|---|---|
| `crawler.py` | Print each discovered URL immediately after it is appended to `results`. |
| `checker.py` | Print each URL and its resolved status immediately after a future completes. |

**Exact output formats:**

Discovered (in `crawler.py`, inside the `crawl` function, after `results.append(...)`):

```
DISCOVERED <url>
```

Checked (in `checker.py`, inside the `as_completed` loop, after `future.result()` is obtained):

```
CHECKED <url> <status>
```

Where `<status>` is either the HTTP status code string (e.g. `200`, `404`) or the `ERROR:<ExceptionClassName>` string — identical to what is written to CSV.

**Print target:** `sys.stdout` using the built-in `print()` function with no additional formatting. Each line is terminated by the default newline.

**Thread safety:** The `CHECKED` prints occur inside `concurrent.futures.as_completed`, where multiple threads may complete near-simultaneously. Python's `print()` is not guaranteed to be atomic across threads. The implementation must wrap each `print()` call in the `as_completed` loop with a `threading.Lock` to prevent interleaved output. The lock instance is created once in `main()` and passed down, or defined at module scope.

**Parallelism note:** `DISCOVERED` prints happen in the single-threaded crawl phase and require no locking. `CHECKED` prints happen in the parallel status-check phase and must be serialised with a lock.

**Signature changes:**

`crawler.crawl` signature is unchanged: `crawl(start_url: str, timeout: int, user_agent: str) -> list[tuple[str, str]]`. The `print` call is added inline; no new parameter is introduced.

`checker.py` `main()` adds a `threading.Lock` instance and uses it to guard each `print` in the `as_completed` loop.

**Edge cases and error handling:**

- If `crawler.crawl` returns an empty list (start URL normalisation fails), no `DISCOVERED` line is printed.
- If `check_url` raises an unhandled exception (it should not — it catches all exceptions internally), the `CHECKED` print is skipped for that URL; the existing `future.result()` call propagates the exception naturally.
- The `DISCOVERED` line for the start URL itself is printed exactly once, before any pages are fetched.
- No change to the final summary line: `Checked {n} links. Results written to {output_path}.` — it remains at the end.

**No changes to:** `fetcher.py`, `normaliser.py`, `parser.py`, `reporter.py`, any test files.

status: ready

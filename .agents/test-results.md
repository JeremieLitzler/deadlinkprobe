# Test Results — CR-3: Add terminal feedback during execution

## Environment

- Python: `/e/Applications/Scoop/apps/python/current/python.exe` (3.14.3)
- Command: `python -m unittest discover -s tests -v`
- Working directory: `E:/Git/GitHub/deadlinkchecker`
- Date: 2026-02-20

---

## Files Modified

- `tests/test_checker_cli.py` — added three new test classes (11 new tests)

No new test files were created. The instruction specified adding to existing files; `test_crawler.py` does not exist, so all new tests were placed in `test_checker_cli.py`.

---

## New Test Classes Added

### `TestCrawlerDiscoveredOutput`

Tests that `crawler.crawl()` prints `DISCOVERED <url>` to stdout for every URL it adds to the results list. Uses `unittest.mock.patch` on `crawler.fetch_html` and `sys.stdout` to isolate network I/O and capture output.

| Test | Description | Result |
|---|---|---|
| `test_discovered_printed_for_start_url` | `DISCOVERED` is printed for the start URL itself before any pages are fetched | PASS |
| `test_discovered_printed_for_each_found_link` | `DISCOVERED` is printed for each internal and external link found during crawl | PASS |
| `test_discovered_count_matches_results` | The count of `DISCOVERED` lines equals the number of `(link, referrer)` tuples returned | PASS |
| `test_no_discovered_when_start_url_invalid` | No `DISCOVERED` line appears and result is `[]` when start URL normalisation returns `None` (e.g. `mailto:` scheme) | PASS |
| `test_duplicate_links_not_discovered_twice` | A URL linked from multiple pages produces exactly one `DISCOVERED` line | PASS |

### `TestCheckerCheckedOutput`

Tests that `checker.main()` prints `CHECKED <url> <status>` to stdout after each future completes. Uses `patch` on `crawler.crawl`, `fetcher.check_url`, and `sys.stdout` to run `main()` without network access.

| Test | Description | Result |
|---|---|---|
| `test_checked_line_printed_for_each_link` | A `CHECKED` line is printed for every link returned by the crawl | PASS |
| `test_checked_line_format_with_status_code` | Format is exactly `CHECKED <url> <status_code>` for numeric statuses | PASS |
| `test_checked_line_format_with_error_status` | Format is exactly `CHECKED <url> ERROR:<ExceptionClassName>` for error statuses | PASS |
| `test_no_checked_lines_when_no_links` | No `CHECKED` lines appear when crawl returns an empty list | PASS |
| `test_summary_line_present_after_checked_lines` | The final `Checked N links. Results written to ...` summary line is present | PASS |

### `TestCheckerThreadSafety`

Tests that `print_lock` in `checker.main()` prevents interleaved output under concurrent execution. Uses 10 workers checking 20 URLs concurrently, with a 10 ms artificial delay per `check_url` call to encourage simultaneous completions.

| Test | Description | Result |
|---|---|---|
| `test_checked_lines_are_not_interleaved` | Every `CHECKED` line matches the expected regex, no partial or merged lines exist, every URL appears exactly once | PASS |

---

## Pre-existing Tests (unchanged, all still pass)

| File | Test Class | Tests | Result |
|---|---|---|---|
| `tests/test_checker_cli.py` | `TestCheckerCLI` | 3 | PASS |
| `tests/test_fetcher.py` | `TestCheckUrl` | 4 | PASS |
| `tests/test_normaliser.py` | `TestNormalise` | 8 | PASS |
| `tests/test_parser.py` | `TestExtractLinks` | 4 | PASS |
| `tests/test_reporter.py` | `TestWriteCsv` | 1 | PASS |
| `tests/test_integration.py` | `TestIntegration` | 5 | PASS |

---

## Full Run Output

```
test_help_exits_zero (test_checker_cli.TestCheckerCLI.test_help_exits_zero) ... ok
test_invalid_url_scheme_exits_nonzero (test_checker_cli.TestCheckerCLI.test_invalid_url_scheme_exits_nonzero) ... ok
test_no_args_exits_nonzero (test_checker_cli.TestCheckerCLI.test_no_args_exits_nonzero) ... ok
test_checked_line_format_with_error_status (test_checker_cli.TestCheckerCheckedOutput.test_checked_line_format_with_error_status) ... ok
test_checked_line_format_with_status_code (test_checker_cli.TestCheckerCheckedOutput.test_checked_line_format_with_status_code) ... ok
test_checked_line_printed_for_each_link (test_checker_cli.TestCheckerCheckedOutput.test_checked_line_printed_for_each_link) ... ok
test_no_checked_lines_when_no_links (test_checker_cli.TestCheckerCheckedOutput.test_no_checked_lines_when_no_links) ... ok
test_summary_line_present_after_checked_lines (test_checker_cli.TestCheckerCheckedOutput.test_summary_line_present_after_checked_lines) ... ok
test_checked_lines_are_not_interleaved (test_checker_cli.TestCheckerThreadSafety.test_checked_lines_are_not_interleaved) ... ok
test_discovered_count_matches_results (test_checker_cli.TestCrawlerDiscoveredOutput.test_discovered_count_matches_results) ... ok
test_discovered_printed_for_each_found_link (test_checker_cli.TestCrawlerDiscoveredOutput.test_discovered_printed_for_each_found_link) ... ok
test_discovered_printed_for_start_url (test_checker_cli.TestCrawlerDiscoveredOutput.test_discovered_printed_for_start_url) ... ok
test_duplicate_links_not_discovered_twice (test_checker_cli.TestCrawlerDiscoveredOutput.test_duplicate_links_not_discovered_twice) ... ok
test_no_discovered_when_start_url_invalid (test_checker_cli.TestCrawlerDiscoveredOutput.test_no_discovered_when_start_url_invalid) ... ok
test_retries_get_on_405 (test_fetcher.TestCheckUrl.test_retries_get_on_405) ... ok
test_returns_200_on_success (test_fetcher.TestCheckUrl.test_returns_200_on_success) ... ok
test_returns_301_on_redirect (test_fetcher.TestCheckUrl.test_returns_301_on_redirect) ... ok
test_returns_error_on_url_error (test_fetcher.TestCheckUrl.test_returns_error_on_url_error) ... ok
test_about_page_is_404 (test_integration.TestIntegration.test_about_page_is_404) ... ok
test_contains_200_status (test_integration.TestIntegration.test_contains_200_status) ... ok
test_contains_404_status (test_integration.TestIntegration.test_contains_404_status) ... ok
test_csv_has_correct_header (test_integration.TestIntegration.test_csv_has_correct_header) ... ok
test_exit_code_is_zero (test_integration.TestIntegration.test_exit_code_is_zero) ... ok
test_is_internal_different_host (test_normaliser.TestNormalise.test_is_internal_different_host) ... ok
test_is_internal_same_host (test_normaliser.TestNormalise.test_is_internal_same_host) ... ok
test_resolves_protocol_relative_href (test_normaliser.TestNormalise.test_resolves_protocol_relative_href) ... ok
test_resolves_relative_path_href (test_normaliser.TestNormalise.test_resolves_relative_path_href) ... ok
test_resolves_root_relative_href (test_normaliser.TestNormalise.test_resolves_root_relative_href) ... ok
test_returns_none_for_javascript (test_normaliser.TestNormalise.test_returns_none_for_javascript) ... ok
test_returns_none_for_mailto (test_normaliser.TestNormalise.test_returns_none_for_mailto) ... ok
test_strips_fragment_from_absolute_url (test_normaliser.TestNormalise.test_strips_fragment_from_absolute_url) ... ok
test_empty_html_returns_empty_list (test_parser.TestExtractLinks.test_empty_html_returns_empty_list) ... ok
test_ignores_non_anchor_tags (test_parser.TestExtractLinks.test_ignores_non_anchor_tags) ... ok
test_returns_hrefs_from_anchor_tags (test_parser.TestExtractLinks.test_returns_hrefs_from_anchor_tags) ... ok
test_skips_empty_href_values (test_parser.TestExtractLinks.test_skips_empty_href_values) ... ok
test_writes_header_and_rows (test_reporter.TestWriteCsv.test_writes_header_and_rows) ... ok

----------------------------------------------------------------------
Ran 36 tests in 4.028s

OK
```

---

## Notes

- Two `ResourceWarning` messages appeared during `test_retries_get_on_405` and `test_returns_error_on_url_error` from the pre-existing `test_fetcher.py`. These originate from Python 3.14's garbage-collection detecting unclosed `HTTPError` objects in mock setups. They are cosmetic and do not affect correctness — all assertions passed.
- The integration tests made live network requests to `https://deadlinkchecker-sample-website.netlify.app` and validated real HTTP responses, including the expected `404` on `/about/`.
- The thread-safety test uses 10 workers and 20 URLs with a 10 ms artificial delay to provoke concurrent `print()` calls, then verifies every output line matches the exact `CHECKED <url> <status>` format with no corruption.

---

### Test Summary

36 tests run across 6 files. 36 passed, 0 failed, 0 errors.
11 new tests added for CR-3 (5 DISCOVERED, 5 CHECKED format, 1 thread safety).

status: passed

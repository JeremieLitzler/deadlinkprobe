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

---

## 2026-02-24 - Issue #8: Add a summary for each website scanned

### Environment

- Python: `/e/Applications/Scoop/apps/python/current/python.exe` (3.14.3)
- Command: `python -m pytest tests/ -v`
- Working directory: `E:/Git/GitHub/deadlinkchecker`
- Date: 2026-02-24

---

### Files Modified

- `tests/test_reporter.py` — added `TestWriteMarkdownSummary` class (8 new tests); existing `TestWriteCsv` class left unchanged.

---

### New Test Class: `TestWriteMarkdownSummary`

Tests for `reporter.write_markdown_summary(results, output_path, timestamp)`.

| Test | Description | Result |
|---|---|---|
| `test_file_is_created` | Output file exists at the given path after the call | PASS |
| `test_first_non_empty_line_is_heading` | First non-empty line is `## <timestamp>` | PASS |
| `test_table_header_row_present` | Content contains `| URL | Referrer | HTTP Status |` | PASS |
| `test_non_200_rows_appear_in_table_body` | Rows with status 404, 500, ERROR:URLError are present in the table body | PASS |
| `test_200_rows_do_not_appear_in_table_body` | Rows with status 200 are absent from the table body | PASS |
| `test_all_200_results_produce_empty_table_body` | When every result is 200, no data rows appear after the separator | PASS |
| `test_empty_results_writes_heading_and_empty_table` | An empty results list still produces the heading, header row and separator with no data rows | PASS |
| `test_oserror_on_unwritable_path_causes_systemexit_1` | An unwritable path (missing parent directory) causes `SystemExit` with code 1 | PASS |

---

### Pre-existing Tests (unchanged, all still pass)

| File | Test Class | Tests | Result |
|---|---|---|---|
| `tests/test_checker_cli.py` | `TestCheckerCLI` | 3 | PASS |
| `tests/test_checker_cli.py` | `TestCrawlerDiscoveredOutput` | 5 | PASS |
| `tests/test_checker_cli.py` | `TestCheckerCheckedOutput` | 5 | PASS |
| `tests/test_checker_cli.py` | `TestCheckerThreadSafety` | 1 | PASS |
| `tests/test_fetcher.py` | `TestCheckUrl` | 4 | PASS |
| `tests/test_normaliser.py` | `TestNormalise` | 8 | PASS |
| `tests/test_parser.py` | `TestExtractLinks` | 4 | PASS |
| `tests/test_reporter.py` | `TestWriteCsv` | 1 | PASS |
| `tests/test_integration.py` | `TestIntegration` | 5 | PASS |

---

### Full Run Output

```
tests/test_checker_cli.py::TestCheckerCLI::test_help_exits_zero PASSED
tests/test_checker_cli.py::TestCheckerCLI::test_invalid_url_scheme_exits_nonzero PASSED
tests/test_checker_cli.py::TestCheckerCLI::test_no_args_exits_nonzero PASSED
tests/test_checker_cli.py::TestCrawlerDiscoveredOutput::test_discovered_count_matches_results PASSED
tests/test_checker_cli.py::TestCrawlerDiscoveredOutput::test_discovered_printed_for_each_found_link PASSED
tests/test_checker_cli.py::TestCrawlerDiscoveredOutput::test_discovered_printed_for_start_url PASSED
tests/test_checker_cli.py::TestCrawlerDiscoveredOutput::test_duplicate_links_not_discovered_twice PASSED
tests/test_checker_cli.py::TestCrawlerDiscoveredOutput::test_no_discovered_when_start_url_invalid PASSED
tests/test_checker_cli.py::TestCheckerCheckedOutput::test_checked_line_format_with_error_status PASSED
tests/test_checker_cli.py::TestCheckerCheckedOutput::test_checked_line_format_with_status_code PASSED
tests/test_checker_cli.py::TestCheckerCheckedOutput::test_checked_line_printed_for_each_link PASSED
tests/test_checker_cli.py::TestCheckerCheckedOutput::test_no_checked_lines_when_no_links PASSED
tests/test_checker_cli.py::TestCheckerCheckedOutput::test_summary_line_present_after_checked_lines PASSED
tests/test_checker_cli.py::TestCheckerThreadSafety::test_checked_lines_are_not_interleaved PASSED
tests/test_fetcher.py::TestCheckUrl::test_retries_get_on_405 PASSED
tests/test_fetcher.py::TestCheckUrl::test_returns_200_on_success PASSED
tests/test_fetcher.py::TestCheckUrl::test_returns_301_on_redirect PASSED
tests/test_fetcher.py::TestCheckUrl::test_returns_error_on_url_error PASSED
tests/test_integration.py::TestIntegration::test_about_page_is_404 PASSED
tests/test_integration.py::TestIntegration::test_contains_200_status PASSED
tests/test_integration.py::TestIntegration::test_contains_404_status PASSED
tests/test_integration.py::TestIntegration::test_csv_has_correct_header PASSED
tests/test_integration.py::TestIntegration::test_exit_code_is_zero PASSED
tests/test_normaliser.py::TestNormalise::test_is_internal_different_host PASSED
tests/test_normaliser.py::TestNormalise::test_is_internal_same_host PASSED
tests/test_normaliser.py::TestNormalise::test_resolves_protocol_relative_href PASSED
tests/test_normaliser.py::TestNormalise::test_resolves_relative_path_href PASSED
tests/test_normaliser.py::TestNormalise::test_resolves_root_relative_href PASSED
tests/test_normaliser.py::TestNormalise::test_returns_none_for_javascript PASSED
tests/test_normaliser.py::TestNormalise::test_returns_none_for_mailto PASSED
tests/test_normaliser.py::TestNormalise::test_strips_fragment_from_absolute_url PASSED
tests/test_parser.py::TestExtractLinks::test_empty_html_returns_empty_list PASSED
tests/test_parser.py::TestExtractLinks::test_ignores_non_anchor_tags PASSED
tests/test_parser.py::TestExtractLinks::test_returns_hrefs_from_anchor_tags PASSED
tests/test_parser.py::TestExtractLinks::test_skips_empty_href_values PASSED
tests/test_reporter.py::TestWriteCsv::test_writes_header_and_rows PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_200_rows_do_not_appear_in_table_body PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_all_200_results_produce_empty_table_body PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_empty_results_writes_heading_and_empty_table PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_file_is_created PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_first_non_empty_line_is_heading PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_non_200_rows_appear_in_table_body PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_oserror_on_unwritable_path_causes_systemexit_1 PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_table_header_row_present PASSED

============================== 44 passed in 3.67s ==============================
```

---

### Test Summary

44 tests run across 6 files. 44 passed, 0 failed, 0 errors.
8 new tests added for Issue #8 in `TestWriteMarkdownSummary`. All 36 pre-existing tests continue to pass with no regressions.

status: passed

## 2026-02-24 - Bug #16: Workflow link checker cannot push scans folder

### Environment

- Python: `/e/Applications/Scoop/apps/python/current/python.exe` (3.14.3)
- Command: `python -m pytest tests/ -v`
- Working directory: `E:/Git/GitHub/deadlinkchecker`
- Date: 2026-02-24
- File under review: `.github/workflows/deadlinkchecker.yml`

### Static Checks Against Spec

| # | Requirement | Result | Notes |
|---|---|---|---|
| 1 | Checkout step does NOT specify `ref: data/scans` (must check out default branch first so it never fails on first run) | PASS | The `actions/checkout@v4` step has no `ref:` key; it checks out the default branch. |
| 2 | Checkout step has `fetch-depth: 0` | PASS | `fetch-depth: 0` is present under the checkout `with:` block. |
| 3 | "Ensure data/scans branch exists" step comes AFTER the checkout step | PASS | Checkout is the first step; "Ensure data/scans branch exists" is the second step — order is correct. |
| 4 | That step runs `git fetch origin data/scans \|\| true` to avoid failure when branch does not exist | PASS | `git fetch origin data/scans \|\| true` is present exactly as specified. |
| 5 | That step runs `git checkout data/scans 2>/dev/null \|\| git checkout -b data/scans` | PASS | `git checkout data/scans 2>/dev/null \|\| git checkout -b data/scans` is present exactly as specified. |
| 6 | Commit/push step uses `git push origin data/scans` (not bare `git push`) | PASS | `git push origin data/scans` — explicit remote and branch are named. |
| 7 | `git diff --cached --quiet \|\| git commit` guard is still present (no commit if nothing changed) | PASS | `git diff --cached --quiet \|\| git commit -m "bot: add scan for $(date +%Y-%m-%d)"` is present. |
| 8 | No changes to any `src/` files or test files | PASS | Only `.github/workflows/deadlinkchecker.yml` was modified; no `src/` or `tests/` files were touched. |

All 8 static checks pass.

### Python Test Suite (Regression Check)

No Python source files changed; the test suite is run to confirm no regressions from any prior change on this branch.

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: E:\Git\GitHub\deadlinkchecker
collected 44 items

tests/test_checker_cli.py::TestCheckerCLI::test_help_exits_zero PASSED
tests/test_checker_cli.py::TestCheckerCLI::test_invalid_url_scheme_exits_nonzero PASSED
tests/test_checker_cli.py::TestCheckerCLI::test_no_args_exits_nonzero PASSED
tests/test_checker_cli.py::TestCrawlerDiscoveredOutput::test_discovered_count_matches_results PASSED
tests/test_checker_cli.py::TestCrawlerDiscoveredOutput::test_discovered_printed_for_each_found_link PASSED
tests/test_checker_cli.py::TestCrawlerDiscoveredOutput::test_discovered_printed_for_start_url PASSED
tests/test_checker_cli.py::TestCrawlerDiscoveredOutput::test_duplicate_links_not_discovered_twice PASSED
tests/test_checker_cli.py::TestCrawlerDiscoveredOutput::test_no_discovered_when_start_url_invalid PASSED
tests/test_checker_cli.py::TestCheckerCheckedOutput::test_checked_line_format_with_error_status PASSED
tests/test_checker_cli.py::TestCheckerCheckedOutput::test_checked_line_format_with_status_code PASSED
tests/test_checker_cli.py::TestCheckerCheckedOutput::test_checked_line_printed_for_each_link PASSED
tests/test_checker_cli.py::TestCheckerCheckedOutput::test_no_checked_lines_when_no_links PASSED
tests/test_checker_cli.py::TestCheckerCheckedOutput::test_summary_line_present_after_checked_lines PASSED
tests/test_checker_cli.py::TestCheckerThreadSafety::test_checked_lines_are_not_interleaved PASSED
tests/test_fetcher.py::TestCheckUrl::test_retries_get_on_405 PASSED
tests/test_fetcher.py::TestCheckUrl::test_returns_200_on_success PASSED
tests/test_fetcher.py::TestCheckUrl::test_returns_301_on_redirect PASSED
tests/test_fetcher.py::TestCheckUrl::test_returns_error_on_url_error PASSED
tests/test_integration.py::TestIntegration::test_about_page_is_404 PASSED
tests/test_integration.py::TestIntegration::test_contains_200_status PASSED
tests/test_integration.py::TestIntegration::test_contains_404_status PASSED
tests/test_integration.py::TestIntegration::test_csv_has_correct_header PASSED
tests/test_integration.py::TestIntegration::test_exit_code_is_zero PASSED
tests/test_normaliser.py::TestNormalise::test_is_internal_different_host PASSED
tests/test_normaliser.py::TestNormalise::test_is_internal_same_host PASSED
tests/test_normaliser.py::TestNormalise::test_resolves_protocol_relative_href PASSED
tests/test_normaliser.py::TestNormalise::test_resolves_relative_path_href PASSED
tests/test_normaliser.py::TestNormalise::test_resolves_root_relative_href PASSED
tests/test_normaliser.py::TestNormalise::test_returns_none_for_javascript PASSED
tests/test_normaliser.py::TestNormalise::test_returns_none_for_mailto PASSED
tests/test_normaliser.py::TestNormalise::test_strips_fragment_from_absolute_url PASSED
tests/test_parser.py::TestExtractLinks::test_empty_html_returns_empty_list PASSED
tests/test_parser.py::TestExtractLinks::test_ignores_non_anchor_tags PASSED
tests/test_parser.py::TestExtractLinks::test_returns_hrefs_from_anchor_tags PASSED
tests/test_parser.py::TestExtractLinks::test_skips_empty_href_values PASSED
tests/test_reporter.py::TestWriteCsv::test_writes_header_and_rows PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_200_rows_do_not_appear_in_table_body PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_all_200_results_produce_empty_table_body PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_empty_results_writes_heading_and_empty_table PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_file_is_created PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_first_non_empty_line_is_heading PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_non_200_rows_appear_in_table_body PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_oserror_on_unwritable_path_causes_systemexit_1 PASSED
tests/test_reporter.py::TestWriteMarkdownSummary::test_table_header_row_present PASSED

============================== 44 passed in 1.86s ==============================
```

### Test Summary

44 tests run across 6 files. 44 passed, 0 failed, 0 errors. No regressions.
8 static workflow checks performed. 8 passed, 0 failed.

status: passed

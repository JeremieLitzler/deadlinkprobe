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

## 2026-02-24 - Issue #18: Agentic Workflow updates

### Environment

- Python: `/e/Applications/Scoop/apps/python/current/python.exe` (3.14.3)
- Command: `python -m pytest tests/ -v`
- Working directory: `E:/Git/GitHub/deadlinkchecker`
- Date: 2026-02-24
- Files under review: `.agents-brain/agent-1-specs.md`, `.agents-brain/agent-2-coder.md`

### Static Checks: `agent-1-specs.md`

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | The bullet "Key functions/types/interfaces with their signatures" is gone | PASS | No such phrase exists anywhere in the updated file. |
| 2 | The prompt includes guidance on describing files and their roles without prescribing internal structure | PASS | Line 12: "Files to create or modify, and what each file's role is (without prescribing internal structure)". |
| 3 | The prompt includes guidance on edge cases as observable consequences (not code paths) | PASS | Line 13: "Edge cases described as user-visible or externally observable consequences". |
| 4 | The prompt includes guidance on concurrency as outcome qualities (not implementation blueprints) | PASS | Line 14: "Concurrency or performance requirements stated as qualities of the outcome ... not as implementation blueprints". |
| 5 | An explicit WHAT vs HOW principle is stated | PASS | Line 16: "A good spec describes WHAT the system does ... It does not describe HOW the system does it." |
| 6 | An explicit prohibition list exists covering: function signatures, pseudocode, code snippets, variable names, import lists | PASS | Lines 22-27 enumerate all five prohibited items plus a catch-all clause. |

All 6 static checks for `agent-1-specs.md` pass.

### Static Checks: `agent-2-coder.md`

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | A "Technical Choice Explanations" section exists requiring "why" notes in `code-ready.md` | PASS | Line 38: `## Technical Choice Explanations`; requires explanation of why for each non-trivial decision. |
| 2 | An "Object Calisthenics" section exists | PASS | Line 51: `## Object Calisthenics`. |
| 3 | All nine rules are enumerated inline | PASS | Lines 57-65 list rules 1 through 9 explicitly with titles and descriptions. |
| 4 | At least one concrete before/after example is included | PASS | Two examples are present: no-else rule (lines 67-86) and one-level-of-indentation rule (lines 88-109). |

All 4 static checks for `agent-2-coder.md` pass.

### Python Test Suite (Regression Check)

No Python source files changed. The test suite is run to confirm no regressions.

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
10 static checks performed across 2 agent prompt files. 10 passed, 0 failed.

status: passed

## 2026-02-25 - Issue #10: Send email notification when a scan contains non HTTP/200 status

### Environment

- Python: `/e/Applications/Scoop/apps/python/current/python.exe` (3.14.3)
- Command: `python -m pytest tests/ -v`
- Working directory: `E:/Git/GitHub/deadlinkchecker`
- Date: 2026-02-25

---

### Fixes Applied Before Running Tests

| File | Problem | Fix |
|---|---|---|
| `tests/test_parser.py` | `import parser as link_parser` failed — `parser.py` was renamed to `web_parser.py` | Changed to `import web_parser as link_parser`; updated module docstring and section comment |

---

### New Files Created

- `tests/test_emailer.py` — 4 test classes, 23 tests covering `emailer.py`

### New Tests Added to Existing Files

- `tests/test_checker_cli.py` — added `TestBuildArgParser` (17 tests) covering `argument_parser.build_arg_parser()`

---

### New Test Classes

#### `TestBuildArgParser` (`tests/test_checker_cli.py`)

Tests `argument_parser.build_arg_parser()` directly by calling `parse_args()` with controlled input lists.

| Test | Description | Result |
|---|---|---|
| `test_start_url_is_required` | Omitting `start_url` raises `SystemExit` | PASS |
| `test_start_url_stored` | `start_url` positional is stored on the namespace | PASS |
| `test_output_default_is_none` | `--output` defaults to `None` | PASS |
| `test_output_long_flag` | `--output` stores the provided path | PASS |
| `test_output_short_flag` | `-o` is an alias for `--output` | PASS |
| `test_workers_default` | `--workers` defaults to `10` | PASS |
| `test_workers_long_flag` | `--workers` stores the given integer | PASS |
| `test_workers_short_flag` | `-w` is an alias for `--workers` | PASS |
| `test_workers_is_int` | `--workers` value is stored as `int` | PASS |
| `test_timeout_default` | `--timeout` defaults to `10` | PASS |
| `test_timeout_long_flag` | `--timeout` stores the given integer | PASS |
| `test_timeout_short_flag` | `-t` is an alias for `--timeout` | PASS |
| `test_timeout_is_int` | `--timeout` value is stored as `int` | PASS |
| `test_user_agent_default` | `--user-agent` defaults to `deadlinkchecker/1.0` | PASS |
| `test_user_agent_custom` | `--user-agent` stores the provided string | PASS |
| `test_notify_email_default_is_none` | `--notify-email` defaults to `None` | PASS |
| `test_notify_email_stores_address` | `--notify-email` stores the provided address | PASS |

#### `TestBuildEmailRows` (`tests/test_emailer.py`)

Tests `emailer._build_email_rows()`.

| Test | Description | Result |
|---|---|---|
| `test_returns_empty_string_for_empty_list` | Empty input returns empty string | PASS |
| `test_single_row_contains_link_referrer_status` | Single result contains link, referrer, status in `<td>` elements | PASS |
| `test_multiple_rows_joined_by_newline` | Multiple rows joined by newlines | PASS |
| `test_html_special_chars_are_escaped` | `<script>` in link is escaped to `&lt;script&gt;` | PASS |

#### `TestBuildEmailHtml` (`tests/test_emailer.py`)

Tests `emailer._build_email_html()`.

| Test | Description | Result |
|---|---|---|
| `test_contains_website` | Output contains website name | PASS |
| `test_contains_timestamp` | Output contains timestamp | PASS |
| `test_contains_total_links_count` | Output contains total links count | PASS |
| `test_contains_non_200_count` | Output contains non-200 count | PASS |
| `test_no_table_when_no_non_200_results` | No `<table>` when non_200_results is empty | PASS |
| `test_table_present_when_non_200_results_exist` | `<table>` present when non_200_results is non-empty | PASS |
| `test_table_contains_thead_and_tbody` | Table has `<thead>` and `<tbody>` | PASS |
| `test_website_html_special_chars_escaped` | HTML chars in website name are escaped | PASS |

#### `TestPostToResend` (`tests/test_emailer.py`)

Tests `emailer._post_to_resend()`. All calls mock `urllib.request.urlopen`.

| Test | Description | Result |
|---|---|---|
| `test_prints_notification_sent_on_200` | `"Notification sent."` printed to stdout on HTTP 200 | PASS |
| `test_warns_to_stderr_on_non_200_response` | Non-200 status code emits warning to stderr | PASS |
| `test_warns_to_stderr_on_http_error` | `HTTPError` emits warning with code to stderr | PASS |
| `test_warns_to_stderr_on_url_error` | `URLError` emits warning with reason to stderr | PASS |
| `test_request_uses_bearer_auth_header` | `Authorization` header is `Bearer <api_key>` | PASS |
| `test_request_is_post_method` | HTTP method is POST | PASS |

#### `TestSendEmailNotification` (`tests/test_emailer.py`)

Tests `emailer.send_email_notification()`. Module-level `_RESEND_API_KEY` and `_RESEND_FROM_ADDRESS` are patched directly via `patch.object` so tests are independent of the runtime environment.

| Test | Description | Result |
|---|---|---|
| `test_warns_and_returns_when_api_key_missing` | `_RESEND_API_KEY is None` warns about `RESEND_API_KEY`, makes no HTTP call | PASS |
| `test_warns_and_returns_when_from_address_missing` | `_RESEND_FROM_ADDRESS is None` warns about `RESEND_FROM_ADDRESS`, makes no HTTP call | PASS |
| `test_warns_for_api_key_not_from_address_when_both_missing` | Both env vars absent: only the first (`RESEND_API_KEY`) warning emitted (early return) | PASS |
| `test_only_non_200_results_included_in_email` | Only non-200 rows passed to `_build_email_html`; 200 rows filtered out | PASS |
| `test_subject_contains_website_and_count` | Subject contains website name and non-200 count | PASS |
| `test_post_to_resend_called_with_correct_credentials` | `_post_to_resend` receives `api_key` and `from_address` from env-var constants | PASS |
| `test_all_200_results_sends_email_with_zero_non_200_count` | All-200 results still send email; subject contains `"0"` | PASS |

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
| `tests/test_reporter.py` | `TestWriteMarkdownSummary` | 8 | PASS |
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
tests/test_checker_cli.py::TestBuildArgParser::test_notify_email_default_is_none PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_notify_email_stores_address PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_output_default_is_none PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_output_long_flag PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_output_short_flag PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_start_url_is_required PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_start_url_stored PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_timeout_default PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_timeout_is_int PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_timeout_long_flag PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_timeout_short_flag PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_user_agent_custom PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_user_agent_default PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_workers_default PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_workers_is_int PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_workers_long_flag PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_workers_short_flag PASSED
tests/test_emailer.py::TestBuildEmailRows::test_html_special_chars_are_escaped PASSED
tests/test_emailer.py::TestBuildEmailRows::test_multiple_rows_joined_by_newline PASSED
tests/test_emailer.py::TestBuildEmailRows::test_returns_empty_string_for_empty_list PASSED
tests/test_emailer.py::TestBuildEmailRows::test_single_row_contains_link_referrer_status PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_contains_non_200_count PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_contains_timestamp PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_contains_total_links_count PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_contains_website PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_no_table_when_no_non_200_results PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_table_contains_thead_and_tbody PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_table_present_when_non_200_results_exist PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_website_html_special_chars_escaped PASSED
tests/test_emailer.py::TestPostToResend::test_prints_notification_sent_on_200 PASSED
tests/test_emailer.py::TestPostToResend::test_request_is_post_method PASSED
tests/test_emailer.py::TestPostToResend::test_request_uses_bearer_auth_header PASSED
tests/test_emailer.py::TestPostToResend::test_warns_to_stderr_on_http_error PASSED
tests/test_emailer.py::TestPostToResend::test_warns_to_stderr_on_non_200_response PASSED
tests/test_emailer.py::TestPostToResend::test_warns_to_stderr_on_url_error PASSED
tests/test_emailer.py::TestSendEmailNotification::test_all_200_results_sends_email_with_zero_non_200_count PASSED
tests/test_emailer.py::TestSendEmailNotification::test_only_non_200_results_included_in_email PASSED
tests/test_emailer.py::TestSendEmailNotification::test_post_to_resend_called_with_correct_credentials PASSED
tests/test_emailer.py::TestSendEmailNotification::test_subject_contains_website_and_count PASSED
tests/test_emailer.py::TestSendEmailNotification::test_warns_and_returns_when_api_key_missing PASSED
tests/test_emailer.py::TestSendEmailNotification::test_warns_and_returns_when_from_address_missing PASSED
tests/test_emailer.py::TestSendEmailNotification::test_warns_for_api_key_not_from_address_when_both_missing PASSED
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

============================== 86 passed in 2.76s ==============================
```

---

### Test Summary

86 tests run across 7 files. 86 passed, 0 failed, 0 errors.
1 broken import fixed (`test_parser.py`: `parser` → `web_parser`).
17 new tests added in `TestBuildArgParser` for `argument_parser.build_arg_parser()`.
23 new tests added in `tests/test_emailer.py` covering `_build_email_rows`, `_build_email_html`, `_post_to_resend`, and `send_email_notification` (including both missing-env-var warning paths).

status: passed

## 2026-02-25 - Issue #10 follow-up: use the Resend Python SDK

### Environment

- Python: `/e/Applications/Scoop/apps/python/current/python.exe` (3.14.3)
- Command: `python -m pytest tests/ -v`
- Working directory: `E:/Git/GitHub/deadlinkchecker`
- Date: 2026-02-25

---

### Setup

- Installed `resend` package via `pip install resend` (version 2.23.0).

---

### Files Modified

- `tests/test_emailer.py` — rewrote `TestPostToResend` and updated `TestSendEmailNotification` to match the SDK-based implementation.

---

### Changes to `tests/test_emailer.py`

#### `TestPostToResend` → renamed `TestSendViaResend`

The class was renamed to match the renamed function `_send_via_resend`. All six urllib-based tests were replaced with four SDK-based tests. The old tests mocked `emailer.urllib.request.urlopen` and called `_post_to_resend` with five arguments (including `api_key`). The new tests mock `resend.Emails.send` and call `_send_via_resend` with four arguments (no `api_key`).

Tests removed (urllib concerns no longer applicable):
- `test_warns_to_stderr_on_non_200_response` — SDK abstracts HTTP status; not separately observable.
- `test_warns_to_stderr_on_http_error` — SDK-specific exception, not `urllib.error.HTTPError`.
- `test_warns_to_stderr_on_url_error` — SDK-specific exception, not `urllib.error.URLError`.
- `test_request_uses_bearer_auth_header` — SDK sets the Authorization header internally.
- `test_request_is_post_method` — SDK method selection is internal.

Tests added (SDK contract):

| Test | Description | Result |
|---|---|---|
| `test_prints_notification_sent_on_success` | `"Notification sent."` printed to stdout when SDK call succeeds | PASS |
| `test_warns_to_stderr_on_exception` | Any `Exception` from the SDK emits `"Warning"` and the message to stderr | PASS |
| `test_sdk_called_with_correct_params` | `resend.Emails.send` receives a dict with `from`, `to`, `subject`, and `html` keys matching the call arguments | PASS |
| `test_exception_does_not_propagate` | An `Exception` from the SDK is caught; the function returns normally (exits 0 guarantee) | PASS |

#### `TestSendEmailNotification` — updated

| Change | Old | New |
|---|---|---|
| "no SDK call made" assertion | `patch("emailer.urllib.request.urlopen")` + `assert_not_called()` | `patch("resend.Emails.send")` + `assert_not_called()` |
| delegate call mock | `patch("emailer._post_to_resend")` | `patch("emailer._send_via_resend")` |
| renamed test | `test_post_to_resend_called_with_correct_credentials` | `test_send_via_resend_called_with_correct_args` |
| removed assertion | checked `api_key` arg passed to `_post_to_resend` | removed — `api_key` no longer passed; set via `resend.api_key` |
| new test | — | `test_resend_api_key_set_before_send` — verifies `resend.api_key` is assigned the value of `_RESEND_API_KEY` before `_send_via_resend` is called |

| Test | Description | Result |
|---|---|---|
| `test_warns_and_returns_when_api_key_missing` | `_RESEND_API_KEY is None` → warning, no SDK call | PASS |
| `test_warns_and_returns_when_from_address_missing` | `_RESEND_FROM_ADDRESS is None` → warning, no SDK call | PASS |
| `test_warns_for_api_key_not_from_address_when_both_missing` | Both absent → only `RESEND_API_KEY` warning emitted (early return) | PASS |
| `test_only_non_200_results_included_in_email` | 200 rows filtered; only non-200 rows reach `_build_email_html` | PASS |
| `test_subject_contains_website_and_count` | Subject contains website and non-200 count | PASS |
| `test_send_via_resend_called_with_correct_args` | `_send_via_resend` receives correct `from_address` and `notify_email` | PASS |
| `test_resend_api_key_set_before_send` | `resend.api_key` equals `_RESEND_API_KEY` at the moment `_send_via_resend` is entered | PASS |
| `test_all_200_results_sends_email_with_zero_non_200_count` | All-200 input still sends; subject contains `"0"` | PASS |

---

### Pre-existing Tests (unchanged, all still pass)

| File | Test Class | Tests | Result |
|---|---|---|---|
| `tests/test_checker_cli.py` | `TestCheckerCLI` | 3 | PASS |
| `tests/test_checker_cli.py` | `TestCrawlerDiscoveredOutput` | 5 | PASS |
| `tests/test_checker_cli.py` | `TestCheckerCheckedOutput` | 5 | PASS |
| `tests/test_checker_cli.py` | `TestCheckerThreadSafety` | 1 | PASS |
| `tests/test_checker_cli.py` | `TestBuildArgParser` | 17 | PASS |
| `tests/test_emailer.py` | `TestBuildEmailRows` | 4 | PASS |
| `tests/test_emailer.py` | `TestBuildEmailHtml` | 8 | PASS |
| `tests/test_fetcher.py` | `TestCheckUrl` | 4 | PASS |
| `tests/test_normaliser.py` | `TestNormalise` | 8 | PASS |
| `tests/test_parser.py` | `TestExtractLinks` | 4 | PASS |
| `tests/test_reporter.py` | `TestWriteCsv` | 1 | PASS |
| `tests/test_reporter.py` | `TestWriteMarkdownSummary` | 8 | PASS |
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
tests/test_checker_cli.py::TestBuildArgParser::test_notify_email_default_is_none PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_notify_email_stores_address PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_output_default_is_none PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_output_long_flag PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_output_short_flag PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_start_url_is_required PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_start_url_stored PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_timeout_default PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_timeout_is_int PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_timeout_long_flag PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_timeout_short_flag PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_user_agent_custom PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_user_agent_default PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_workers_default PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_workers_is_int PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_workers_long_flag PASSED
tests/test_checker_cli.py::TestBuildArgParser::test_workers_short_flag PASSED
tests/test_emailer.py::TestBuildEmailRows::test_html_special_chars_are_escaped PASSED
tests/test_emailer.py::TestBuildEmailRows::test_multiple_rows_joined_by_newline PASSED
tests/test_emailer.py::TestBuildEmailRows::test_returns_empty_string_for_empty_list PASSED
tests/test_emailer.py::TestBuildEmailRows::test_single_row_contains_link_referrer_status PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_contains_non_200_count PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_contains_timestamp PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_contains_total_links_count PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_contains_website PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_no_table_when_no_non_200_results PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_table_contains_thead_and_tbody PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_table_present_when_non_200_results_exist PASSED
tests/test_emailer.py::TestBuildEmailHtml::test_website_html_special_chars_escaped PASSED
tests/test_emailer.py::TestSendViaResend::test_exception_does_not_propagate PASSED
tests/test_emailer.py::TestSendViaResend::test_prints_notification_sent_on_success PASSED
tests/test_emailer.py::TestSendViaResend::test_sdk_called_with_correct_params PASSED
tests/test_emailer.py::TestSendViaResend::test_warns_to_stderr_on_exception PASSED
tests/test_emailer.py::TestSendEmailNotification::test_all_200_results_sends_email_with_zero_non_200_count PASSED
tests/test_emailer.py::TestSendEmailNotification::test_only_non_200_results_included_in_email PASSED
tests/test_emailer.py::TestSendEmailNotification::test_resend_api_key_set_before_send PASSED
tests/test_emailer.py::TestSendEmailNotification::test_send_via_resend_called_with_correct_args PASSED
tests/test_emailer.py::TestSendEmailNotification::test_subject_contains_website_and_count PASSED
tests/test_emailer.py::TestSendEmailNotification::test_warns_and_returns_when_api_key_missing PASSED
tests/test_emailer.py::TestSendEmailNotification::test_warns_and_returns_when_from_address_missing PASSED
tests/test_emailer.py::TestSendEmailNotification::test_warns_for_api_key_not_from_address_when_both_missing PASSED
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

============================= 85 passed in 3.43s ==============================
```

---

### Test Summary

85 tests run across 7 files. 85 passed, 0 failed, 0 errors.
Net change from previous run: -1 test (6 urllib-based `TestPostToResend` tests removed, 4 SDK-based `TestSendViaResend` tests added; 1 new `test_resend_api_key_set_before_send` added to `TestSendEmailNotification`).

status: passed

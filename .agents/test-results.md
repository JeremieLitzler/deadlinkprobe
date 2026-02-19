# Test Results

## Environment

- Python: 3.14.3 (`/e/Applications/Scoop/apps/python/current/python.exe`)
- Runner: `python -m unittest discover -s tests -v`
- Test file: `tests/test_checker.py`
- Date: 2026-02-19

## Test Execution Output

```
test_retries_get_on_405 (test_checker.TestCheckUrl.test_retries_get_on_405) ... ok
test_returns_200_on_success (test_checker.TestCheckUrl.test_returns_200_on_success) ... ok
test_returns_301_on_redirect (test_checker.TestCheckUrl.test_returns_301_on_redirect) ... ok
test_returns_error_on_url_error (test_checker.TestCheckUrl.test_returns_error_on_url_error) ... ok
test_help_exits_zero (test_checker.TestCheckerCLI.test_help_exits_zero) ... ok
test_invalid_url_scheme_exits_nonzero (test_checker.TestCheckerCLI.test_invalid_url_scheme_exits_nonzero) ... ok
test_no_args_exits_nonzero (test_checker.TestCheckerCLI.test_no_args_exits_nonzero) ... ok
test_empty_html_returns_empty_list (test_checker.TestExtractLinks.test_empty_html_returns_empty_list) ... ok
test_ignores_non_anchor_tags (test_checker.TestExtractLinks.test_ignores_non_anchor_tags) ... ok
test_returns_hrefs_from_anchor_tags (test_checker.TestExtractLinks.test_returns_hrefs_from_anchor_tags) ... ok
test_skips_empty_href_values (test_checker.TestExtractLinks.test_skips_empty_href_values) ... ok
test_about_page_is_404 (test_checker.TestIntegration.test_about_page_is_404) ... ok
test_contains_200_status (test_checker.TestIntegration.test_contains_200_status) ... ok
test_contains_404_status (test_checker.TestIntegration.test_contains_404_status) ... ok
test_csv_has_correct_header (test_checker.TestIntegration.test_csv_has_correct_header) ... ok
test_exit_code_is_zero (test_checker.TestIntegration.test_exit_code_is_zero) ... ok
test_is_internal_different_host (test_checker.TestNormalise.test_is_internal_different_host) ... ok
test_is_internal_same_host (test_checker.TestNormalise.test_is_internal_same_host) ... ok
test_resolves_protocol_relative_href (test_checker.TestNormalise.test_resolves_protocol_relative_href) ... ok
test_resolves_relative_path_href (test_checker.TestNormalise.test_resolves_relative_path_href) ... ok
test_resolves_root_relative_href (test_checker.TestNormalise.test_resolves_root_relative_href) ... ok
test_returns_none_for_javascript (test_checker.TestNormalise.test_returns_none_for_javascript) ... ok
test_returns_none_for_mailto (test_checker.TestNormalise.test_returns_none_for_mailto) ... ok
test_strips_fragment_from_absolute_url (test_checker.TestNormalise.test_strips_fragment_from_absolute_url) ... ok
test_writes_header_and_rows (test_checker.TestWriteCsv.test_writes_header_and_rows) ... ok

----------------------------------------------------------------------
Ran 25 tests in 3.012s

OK
```

## Test Coverage by Module

### normaliser.py (8 tests — all passed)

| # | Test | Result |
|---|------|--------|
| 1 | `normalise` strips fragment from absolute URL | PASS |
| 2 | `normalise` resolves root-relative href against base | PASS |
| 3 | `normalise` resolves protocol-relative href inheriting scheme | PASS |
| 4 | `normalise` resolves relative path href against base | PASS |
| 5 | `normalise` returns None for mailto: scheme | PASS |
| 6 | `normalise` returns None for javascript: scheme | PASS |
| 7 | `is_internal` returns True for same scheme+host | PASS |
| 8 | `is_internal` returns False for different host | PASS |

### parser.py (4 tests — all passed)

| # | Test | Result |
|---|------|--------|
| 9  | `extract_links` returns href values from `<a>` tags | PASS |
| 10 | `extract_links` ignores tags other than `<a>` | PASS |
| 11 | `extract_links` returns empty list for empty HTML | PASS |
| 12 | `extract_links` skips empty href values | PASS |

### fetcher.py (4 tests — all passed, mocked)

| # | Test | Result |
|---|------|--------|
| 13 | `check_url` returns "200" on success | PASS |
| 14 | `check_url` returns "301" on redirect (no follow) | PASS |
| 15 | `check_url` returns "ERROR:URLError" on URLError | PASS |
| 16 | `check_url` retries with GET on 405 and returns result | PASS |

### reporter.py (1 test — passed)

| # | Test | Result |
|---|------|--------|
| 17 | `write_csv` writes correct header and rows to a temp file | PASS |

### checker.py CLI (3 tests — all passed)

| # | Test | Result |
|---|------|--------|
| 18 | Running with no args exits non-zero | PASS |
| 19 | Running `--help` exits 0 | PASS |
| 20 | Running with invalid URL scheme exits non-zero | PASS |

### Integration — live site (5 tests — all passed)

Site: `https://deadlinkchecker-sample-website.netlify.app`

| # | Test | Result |
|---|------|--------|
| 21a | Exit code is 0 | PASS |
| 21b | CSV header row is `link,referrer,http_status_code` | PASS |
| 21c | At least one row with status `404` | PASS |
| 21d | At least one row with status `200` | PASS |
| 21e | `/about/` appears with status `404` | PASS |

## Notes

- A `ResourceWarning` about implicit cleanup of `HTTPError 405` and a temp file appeared during the 405-retry mock test. These are Python 3.14 garbage-collection warnings and do not affect correctness; all assertions passed.
- Integration test completed in approximately 3 seconds total wall time.

### Test Summary

25 tests run, 25 passed, 0 failed, 0 errors.

status: passed

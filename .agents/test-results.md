# Test Results

## Environment

- Python: `/e/Applications/Scoop/apps/python/current/python.exe` (3.14.3)
- Command: `python -m unittest discover -s tests -v`
- Working directory: `E:/Git/GitHub/deadlinkchecker`
- Date: 2026-02-19

---

## Test Files Run

| File | Test Class | Tests | Result |
|---|---|---|---|
| `tests/test_normaliser.py` | `TestNormalise` | 8 | PASS |
| `tests/test_parser.py` | `TestExtractLinks` | 4 | PASS |
| `tests/test_fetcher.py` | `TestCheckUrl` | 4 | PASS |
| `tests/test_reporter.py` | `TestWriteCsv` | 1 | PASS |
| `tests/test_checker_cli.py` | `TestCheckerCLI` | 3 | PASS |
| `tests/test_integration.py` | `TestIntegration` | 5 | PASS |

---

## Full Output

```
test_help_exits_zero (test_checker_cli.TestCheckerCLI.test_help_exits_zero)
Running checker.py --help exits with code 0. ... ok
test_invalid_url_scheme_exits_nonzero (test_checker_cli.TestCheckerCLI.test_invalid_url_scheme_exits_nonzero)
Running checker.py with a non-http/https URL exits non-zero. ... ok
test_no_args_exits_nonzero (test_checker_cli.TestCheckerCLI.test_no_args_exits_nonzero)
Running checker.py with no arguments exits with a non-zero code. ... ok
test_retries_get_on_405 (test_fetcher.TestCheckUrl.test_retries_get_on_405)
check_url retries with GET when HEAD returns 405 and returns the GET result. ... ok
test_returns_200_on_success (test_fetcher.TestCheckUrl.test_returns_200_on_success)
check_url returns '200' when HEAD succeeds with status 200. ... ok
test_returns_301_on_redirect (test_fetcher.TestCheckUrl.test_returns_301_on_redirect)
check_url returns '301' when the no-redirect handler raises HTTPError. ... ok
test_returns_error_on_url_error (test_fetcher.TestCheckUrl.test_returns_error_on_url_error)
check_url returns 'ERROR:URLError' when a URLError is raised. ... ok
test_about_page_is_404 (test_integration.TestIntegration.test_about_page_is_404)
The /about/ page appears in results with status 404. ... ok
test_contains_200_status (test_integration.TestIntegration.test_contains_200_status)
At least one row has http_status_code of 200. ... ok
test_contains_404_status (test_integration.TestIntegration.test_contains_404_status)
At least one row has http_status_code of 404. ... ok
test_csv_has_correct_header (test_integration.TestIntegration.test_csv_has_correct_header)
The output CSV contains the expected header row. ... ok
test_exit_code_is_zero (test_integration.TestIntegration.test_exit_code_is_zero)
The checker exits with code 0 on a successful run. ... ok
test_is_internal_different_host (test_normaliser.TestNormalise.test_is_internal_different_host)
is_internal returns False for a different host. ... ok
test_is_internal_same_host (test_normaliser.TestNormalise.test_is_internal_same_host)
is_internal returns True for same scheme and host. ... ok
test_resolves_protocol_relative_href (test_normaliser.TestNormalise.test_resolves_protocol_relative_href)
Protocol-relative href inherits the scheme from base. ... ok
test_resolves_relative_path_href (test_normaliser.TestNormalise.test_resolves_relative_path_href)
Relative path href is resolved against the full base URL. ... ok
test_resolves_root_relative_href (test_normaliser.TestNormalise.test_resolves_root_relative_href)
Root-relative href is resolved against the base host. ... ok
test_returns_none_for_javascript (test_normaliser.TestNormalise.test_returns_none_for_javascript)
javascript: scheme returns None. ... ok
test_returns_none_for_mailto (test_normaliser.TestNormalise.test_returns_none_for_mailto)
mailto: scheme returns None. ... ok
test_strips_fragment_from_absolute_url (test_normaliser.TestNormalise.test_strips_fragment_from_absolute_url)
Fragment portion is removed from an already-absolute URL. ... ok
test_empty_html_returns_empty_list (test_parser.TestExtractLinks.test_empty_html_returns_empty_list)
Empty string input yields an empty list. ... ok
test_ignores_non_anchor_tags (test_parser.TestExtractLinks.test_ignores_non_anchor_tags)
href values on non-<a> tags are not returned. ... ok
test_returns_hrefs_from_anchor_tags (test_parser.TestExtractLinks.test_returns_hrefs_from_anchor_tags)
href values from <a> tags are returned. ... ok
test_skips_empty_href_values (test_parser.TestExtractLinks.test_skips_empty_href_values)
An <a> tag with an empty href is not included in the output. ... ok
test_writes_header_and_rows (test_reporter.TestWriteCsv.test_writes_header_and_rows)
write_csv produces the correct header and data rows in a temp file. ... ok

----------------------------------------------------------------------
Ran 25 tests in 1.626s

OK
```

---

## Notes

- Two `ResourceWarning` messages appeared during `test_retries_get_on_405` and the integration `setUpClass`, both from Python's `tempfile` module performing implicit cleanup. These are cosmetic warnings from Python 3.14's garbage-collection and do not affect correctness — all assertions passed.
- The integration test made live network requests to `https://deadlinkchecker-sample-website.netlify.app` and validated real HTTP responses, including the expected `404` on `/about/`.

---

### Test Summary

25 tests run across 6 files. 25 passed, 0 failed, 0 errors.

status: passed

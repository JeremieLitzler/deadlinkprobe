# Test Results — Issue #39: Add filter to keep status code in report

## Tests Run

### New test file: `tests/test_status_filter.py`
- `TestIs3xx` (8 tests) — boundary conditions for `_is_3xx()`
- `TestStatusFilterMatches` (8 tests) — `StatusFilter.matches()` with various code/filter combinations
- `TestStatusFilterExcludedSummary` (6 tests) — `StatusFilter.excluded_summary()` counting
- `TestBuildFilter` (6 tests) — `build_filter()` factory

### Updated: `tests/test_issue_35_include_3xx.py`
Rewrote `_call_send` helper to use new `StatusFilter` + `send_email_notification` API. Added new test class.
- `TestDefaultFilterExcludes3xx` (6 tests) — default filter (404,500) excludes 3xx and 200
- `TestInclude3xxCompatIncludes3xx` (5 tests) — include_3xx_compat=True passes 3xx through
- `TestOnly3xxResultsDefaultFilter` (3 tests) — all-3xx results produce empty filtered output
- `TestErrorRowsAlwaysIncluded` (4 tests) — ERROR:* rows bypass filter
- `TestSubjectCountMatchesRowCount` (4 tests) — subject count equals rendered row count
- `TestAll200Results` (4 tests) — all-200 scan filtered out; excluded_summary populated
- `TestIs3xx` (16 tests) — unchanged boundary tests for `emailer._is_3xx()`
- `TestArgumentParserInclude3xxFlag` (6 tests) — deprecated flag parsing + help text
- `TestBuildFilterDeprecation` (7 tests) — deprecation warning, backward compat, new flag wins

### Updated: `tests/test_emailer.py`
- `TestBuildEmailHtml` (8 tests) — updated `_build` helper to accept `excluded_summary`
- `TestSendEmailNotification` (8 tests) — updated `_call_with_env` for new signature; updated subject assertions

### Updated: `tests/test_reporter.py`
- Renamed 2 tests to document new "write all received rows" contract

### Updated: `tests/test_argument_parser.py`
- Added 5 tests for `--keep-status-codes` parameter

### Updated: `tests/test_integration.py`
- Updated `test_contains_200_status` → `test_200_status_excluded_by_default_filter`
- Added `TestIntegrationNoFilter` class with `--keep-status-codes ""` verifying 200 appears

### Bug found and fixed during testing
`checker._build_filter` used `args.keep_status_codes or "404,500"` which coerces an explicit `""` to the default. Fixed to `args.keep_status_codes if args.keep_status_codes is not None else "404,500"`.

## Results

```
Ran 175 tests in 8.059s

OK
```

All 175 tests passed. No failures, no errors.

### Test Summary

175 tests run across 10 test files. All passed. The new `--keep-status-codes` parameter, the `StatusFilter` domain type, the excluded-codes email summary, and the deprecated flag backward-compat behavior are all covered.

status: passed

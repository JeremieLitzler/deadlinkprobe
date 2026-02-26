# Test Results — Issue #35: Add option to exclude 3xx from email notifications

## Pre-existing test suite

Ran before any new tests to establish baseline.

- Suite: `tests/` (all files)
- Runner: `python -m pytest tests/ -v`
- Result: **85 passed, 0 failed**

## New test file

`tests/test_issue_35_include_3xx.py`

46 new tests across 8 test classes.

## Test cases and results

### TestDefaultExcludes3xx — flag absent, 3xx excluded from email

| Test | Result |
|---|---|
| `test_3xx_rows_absent_from_non_200_results` | PASSED |
| `test_404_and_500_rows_present` | PASSED |
| `test_200_row_absent` | PASSED |
| `test_subject_count_excludes_3xx` | PASSED |
| `test_subject_count_matches_row_count` | PASSED |

Verified: with `include_3xx=False` (default), 301 and 302 rows are absent from `non_200_results`; 404, 500, and ERROR rows remain; subject count is 3 (404 + 500 + ERROR).

### TestFlagPresentIncludes3xx — flag present, 3xx included

| Test | Result |
|---|---|
| `test_3xx_rows_present_in_non_200_results` | PASSED |
| `test_404_500_and_error_rows_present` | PASSED |
| `test_200_row_still_absent` | PASSED |
| `test_subject_count_includes_3xx` | PASSED |
| `test_subject_count_matches_row_count` | PASSED |

Verified: with `include_3xx=True`, 301 and 302 appear in `non_200_results`; count in subject is 5 (301 + 302 + 404 + 500 + ERROR); 200 never appears.

### TestOnly3xxResultsFlagAbsent — only 3xx non-200s exist, flag absent

| Test | Result |
|---|---|
| `test_non_200_results_is_empty` | PASSED |
| `test_subject_count_is_zero` | PASSED |
| `test_subject_count_matches_row_count` | PASSED |

Verified: when all non-200 rows are 3xx and flag is absent, `non_200_results` is empty and subject shows `0 non-200 result(s)`.

### TestErrorRowsAlwaysIncluded — ERROR:* strings always present

| Test | Result |
|---|---|
| `test_error_rows_present_flag_absent` | PASSED |
| `test_error_rows_present_flag_present` | PASSED |
| `test_3xx_excluded_but_errors_included_flag_absent` | PASSED |
| `test_only_error_results_flag_absent` | PASSED |

Verified: `ERROR:ConnectionError` and `ERROR:Timeout` appear in `non_200_results` regardless of `include_3xx`; 301 is correctly excluded while errors remain when flag is absent.

### TestSubjectCountMatchesRowCount — subject count always equals row count

| Test | Result |
|---|---|
| `test_flag_absent_mixed_results` | PASSED (count=3) |
| `test_flag_present_mixed_results` | PASSED (count=5) |
| `test_flag_absent_all_3xx` | PASSED (count=0) |
| `test_flag_present_one_3xx` | PASSED (count=1) |

Verified: subject count string matches `len(non_200_results)` in all four combinations tested.

### TestAll200Results — all-200 scan, both flag states

| Test | Result |
|---|---|
| `test_empty_table_flag_absent` | PASSED |
| `test_empty_table_flag_present` | PASSED |
| `test_subject_count_zero_flag_absent` | PASSED |
| `test_subject_count_zero_flag_present` | PASSED |

Verified: all-200 results yield empty `non_200_results` and `0 non-200 result(s)` in subject under both flag states.

### TestIs3xx — _is_3xx helper boundary conditions

| Test | Result |
|---|---|
| `test_300_is_3xx` | PASSED |
| `test_301_is_3xx` | PASSED |
| `test_302_is_3xx` | PASSED |
| `test_307_is_3xx` | PASSED |
| `test_308_is_3xx` | PASSED |
| `test_399_is_3xx` | PASSED |
| `test_200_is_not_3xx` | PASSED |
| `test_400_is_not_3xx` | PASSED |
| `test_404_is_not_3xx` | PASSED |
| `test_500_is_not_3xx` | PASSED |
| `test_error_string_is_not_3xx` | PASSED |
| `test_error_timeout_is_not_3xx` | PASSED |
| `test_short_string_is_not_3xx` | PASSED |
| `test_long_string_is_not_3xx` | PASSED |
| `test_non_digit_3xx_like_is_not_3xx` | PASSED |
| `test_empty_string_is_not_3xx` | PASSED |

Verified: guard conditions (len==3, startswith("3"), isdigit()) correctly classify all boundary inputs. `ERROR:*` strings are correctly identified as non-3xx.

### TestArgumentParserInclude3xxFlag — CLI flag registration

| Test | Result |
|---|---|
| `test_include_3xx_status_code_default_is_false` | PASSED |
| `test_include_3xx_status_code_flag_sets_true` | PASSED |
| `test_include_3xx_status_code_is_bool` | PASSED |
| `test_include_3xx_flag_independent_of_notify_email` | PASSED |
| `test_include_3xx_false_when_notify_email_also_absent` | PASSED |

Verified: flag defaults to `False`; providing `--include-3xx-status-code` sets it to `True`; it is a `bool`; it is independent of `--notify-email`.

## Full suite after new tests

- Total: **131 passed, 0 failed**
- No regressions introduced.

## Observations

The implementation in `src/emailer.py`, `src/argument_parser.py`, and `src/checker.py` conforms exactly to the technical specification:

- `_is_3xx()` helper correctly identifies 3xx HTTP status strings and rejects `ERROR:*` and non-numeric patterns.
- Filter expression `row[2] != "200" and (include_3xx or not _is_3xx(row[2]))` correctly includes/excludes 3xx rows based on the flag.
- `non_200_count = len(non_200_results)` is derived from the already-filtered list, guaranteeing subject count always matches rendered row count.
- `include_3xx` parameter has `default=False`, preserving backward compatibility for existing callers that omit it.
- `argument_parser.py` registers `--include-3xx-status-code` as `store_true` with `default=False`; argparse converts the dashed name to `include_3xx_status_code` automatically; `checker.py` passes `args.include_3xx_status_code` to `emailer.send_email_notification`.
- CSV output is untouched; only email content is affected.

status: passed

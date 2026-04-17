# Business Specifications — Issue #39: Add filter to keep status code in report

## Goal and Scope

Introduce a new CLI parameter that controls which HTTP status codes appear in both the CSV output and the email notification. The parameter replaces the narrow `--include-3xx-status-code` flag with a general-purpose filter. The existing flag is deprecated and will emit a warning when used, pointing users to the new parameter.

## New Parameter

A new optional CLI parameter accepts a comma-separated list of HTTP status code strings (e.g. `404,500`). The default value is `404,500`.

Name: `--keep-status-codes`

## Observable Behaviours

### CSV Output

- Only rows whose `http_status_code` value exactly matches one of the codes in the filter are written to the CSV file.
- Rows with status `200` are excluded by default (since `200` is not in the default filter).
- Rows with status codes not in the filter list are silently omitted from the CSV.
- Rows whose status is an `ERROR:*` value are always included regardless of the filter (error rows are never suppressed).
- If the filter list is empty, all rows are written (no filtering applied).

### Markdown Summary (README.md, scan-folder mode)

- Same filtering rules as CSV apply: only rows matching the filter appear in the table.
- `ERROR:*` rows are always included.

### Email Notification

- The details table in the email body shows only rows whose status code matches the filter (same rules as CSV).
- `ERROR:*` rows are always included in the details table.
- The email body includes a count summary section listing each status code that was excluded from the filter, with its occurrence count, so users retain visibility into the full picture.
- The subject line count reflects only the rows shown in the table (filtered count).

### Deprecation of `--include-3xx-status-code`

- The flag remains accepted by the CLI but is marked as deprecated in the help text.
- When supplied, the tool prints a deprecation warning to stderr: `Warning: --include-3xx-status-code is deprecated; use --keep-status-codes instead.`
- The flag has no effect on output when `--keep-status-codes` is also supplied.
- When `--include-3xx-status-code` is supplied alone (without `--keep-status-codes`), the tool behaves as if `--keep-status-codes 3xx,404,500` was passed — i.e. the effective filter includes all 3xx codes alongside the defaults. This preserves backward-compatible output for users who have not yet migrated.

## Files to Create or Modify

| File | Role |
|---|---|
| `src/argument_parser.py` | Add `--keep-status-codes` parameter; mark `--include-3xx-status-code` as deprecated in help text |
| `src/checker.py` | Parse the new parameter; apply backward-compat logic for deprecated flag; pass filter down to reporter and emailer |
| `src/reporter.py` | Apply status-code filter when writing CSV rows and Markdown table rows; always pass through `ERROR:*` rows |
| `src/emailer.py` | Apply filter to the details table; add excluded-codes count summary section to email body; always pass through `ERROR:*` rows |
| `tests/test_argument_parser.py` | Cover new parameter defaults, custom values, and deprecated flag |
| `tests/test_reporter.py` | Cover filtered and unfiltered CSV/Markdown output including `ERROR:*` pass-through |
| `tests/test_emailer.py` | Cover filtered email table and excluded-codes summary section |
| `tests/test_checker_cli.py` | Cover end-to-end CLI invocation with default and custom filter values |
| `tests/test_issue_35_include_3xx.py` | Update or extend to verify deprecated-flag warning and backward-compat behaviour |

## Edge Cases

- A user passes `--keep-status-codes ""` (empty string): all rows are written (no filter).
- A user passes a code that matches no results (e.g. `--keep-status-codes 418`): CSV is written with zero data rows (only header).
- A user passes `--keep-status-codes 200`: 200 rows appear in the CSV; all other codes are excluded.
- A user passes both `--keep-status-codes 404` and `--include-3xx-status-code`: the new flag wins; deprecated flag is ignored (warning emitted).
- A scan with only `ERROR:*` results and a filter of `404,500`: all `ERROR:*` rows still appear in the CSV and email.
- The excluded-codes count summary in the email is omitted entirely when there are no excluded codes (i.e. the filter matches all results).

## Concurrency and Performance

- Filtering is applied after all link checks complete and results are fully assembled, maintaining the existing guarantee that results are written only after all checks complete.
- No change to parallel check behaviour.

status: ready

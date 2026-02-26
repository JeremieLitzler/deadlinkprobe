# Business Specification — Issue #35: Add option to include 3xx results in email notifications

## Context

The email notification currently reports all non-200 HTTP results. 3xx (redirect) status codes are included in that set. Users who consider redirects acceptable want to suppress them from email notifications without losing them in the CSV report.

## Scope

This change affects email notification content only. CSV output and console output are unchanged.

## Rules and Examples

### Rule 1: Default behaviour excludes 3xx results from email

When `--notify-email` is provided and `--include-3xx-status-code` is absent, the email table lists only results whose status code is not 200 and not in the 3xx range (300–399).

Example — scan returns 200, 301, 302, 404, 500, other errors; flag absent:

- Email table contains: 404, 500 and Error (no HTTP Status code) rows only.
- Email subject line "non-200 result(s)" count reflects only the rows shown (2 in this example).
- CSV contains all six rows.

Example — scan returns 200, 301, 302 only; flag absent:

- No non-200-non-3xx results exist.
- Email table is empty (no rows rendered).
- Subject line shows 0 non-200 result(s).
- Email is still sent (not suppressed entirely).
- CSV contains all three rows.

### Rule 2: `--include-3xx-status-code` flag causes 3xx results to appear in email

When `--notify-email` is provided and `--include-3xx-status-code` is present, the email table lists all results whose status code is not 200, including 3xx codes.

Example — scan returns 200, 301, 302, 404, 500; flag present:

- Email table contains: 301, 302, 404, 500 rows.
- Subject line "non-200 result(s)" count is 4.
- CSV contains all five rows.

Example — scan returns 200 and 301 only; flag present:

- Email table contains: 301 row only.
- Subject line count is 1.
- CSV contains both rows.

### Rule 3: `--include-3xx-status-code` has no effect when `--notify-email` is absent

When `--notify-email` is not provided, no email is sent regardless of `--include-3xx-status-code`. The flag is silently ignored.

Example — `--include-3xx-status-code` passed without `--notify-email`:

- No email is attempted.
- CSV output is unchanged.

### Rule 4: `--include-3xx-status-code` has no effect on CSV output

The CSV always contains every discovered link with its status, regardless of `--include-3xx-status-code`.

Example — scan returns 200, 301, 404; flag present:

- CSV rows: 200, 301, 404.

Example — scan returns 200, 301, 404; flag absent:

- CSV rows: 200, 301, 404.

### Rule 5: All-200 scan with flag present or absent

When every checked link returns 200, the email table is empty under both flag states.

Example — scan returns 200 only; flag present:

- Email table is empty.
- Subject line shows 0 non-200 result(s).

Example — scan returns 200 only; flag absent:

- Email table is empty.
- Subject line shows 0 non-200 result(s).

## New CLI Flag

| Property | Value                                                  |
| -------- | ------------------------------------------------------ |
| Name     | `--include-3xx-status-code`                            |
| Type     | Boolean flag (store_true)                              |
| Default  | absent (false)                                         |
| Scope    | Email content only                                     |
| Requires | Has no effect unless `--notify-email` is also provided |

## Email Subject Line

The "non-200 result(s)" count in the subject line must match the number of rows rendered in the email table, not the total number of non-200 results in the scan. When `--include-3xx-status-code` is absent, 3xx results are excluded from both the count and the table.

## Out of Scope

- The flag does not affect which links are crawled or checked.
- The flag does not affect the CSV output.
- The flag does not affect the Markdown summary written to disk.
- No new environment variables are introduced.

status: ready

# Technical Specification — Issue #35: Add option to include 3xx results in email notifications

## Files changed

| File | Change |
|------|--------|
| `src/argument_parser.py` | Added `--include-3xx-status-code` boolean flag (`store_true`) |
| `src/checker.py` | Passed `args.include_3xx_status_code` to `emailer.send_email_notification` |
| `src/emailer.py` | Added `_is_3xx()` helper and `include_3xx` parameter to `send_email_notification`; filter logic applied before building email |

## Implementation details

### `src/argument_parser.py`

Added after `--notify-email`:

```python
parser.add_argument(
    "--include-3xx-status-code",
    action="store_true",
    default=False,
    help=(
        "Include 3xx redirect results in the email notification table. "
        "By default, 3xx results are excluded from the email (but still appear in the CSV). "
        "Has no effect when --notify-email is absent."
    ),
)
```

argparse converts `--include-3xx-status-code` to `args.include_3xx_status_code` automatically.

### `src/checker.py`

`_maybe_send_notification` now passes the flag value:

```python
emailer.send_email_notification(
    results,
    website,
    scan_timestamp,
    len(results),
    args.notify_email,
    args.include_3xx_status_code,
)
```

No other changes in `checker.py`. CSV writing is untouched.

### `src/emailer.py`

Added private helper above `send_email_notification`:

```python
def _is_3xx(status: str) -> bool:
    return len(status) == 3 and status.startswith("3") and status.isdigit()
```

`send_email_notification` gains one new parameter with a safe default:

```python
def send_email_notification(
    results: list[tuple[str, str, str]],
    website: str,
    timestamp: str,
    total_links: int,
    notify_email: str,
    include_3xx: bool = False,
) -> None:
```

Filter applied before building the email (replaces the old one-liner):

```python
non_200_results = [
    row for row in results
    if row[2] != "200" and (include_3xx or not _is_3xx(row[2]))
]
```

- When `include_3xx=False` (default): rows where `_is_3xx(status)` is True are excluded.
- When `include_3xx=True`: all non-200 rows are included, 3xx among them.
- `non_200_count = len(non_200_results)` is derived from the filtered list, so the subject-line count always matches the rendered row count.

## Invariants preserved

- `reporter.py` is unchanged — CSV always contains every result.
- `reporter.write_markdown_summary` is unchanged.
- The `default=False` on `include_3xx` means existing call sites (e.g. tests) that omit the parameter continue to work without modification.
- The `_is_3xx` guard (`len == 3`, `startswith("3")`, `isdigit()`) correctly handles `ERROR:*` statuses, which are neither 200 nor 3xx and are always included in the email.

status: ready

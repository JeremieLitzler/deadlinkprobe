# Technical Specifications — Issue #39: Add filter to keep status code in report

## Files Changed

| File | Change |
|---|---|
| `src/status_filter.py` | **New.** `StatusFilter` class with `matches()` and `excluded_summary()` methods. `build_filter()` factory. `_is_3xx()` helper. |
| `src/argument_parser.py` | Added `--keep-status-codes` (default `None`). Updated `--include-3xx-status-code` help text to mark it deprecated. |
| `src/checker.py` | Added `_build_filter()` to construct a `StatusFilter` from CLI args (with deprecation warning + backward-compat logic). Updated `main()` to apply filter after results are collected, passing pre-filtered rows to reporter and emailer. Updated `_maybe_send_notification()` signature to accept `excluded_summary` and `total_links`. |
| `src/reporter.py` | Removed internal `non_200` filter from `write_markdown_summary()`. Function now writes all received rows (caller is responsible for filtering). |
| `src/emailer.py` | Replaced `include_3xx` parameter with `excluded_summary: dict`. Added `_build_excluded_summary_html()` and `_build_email_summary_lines()` helpers. Added `_build_table_html()` extractor. Updated `_build_email_html()` to include excluded-codes section. Updated `send_email_notification()` to accept pre-filtered results and excluded summary. Subject line now reads "X result(s) matching filter". |

## Technical Decisions

**New `status_filter` module:** The filter logic is shared by `checker.py`, and its output feeds both `reporter.py` and `emailer.py`. Placing it in its own module avoids coupling the two output modules to each other and keeps `checker.py` as the only consumer of the filter DSL.

**Filtering in `checker.py`, not in reporter/emailer:** All filtering happens once in `checker.py` after results are assembled. Reporter and emailer receive already-filtered lists. This avoids duplicating filter logic across two modules and keeps output functions focused on formatting, not policy.

**`--keep-status-codes` default is `None` in argparse:** Allows `checker.py` to distinguish "user explicitly passed a value" from "user omitted the flag". This is required for the backward-compat logic: when `--include-3xx-status-code` is set without `--keep-status-codes`, the effective filter expands to include 3xx codes.

**`_is_3xx` kept in `emailer.py` as well:** The function is still present in `emailer.py` to avoid breaking existing tests that import it directly from there. The canonical implementation lives in `status_filter.py`.

**OC exceptions documented:**
- `main()` in `checker.py` exceeds 5 lines; it is the CLI entry point and extracting further would obscure the top-level flow.
- `write_csv` and `write_markdown_summary` in `reporter.py` use `with` blocks that inherently add indentation; no deeper nesting is introduced.

status: ready

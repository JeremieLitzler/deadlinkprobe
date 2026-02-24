# Code Ready

## CR-2: Split tests/test_checker.py into per-module test files

- Created `tests/test_normaliser.py` — contains `TestNormalise`
- Created `tests/test_parser.py` — contains `TestExtractLinks`
- Created `tests/test_fetcher.py` — contains `TestCheckUrl`
- Created `tests/test_reporter.py` — contains `TestWriteCsv`
- Created `tests/test_checker_cli.py` — contains `TestCheckerCLI`
- Created `tests/test_integration.py` — contains `TestIntegration`
- Deleted `tests/test_checker.py`

## CR-3: Add terminal feedback during execution

- Modified `crawler.py` — added `print(f"DISCOVERED {url}")` immediately after each URL is appended to `results` (start URL and all subsequently discovered URLs).
- Modified `checker.py` — imported `threading`, created `print_lock = threading.Lock()` in `main()`, and added a lock-guarded `print(f"CHECKED {link} {status}")` after each future completes in the `as_completed` loop.

## 2026-02-24 - Issue #8: Add a summary for each website scanned

- Modified `src/reporter.py` — added `write_markdown_summary(results, output_path, timestamp)` that writes a Markdown table of non-200 results (heading + table always present; data rows only for non-200 entries).
- Modified `src/checker.py` — added `datetime` and `os` imports; changed `--output` default from `"results.csv"` to `None`; captures `scan_timestamp` at start of `main()` using UTC; when `--output` is omitted builds `scans/[netloc]/[timestamp]/` with `os.makedirs`, writes `results.csv` and `README.md` inside it; when `--output` is provided uses legacy flat-file mode with no README.md; final print uses `csv_path`.

status: ready

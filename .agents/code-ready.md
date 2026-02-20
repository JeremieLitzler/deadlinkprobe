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

status: ready

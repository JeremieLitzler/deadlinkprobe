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

## 2026-02-24 - Issue #14: Add a CI step to run tests on PRs

- Created `.github/workflows/ci.yml` — GitHub Actions workflow that runs `python -m pytest tests/ -v` on every pull request targeting any branch, using `ubuntu-latest` and Python `3.10`.

## 2026-02-24 - Bug #16: Workflow link checker cannot push scans folder

- Modified `.github/workflows/deadlinkprobe.yml` — replaced bare checkout with a `data/scans`-branch checkout (`ref: data/scans`, `fetch-depth: 0`), added an "Ensure data/scans branch exists" step that creates the branch locally if the remote does not yet have it, and changed `git push` to `git push origin data/scans` so scan results are committed to the `data/scans` branch instead of `main`, bypassing the `protect-main` ruleset.

## 2026-02-24 - Issue #18: Agentic Workflow updates

- Modified `.agents-brain/agent-1-specs.md` — removed the "Key functions/types/interfaces with their signatures" bullet and replaced it with guidance directing the specs agent to describe WHAT the system does (goals, rules, observable outcomes) and explicitly prohibiting implementation-level content (function signatures, pseudocode, variable names, code snippets, import lists).
- Modified `.agents-brain/agent-2-coder.md` — added a "Technical Choice Explanations" section requiring the coder agent to document the reason behind each non-trivial implementation decision in `code-ready.md`; added an "Object Calisthenics" section enumerating all nine rules inline with two concrete before/after examples (the no-else rule and the one-level-of-indentation rule).

### Technical choices

The nine Object Calisthenics rules were enumerated directly inside the agent prompt rather than referenced by URL so the agent can apply them without fetching external content. Two code examples were embedded inline to give the agent concrete patterns to follow, as abstract rules alone are insufficient guidance for consistent application. The "no-else" and "one-level-of-indentation" rules were chosen for illustration because they are the most frequently violated and their before/after contrast is immediately legible.

The `agent-1-specs.md` change uses an explicit prohibition list (function signatures, pseudocode, variable names, code snippets, import lists) rather than a general statement like "avoid implementation details", because general statements have proven insufficient — the current specs already demonstrate that the agent defaults to including those artefacts when not explicitly forbidden.

## 2026-02-24 - Issue #10: Send email notification when a scan contains non HTTP/200 status

- Created `src/emailer.py` — contains `_build_email_rows`, `_build_email_html`, `_post_to_resend`, and `send_email_notification`. All email logic lives here.
- Modified `src/reporter.py` — removed all email functions and their imports (`html`, `json`, `urllib.error`, `urllib.request`); now only handles CSV and Markdown output.
- Modified `src/checker.py` — added `--notify-email` CLI argument; extracted argparse setup into `build_arg_parser()`; extracted env-var reading and `send_email_notification` call into `_maybe_send_notification()`; `main()` delegates to both helpers.
- Created `tests/test_emailer.py` — covers `_build_email_rows`, `_build_email_html`, `_post_to_resend`, and `send_email_notification`.
- Modified `tests/test_checker_cli.py` — added `TestBuildArgParser` covering all flags and defaults.

### Technical choices

Email construction is split across three private helpers to keep each function at one level of indentation (Object Calisthenics rule 1). `_build_email_rows` isolates the per-row HTML generation; `_build_email_html` assembles the full body; `_post_to_resend` handles the HTTP call and all error branches. `send_email_notification` is the single public entry point that coordinates them.

Email logic was moved to `emailer.py` to isolate the Resend API concern from CSV/Markdown output in `reporter.py` and from CLI orchestration in `checker.py`. This lets each module be tested independently without the other's concerns leaking in.

`build_arg_parser()` is extracted from `main()` so tests can instantiate the parser directly and call `parse_args()` with controlled input, without spawning a subprocess or mocking `sys.argv` for every case.

`_maybe_send_notification()` is extracted from `main()` so the env-var validation and dispatch logic can be unit-tested without running the full crawl and check pipeline.

`urllib.error.HTTPError` is caught separately from `urllib.error.URLError` because Resend returns structured HTTP errors (with a `.code`) that the spec requires to be reported by status code. `URLError` covers lower-level failures (DNS, timeout) whose `.reason` is more informative than a status code.

`html.escape` is applied to all user-supplied values in the HTML body to prevent injection from malformed URLs in scan results.

The `elif` pattern in `_maybe_send_notification()` for env-var validation is intentional: distinct warning messages per missing variable, and two sequential `if` checks would incorrectly warn twice when both are absent.

## 2026-02-25 - Issue #10 follow-up: use the Resend Python SDK

- Modified `src/emailer.py` — replaced urllib-based transport with the `resend` SDK: removed `_RESEND_API_URL`, `json`, `urllib.error`, `urllib.request`; added `import resend`; renamed `_post_to_resend` to `_send_via_resend`; sets `resend.api_key` inside `send_email_notification` before dispatching; uses `resend.Emails.SendParams` typed dict and `resend.Emails.send(params)`; catches broad `Exception` and prints to stderr so the tool always exits 0.
- Created `requirements.txt` — single line `resend`; declares the only third-party dependency so `pip install -r requirements.txt` is sufficient before running the tool.

### Technical choices

`resend.api_key` is assigned inside `send_email_notification` (after the env-var guard clauses) rather than at module level so the module can be imported and tested without a valid key present in the environment; the assignment only runs on the hot path where the key has already been validated as non-None.

`_post_to_resend` was renamed to `_send_via_resend` to reflect that the transport is now the SDK rather than a raw HTTP POST; the public interface of `send_email_notification` is unchanged.

`Exception` is caught broadly because the Resend SDK may raise SDK-specific exception types that vary across SDK versions. Catching `Exception` ensures the tool exits 0 regardless of SDK version or failure mode, which the spec requires.

status: ready

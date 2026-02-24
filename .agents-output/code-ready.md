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

- Modified `.github/workflows/deadlinkchecker.yml` — replaced bare checkout with a `data/scans`-branch checkout (`ref: data/scans`, `fetch-depth: 0`), added an "Ensure data/scans branch exists" step that creates the branch locally if the remote does not yet have it, and changed `git push` to `git push origin data/scans` so scan results are committed to the `data/scans` branch instead of `main`, bypassing the `protect-main` ruleset.

## 2026-02-24 - Issue #18: Agentic Workflow updates

- Modified `.agents-brain/agent-1-specs.md` — removed the "Key functions/types/interfaces with their signatures" bullet and replaced it with guidance directing the specs agent to describe WHAT the system does (goals, rules, observable outcomes) and explicitly prohibiting implementation-level content (function signatures, pseudocode, variable names, code snippets, import lists).
- Modified `.agents-brain/agent-2-coder.md` — added a "Technical Choice Explanations" section requiring the coder agent to document the reason behind each non-trivial implementation decision in `code-ready.md`; added an "Object Calisthenics" section enumerating all nine rules inline with two concrete before/after examples (the no-else rule and the one-level-of-indentation rule).

### Technical choices

The nine Object Calisthenics rules were enumerated directly inside the agent prompt rather than referenced by URL so the agent can apply them without fetching external content. Two code examples were embedded inline to give the agent concrete patterns to follow, as abstract rules alone are insufficient guidance for consistent application. The "no-else" and "one-level-of-indentation" rules were chosen for illustration because they are the most frequently violated and their before/after contrast is immediately legible.

The `agent-1-specs.md` change uses an explicit prohibition list (function signatures, pseudocode, variable names, code snippets, import lists) rather than a general statement like "avoid implementation details", because general statements have proven insufficient — the current specs already demonstrate that the agent defaults to including those artefacts when not explicitly forbidden.

status: ready

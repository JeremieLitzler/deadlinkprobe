## 2026-02-19

Build the dead link checker CLI tool in **Python** as described in CLAUDE.md and README.md.

Given a starting URL:

1. Crawl all internal links recursively until all are discovered.
2. Collect external links but do not recurse into them.
3. Check all discovered links for their HTTP status code.
4. Output results as CSV: `link, referrer, http_status_code`.
5. Use parallel requests for performance.

Language: Python 3. Prefer stdlib only (urllib, concurrent.futures, html.parser). Third-party libraries only if strictly necessary.

## 2026-02-19 — Change request

- Split test file into several file, one per code file and one for the integration tests.

## 2026-02-20 — Feature request

Add terminal feedback during execution:

- Each time a URL is **discovered** (found by the crawler): print the URL.
- Each time a URL is **checked** (HTTP status resolved): print the URL and its status code or ERROR string.

## 2026-02-24 — Issue #8: Add a summary for each website scanned

After running a scan, produce a Markdown file per website containing:

- A level-2 heading with the timestamp of the scan
- A table showing URL, referrer, and HTTP status code — but **only for non-200 responses**

Also, scans must be stored in the folder `scans/[WEBSITE]` and should contains a sub folder per scan with a file `README.md` with the summary and `results.csv` for the scan's result.

## 2026-02-24 — Issue #14: Add a CI step to run tests on PRs

Add a GitHub Actions workflow that automatically runs the test suite when a pull request is created or updated against any branch.

## 2026-02-24 — Bug #16: Workflow link checker cannot push scans folder

A `protect-main` ruleset was added to the repository requiring all changes to `main` to go through a PR. The `deadlinkchecker.yml` workflow does a direct `git push` to `main` after committing scan results, which is now blocked by this ruleset.

Root cause: the `protect-main` ruleset enforces a `pull_request` rule on `~DEFAULT_BRANCH`. The `github-actions[bot]` is not in the bypass actors list. The workflow at `.github/workflows/deadlinkchecker.yml` runs `git push` directly to `main` after committing scan CSVs to `scans/`.

Expected fix: the workflow should push scan results to a dedicated branch (e.g., `data/scans`) that is not covered by the `protect-main` ruleset, instead of pushing directly to `main`.

## 2026-02-24 — Issue #18: Agentic Workflow updates

- Make the specs agent suggest less code and let the coding agent figure it out. The specs are too technical and should stick to the business logic.
- Make the coding agent:
  - Explain its technical choices.
  - Follow code style rules like Object Calisthenics (https://dev.to/muzammilnm/understanding-object-calisthenics-writing-cleaner-code-maj).

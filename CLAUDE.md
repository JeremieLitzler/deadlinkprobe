# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

No dependencies beyond the Python standard library. No install step needed.

```bash
# Run the checker
python checker.py <start_url> [--output results.csv] [--workers 10] [--timeout 10] [--user-agent deadlinkchecker/1.0]

# Run all tests
python -m pytest tests/

# Run a single test file
python -m pytest tests/test_fetcher.py

# Run a single test by name
python -m pytest tests/test_fetcher.py::TestCheckUrl::test_head_success
```

Tests also work with the standard library runner: `python -m unittest tests/test_fetcher.py`.

## Code Architecture

The tool is a pipeline of five modules driven by `checker.py`:

```plaintext
checker.py  →  crawler.py  →  fetcher.py    (fetch_html, per-page GET)
                           →  normaliser.py (resolve + strip fragments)
                           →  parser.py     (extract <a href> values)
            →  fetcher.py  (check_url, parallel HEAD/GET per link)
            →  reporter.py (write CSV)
```

**Data flow:**

1. `crawler.crawl()` performs BFS from the start URL. It fetches each internal page's HTML, extracts hrefs, normalises them, and enqueues only internal URLs. External URLs are collected but never fetched for HTML.
2. `crawl()` returns `list[tuple[str, str]]` — `(link, referrer)` pairs covering every discovered URL (internal + external), with the start URL having an empty referrer.
3. `checker.py` feeds those pairs into a `ThreadPoolExecutor`, calling `fetcher.check_url()` for each. Results are `(link, referrer, status_str)` where status is an HTTP code string or `ERROR:<ExceptionClassName>`.
4. Results are sorted by `(referrer, link)` then written to CSV by `reporter.write_csv()`.

**Key rules in `normaliser.py`:** fragments are stripped; non-http/https schemes return `None` and are dropped. Internal vs external is determined by matching scheme + netloc against the start URL.

**`fetcher.py` has two separate functions:** `fetch_html` (follows redirects, returns body for HTML content types only, used by crawler) and `check_url` (does NOT follow redirects, records 3xx as-is, tries HEAD then falls back to GET on 405, used for status checking).

## Who is Claude Code

It is a senior engineer understanding Git Flow strategy, suggesting performant, secure and clean solutions.

It can have different role per sub agent: orchestrator, specification, coding, testing or versionning. A sub agent should always stay in that role.

The versionning agent must create branch before the any other sub agent start creating or modifying files.

It creates branches using Git Flow method:

- a feature branch when adding functionnality,
- a fix branch when resolving an issue,
- a docs branch when updating Markdown files only.
- a new branch when a file is modified and it doesn't fall in the three previous scenarii. Follow conventional commit and Git Flow rules when naming branches.

The specification agent always plans tasks and requests approval before handing work to the code agent.

The coding agent requests approval after writing code. No need to confirm file creation or modification, but confirm content is OK with human.

The testing agent tries to provide useful yet complete test suite to cover nominal use case and edge cases. It provides clear feedback to the other sub agents.

No agent needs to congratulate or use language that use unnecessary output tokens. Go to the point and stay succint.

## Project Goal

A dead link checker CLI tool. Given a starting URL:

1. Crawl all **internal** links recursively until all are discovered.
2. Collect **external** links but do not recurse into them.
3. Check all discovered links for their HTTP status code.
4. Output results as CSV: `link, referrer, http_status_code`.
5. Use parallel requests for performance.

## Multi-Agent Pipeline

**When the user provides a feature request or bug fix, act as the orchestrator:**

1. Save the request to `.agents/user-requests.md`.
2. Follow the pipeline in `prompts/agent-0-orchestrator.md` step by step.

The user never needs to run a command — just describe what they want and the pipeline starts.

### Agents and their prompt files

| Agent         | Prompt                      | Reads                                         | Writes                    |
| ------------- | --------------------------- | --------------------------------------------- | ------------------------- |
| Specification | `prompts/agent-1-specs.md`  | `.agents/user-requests.md`                    | `.agents/specs.md`        |
| Coder         | `prompts/agent-2-coder.md`  | `.agents/specs.md`                            | `.agents/code-ready.md`   |
| Tester        | `prompts/agent-3-tester.md` | `.agents/specs.md`, `.agents/code-ready.md`   | `.agents/test-results.md` |
| Versioning    | `prompts/agent-4-git.md`    | `.agents/specs.md`, `.agents/test-results.md` | git history               |

### Pipeline flow

```
[user-requests.md]
       ↓
  Specs agent → specs.md
       ↓ ← human approval
  Coder agent → code-ready.md
       ↓           ↑ status: review specs (loops back)
       ↓ ← human approval
 Tester agent → test-results.md
       ↓           ↑ status: failed (loops back to coder)
Versioning agent → branch + commit + push
```

Human approval gates pause the pipeline after specs and after coding. The orchestrator retries failed loops up to 3 times before aborting.

## Key Design Constraints

- Internal vs external link distinction drives crawl behavior: internal links are followed, external links are checked but not crawled.
- The crawler must track visited URLs to avoid infinite loops.
- CSV output must include the referring page for each link, making broken links actionable.
- Parallelism is a first-class requirement, not an optimization.

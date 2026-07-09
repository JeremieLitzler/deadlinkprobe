# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tool Paths (Windows bash shell)

Tools are NOT on the default PATH and `export PATH=...` does not work in this shell. Always use full paths:

- `python`: `/e/Applications/Scoop/apps/python/current/python.exe`
- `git`: `/e/Applications/Scoop/apps/git/current/bin/git`
- `gh`: `/e/Applications/Scoop/apps/gh/current/bin/gh`
- `rtk`: `/e/rtk/bin/rtk`

## Commands

Runtime code needs only the Python standard library plus `resend` (`requirements.txt`). The
`jli-` command chain's review and test steps additionally use `ruff`, `mypy`, and `pytest`,
pinned in `requirements-dev.txt` (`pip install -r requirements-dev.txt`).

```bash
# Run the checker
python src/checker.py <start_url> [--output results.csv] [--workers 10] [--timeout 10] [--user-agent deadlinkprobe/1.0]

# Run all tests
python -m pytest tests/

# Run a single test file
python -m pytest tests/test_fetcher.py

# Run a single test by name
python -m pytest tests/test_fetcher.py::TestCheckUrl::test_head_success

# Lint + type-check (jli-reviews-code runs these)
ruff check src tests
mypy src
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

## Feature Workflow — the `jli-` command chain

The supported way to build a feature or fix is the **manual `jli-` slash-command chain** in
`.claude/commands/`. Each command is one stateless step the human runs by hand; state flows
through a task folder `docs/tasks/issue-<id>-<slug>/` in the feature worktree. Full reference:
`AGENT-COMMAND-MIGRATION.md` (mapping table, chain diagram, pipeline scripts).

Worktree layout (bare repo with sibling worktrees):

```plaintext
E:/Git/GitHub/deadlinkprobe.git             bare repo
E:/Git/GitHub/deadlinkprobe_main            main worktree (chain home)
E:/Git/GitHub/deadlinkprobe_<type>-<slug>   a feature worktree
```

`/jli-sets-up` and `/jli-cleans` run from the `deadlinkprobe_main` worktree; every phase
command runs from inside the feature worktree opened with `code <worktree>`. The order:

```plaintext
/jli-sets-up  >  /jli-writes-spec  >  /jli-verifies-security  >  /jli-writes-tests-spec
   >  /jli-codes  >  /jli-reviews-code  >  /jli-writes-tests  >  /jli-runs-tests
   >  /jli-ships  >  /jli-cleans
```

Run `/jli-commits` after each phase. Loop-backs: review "changes requested" and test "failed"
return to `/jli-codes`; `/jli-codes` "review specs" returns to `/jli-writes-spec`. Approval
gates: ADR warnings after spec/code, and PR-open + merge confirmations in `/jli-ships`. Edit
the chain itself only through `/jli-tweaks-command-chain`.

### Deprecated: orchestrator pipeline

The older orchestrator flow under `.agents-brain/` (agent-0 … agent-4) is **deprecated** —
superseded by the `jli-` chain and kept only for history. Its former `.agents-output/`
artifacts were migrated into per-issue folders under `docs/tasks/`. Do not start new work
through it.

## Key Design Constraints

- Internal vs external link distinction drives crawl behavior: internal links are followed, external links are checked but not crawled.
- The crawler must track visited URLs to avoid infinite loops.
- CSV output must include the referring page for each link, making broken links actionable.
- Parallelism is a first-class requirement, not an optimization.

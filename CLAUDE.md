# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Who is Claude Code

It is a senior engineer understanding Git Flow strategy, suggesting performant, secure and clean solutions.

It has a specific role (specification, coding, testing, versionning) and should always stay in that role.

The versionning agent must create:

- a feature branch when adding functionnality,
- a fix branch when resolving an issue,
- a docs branch when updating Markdown files only.
- a new branch when a file is modified and it doesn't fall in the three previous scenarii. Follow conventional commit and Git Flow rules when naming branches.

The specification agent always plans tasks and requests approval before handing work to the code agent.

The coding agent requests approval before after writing code. No need to confirm file creation or modification, but confirm content is OK with Claude code's user.

The testing agent tries to provide useful yet complete test suite to cover nominal use case and edge cases.

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

| Agent | Prompt | Reads | Writes |
|---|---|---|---|
| Specification | `prompts/agent-1-specs.md` | `.agents/user-requests.md` | `.agents/specs.md` |
| Coder | `prompts/agent-2-coder.md` | `.agents/specs.md` | `.agents/code-ready.md` |
| Tester | `prompts/agent-3-tester.md` | `.agents/specs.md`, `.agents/code-ready.md` | `.agents/test-results.md` |
| Versioning | `prompts/agent-4-git.md` | `.agents/specs.md`, `.agents/test-results.md` | git history |

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

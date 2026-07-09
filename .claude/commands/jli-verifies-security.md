Write security guidelines for a feature. Task folder: $ARGUMENTS

`$ARGUMENTS` is the task folder, given as a `@`-mention relative to the worktree root you
opened (e.g. `@docs/tasks/issue-<id>-<slug>`). If it is empty, stop and reply:

> Usage: `/jli-verifies-security @<task-folder>` — open the feature worktree (`code <worktree>`) first,
> then pass the task folder relative to it.

Run from the worktree root (your current directory). All paths below are relative to it; read
and write only inside this worktree.

## What this command does

Read `[task-folder]/business-specifications.md`. Produce security guidelines for the
implementer, based on the project's stack (Python 3 standard library, `resend` for email,
`ThreadPoolExecutor` for parallelism) and the architecture in `CLAUDE.md`. Write them to
`[task-folder]/security-guidelines.md` as a numbered list of actionable rules.

### Scope to analyse (only what this feature touches)
- Input validation (start URL, CLI arguments, crawl depth, worker/timeout bounds)
- URL fetching safety — SSRF and scheme abuse: the tool fetches arbitrary discovered URLs;
  non-http/https schemes must be dropped (see `normaliser.py`), redirects and internal/
  external classification must not be trickable into probing unintended hosts
- HTML parsing safety (untrusted markup, entity/encoding handling, resource exhaustion on
  large or malicious pages)
- Output safety (CSV injection in `reporter.py`, path handling for `--output`)
- Email boundary (`emailer.py` / `resend`): recipient/address validation, no injection into
  headers or body, API key never logged
- Secrets / environment variable handling; dependency risks for any new package

Each rule states **What** must be enforced, **Where** (file/layer), and **Why** (the attack
vector, one sentence max).

### Conciseness rules (strictly enforced)
- Skip any scope area not touched by this feature — no "N/A" rules.
- Do not restate rules already enforced by an existing ADR; cite the ADR number instead.
- Do not restate constraints already in `business-specifications.md`.
- Target 4–6 rules maximum (2–3 for a small attack surface).

Do NOT prescribe implementation details — no signatures, code snippets, or variable names.

## ADR requirement

If the guidelines introduce a new security pattern not yet in `docs/decisions/`, add before
the final status line:

```
### ADR Required

[Description of the new security pattern and why it is needed]
```

## Output contract

Create `[task-folder]/security-guidelines.md`. End it with `status: ready` as the last line.

## Shell command retry limit

Do not run more than 3 failing shell commands in total. After 3 failures, stop and report
the full error output to the user.

## Next

> Security guidelines ready. Review `security-guidelines.md` in the task folder, then run
> `/jli-commits @<task-folder>`, then (optionally `/clear` and)
> `/jli-writes-tests-spec @<task-folder>` to write the plain-language test cases.

If the file contains `### ADR Required`, warn the user to approve the ADR before continuing.

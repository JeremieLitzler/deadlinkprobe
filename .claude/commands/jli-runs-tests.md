Run the test suite. Task folder: $ARGUMENTS

`$ARGUMENTS` is the task folder, given as a `@`-mention relative to the worktree root you
opened (e.g. `@docs/tasks/issue-<id>-<slug>`). If it is empty, stop and reply:

> Usage: `/jli-runs-tests @<task-folder>` — open the feature worktree (`code <worktree>`) first,
> then pass the task folder relative to it.

Run from the worktree root (your current directory) — that is where the tests and dev tooling
live.

## What this command does

Run the pytest suite from the worktree (failures surfaced clearly — saves tokens):

```bash
rtk test python -m pytest tests/
```

## Output contract

Write `[task-folder]/test-results.md` using this template:

```markdown
# Test Results — Issue #[id]: [title]

## Test Run

Command: `python -m pytest tests/` (pytest vX.Y.Z) from the `[worktree name]` worktree.

## Files Run

All those mentioned in [technical specs](technical-specifications.md).

## Results

<if all pass>
All tests passed. No failures.

### Test Summary

[N] test files, [N] tests total — all passed.

- Duration: ~[N] seconds
<else>
### Failures

<each failing test with its traceback / error output>
<end-if>

status: passed
```

Rules:
- If any test fails, replace the Results section with failure details and replace
  `status: passed` with `status: failed`.
- The status line is always the last line of the file.

## Shell command retry limit

Do not run more than 3 failing shell commands in total. After 3 failures, stop, record the
full error output in `test-results.md`, and end the file with `status: failed`.

## Next

- If `status: failed`:
  > Tests failed (see `test-results.md` in the task folder). Run `/jli-commits @<task-folder>`
  > to record the results, then diagnose the failure: if the code is wrong, fix it with
  > `/jli-codes @<task-folder>`; if the test itself is wrong, correct it with
  > `/jli-writes-tests @<task-folder>`. Then re-run `/jli-reviews-code @<task-folder>` and
  > `/jli-runs-tests @<task-folder>`.
- If `status: passed`:
  > All tests pass. Run `/jli-commits @<task-folder>`, then `/jli-ships @<task-folder>`
  > to push, open the PR, and merge after approval.

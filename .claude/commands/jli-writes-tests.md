Write the executable test files for a feature. Task folder: $ARGUMENTS

`$ARGUMENTS` is the task folder, given as a `@`-mention relative to the worktree root you
opened (e.g. `@docs/tasks/issue-<id>-<slug>`). If it is empty, stop and reply:

> Usage: `/jli-writes-tests @<task-folder>` — open the feature worktree
> (`code <worktree>`) first, then pass the task folder relative to it.

Run from the worktree root (your current directory). All paths below are relative to it; read
and write only inside this worktree.

## What this command does

This is the **after-coding** test pass. It turns the plain-language scenarios from
`/jli-writes-tests-spec` into executable `pytest` `tests/test_*.py` files, now that the
implementation exists.

Read `[task-folder]/test-cases.md` and `[task-folder]/technical-specifications.md` (which
lists every file the implementer created or changed). Read each listed implementation file
to learn the public API (function/class names and their modules under `src/`).

Translate each scenario in `test-cases.md` into a `pytest` test. Place test files in `tests/`
following the existing `test_<module>.py` naming convention. Import only from paths confirmed
to exist in the implementation files. Match the existing suite's style (the tests already use
`unittest.TestCase` classes and run under both `pytest` and `python -m unittest`).

If `[task-folder]/test-results.md` ends with `status: failed` and the failure is a wrong
assertion rather than a code bug, read it first and correct the offending `test_*.py` (this
command is being re-run in a loop-back from `/jli-runs-tests`).

Do NOT:
- write tests for scenarios not in `test-cases.md`
- write tests whose only assertion is that a value is not `None` when it cannot be `None` by
  construction (type correctness is `mypy`'s job)
- hit the real network — mock `fetcher` I/O (`unittest.mock`) or use local fixtures; a unit
  test must not depend on an external host being reachable
- duplicate what `ruff`/`mypy` already catch

End your report with `status: ready`.

## Shell command retry limit

Do not run more than 3 failing shell commands in total. After 3 failures, stop and report
the full error output to the user.

## Next

> Test files written. Run `/jli-commits @<task-folder>`, then (optionally `/clear` and)
> `/jli-runs-tests @<task-folder>` to run the suite.

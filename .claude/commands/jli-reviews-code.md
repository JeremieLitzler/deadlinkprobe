Review the implementation. Task folder: $ARGUMENTS

`$ARGUMENTS` is the task folder, given as a `@`-mention relative to the worktree root you
opened (e.g. `@docs/tasks/issue-<id>-<slug>`). If it is empty, stop and reply:

> Usage: `/jli-reviews-code @<task-folder>` — open the feature worktree (`code <worktree>`) first,
> then pass the task folder relative to it.

Run from the worktree root (your current directory) — that is where the dev tooling installed
by `worktree-create.sh` lives and where the shell commands below must run.

## What this command does

Read `[task-folder]/technical-specifications.md` (the list of changed files),
`[task-folder]/security-guidelines.md`, and `[task-folder]/business-specifications.md`. Then
read every source file listed in the technical spec.

Run exactly these two commands from the worktree and include their output in your findings:

```bash
rtk ruff check src tests   # lint (style, unused imports, common bugs)
mypy src                   # static type check (no rtk equivalent)
```

Do NOT run `pytest` — that is `/jli-runs-tests`'s job.

Before reviewing Python issues, fetch these reference pages to ground the review:
- `https://docs.python.org/3/library/concurrent.futures.html`
- `https://docs.python.org/3/library/urllib.request.html`
- `https://docs.python.org/3/library/urllib.parse.html`

## Review checklist

- Every rule in `security-guidelines.md` is verifiably addressed in the changed files.
- Object Calisthenics respected (one indentation level, no `else`, domain types,
  first-class collections, one dot per line, no abbreviations, small entities, ≤2 instance
  variables, no getters/setters).
- Implementation matches the business spec — no missing requirements, no scope creep.
- No dead code, unused imports, or unreachable branches.
- Naming clarity — no abbreviations (`res`>`fetch_response`, `idx`>`index`, `tmp`>`temporary`);
  no single-letter loop variables outside trivial math.
- Python/concurrency pitfalls:
  - Mutable default arguments (`def f(items=[])`) — use `None` + guard instead.
  - Bare `except:` or `except Exception` that swallows errors the checker should record.
  - Shared mutable state written from multiple `ThreadPoolExecutor` workers without isolation.
  - Network calls without a timeout, or that follow redirects where `check_url` must not.
  - Resource leaks — responses/files not closed; prefer context managers (`with`).
  - Non-http/https schemes or fragments not stripped in `normaliser.py`.
  - `mypy` gaps: missing return-type annotations on public functions, `Any` without a
    narrowing check, `# type: ignore` without a reason.

## Output contract

Create `[task-folder]/review-results.md`:
- Show the `ruff check` and `mypy` output (in fenced blocks if there are errors; otherwise
  state they passed cleanly for the changed files).
- A Checklist section: mark each item ✓, or list details per failing item.
- No summary section.
- End with `status: approved` as the last line. If any finding exists, use
  `status: changes requested` instead. The status line is always last.

If you hit the 3-failing-shell-command limit, record the error output and end the file with
`status: changes requested`.

## Next

- If `status: changes requested`:
  > Review found issues (see `review-results.md` in the task folder). Run
  > `/jli-commits @<task-folder>` to record the review, then `/jli-codes @<task-folder>` to
  > address the findings, then `/jli-reviews-code @<task-folder>` again.
- If `status: approved`:
  > Review approved. Run `/jli-commits @<task-folder>`, then (optionally `/clear` and)
  > `/jli-writes-tests @<task-folder>` to write the `test_*.py` files.

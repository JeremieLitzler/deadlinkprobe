Remove a merged feature worktree and refresh main. Worktree: $ARGUMENTS

`$ARGUMENTS` is the feature worktree to remove — either its folder name
(e.g. `deadlinkprobe_<type>-<slug>`) or an absolute path. If it is empty, list the candidates
and ask which to remove:

```bash
git worktree list
```

> Usage: `/jli-cleans <worktree-folder-name>` — run this from the `deadlinkprobe_main`
> worktree, after the PR has merged.

## Run location

Run this from the **`deadlinkprobe_main` worktree**, never from inside the worktree being
removed (you cannot delete the directory you are standing in). If your current directory is
the feature worktree, stop and tell the user to `code [main-worktree]` and run the command
there.

## What this command does

The PR for this feature is already merged (by `/jli-ships` or manually on GitHub). This
removes the local worktree, prunes stale git entries, deletes the local branch, and
fast-forwards `main`.

```bash
bash scripts/pipeline/worktree-cleanup.sh "$ARGUMENTS"
bash scripts/pipeline/refresh-main.sh
```

`worktree-cleanup.sh` accepts either a bare folder name (resolved against the parent of the
bare repo) or an absolute path. It removes the worktree, prunes, and force-deletes the local
branch (GitHub rebase/squash-merge leaves the local branch looking "unmerged"). Both scripts
are safe to re-run if a prior attempt was partial.

If `worktree-cleanup.sh` reports the worktree is still in use, confirm you are not running
from inside it, then re-run.

## Shell command retry limit

Do not run more than 3 failing shell commands in total. After 3 failures, stop and report
the full error output to the user.

## Next

> Feature shipped and cleaned up: worktree removed, local branch deleted, `main` updated.
> The chain is complete.

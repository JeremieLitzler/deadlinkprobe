#!/usr/bin/env bash
# Remove a merged feature worktree and force-delete its local branch.
# Usage: worktree-cleanup.sh <worktree-folder-name-or-abs-path>
# Accepts a bare folder name (resolved against the bare repo's parent) or an
# absolute path. Safe to re-run if a prior attempt was partial.
set -euo pipefail

arg="${1:?usage: worktree-cleanup.sh <worktree-folder-name-or-abs-path>}"

git_common_dir="$(git rev-parse --git-common-dir)"
bare_dir="$(cd "$git_common_dir" && pwd)"
parent_dir="$(dirname "$bare_dir")"

# Resolve to an absolute worktree path.
if [ -d "$arg" ]; then
  worktree_dir="$(cd "$arg" && pwd)"
else
  worktree_dir="${parent_dir}/${arg}"
fi

if [ ! -d "$worktree_dir" ]; then
  git worktree prune
  echo "note: worktree path not found (${worktree_dir}); pruned stale entries."
  exit 0
fi

# Capture the branch before removing the worktree.
branch="$(git -C "$worktree_dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"

git worktree remove --force "$worktree_dir"
git worktree prune

if [ -n "$branch" ] && [ "$branch" != "main" ]; then
  # GitHub rebase/squash-merge leaves the local branch looking "unmerged"; force-delete.
  git branch -D "$branch" 2>/dev/null || echo "note: local branch ${branch} already gone."
fi

echo "Removed worktree ${worktree_dir} and local branch ${branch:-<none>}."

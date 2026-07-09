#!/usr/bin/env bash
# Fetch latest from origin into the bare repo, pruning stale branches.
# Safe to re-run. Run from any worktree.
set -euo pipefail

git fetch origin --prune
echo "Fetched origin (pruned stale remote branches)."

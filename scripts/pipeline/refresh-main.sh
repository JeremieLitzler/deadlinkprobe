#!/usr/bin/env bash
# Fast-forward the main worktree to origin/main. Run from the main worktree.
set -euo pipefail

git fetch origin --quiet
git checkout main
git merge --ff-only origin/main
echo "main fast-forwarded to origin/main."

#!/usr/bin/env bash
# Create a feature worktree off origin/main.
# Usage: worktree-create.sh <type> <slug>
#   <type>  conventional-commit type (feat, fix, docs, refactor, ...)
#   <slug>  short kebab-case summary (<= 30 chars)
# Creates branch <type>/<slug> in a sibling worktree <repo-name>_<type>-<slug>,
# installs dev tooling if requirements-dev.txt exists, and prints the absolute path.
set -euo pipefail

type="${1:?usage: worktree-create.sh <type> <slug>}"
slug="${2:?usage: worktree-create.sh <type> <slug>}"

# Resolve the bare repo and its parent directory from wherever we run.
git_common_dir="$(git rev-parse --git-common-dir)"
bare_dir="$(cd "$git_common_dir" && pwd)"
parent_dir="$(dirname "$bare_dir")"
repo_name="$(basename "$bare_dir" .git)"

branch="${type}/${slug}"
worktree_dir="${parent_dir}/${repo_name}_${type}-${slug}"

git fetch origin --quiet
git worktree add -b "$branch" "$worktree_dir" origin/main

# Install dev tooling (ruff, mypy, pytest, resend) if the manifest is present.
if [ -f "${worktree_dir}/requirements-dev.txt" ]; then
  python -m pip install -q -r "${worktree_dir}/requirements-dev.txt" \
    || echo "warning: could not install requirements-dev.txt; install ruff/mypy/pytest manually"
fi

echo "Worktree: ${worktree_dir}"

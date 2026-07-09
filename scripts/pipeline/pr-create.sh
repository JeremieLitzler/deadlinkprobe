#!/usr/bin/env bash
# Push the feature branch and open a PR against main.
# Usage: pr-create.sh <worktree-dir> <title> <body-file>
set -euo pipefail

worktree_dir="${1:?usage: pr-create.sh <worktree-dir> <title> <body-file>}"
title="${2:?missing PR title}"
body_file="${3:?missing PR body file}"

cd "$worktree_dir"
branch="$(git rev-parse --abbrev-ref HEAD)"

git push -u origin "$branch"
url="$(gh pr create --base main --head "$branch" --title "$title" --body-file "$body_file")"
echo "PR: ${url}"

#!/usr/bin/env bash
# Merge a PR with rebase and delete the remote branch.
# Usage: pr-complete.sh <pr-url-or-number>
# Skips gracefully if the PR is already merged or closed. Safe to re-run.
set -euo pipefail

pr="${1:?usage: pr-complete.sh <pr-url-or-number>}"

state="$(gh pr view "$pr" --json state --jq .state 2>/dev/null || echo UNKNOWN)"
if [ "$state" = "MERGED" ]; then
  echo "PR already merged; nothing to do."
  exit 0
fi
if [ "$state" = "CLOSED" ]; then
  echo "PR is closed (not merged); refusing to merge."
  exit 1
fi

gh pr merge "$pr" --rebase --delete-branch
echo "Merged ${pr} (rebase) and deleted the remote branch."

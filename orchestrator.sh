#!/bin/bash
set -euo pipefail

MAX_RETRIES=3

# ── Helpers ───────────────────────────────────────────────────────────────────

wait_for_status() {
  local file=$1
  local expected=$2
  echo "Waiting for $file → status: $expected"
  while true; do
    if grep -q "status: $expected" "$file" 2>/dev/null; then break; fi
    sleep 3
  done
}

wait_for_any_status() {
  local file=$1
  shift
  local statuses=("$@")
  echo "Waiting for $file → status: ${statuses[*]}"
  while true; do
    for s in "${statuses[@]}"; do
      if grep -q "status: $s" "$file" 2>/dev/null; then return; fi
    done
    sleep 3
  done
}

approve() {
  local stage=$1
  echo ""
  echo "=== APPROVAL REQUIRED: $stage ==="
  read -rp "Proceed? (y/n): " confirm
  if [ "$confirm" != "y" ]; then
    echo "Aborted."
    exit 1
  fi
}

run_agent() {
  local prompt=$1
  claude --print < "prompts/$prompt"
}

# ── Stage 1: Specs ────────────────────────────────────────────────────────────

echo "=== STAGE 1: Specs ==="
run_agent agent-1-specs.md
wait_for_status .agents/specs.md "ready"
approve "Review spec before coding"

# ── Stage 2: Coding (with spec-review feedback loop) ─────────────────────────

coder_attempts=0
while true; do
  coder_attempts=$((coder_attempts + 1))
  if [ "$coder_attempts" -gt "$MAX_RETRIES" ]; then
    echo "Coder exceeded $MAX_RETRIES attempts. Aborting."
    exit 1
  fi

  echo ""
  echo "=== STAGE 2: Coding (attempt $coder_attempts) ==="
  # Reset status before run
  sed -i 's/status: .*/status: idle/' .agents/code-ready.md
  run_agent agent-2-coder.md
  wait_for_any_status .agents/code-ready.md "ready" "review specs"

  if grep -q "status: review specs" .agents/code-ready.md; then
    echo "Coder flagged a spec issue — re-running specs agent."
    sed -i 's/status: .*/status: idle/' .agents/specs.md
    run_agent agent-1-specs.md
    wait_for_status .agents/specs.md "ready"
    approve "Review updated spec before re-coding"
    continue
  fi

  approve "Review code before testing"
  break
done

# ── Stage 3: Testing (with coder feedback loop) ───────────────────────────────

tester_attempts=0
while true; do
  tester_attempts=$((tester_attempts + 1))
  if [ "$tester_attempts" -gt "$MAX_RETRIES" ]; then
    echo "Tests failed after $MAX_RETRIES attempts. Aborting."
    exit 1
  fi

  echo ""
  echo "=== STAGE 3: Testing (attempt $tester_attempts) ==="
  sed -i 's/status: .*/status: idle/' .agents/test-results.md
  run_agent agent-3-tester.md
  wait_for_any_status .agents/test-results.md "passed" "failed"

  if grep -q "status: failed" .agents/test-results.md; then
    echo "Tests failed — re-running coder."
    sed -i 's/status: .*/status: idle/' .agents/code-ready.md
    run_agent agent-2-coder.md
    wait_for_status .agents/code-ready.md "ready"
    continue
  fi

  break
done

# ── Stage 4: Git ──────────────────────────────────────────────────────────────

echo ""
echo "=== STAGE 4: Git ==="
run_agent agent-4-git.md

echo ""
echo "=== Pipeline complete ==="

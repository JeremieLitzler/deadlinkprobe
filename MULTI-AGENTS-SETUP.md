# Setup for Multi Agent Work

Here's a concrete setup:

## Directory Structure

```plaintext
project/
├── .agents/
│   ├── specs.md          # specs-agent output
│   ├── code-ready.md     # coder-agent output
│   ├── test-results.md   # test-agent output
│   └── status.md         # current pipeline stage
├── orchestrator.sh       # glues agents together
└── prompts/
    ├── agent-1-specs.md
    ├── agent-2-coder.md
    ├── agent-3-tester.md
    └── agent-4-git.md
```

## Step 2 — Orchestrator

**`orchestrator.sh`**

```bash
#!/bin/bash

wait_for_status() {
  local file=$1
  local expected=$2
  echo "Waiting for $file to reach: $expected"
  while true; do
    if grep -q "status: $expected" "$file" 2>/dev/null; then
      break
    fi
    sleep 3
  done
}

echo "=== STAGE 1: Specs ==="
claude < prompts/specs.txt

wait_for_status .agents/specs.md "ready"

echo "=== STAGE 2: Coding ==="
claude < prompts/coder.txt

wait_for_status .agents/code-ready.md "ready"

echo "=== STAGE 3: Testing ==="
claude < prompts/tester.txt

wait_for_status .agents/test-results.md "passed"

echo "=== STAGE 4: Git ==="
claude < prompts/git.txt

echo "=== Pipeline complete ==="
```

## Step 3 — Add a Human Gate (Optional but Recommended)

Between stages 2 and 3, pause for review:

```bash
echo "=== Review code before testing? (y/n) ==="
read confirm
if [ "$confirm" != "y" ]; then exit 1; fi
```

## Step 4 — Run It

```bash
# Write your feature request
echo "Build a login endpoint with JWT auth" > .agents/request.md

# Launch the pipeline
chmod +x orchestrator.sh
./orchestrator.sh
```

## Tips

- **Failed tests:** Have the orchestrator loop back to the coder-agent with `test-results.md` as additional context, up to N retries
- **Git agent:** Restrict it to a feature branch, never main
- **Audit trail:** The `.agents/` files give you a full log of every decision made what a Markdown heading 2 with the date and time of the request, decision, solution or response.

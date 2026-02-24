# Setup for Multi Agent Work

Here's a concrete setup:

## Directory Structure

```plaintext
project/
├── .agents-output/
│   ├── specs.md          # specs-agent output
│   ├── code-ready.md     # coder-agent output
│   ├── test-results.md   # test-agent output
│   └── status.md         # current pipeline stage
└── .agents-brain/
    ├── agent-0-orchestrator.md
    ├── agent-1-specs.md
    ├── agent-2-coder.md
    ├── agent-3-tester.md
    └── agent-4-git.md
```

## Step 2 — Add a Human Gate (Optional but Recommended)

Between stages 2 and 3, pause for review:

```bash
echo "=== Review code before testing? (y/n) ==="
read confirm
if [ "$confirm" != "y" ]; then exit 1; fi
```

## Step 3 — Run It

```bash
claude
# Write your feature request in the terminal. Claude will handle it.

```

## Tips

- **Failed tests:** Have the orchestrator loop back to the coder-agent with `test-results.md` as additional context, up to N retries
- **Git agent:** Restrict it to a feature branch, never main
- **Audit trail:** The `.agents-output/` files give you a full log of every decision made what a Markdown heading 2 with the date and time of the request, decision, solution or response.

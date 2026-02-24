# I am an Orchestrator Agent

I coordinate the multi-agent pipeline for this repository. I use the Task tool to spawn specialist subagents and AskUserQuestion for human approval gates.

## Setup

MAX_RETRIES = 3

All sub agents must retry `MAX_RETRIES` at most before notifying human.

## Pipeline

### Step 0 — Branching

Read `.agents-brain/agent-4-git.md` and spawn a subagent using the Task tool with that prompt, instructing it to perform **Task 1 and Task 2 only** (pull latest main and create the branch). Do not ask it to commit or push yet.

Wait for the branch to be created before proceeding.

### Step 1 — Specs

Read `.agents-brain/agent-1-specs.md` and spawn a subagent using the Task tool with that prompt as the task description. The subagent will read `.agents-output/user-requests.md` and write `.agents-output/specs.md`.

Wait for `.agents-output/specs.md` to end with `status: ready`.

Use AskUserQuestion to show the user a summary of `.agents-output/specs.md` and ask for approval before proceeding to commit changes.
If the user does not approve, stop the pipeline and report why.

Read `.agents-brain/agent-4-git.md` and spawn a subagent using the Task tool with that prompt, instructing it to perform **Task 3 only** (commit specs output). Then proceed to coding.

### Step 2 — Coding

Read `.agents-brain/agent-2-coder.md` and spawn a subagent using the Task tool with that prompt.

Wait for `.agents-output/code-ready.md` to end with either `status: ready` or `status: review specs`.

If `status: review specs`:

- Inform the user and re-run Step 1 (counts toward MAX_RETRIES).
- On approval, retry Step 2.

If `status: ready`:

- Use AskUserQuestion to show the user a summary of `.agents-output/code-ready.md` and ask for approval before testing.
  - If the user does not approve, stop the pipeline.
- Read `.agents-brain/agent-4-git.md` and spawn a subagent using the Task tool with that prompt, instructing it to perform **Task 4 only** (commit code changes).

### Step 3 — Testing

Read `.agents-brain/agent-3-tester.md` and spawn a subagent using the Task tool with that prompt.

Wait for `.agents-output/test-results.md` to end with either `status: passed` or `status: failed`.

If the tester agent does not produce a result (no status line written), treat it as `status: failed` and count it toward MAX_RETRIES.

If `status: failed`:

- Show the user the test failure summary from `.agents-output/test-results.md`.
- Re-run Step 2 (counts toward MAX_RETRIES).
- Then re-run Step 3.

If MAX_RETRIES is exceeded at any step, stop the pipeline and report the failure to the user.

### Step 4 — Versioning

Read `.agents-brain/agent-4-git.md` and spawn a subagent using the Task tool with that prompt, instructing it to perform **Task 5 only** (commit test results and push the branch).

Report the branch name and commit message to the user when done.

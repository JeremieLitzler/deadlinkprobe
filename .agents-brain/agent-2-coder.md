# I am a Coder Agent

Read specification agent request in `.agents-output/specs.md` and implement exactly what is specified.

Follow the architecture described in CLAUDE.md. Do not add features beyond the spec.

When implementation is complete:

- Write a summary of every file created or changed to `.agents-output/code-ready.md`, including a one-line description of each change.
- Do not include test files in the summary (the test-agent handles those).

## Writing to `.agents-output/code-ready.md`

The file accumulates entries across tasks. Do not overwrite previous content.

- If the file does not exist, create it with the first line `# Output of Agent Coder`, then a blank line.
- Append a new `## YYYY-MM-DD - [Short description of feature or Issue id with a #]` section (today's date) with the summary beneath it.
- End the new section with the line:

```plaintext
status: ready
```

The `status: ready` line must always be the last line of the file.

Listen to tester agent feedback in `.agents-output/test-results.md`.
If the last line is `status: failed`, read the feedback following `### Testing failed`.
If you find an incoherence in the specifications causing tests to fail, end the current section of `.agents-output/code-ready.md` with:

```plaintext
### Specifications Need Review

Please review current code and test results in `.agents-output/test-results.md`.

status: review specs
```

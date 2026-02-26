## 2026-02-26 — Issue #23: Reorganize .agents-output folder

Instead of flat `.md` files, use subfolders with timestamp-named files:

```plaintext
.agents-output/
├── user-requests/                  # orchestrator writes here
│       └── [timestamp]-issue-[id]-[slug].md
├── business-specifications/        # specs agent writes here
│       └── [timestamp]-issue-[id]-[slug].md
├── technical-specifications/       # coder agent writes here
│       └── [timestamp]-issue-[id]-[slug].md
├── test-results/                   # tester agent writes here
│       └── [timestamp]-issue-[id]-[slug].md
└── status.md
```

File naming: `[timestamp iso]-issue-[issue id]-[slugified issue title].md`
Example: `2026-02-26-07-33-28-issue-23-reorganize-agents-output-folder.md`

All existing `.md` file contents migrate to `_initial.md` in each respective subfolder. Old flat files are removed.

All agent brain files and CLAUDE.md must be updated to reference the new paths. All commits for this issue use type `ci(agent)`.

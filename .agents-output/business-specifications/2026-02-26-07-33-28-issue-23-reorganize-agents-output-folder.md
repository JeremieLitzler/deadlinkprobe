# Business Specification — Issue #23: Reorganize .agents-output Folder

## 2026-02-26 - Reorganize .agents-output folder

## Goal

Replace the flat `.agents-output/` file layout with a structured subfolder layout. Each agent type writes to its own dedicated subfolder, and each run produces a timestamped file rather than appending to a shared accumulating file. This makes it possible to trace individual pipeline runs by date and issue, and eliminates write conflicts when multiple runs coexist.

## Scope

This change affects:

- The physical layout of `.agents-output/`
- The file naming convention for all agent output files
- The content of all five agent brain files (`.agents-brain/agent-0-orchestrator.md` through `agent-4-git.md`)
- The content of `CLAUDE.md`
- The migration of existing flat files to the new subfolder structure
- The removal of `_sample.md`

This change does NOT affect source code under `src/`, tests under `tests/`, or any CI/CD workflow files.

## New Folder Structure

Rule: `.agents-output/` contains exactly four named subfolders plus `status.md` at the root level.

| Subfolder                   | Written by          |
| --------------------------- | ------------------- |
| `user-requests/`            | Orchestrator        |
| `business-specifications/`  | Specification agent |
| `technical-specifications/` | Coder agent         |
| `test-results/`             | Tester agent        |

Example: after a run for issue #23 on 2026-02-26 between 07:33:28 and 07:37:28, the layout is:

```plaintext
.agents-output/
├── user-requests/
│       └── 2026-02-26-07-33-28-issue-23-reorganize-agents-output-folder.md
├── business-specifications/
│       └── 2026-02-26-07-34-28-issue-23-reorganize-agents-output-folder.md
├── technical-specifications/
│       └── 2026-02-26-07-35-28-issue-23-reorganize-agents-output-folder.md
├── test-results/
│       └── 2026-02-26-07-37-28-issue-23-reorganize-agents-output-folder.md
└── status.md
```

Rule: no files exist directly under `.agents-output/` other than `status.md`.

## File Naming Convention

Rule: every file written by any agent into a subfolder must follow this exact naming format:

```plaintext
[YYYY-MM-DD]-[HH-MM-SS]-issue-[issue-id]-[slugified-title].md
```

Where:

- `[YYYY-MM-DD]` is the ISO date of the pipeline run.
- `[HH-MM-SS]` is the 24-hour time of the pipeline run, with colons replaced by hyphens. Use the Romance Standard Time (`powershell -Command "[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow,'Romance Standard Time').ToString('yyyy-MM-dd-HH-mm-ss')"`).
- `[issue-id]` is the numeric GitHub issue identifier.
- `[slugified-title]` is the issue title lowercased with spaces and special characters replaced by hyphens.

Example — issue #23 "Reorganize agents-output folder" triggered on 2026-02-26 at 07:33:28:

```plaintext
2026-02-26-07-33-28-issue-23-reorganize-agents-output-folder.md
```

Rule: all four files produced for a single pipeline run share the same slug but **use the timestamp prefix at file creation**.

## Migration of Existing Files

Rule: existing content from the four flat accumulating files must be preserved.

| Existing flat file                | Migrates to                                          |
| --------------------------------- | ---------------------------------------------------- |
| `.agents-output/user-requests.md` | `.agents-output/user-requests/_initial.md`            |
| `.agents-output/specs.md`         | `.agents-output/business-specifications/_initial.md`  |
| `.agents-output/code-ready.md`    | `.agents-output/technical-specifications/_initial.md` |
| `.agents-output/test-results.md`  | `.agents-output/test-results/_initial.md`             |

Rule: after their content is moved to `_initial.md` in the respective subfolder, the four original flat files are removed.

Example — a reader looking for previous spec entries will find them at `.agents-output/business-specifications/_initial.md`, not at `.agents-output/specs.md`.

Rule: `status.md` is not migrated. It remains at `.agents-output/status.md` unchanged.

Rule: `_sample.md` is removed entirely. It described the old flat accumulating file format, which no longer exists.

## Agent Responsibilities After Reorganization

Rule: each agent writes a single self-contained file per pipeline run; agents no longer append to a shared accumulating file.

| Agent               | Writes to                                                                 |
| ------------------- | ------------------------------------------------------------------------- |
| Orchestrator        | `.agents-output/user-requests/[timestamp]-issue-[id]-[slug].md`           |
| Specification agent | `.agents-output/business-specifications/[timestamp]-issue-[id]-slug].md`  |
| Coder agent         | `.agents-output/technical-specifications/[timestamp]-issue-[id]-slug].md` |
| Tester agent        | `.agents-output/test-results/[timestamp]-issue-[id]-slug].md`             |

Rule: no agent reads from or writes to a subfolder owned by a different agent.

Example — the coder agent reads from `.agents-output/business-specifications/` (the latest file by filename sort) and writes to `.agents-output/technical-specifications/`.

## Agent Brain File Updates

Rule: every path reference in agent brain files that points to the old flat file must be updated to the new subfolder path.

### agent-0-orchestrator.md

| Old reference                     | New reference                                        |
| --------------------------------- | ---------------------------------------------------- |
| `.agents-output/user-requests.md` | `.agents-output/user-requests/_initial.md`            |
| `.agents-output/specs.md`         | `.agents-output/business-specifications/_initial.md`  |
| `.agents-output/code-ready.md`    | `.agents-output/technical-specifications/_initial.md` |
| `.agents-output/test-results.md`  | `.agents-output/test-results/_initial.md`             |

Rule: the orchestrator brain file must describe how agents determine the correct timestamped filename for the current run (shared timestamp established at Step 0).

### agent-1-specs.md

| Old reference                     | New reference                                                                    |
| --------------------------------- | -------------------------------------------------------------------------------- |
| `.agents-output/user-requests.md` | `.agents-output/user-requests/[timestamp-slug].md`                               |
| `.agents-output/specs.md`         | `.agents-output/business-specifications/[timestamp-slug].md`                     |
| `.agents-output/code-ready.md`    | `.agents-output/technical-specifications/[timestamp-slug].md` (feedback polling) |

Rule: the instruction to not overwrite previous content and to append a dated section is removed, because each run now writes a new file.

Rule: the instruction to create the file with a header line `# Output of Agent Specification` if it does not exist is removed; the new file format is a standalone document for the current run only.

### agent-2-coder.md

| Old reference                    | New reference                                                        |
| -------------------------------- | -------------------------------------------------------------------- |
| `.agents-output/specs.md`        | `.agents-output/business-specifications/[timestamp-slug].md`         |
| `.agents-output/code-ready.md`   | `.agents-output/technical-specifications/[timestamp-slug].md`        |
| `.agents-output/test-results.md` | `.agents-output/test-results/[timestamp-slug].md` (feedback polling) |

Rule: the instruction to not overwrite previous content and to append a dated section is removed.

Rule: the instruction to create the file with a header line `# Output of Agent Coder` if it does not exist is removed.

### agent-3-tester.md

| Old reference                    | New reference                                                 |
| -------------------------------- | ------------------------------------------------------------- |
| `.agents-output/code-ready.md`   | `.agents-output/technical-specifications/[timestamp-slug].md` |
| `.agents-output/specs.md`        | `.agents-output/business-specifications/[timestamp-slug].md`  |
| `.agents-output/test-results.md` | `.agents-output/test-results/[timestamp-slug].md`             |

Rule: the instruction to not overwrite previous content and to append a dated section is removed.

Rule: the instruction to create the file with a header line `# Output of Agent Tester` if it does not exist is removed.

### agent-4-git.md

| Old reference                     | New reference                                                 |
| --------------------------------- | ------------------------------------------------------------- |
| `.agents-output/user-requests.md` | `.agents-output/user-requests/[timestamp-slug].md`            |
| `.agents-output/specs.md`         | `.agents-output/business-specifications/[timestamp-slug].md`  |
| `.agents-output/code-ready.md`    | `.agents-output/technical-specifications/[timestamp-slug].md` |
| `.agents-output/test-results.md`  | `.agents-output/test-results/[timestamp-slug].md`             |

## CLAUDE.md Updates

Rule: the "Multi-Agent Pipeline" section in `CLAUDE.md` references the old flat file paths. Every path in that section must be updated to reflect the new subfolder conventions.

The following paths must be replaced:

| Old path                          | New path                                               |
| --------------------------------- | ------------------------------------------------------ |
| `.agents-output/user-requests.md` | `.agents-output/user-requests/` (subfolder)            |
| `.agents-output/specs.md`         | `.agents-output/business-specifications/` (subfolder)  |
| `.agents-output/code-ready.md`    | `.agents-output/technical-specifications/` (subfolder) |
| `.agents-output/test-results.md`  | `.agents-output/test-results/` (subfolder)             |

Rule: the pipeline flow diagram in CLAUDE.md must be updated to show subfolders rather than flat file names.

Rule: the agents table in CLAUDE.md must be updated so the "Reads" and "Writes" columns show the new subfolder paths.

## status.md

Rule: `status.md` stays at `.agents-output/status.md`. Its content and format are unchanged.

Rule: no agent is responsible for writing to `status.md` as part of this reorganization.

## \_sample.md

Rule: `.agents-output/_sample.md` is removed. It was a reference example for the old accumulating flat-file format. The new timestamped per-run format does not require a sample file.

Example — after the migration, `ls .agents-output/` shows only the four subfolders and `status.md`. The `_sample.md` file is absent.

## Commit Convention

Rule: all commits produced for issue #23 use the type and scope `ci(agent)`.

Example commit messages:

```plaintext
ci(agent): migrate agent output to subfolders #23
ci(agent): update agent brain files for new output paths #23
ci(agent): update CLAUDE.md to reference new output structure #23
```

## Edge Cases

Rule: if a flat file does not exist at migration time (e.g. `code-ready.md` was never created), no `_initial.md` is created for that subfolder. The subfolder is still created.

Rule: if `business-specifications/` already exists (as in this very run), the existing files in it are not overwritten.

Rule: agents must not fail if a subfolder they need to read from contains no files yet. Reading the latest file by filename sort from an empty subfolder returns no content; the agent proceeds as if given an empty input.

status: ready

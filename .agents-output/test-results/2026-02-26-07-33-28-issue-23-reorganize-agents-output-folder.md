# Test Results — Issue #23: Reorganize .agents-output Folder

## Check 1: Folder structure

Verified that `.agents-output/` contains exactly the expected entries.

Actual contents of `.agents-output/`:
```
business-specifications/
status.md
technical-specifications/
test-results/
user-requests/
```

- `user-requests/` present: PASS
- `business-specifications/` present: PASS
- `technical-specifications/` present: PASS
- `test-results/` present: PASS
- `status.md` present: PASS
- No extra files or directories at root level: PASS

**Result: PASS**

## Check 2: Old flat files removed

Checked for presence of each old flat file under `.agents-output/`:

- `user-requests.md`: ABSENT — PASS
- `specs.md`: ABSENT — PASS
- `code-ready.md`: ABSENT — PASS
- `test-results.md`: ABSENT — PASS
- `_sample.md`: ABSENT — PASS

**Result: PASS**

## Check 3: Migration — initial.md files exist and are non-empty

Checked each subfolder for `initial.md` and its byte size:

| Subfolder                   | initial.md exists | Size (bytes) |
| --------------------------- | ----------------- | ------------ |
| `user-requests/`            | yes               | 3 797        |
| `business-specifications/`  | yes               | 50 026       |
| `technical-specifications/` | yes               | 8 322        |
| `test-results/`             | yes               | 56 133       |

All four `initial.md` files are present and non-empty.

**Result: PASS**

## Check 4: Agent brain files — old path references

Scanned all five agent brain files for patterns matching the old flat paths (`agents-output/user-requests.md`, `agents-output/specs.md`, `agents-output/code-ready.md`, `agents-output/test-results.md`).

Findings:

- `agent-0-orchestrator.md`: no old flat path references — PASS
- `agent-1-specs.md`: no old flat path references — PASS
- `agent-2-coder.md`: no old flat path references — PASS
- `agent-3-tester.md`: no old flat path references — PASS
- `agent-4-git.md`: one match on line 8:
  ```
  - any modification to `.agents-output/specs.md` file must use commit type = `docs`, **except for issue #23** for which it should use `ci(agent)`.
  ```
  This reference is the intentional historical commit-rule exception explicitly called out in the business specification. It is not a live path reference that agents will follow for new runs. **This is expected and acceptable — PASS**

**Result: PASS**

## Check 5: CLAUDE.md — Multi-Agent Pipeline section

Verified that the "Multi-Agent Pipeline" section in `CLAUDE.md` no longer references the old flat file paths and correctly shows subfolder conventions.

### Save path (line 85)
```
Save the request to `.agents-output/user-requests/[timestamp-slug].md`.
```
No old `user-requests.md` reference. PASS

### Agents table (lines 94–97)
All Reads/Writes columns reference subfolder paths with `[timestamp-slug].md` filenames:
- Specification reads `user-requests/[timestamp-slug].md`, writes `business-specifications/[timestamp-slug].md` — PASS
- Coder reads `business-specifications/[timestamp-slug].md`, writes `technical-specifications/[timestamp-slug].md` — PASS
- Tester reads both spec subfolders, writes `test-results/[timestamp-slug].md` — PASS
- Versioning reads `business-specifications/[timestamp-slug].md` and `test-results/[timestamp-slug].md` — PASS

### Pipeline flow diagram (lines 101–118)
Diagram shows subfolder names rather than flat filenames:
```
[user-requests/[timestamp-slug].md]
  Specs agent → business-specifications/[timestamp-slug].md
  Coder agent → technical-specifications/[timestamp-slug].md
 Tester agent → test-results/[timestamp-slug].md
```
No old flat file names present. PASS

Grep for old flat path patterns in CLAUDE.md returned no matches. PASS

**Result: PASS**

## Check 6: Source code untouched

`git diff HEAD -- src/ tests/` produced no output, confirming zero modifications to files under `src/` or `tests/`.

**Result: PASS**

### Test Summary

All six checks passed. The folder restructure is complete: old flat files are removed, the four subfolders each contain `initial.md` with migrated content, agent brain files use the new subfolder paths (with the single intentional legacy exception in `agent-4-git.md`), CLAUDE.md reflects the new subfolder conventions throughout, and no source or test code was touched.

status: passed

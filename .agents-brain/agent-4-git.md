# I am a Versionning Agent

The orchestrator will call me multiple times during the pipeline. Execute only the tasks the orchestrator instructs.

## Commit Rules

- any modification to `.agents-brain` files, or `CLAUDE.md` or `.claude\settings.local.json` must use commit type and scope = `ci(agent)`.
- any modification to `.agents-output/specs.md` file must use commit type = `docs`
- any modification to `.github\workflows` files must use commit type = `ci`
- any other modification to files must follow the conventional commits. Here is a summary:

**Types:** `feat` (new feature), `fix` (bug fix), `docs` (documentation), `style` (formatting, no logic change), `refactor` (code restructure, no feat/fix), `test` (tests), `chore` (maintenance, build, deps), `perf` (performance), `ci` (CI/CD config).

**Format:**

```plaintext
<type>(<optional scope>): <short description>

[optional body]

[optional footer: BREAKING CHANGE: ... or closes #issue]
```

**Rules:**

- Subject line: imperative mood, lowercase, no period, ≤72 chars.
- `BREAKING CHANGE:` in footer (or `!` after type) signals a major version bump.
- Scope is optional but recommended when change is isolated to a module/area.

**Examples:**

```plaintext
feat(auth): add OAuth2 login support
fix(parser): handle null input gracefully
refactor!: drop support for Node 14
docs: update API usage in README
```

## Tasks

### Task 1: Make Sure Local Repository Is Up-to-date

Pull latest `main` to ensure the branch is created from a clean base.

### Task 2: Create new branch

Read `.agents-output/user-requests.md` to understand the nature of the change (feature, fix, or docs).

Create the branch according to `CLAUDE.md` instructions before any other agent writes files.

### Task 3: Commit specs output

Stage `.agents-output/specs.md` and commit it on the current branch with a short message such as:

```
chore: record specs for [short description]
```

Do not push yet.

### Task 4: Commit code changes

Read `.agents-output/code-ready.md` (latest section) for the list of files changed.

Stage those source files plus `.agents-output/code-ready.md` and commit on the current branch with a message summarising the implementation based on `.agents-output/specs.md`. Do not push yet.

### Task 5: Commit test results and push

Read `.agents-output/test-results.md`.

If the last line is `status: passed`:

- Stage the test files introduced or modified and `.agents-output/test-results.md`.
- Write a meaningful commit message that summarises the change based on `.agents-output/specs.md` within Git recommended message length. Put anything beyond the commit message limit into the commit description.
- Commit on the current feature branch — never commit directly to main.
- Push the branch to origin.

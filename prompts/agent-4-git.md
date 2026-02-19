# I am a Versionning Agent

## Task 1: Make Sure Local Repository Is Up-to-date

## Task 2: Create new branch

Once task 1 is complete, ask specification agent the title of the feature or bug.

Create the branch according to `CLAUDE.md` instructions for you.

## Task 3: Commit the work done

Read `.agents/test-results.md`.

If the last line is `status: passed`:

- Stage only the files listed in .agents/code-ready.md and `.agents/` files.
- Write a meaningful commit message that summarises the change based on .agents/specs.md within Git recommended message length. Put anything beyond the commit message limit into the commit description.
- Commit on the current feature branch — never commit directly to main
- Push the branch to origin

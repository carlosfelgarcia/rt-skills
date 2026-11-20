# Ratchet

How a comment audit installs and lowers the ratchet in a stack whose `setup.md` says `Ratchet: yes` (ADR 0013). The repo gets two files: a copy of `<skill>/comment_ratchet.py`, and `.comment-ratchet.json` at its root, the baseline that holds each file's allowed comment lines and the paths the ratchet skips.

## First run

When the repo has no `.comment-ratchet.json`:

1. Copy `<skill>/comment_ratchet.py` into the repo's scripts folder (`scripts/`, `Scripts/` or `bin/`), or into `scripts/` when it has none. `<repo script>` below is its path.
2. Pick the excludes: vendored and generated code the repo commits, such as `Pods/*`, `Carthage/*` or `Vendor/*`.
3. Run `<script> init --exclude <glob>` once per glob, after the audit's edits, so the baseline starts at today's lower counts.
4. Wire the check into everything the repo already has:
   - `.pre-commit-config.yaml`: add a `repo: local` hook with `id: comment-ratchet`, `entry: python3 <repo script> check`, `language: system` and `pass_filenames: false`.
   - A pre-commit hook in the folder `git config core.hooksPath` names, or in `.husky/`: add `python3 <repo script> check --lower && git add .comment-ratchet.json`.
   - A CI workflow that runs the tests: add a step that runs `python3 <repo script> check`.
   - None of these: create `.githooks/pre-commit`, executable, holding `#!/bin/sh`, `set -e` and the hook line above, then run `git config core.hooksPath .githooks`. The report says each clone runs that `git config` once.

## Later runs

When the repo's copy of the script differs from `<skill>/comment_ratchet.py`, replace it with the plugin's copy.

Run `<script> check --lower`. A full audit only removes comments, so it passes. In a diff audit, a file can fail because the user's work added comments the audit kept. When every comment in each failing file is one the audit judged, run `<script> init` to raise those files to their counts. A file that fails for a comment with no row in `judgements.md` goes back to step 3 of `SKILL.md` for that comment.

## Commit

A full audit commits everything this step changed in one commit, after the last batch. A diff audit leaves it uncommitted, with the rest of its edits.

**Done when** `<script> check` exits 0, and the report can say whether the check is installed and where it runs.

# Full audit

A full audit judges every comment in the repo, batch by batch. It replaces steps 2 to 5 of [`SKILL.md`](SKILL.md) and continues with its step 6, the report. [`judging.md`](judging.md) and [`edits.md`](edits.md) apply throughout. Start each step only when the one before is done.

## 0. Branch

Stop with one sentence when `git status --porcelain` prints anything: the batch commits would sweep that work in. On the default branch, found as the Branch work row of `<review folder>/target.md` finds `<default>`, `git switch -c chore/comment-audit-<YYYYmmdd>`, adding `-2`, `-3` when the name is taken; on any other branch, stay on it.

**Done when** the tree is clean and the branch is not the default branch.

## 1. List and batch

Run `<script> list` into `<run folder>/comments.tsv`. Split the rows into batches by directory: one batch per top-level source folder, such as a target, module or package; a batch with more than 200 rows splits by its subfolders. Write `<run folder>/batches.md`: each batch's name, its files, and its row count.

**Done when** every row of `comments.tsv` is in exactly one batch.

## 2. Judge

One agent per batch, all started in one message: one `Agent` call each, `subagent_type` `rt-skills:rt-comment-auditor`, no model override. Its prompt: the stack, the repo root, the batch's name and files, its rows from `comments.tsv`, then "Read `<skill>/auditor-brief.md` and `<skill>/judging.md`, then follow them. Return the judgements table in the shape `judging.md` defines, and nothing else." Write each return verbatim to `<run folder>/judgements-<batch>.md`.

Compare each table's rows with the batch's rows in `comments.tsv`. Send the rows a table misses to a new agent.

**Done when** every row of `comments.tsv` has a category, an action and an evidence line.

## 3. Ask

Merge issues that two batches raise for the same hack, and ADRs that record the same decision. Show one judgements table per batch, then each issue and ADR with the comments it absorbs, as step 4 of `SKILL.md` says. Wait for the user's answer.

**Done when** the user has approved the batches and rows to act on, or rejected them all, which ends the run at step 6 of `SKILL.md`, the report.

## 4. Edit, batch by batch

For each approved batch, apply its rows as `edits.md` says, run its checks, and commit the batch alone in the repo's commit style, naming the batch and what it removed. An ADR or issue shared by several batches goes in the first batch that needs it.

**Done when** every approved batch has a commit, and `git status --porcelain` prints nothing.

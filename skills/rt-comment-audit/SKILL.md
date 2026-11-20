---
name: rt-comment-audit
description: Audit the comments a branch's changes add or sit inside (`diff`), or every comment in the repo (`codebase`), and move what each one says into the code, an ADR or an issue. In your own projects, a ratchet stops new comments.
disable-model-invocation: true
argument-hint: "<diff | codebase> [stack]"
---

# RT comment audit

Code comments are banned (ADR 0013). A **comment audit** judges each comment as a **tautology**, **stale**, an **excuse** or a **decision record**, and moves what it says to a place that can be checked: the code's names, structure or tests, an ADR, or an issue. Then the comment goes. In a stack whose `setup.md` says `Ratchet: yes`, a **ratchet** stops new comments from arriving.

A **diff audit** (`diff`) covers the comments the branch's changes add or sit inside, committed or not, and commits nothing: the user commits the cleanup with their work. A **full audit** (`codebase`) covers every comment, batch by batch, one commit per batch.

`<skill>` below is this skill's base directory, `<review folder>` is `<skill>/../rt-code-review/`, and `<script>` is `python3 <skill>/comment_ratchet.py --root <repo root>`. Always run the plugin's copy of the script, never a copy inside the repo.

## 1. Set up

The arguments, in any order: `diff` or `codebase`, which is required, and an optional stack, a folder name in `<review folder>/stacks/`. Stop with one sentence that lists both modes and the stacks when the mode is missing or an argument is neither.

Pick the stack as the `Stack` section of `<review folder>/target.md` says, with `git ls-files` plus untracked files as the list-files command; with none or several, stop and ask for the stack as an argument. Read its `stack.md` and the `Ratchet` line of its `setup.md`. Record `PRE_AUDIT=$(git rev-parse HEAD)`, make the run folder `/tmp/rt-comment-audit/runs/<repo>-<YYYYmmdd-HHMMSS>/`, and write `<script> count` to `count-before.json` in it.

With `codebase`, follow [`full-audit.md`](full-audit.md) now, in place of steps 2 to 5.

**Done when** the stack, ratchet setting, `PRE_AUDIT` and run folder are set, and `count-before.json` is written.

## 2. List the comments

Set `BASE=$(git merge-base <default> HEAD)`, with `<default>` as the Branch work row of `<review folder>/target.md` finds it. Stop with one sentence when `git diff BASE` and `git ls-files --others --exclude-standard` both print nothing.

Run `<script> list --base BASE` into `<run folder>/comments.tsv`: each Swift and Python comment the diff adds or sits inside, with its kind (`comment`, `doc`, `directive`, `license`, `shebang`, `encoding`). For every other source file the diff touches, read its diff and add each comment inside a changed hunk as a row, kind `comment`.

**Done when** every comment inside the diff's changed hunks has a row.

## 3. Judge

Read [`judging.md`](judging.md). Judge every row and write the judgements table it defines to `<run folder>/judgements.md`.

**Done when** every row of `comments.tsv` has a category, an action and an evidence line.

## 4. Ask

Show the judgements table, then each issue and ADR the actions would create, with its title and the comments it absorbs. When an Excuse would file an issue and the repo has no `docs/agents/issue-tracker.md`, ask where its issues go. Wait for the user's answer. A row the user rejects stays, as **kept by you**.

**Done when** the user has approved the rows to act on, or rejected them all, which ends the run at step 7.

## 5. Edit

Read [`edits.md`](edits.md) and apply every approved row as it says. Leave every edit uncommitted.

**Done when** every approved row is applied, or reverted with its reason, the checks `edits.md` names have a result, and every issue is filed with its URL recorded.

## 6. Ratchet

With `Ratchet: yes`, follow [`ratchet.md`](ratchet.md). With `Ratchet: no`, the repo gets no script and no baseline.

**Done when** `ratchet.md` is done, or the setting is `no`.

## 7. Report

Write `<script> count` to `<run folder>/count-after.json`. **Lines shed** is the fall in `own_line`; trailing comments go without shedding a line. **Not yet audited** is the `total` after, less the lines of every kept comment. Reply with only this, leaving out empty sections:

```
<diff audit | full audit> · <stack> · <branch> · <PRE_AUDIT short>[..<HEAD short>]

| Category | Comments | Done |
|---|---|---|
| Tautology | <n> | deleted |
| Stale | <n> | deleted |
| Excuse | <n> | deleted, <n> issues |
| Decision record | <n> | <n> ADRs, <n> into the code |
| Kept | <n> | <n> exceptions, <n> unsure, <n> kept by you |

Lines shed: <n> · comment lines <total before> → <total after>
Left: <total after> comment lines: exceptions <n>, unsure <n>, kept by you <n>, not yet audited <n>

ADRs:
- `<path>`: <title>

Issues:
- <url>: <title>

Kept:
- `<file:line>` exception: <why no name, structure or test can carry it>
- `<file:line>` unsure: <what the evidence did not settle>
- `<file:line>` kept by you

Ratchet: <installed, wired into <hook | CI> | lowered <n> files | not wired: <reason> | not used for this stack>

Checks:
- Ran: <command>: <passed | failed>
- Not run: <check>: <reason>. Run: `<command>`

Uncommitted: <each file this audit changed>
```

`Uncommitted` is for a diff audit only. End with `Next step: review the changes and commit them with your work.` for a diff audit, or `Next step: run /rt-code-review on this branch, then push when ready.` for a full audit.

**Done when** every count in the reply comes from the count files or the judgements, and every check is under `Ran` or `Not run`.

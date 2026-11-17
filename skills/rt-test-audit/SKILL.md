---
name: rt-test-audit
description: Audit the existing tests under a path in a Swift app or pipeline package, removing the ones that cannot catch a defect or repeat proof another test gives, with the production code only they use. Add `campaign` to account for every test.
disable-model-invocation: true
argument-hint: "<path> [stack] [campaign]"
---

# RT test audit

A **test audit** removes or repairs existing tests that cannot catch a defect or that repeat proof another test already gives, and deletes the **test-only seams** they needed. Each **contract** has one **owner** and one **keeper**, the test that proves it. The audit edits in **batches**, one owner per batch and one commit per batch. Commits stay local; the user pushes.

An audit returns a few certain candidates; a test you are unsure of stands. A **campaign** (the `campaign` argument) accounts for every test under the path instead.

`<skill>` below is this skill's base directory, and `<review folder>` is `<skill>/../rt-code-review/`.

## 1. Resolve the scope

The first argument is the path. After it, in any order: a stack (a folder name in `<review folder>/stacks/`) and the word `campaign`. Stop with one sentence when the path is missing or does not exist, another argument is neither, `git status --porcelain` prints anything, or the current branch is the default branch.

Pick the stack as the `Stack` section of `<review folder>/target.md` says, with `git ls-files` as the list-files command. With none or several, stop, say which matched, and ask for the stack as an argument. Read `<review folder>/stacks/<stack>/stack.md`.

Record `PRE_AUDIT=$(git rev-parse HEAD)` and make the run folder `/tmp/rt-test-audit/runs/<repo>-<branch>-<YYYYmmdd-HHMMSS>/` (`/` in the branch becomes `-`). It holds every file this run writes, so a long run can resume from it.

With `campaign`, follow [`campaign.md`](campaign.md) now, in place of steps 2 to 5.

**Done when** the path, stack, mode, `PRE_AUDIT` and run folder are set.

## 2. Baseline

Read [`proof.md`](proof.md) and run the baseline it describes.

**Done when** every test file under the path has a recorded pass, fail or not run.

## 3. Find the candidates

Read [`judging.md`](judging.md) and the rule files it names. Read every test file under the path in full. Mark each test that `judging.md` condemns **Fix**, **Consolidate** or **Delete**, with every evidence line it asks for. A test that fails at baseline goes to `Defects` in `proof.md`, never to the candidates.

Group the candidates into batches by owner, and write them to `<run folder>/candidates.md`.

**Done when** every candidate has a mark, a complete evidence block and a batch.

## 4. Ask

Show the candidates, one table per batch: the test (`file:line` and name), its mark, the contract, and the keeper or the reason no contract exists. Name each test-only seam its batch would delete. Wait for the user's answer, and drop what they reject.

**Done when** the user has approved the batches to edit, or rejected them all, which ends the run at step 6.

## 5. Edit, batch by batch

For each approved batch:

1. Apply each mark. **Fix** rewrites the assertion as `<review folder>/rules/test.md` says. **Consolidate** first moves the test's distinct assertion into the keeper, then removes the test. **Delete** removes it.
2. Delete each test-only seam whose last caller was a removed test, and each fixture, helper or support file that nothing uses any more.
3. Run the batch's tests and keepers as `proof.md` says. On a failure, make one repair; when it still fails, `git restore .`, and the batch is **held** with the failure.
4. Commit the batch alone, naming its owner and what it removed, in the repo's commit style.

After the last batch, run the whole suite once as `proof.md` says.

**Done when** every approved batch has a commit or is held with its failure, the full run has a result, and `git status --porcelain` prints nothing.

## 6. Report

Count the lines with `git diff --numstat PRE_AUDIT`: files the stack's test framework collects, with their fixtures and helpers, are tests and support; the rest are production. Reply with only this, leaving out empty sections:

```
<path> · <stack> · <audit | campaign> · <PRE_AUDIT short>..<HEAD short>

| Batch | Commit or held | Removed | Fixed | Seams deleted |
|---|---|---|---|---|
| <owner> | <short SHA | held: failure> | <n> | <n> | <names> |

Lines: production <±n> · tests and support <±n>

Kept on purpose:
- `<file:line>` <test>: <the contract that keeps it>

Checks:
- Ran: <command>: <passed | failed>
- Not run: <check>: <reason>. Run: `<command>`

Defects:
- `<file:line>` <test>: <fix commit with its control, or follow-up>

Follow-ups:
- <an ownership rule worth adding to the repo's CLAUDE.md, or a discrepancy outside the audit>

Next step: run `/rt-code-review` on this branch, then push when ready.
```

`Kept on purpose` lists the tests that matched a pattern but passed the retention bar in `judging.md`.

**Done when** every batch is in the table and every check is under `Ran` or `Not run`.

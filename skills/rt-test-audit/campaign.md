# Campaign

A **campaign** is a test audit in which every test under the path ends in a **ledger**, and a preservation review checks that no contract lost its only proof. It replaces steps 2 to 5 of [`SKILL.md`](SKILL.md) and ends with its step 6. [`judging.md`](judging.md) and [`proof.md`](proof.md) apply throughout. Start each step only when the one before is done.

Every agent below is one `Agent` call, `subagent_type` `rt-skills:rt-test-auditor`, no model override. Its prompt is: the stack, the repo root, `PRE_AUDIT`, the batch's owner and test files, the step's inputs, a role line, then "Return <what> in the shape the file defines, and nothing else." Start a step's agents in one message. Write each return verbatim to the run folder file the step names.

## 1. Baseline

Count the lines of tests and support, and of production, under the path, as step 6 of `SKILL.md` splits them, into `<run folder>/baseline.md`. Run the baseline as `proof.md` says.

**Done when** every test file under the path has a recorded pass, fail or not run, and both line counts are recorded.

## 2. Batches

Split the tests into batches along production owners, not file names or folders. Write `<run folder>/batches.md`: each batch's owner and its test files.

**Done when** every test file under the path is in exactly one batch.

## 3. Ledgers

One agent per batch. Role line: "You write the ledger. Read `<skill>/auditor-brief.md` (Ledger), `<skill>/judging.md`, `<review folder>/rules/test.md`, `<review folder>/stacks/<stack>/test.md` and `<review folder>/stacks/<stack>/stack.md`, then follow them." Write `<run folder>/ledger-<batch>.md`.

Count the test declarations in each batch's files yourself, and compare with the ledger's rows. Send a ledger that misses one back to a new agent with the missing names.

**Done when** every declaration in every batch has a mark and an evidence line.

## 4. Layer plans

One agent per batch, with its ledger. Role line: "You write the layer plan. Read `<skill>/auditor-brief.md` (Layer plan) and the files the Ledger section names, then follow them." Write `<run folder>/plan-<batch>.md`.

**Done when** each plan names its retired files, a keeper for every contract, the assertions to carry into keepers, and the test-only seams it unlocks.

## 5. Ask

Show each batch's plan: the retired files, the keeper per contract, the seams to delete, and the ledger's Fix rows. Wait for the user's answer, and drop what they reject.

**Done when** the user has approved the batches to edit, or rejected them all, which ends the campaign at step 6 of `SKILL.md`.

## 6. Cutover

Edit each approved batch as step 5 of `SKILL.md` says, applying its plan. A change to a shared fixture or support file goes in the first batch that needs it, and later batches build on it. Register a moved test wherever the repo lists its tests, such as CI config.

**Done when** step 5 of `SKILL.md` is done for every approved batch.

## 7. Preservation review

One agent per committed batch, with its plan and the output of `git diff PRE_AUDIT -- <the batch's files>`. Role line: "You review preservation. Read `<skill>/auditor-brief.md` (Preservation review) and the files the Ledger section names, then follow them." Write `<run folder>/preservation-<batch>.md`.

Restore each gap in its keeper, in its own commit, or reject it with the source line that shows the contract still has proof. For each restored contract, run a mutation as `proof.md` says.

**Done when** every gap is restored or rejected with source evidence, and every restored contract has a mutation that went red.

## 8. Defects

Handle each baseline failure as `Defects` in `proof.md` says.

**Done when** each fixed defect has a red control and a green run on the same command, or is a follow-up.

## 9. Report

Follow step 6 of `SKILL.md`, and add before `Next step`:

```
Baseline: tests and support <n> lines, production <n> lines → tests and support <n>, production <n>

Keepers:
- <batch>: <contract> → `<keeper file>`; retired <files>

Preservation:
- <batch> `<file:line>`: <gap> → <restored in SHA, mutation <what> went red | rejected: <source line>>
```

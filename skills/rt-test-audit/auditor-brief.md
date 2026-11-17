# Auditor brief

You are one auditor in an `rt-test-audit` campaign, with one batch: the tests of one owner. Your role line names your section. You read code and git history; the main session runs every test and makes every edit.

Read each test file of the batch in full, parameter tables included. A parametrized test (`@pytest.mark.parametrize`, Swift Testing `arguments:`) is one declaration unless its rows need different marks; then each row is one.

## Ledger

Mark every test declaration in the batch as `judging.md` says: Retain, Fix, Consolidate or Delete. A Retain names the contract and the defect it catches. A Retain that only moves to a better-named file stays Retain, with the move noted. Every other mark carries the evidence block of `judging.md`.

```
# Ledger: <batch>

| Test | Mark | Contract | Evidence |
|---|---|---|---|
| `<file:line>` <name> | <Retain | Fix | Consolidate | Delete> | <contract, or none> | <one line> |

## <file:line> <name>
- <each line of the evidence list in judging.md, for every row but a Retain>
```

**Done when** every declaration has a row, and every row but a Retain has its block.

## Layer plan

The ledger judges one test at a time; the plan looks for a redundant **layer**: a whole suite that replays what a stronger suite proves, such as several suites driving a shared helper through a mock around one that runs it for real. Name the keeper for each contract, preferring the real boundary with fake I/O over a mocked collaborator. Correct any ledger mark this pass shows is wrong.

```
# Layer plan: <batch>

Retired files:
- `<file>`: <why its contracts are proven elsewhere>

Keepers:
- <contract> → `<keeper file or test>`

Carried assertions:
- `<file:line>` <assertion> → `<keeper>`

Seams unlocked:
- `<file:line>` <seam>: <its last callers are the retired tests>

Ledger corrections:
- `<file:line>` <name>: <old mark> → <new mark>, because <reason>
```

**Done when** the plan names its retired files, a keeper for every contract in the ledger, the assertions to carry, and the seams unlocked.

## Preservation review

Compare the coverage the diff removed with the keepers that remain. Report two kinds of **gap**: a contract whose only proof the diff removed, and a new or carried assertion that cannot fail, such as a rejection the production code never reaches. Every removed assertion is either covered by a keeper you name, or a gap.

```
# Preservation: <batch>

- `<removed file:line>` <contract>: covered by `<keeper file:line>`
- GAP `<removed file:line>` <contract>: <why no keeper proves it>
- GAP `<keeper file:line>` <assertion>: <why it cannot fail>
```

**Done when** every assertion the diff removed has a line.

---
name: rt-fix-findings
description: Fix the findings of an rt-code-review report or of pasted GitHub bot comments that exist and score at or above a threshold, then re-review the branch and summarise.
disable-model-invocation: true
argument-hint: "[stack] [min=<1-10>] [report path | pasted bot findings]"
---

# RT fix findings

A **fix run** fixes the findings that exist and score at or above the **threshold**, re-reviews once, and ends with a summary and one next step. Each finding ends **Fixed**, **Dismissed**, **Held** or **Skipped**. Fixes stay in local commits; the user pushes.

The **review folder** is `<this skill's base directory>/../rt-code-review/`; in its files, "this skill's base directory" and relative links mean that folder. Read its `findings-file.md` first.

## 1. Resolve the source

A first word that names a folder in `<review folder>/stacks/` is the stack. A next word `min=<n>` (1 to 10) is the threshold; another `min=` value stops the run. The default is 4, so Nits are skipped. The rest:

| The rest | Run |
|---|---|
| Nothing | **Report run** on the newest findings file for this branch |
| Path to an existing `.html` or `.findings.md` | **Report run** on that findings file (`.html` → `.findings.md`) |
| One word ending in `.html` or `.findings.md` that does not exist | Stop, and name it |
| Any other text | **Bot run** on that text |

Newest findings file, `<repo>` being the folder name of `git rev-parse --show-toplevel`:

```
grep -lxF -- "- Repo: <repo>" /tmp/rt-code-review/*.findings.md | xargs -r grep -lxF -- "- Branch: <current branch>" | xargs -r ls -t | head -1
```

A report run with none stops and asks for `/rt-code-review`. A bot run uses it when it exists.

## 2. Check the branch

Stop with one sentence when: `git status --porcelain` prints anything; the current branch is empty or the default branch; a report run's findings file names another `Branch`; or, in a bot run, `git fetch origin <branch>` or `git merge-base --is-ancestor FETCH_HEAD HEAD` fails (the local branch must hold what the bots read; use only the accounts `gh` and `git` are on). Then record `PRE_FIX=$(git rev-parse HEAD)`.

## 3. Build the target block

| Run | BASE | Source |
|---|---|---|
| Report | The findings file's `Base` | `findings file` |
| Bot | `origin/<baseRefName>` from `gh pr view --json baseRefName`, after fetching it | `PR` |
| Bot, `gh` fails | The newest findings file's `Base` | `findings file` |
| Bot, neither | None: use Branch work | `default branch` |

The stack is the argument, else the findings file's `Stack`, else detection. Follow step 1 of `<review folder>/SKILL.md` with BASE as the ref (none for Branch work) and the stack; stop when it stops.

## 4. Collect the findings

**Report run**: read each finding with the `Score` under its `Status`. When `Head` equals `PRE_FIX` and `Uncommitted` is `no`, statuses stand and only Unverified findings go to a verifier. Otherwise every finding goes to a verifier, with its reviewer's block alone.

**Bot run**: follow [`bot-findings.md`](bot-findings.md).

The starting fix context is the findings file's `Fix context`, when it has one.

## 5. Verify

Start one verifier per marked finding, in one message, as step 3 of `<review folder>/SKILL.md` says, including its host probes. The prompt holds the finding's block alone: no earlier verdict, fix context or other bot's opinion.

## 6. Sort

The first matching row gives the outcome; the score is the one after step 5.

| Status and score | Outcome |
|---|---|
| Not worth fixing, Refuted | **Dismissed** |
| Any other, scored below the threshold | **Skipped**: `Score <n> below threshold <t>` |
| Confirmed (Proven), Regraded (Proven) | **To fix** |
| Any other | **Held** |

## 7. Fix

One finding at a time, highest score first, then by ID. A verifier's `Fix` replaces the reviewer's.

1. Read the code at the head. When an earlier fix of this run already solved it, it is **Fixed** with that commit.
2. Make the smallest change that solves it. When it needs more than the finding describes, such as a redesign, it is **Held** with that reason: `git restore .` and delete any file you created.
3. When the fix changes behavior and the repo already tests that module, add or update a test in the same commit. Set up no test infrastructure.
4. Commit it alone, with the finding ID and title, in the repo's commit style.

## 8. Run the fix checks

With commits since `PRE_FIX`, run what `Fix checks` in `<review folder>/stacks/<stack>/setup.md` allows, and record each command and result, or why it could not run. A failure belongs to the fixes when it names a file they changed, a test of one, or a caller. Make one repair in its own commit and rerun. When a failure of the fixes remains, keep every commit and record it: step 9 skips the re-review. Note other failures and continue.

## 9. Re-review

Build the **fix context**: the starting rows, then one row per finding of this run, `Run` being one more than the highest starting row, or 1. A bot finding that repeats an earlier one has the reason `Repeats <ID>`. In a bot run with a findings file, also add a row for each of its findings: its `Outcome` line when it has one, else Dismissed with the verifier's reason when dismissed, Skipped when it scores below the threshold, and Held with `No fix run handled it` otherwise.

In a report run, write each finding's result into the findings file as its `Outcome` line, even when this run stops here.

With no commits since `PRE_FIX`, or a remaining failure of the fixes, skip the re-review and record why. Otherwise follow all of `<review folder>/SKILL.md` for BASE and the stack, with this fix context.

## 10. Summarise

Reply with only this, leaving out empty sections. Re-review IDs read `re-review Q1`.

```
<branch> · <report | bot> run · base <BASE> (<source>) · threshold <t>

Stopped: <only with a remaining failure of the fixes: the command and failure>

| Finding | Score | Source | Outcome | Commit or reason |
|---|---|---|---|---|
| <ID> | <n>/10 | <lane, or the bots> | <outcome> | <short SHA or reason> |

Checks:
- Ran: <command>: <passed | failed>
- Not run: <check>: <reason>

Re-review: <"skipped:" and why, or the rt-code-review counts table>
- re-review <ID> [<score>/10, <reviewer>] `file:line`: <What>, for each new finding at or above the threshold
- Skipped below the threshold: <n>

Reversibility: <level; when not Revert-safe, one line per trigger>

Manual checks:
- <what only the user can do>

Notes dropped: <n>

Suggested replies, to post after you push:
- <ID>: <one sentence for the bot>

Reports: <source report> · <re-review report>

Next step: <one recommendation>
```

Show each bot finding that matched an earlier finding with that ID, and note when the earlier one is Held or open. The next step is the first that applies:

1. A failure of the fixes remains: repair it.
2. The re-review has a finding at or above the threshold: run `/rt-fix-findings <re-review report>`, with the same `min=`.
3. No commits and no findings file: run `/rt-code-review`.
4. Held or open findings, or manual checks: name them and ask the user.
5. Otherwise: push when ready; when One-way, first name what a revert cannot undo.

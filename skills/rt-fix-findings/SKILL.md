---
name: rt-fix-findings
description: Fix the findings of an rt-code-review report or of pasted GitHub bot comments that exist and score at or above a threshold, then re-review the branch and summarise.
disable-model-invocation: true
argument-hint: "[stack] [min=<1-10>] [report path | pasted bot findings]"
---

# RT fix findings

A **fix run** fixes the findings that exist and score at or above the **threshold**, re-reviews once, and ends with a summary and one next step. Each re-review finding has an **origin** (ADR 0009), so a fix run fixes what fixes added or failed to solve and holds what earlier reviews missed. Each finding ends **Fixed**, **Dismissed**, **Held** or **Skipped**. Fixes stay in local commits; the user pushes.

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

A report run with none stops and asks for `/rt-code-review`. A bot run uses it when it exists, and reads [`bot-findings.md`](bot-findings.md) now: its sections add to steps 2, 3, 4, 9 and 11.

## 2. Check the branch

Stop with one sentence when: `git status --porcelain` prints anything; the current branch is empty or the default branch; a report run's findings file names another `Branch`; or a bot run's branch check fails. Then record `PRE_FIX=$(git rev-parse HEAD)`.

The **fix base** is the findings file's `Fix base`, else `PRE_FIX`. When `git merge-base --is-ancestor <Fix base> HEAD` fails, as after a rebase, use `PRE_FIX` and note it for step 11. The starting **fix commits** are the findings file's `Fix commits`, else none. **Other commits** are those in `git rev-list <fix base>..PRE_FIX` that are not fix commits.

## 3. Build the target block

In a report run, BASE is the findings file's `Base`, with source `findings file`. A bot run takes BASE and source from `bot-findings.md`.

The stack is the argument, else the findings file's `Stack`, else detection. Follow step 1 of `<review folder>/SKILL.md` with BASE as the ref (none for Branch work) and the stack; stop when it stops. In a report run whose findings file has a `Fix base`, add the fix base to the target block.

## 4. Collect the findings

**Report run**: read each finding with the `Score` and `Origin` under its `Status`. When `Head` equals `PRE_FIX` and `Uncommitted` is `no`, statuses and origins stand and only Unverified findings go to a verifier. Otherwise every finding goes to a verifier, with its reviewer's block alone, less its `Origin` line. A new verdict settles the origin again for a finding that has one, as the `Origin` section of `findings-file.md` says; a finding with none keeps none.

**Bot run**: follow the `Collect the findings` section of `bot-findings.md`.

The starting fix context is the findings file's `Fix context`, when it has one.

## 5. Verify

Start one verifier per marked finding, in one message, as step 3 of `<review folder>/SKILL.md` says, including its host probes. The prompt holds the finding's block alone: no earlier verdict, fix context or other bot's opinion.

## 6. Sort

The first matching row gives the outcome; the score is the one after step 5.

| Status and score | Outcome |
|---|---|
| Not worth fixing, Refuted | **Dismissed** |
| Any other, scored below the threshold | **Skipped**: `Score <n> below threshold <t>` |
| Origin Missed (not settled) | **Held**: `Origin not settled` |
| Origin Missed | **Held**: `Missed by the first review` |
| Origin `Failed fix of` row R, where R's own `Origin` is a Failed fix, or another fix context row already reads `Failed fix of R` | **Held**: `Fix failed twice` |
| Confirmed (Proven), Regraded (Proven) | **To fix** |
| Any other | **Held** |

A finding with no origin, from a first review or a bot, skips the three origin rows. A Failed fix that this table does not hold as `Fix failed twice` is a **first Failed fix**.

**Done when** every finding has exactly one outcome.

## 7. Fix

One finding at a time, highest score first, then by ID. A verifier's `Fix` replaces the reviewer's.

1. Read the code at the head. When an earlier fix of this run already solved it, it is **Fixed** with that commit.
2. Make the smallest change that solves it. When it needs more than the finding describes, such as a redesign, it is **Held** with that reason: `git restore .` and delete any file you created.
3. When the fix changes behavior and the repo already tests that module, add or update a test in the same commit. Set up no test infrastructure.
4. Commit it alone, with the finding ID and title, in the repo's commit style.

**Done when** every To fix finding is Fixed, with a commit, or Held, with a reason, and `git status --porcelain` prints nothing.

## 8. Run the fix checks

With commits since `PRE_FIX`, run what `Fix checks` in `<review folder>/stacks/<stack>/setup.md` allows, and record each command and result, or why it could not run. A failure belongs to the fixes when it names a file they changed, a test of one, or a caller. Make one repair in its own commit and rerun. When a failure of the fixes remains, keep every commit and record it: step 10 skips the re-review. Note other failures and continue.

**Done when** every check has a result or a reason it did not run, and every failure belongs to the fixes or is noted.

## 9. Record

Build the **fix context** in the shape `findings-file.md` gives: the starting rows, with `—` added as the `Origin` of a row that has none, then one row per finding of this run, `Run` being one more than the highest starting row, or 1. A row's `Origin` is its finding's, or `—`. A bot run adds the rows `bot-findings.md` gives.

The **fix commits** become the starting fix commits plus `git rev-list PRE_FIX..HEAD`. In a report run, write each finding's result into the findings file as its `Outcome` line, its origin as its `Origin` line when step 4 settled it again, and this run's fix base and fix commits as its `Fix base` and `Fix commits` lines. A later run then keeps the fix base when this run skips its re-review.

**Done when** every finding of this run has its fix context row, and in a report run the findings file holds every `Outcome` line and this run's `Fix base` and `Fix commits`.

## 10. Re-review

With no commits since `PRE_FIX`, or a remaining failure of the fixes, skip the re-review and record why. Otherwise follow all of `<review folder>/SKILL.md` for BASE and the stack, with this fix context, the fix base and the fix commits.

**Done when** the re-review's report is shown and its findings file is written, or the skip and its reason are recorded.

## 11. Summarise

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
Added by a fix:
- re-review <ID> [<score>/10, <reviewer>] `file:line`: <What>, for each new finding at or above the threshold with this origin
Failed fix:
- re-review <ID> [<score>/10, <reviewer>] `file:line`: <What> (of <Run> <Finding>; <"retry" | "held: failed twice">)
Missed (held):
- re-review <ID> [<score>/10, <reviewer>] `file:line`: <What>, "not settled" when so
Skipped below the threshold: <n>

Fix base: <short SHA>. <only with other commits: "No fix run made <n> commits since it, so 'Added by a fix' may include their changes."> <only when step 2 reset it: "The old fix base is not in the branch, so this run's PRE_FIX replaced it.">

Reversibility: <level; when not Revert-safe, one line per trigger>

Manual checks:
- <what only the user can do>

Notes dropped: <n>

Suggested replies, to post after you push:
- <ID>: <one sentence for the bot>

Reports: <source report> · <re-review report>

Next step: <one recommendation>
```

**Done when** every finding is in the table, every check is under `Ran` or `Not run`, and the reply ends with exactly one next step, the first that applies:

1. A failure of the fixes remains: repair it.
2. The re-review has an Added by a fix finding or a first Failed fix at or above the threshold, and this run's `Run` is below 3: run `/rt-fix-findings <re-review report>`, with the same `min=`.
3. Such a finding remains and this run's `Run` is 3 or more: say the branch has had three fix runs, name the findings, and ask the user. A run they start by hand still works.
4. No commits and no findings file: run `/rt-code-review`.
5. Held or open findings, Missed re-review findings, or manual checks: name them and ask the user.
6. Otherwise: push when ready; when One-way, first name what a revert cannot undo.

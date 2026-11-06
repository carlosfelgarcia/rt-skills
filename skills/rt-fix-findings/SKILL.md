---
name: rt-fix-findings
description: Fix the findings of an rt-code-review report or of pasted GitHub bot comments when they exist and are worth fixing, then re-review the branch and summarise the outcome.
disable-model-invocation: true
argument-hint: "[stack] [report path | pasted bot findings]"
---

# RT fix findings

A **fix run** takes one set of findings, fixes the ones that exist and are worth fixing, re-reviews the branch once, and ends with a summary and one next step. Every finding ends as **Fixed**, **Dismissed** or **Held**. Fixes stay in local commits: pushing is the user's decision.

The **review folder** is `<this skill's base directory>/../rt-code-review/`. Read `findings-file.md` there before step 1: it defines the findings file and the fix context. Whenever you follow a file from the review folder, its "this skill's base directory" and its relative links mean the review folder.

## 1. Resolve the source

Read the arguments. A first word that is a folder name in `<review folder>/stacks/` is the stack. The rest is the source:

| The rest | Run |
|---|---|
| Nothing | **Report run**, on the newest findings file for this branch |
| A path to an existing `.html` or `.findings.md` file | **Report run**, on that findings file. For `.html`, use the path with `.findings.md` in place of `.html` |
| One word that ends in `.html` or `.findings.md`, for a file that does not exist | Stop, and name the path |
| Any other text | **Bot run**, on that text |

To find the newest findings file, with `<repo>` as the folder name of `git rev-parse --show-toplevel`:

```
grep -lxF -- "- Repo: <repo>" /tmp/rt-code-review/*.findings.md | xargs -r grep -lxF -- "- Branch: <current branch>" | xargs -r ls -t | head -1
```

A report run stops when there is no findings file, and asks the user to run `/rt-code-review`. A bot run uses the newest findings file when there is one, and continues without one when there is none.

**Done when** the run type, the source and the stack argument (if any) are known.

## 2. Check the branch

Stop, and tell the user why in one sentence, when any of these holds:

- `git status --porcelain` prints anything.
- `git branch --show-current` prints nothing, or the default branch.
- This is a report run and the findings file's `Branch` is not the current branch.
- This is a bot run, and `git fetch origin <current branch>` fails, or `git merge-base --is-ancestor FETCH_HEAD HEAD` fails. The local branch must hold what the bots read. Use only the account `gh` and `git` are already on.

Record `PRE_FIX=$(git rev-parse HEAD)`.

**Done when** every check passes and `PRE_FIX` is recorded.

## 3. Build the target block

Pick BASE, and record its source for the summary:

| Run | BASE | Source |
|---|---|---|
| Report run | The findings file's `Base` | `findings file` |
| Bot run | `origin/<baseRefName>` from `gh pr view --json baseRefName`, after `git fetch origin <baseRefName>` | `PR` |
| Bot run, when `gh` fails | The `Base` of the newest findings file | `findings file` |
| Bot run, with neither | None: step 9 and this step use Branch work | `default branch` |

The stack is the stack argument, else the findings file's `Stack`, else what detection finds.

Follow step 1 of `<review folder>/SKILL.md` with BASE as the ref and the stack as the second argument, or with the stack alone when there is no BASE. Stop there when it stops. Reuse the resulting **target block** in step 5.

**Done when** the target block is complete.

## 4. Collect the findings

**Report run.** Read every finding in the findings file. When `Head` equals `PRE_FIX` and `Uncommitted` is `no`, each finding keeps its status. Only the Unverified ones go to a verifier. Otherwise the code has moved, and every finding goes to a verifier, with its reviewer's block alone.

**Bot run.** Read [`bot-findings.md`](bot-findings.md) and follow it.

In both runs, the starting fix context is the `Fix context` section of the findings file, when it has one.

**Done when** every finding has an ID and is either settled or marked for a verifier.

## 5. Verify

Start one `rt-skills:rt-verifier` per marked finding, all in one message. Use the prompt in step 3 of `<review folder>/SKILL.md`, apply each verdict by its table, and run host probes as its `Host probes` section says. The prompt holds the finding's block alone: nothing from an earlier verdict, a fix context or another bot.

**Done when** every marked finding has a status.

## 6. Sort

| Status | Outcome |
|---|---|
| Confirmed (Proven), Regraded | **To fix** |
| Not worth fixing, Refuted | **Dismissed** |
| Confirmed (Not proven), Unproven, Unverified | **Held** |

**Done when** every finding has an outcome.

## 7. Fix

Fix one finding at a time: Blocking, then Should-fix, then Nit, using each finding's severity after step 5. A verifier's `Fix` replaces the finding's own.

For each finding:

1. Read the code at the head. An earlier fix of this run can already have solved the finding: then it is **Fixed**, with that fix's commit.
2. Make the smallest change that solves the finding. When it needs more than the finding describes, such as a redesign or changes to code the finding does not name, the finding is **Held**, with that reason. Restore the tree with `git restore .`, and delete any file you created.
3. When the fix changes behaviour and the repo already tests that module, add or update a test in the same commit. Set up no new test infrastructure. Nits and structure-only fixes need no test.
4. Commit it alone. The message holds the finding ID and title, in the repo's commit style (`git log`, `CLAUDE.md`).

**Done when** every To fix finding is Fixed, with a commit, or is Held, with a reason.

## 8. Run the fix checks

With no commits since `PRE_FIX`, go to step 9. Otherwise run what the `Fix checks` section of `<review folder>/stacks/<stack>/stack.md` allows. Record each command and its result, and record each check that could not run, with the reason.

A failure belongs to the fixes when it names a file they changed, a test of one, or code that calls what they changed. Make one repair, in its own commit, and run the checks again. When a failure of the fixes remains, keep every commit and record the failure: step 9 then skips the re-review. Note any other failure for the summary, and continue.

**Done when** every check ran or has a reason it did not, and every failure belongs to the fixes or is noted.

## 9. Re-review

Build the **fix context**: the starting fix context, then one row per finding of this run, with `Run` one higher than the highest in the starting rows, or 1. A bot finding that repeats an earlier finding has its reason as `Repeats <ID>`.

In a bot run with a findings file, also add a row in this run for each finding in its `Findings` section. The row takes the finding's `Outcome` line when it has one. Otherwise a dismissed finding is Dismissed, with its verifier's reason, and an **open finding** is Held, with the reason `No fix run handled it`.

In a report run, record each finding's result in the findings file, as its `Outcome` line. A later bot run reads it, even when this run stops here.

With no commits since `PRE_FIX`, or with a failure of the fixes left from step 8, skip the re-review and record why. Otherwise read `<review folder>/SKILL.md` and follow all of it for BASE and the stack, as in step 3, with this fix context.

**Done when** every finding has its row, and the re-review's report is shown and its findings file is written, or the skip is recorded.

## 10. Summarise

Reply in the chat with only this, leaving out any section that has nothing to show. Write the re-review's finding IDs as `re-review Q1`, so they do not clash with this run's.

```
<branch> · <report run | bot run> · base <BASE> (<source>)

Stopped: <only when a failure of the fixes remains: the command and the failure>

| Finding | Source | Outcome | Commit or reason |
|---|---|---|---|
| <ID> | <reviewer lane, or the bots that raised it> | Fixed / Dismissed / Held | <short SHA or reason> |

Checks:
- Ran: <command>: <passed | failed>
- Not run: <check>: <reason>

Re-review: <"skipped:" and the reason, or the Reviewer table from rt-code-review step 5>
- re-review <ID> [<severity>, <reviewer>] `file:line`: <What sentence>, for each new finding

Manual checks:
- <what only the user can do>

Notes dropped: <n>

Suggested replies, for you to post after you push:
- <ID>: <one sentence for the bot: what was fixed, or why not>

Reports: <path of the source report, if any> · <path of the re-review report>

Next step: <one recommendation>
```

Show every bot finding that matched an earlier finding with that finding's ID, including one a verifier then checked. When the earlier finding is Held or open, note that a bot raised it too. The user can then check each match.

The next step is the first of these that applies:

1. A failure of the fixes remains: repair it.
2. The re-review has a Blocking or Should-fix finding: run `/rt-fix-findings <re-review report path>`.
3. No commits were made and the branch has no findings file: run `/rt-code-review`.
4. Findings are Held or open, or manual checks are listed: name them and ask the user to decide.
5. Otherwise: push when ready.

**Done when** every finding appears in the table, every check is under `Ran` or `Not run`, and the reply ends with exactly one next step.

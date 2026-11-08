# Re-review only the fix run, and only for failed fixes and Blocking issues

ADR 0009 kept Missed findings out of the fixes, but fix runs still did not end. Each re-review read the whole branch with every lane rule. So it reported Missed findings that cost a reviewer's time and a verifier each, only to be held, and it judged each fix's new code as a fresh change. Most of the Added by a fix findings that kept the runs going were Should-fix design or test gaps in the fixes' code, and each fix of one gave the next re-review more new code to judge.

A re-review now judges only the commits of its own fix run, from the commit the run recorded before its first fix to the head. It reports two things: a fix that does not solve its finding (**Failed fix**), and an issue that a fix added and that scores in the Blocking band (**Added by a fix**, 8 to 10). It does not look for issues that existed before the fixes, or for smaller issues in the fixes' code. The three lane reviewers still do it, each with this narrower brief, and they still read the callers of the changed code, so a fix that breaks an untouched caller is still found.

## Considered options

- **Check only that each fix solves its finding.** Rejected: a fix that breaks a caller would get no review before a person starts one.
- **Apply every lane rule, but only to the fixes' code.** Rejected: this is where the Should-fix findings that kept the runs going came from.
- **One checker agent per fix commit.** Rejected: it needs a new agent and brief, and it cannot see two fixes that conflict.

## Consequences

- The **Missed** origin and the **fix base** are gone. A verifier settles origin against the start of the fix run, because the re-review never reads an earlier run's code. The bookkeeping that ADR 0009 added for the fix base (its line in the findings file, the list of fix commits, the reset after a rebase, the note about other commits) goes with it.
- When a reviewer reports an issue anyway and its verifier finds it in the code before the fix run, its origin is **Before the fix run** and the report dismisses it. When a verifier regrades an Added by a fix finding below 8, the fix run skips it. Neither starts another fix run.
- An issue that existed before the fixes is found only when a person starts a new `/rt-code-review`. A Should-fix or Nit issue in a fix's code is not reported at all. We accept both: a fix run fixes what a review found, and it does not search for more.
- The reviewers receive only the fix context rows of their own fix run. The findings file keeps every row.
- The change summary describes only the fixes. The fix run's summary shows the less safe reversibility level of the source report and the fixes, so a One-way branch keeps its warning.
- Bot runs re-review with the same scope.
- A fix run stops on a findings file from before this change, which has a `Fix base` line or a Missed origin, and asks for a new `/rt-code-review`. Under the new sort, a Missed finding would be fixed and start the old chain again.
- The cap of three fix runs and the "Fix failed twice" hold stay.
- This replaces the whole-branch re-review in ADR 0004 and ADR 0009, and ADR 0009's fix base and Missed origin. ADR 0004's rule that verifiers never receive the fix context stays.

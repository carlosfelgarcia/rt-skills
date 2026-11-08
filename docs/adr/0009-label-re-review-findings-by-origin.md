# Label re-review findings by origin, and hold missed ones

Status: superseded in part by ADR 0010, which limits the re-review to the commits of its fix run.

A fix run re-reviews the whole branch, and its next step was to fix any re-review finding at or above the threshold. Fresh reviewers do not find the same things twice, so each re-review also reported issues that existed before any fix and that the earlier review did not report. Those findings looked the same as bugs a fix added, and they kept the fix runs going with no end. Each re-review finding now has an **origin**: **Added by a fix**, **Failed fix** or **Missed**. A fix run fixes the first two and holds the third for the user.

The test is causal: a finding is Added by a fix when its issue does not exist at the **fix base**, the code before the branch's first fix run. We rejected a positional test (the finding's line is in the fix diff), because a fix can break an untouched caller, and an old bug can sit next to a line a fix changed. We use the first fix run's base and not the latest one, so a bug that one fix run added and its re-review did not report is still Added by a fix when a later re-review finds it.

## Consequences

- The reviewer proposes the origin, and names the fix-context row for a Failed fix. The verifier settles it: it reads the code at the fix base and says if the issue exists there. It receives the fix base ref only, not the fix context, so ADR 0004 holds. When the verifier cannot tell, the finding is Held with `Origin not settled`.
- A Failed fix must name a Fixed row. A failed fix of a bug that a fix added is not in the code at the fix base, so it is a Failed fix only when its named row is itself Added by a fix or a Failed fix.
- A Missed finding at or above the threshold is Held, even when it is Blocking. The user decides on it; no fix run does. The threshold comes first, so a Missed finding below it is Skipped.
- A Failed fix gets one more fix run. When a later re-review reports the same original finding as a Failed fix again, through either row, it is Held with `Fix failed twice`.
- The next step suggests another fix run only for an Added by a fix finding or a first Failed fix, at or above the threshold, and only before the third fix run on the branch. A user can still start a fix run by hand.
- A fix run writes the fix base into its source findings file, so a run that skips its re-review does not lose it.
- The causal test cannot tell the user's own commits after the fix base from a fix run's, so what they break is Added by a fix too. The fix run does not stop for them: its summary says how many commits since the fix base no fix run made.
- Bot findings have no origin and keep ADR 0005's rules. A bot run's re-review findings have one, and bot runs count toward the three runs.

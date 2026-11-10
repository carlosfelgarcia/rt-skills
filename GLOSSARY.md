# RT Skills

Agent skills for RationalBit Swift apps and OD Studios pipeline packages, packaged as an installable Claude Code plugin.

## Language

**Architecture reviewer**:
The code reviewer that judges how a change is structured.
_Avoid_: design reviewer, standards reviewer

**Test reviewer**:
The code reviewer that judges a change's tests, and the new behavior that has none.
_Avoid_: coverage reviewer

**QA reviewer**:
The code reviewer that judges whether the production code in a change works.
_Avoid_: Q&A reviewer, quality reviewer

**Target**:
The change a code review judges or a walkthrough explains.
_Avoid_: review target, scope, input

**Change summary**:
An overview of the target, its reversibility when its stack is known, a change entry for each behavior change, and a list of the other changes. It opens a code review report and is the whole of a walkthrough. It judges no code.
_Avoid_: description, changelog

**Change entry**:
One behavior change that the target makes, in the change summary: how it worked at BASE, how it works at the head, and why it changed. Small mechanical edits get no change entry.
_Avoid_: bug, lesson, item

**Stack**:
The kind of codebase a target belongs to, such as a Swift app or a pipeline package. It picks the rule sets the three reviewers apply.
_Avoid_: language, platform, profile

**Change summariser**:
The agent that writes the change summary: in a code review while the three reviewers work, and alone in a walkthrough.
_Avoid_: fourth reviewer, summary reviewer

**Walkthrough**:
A change summary of a change on its own, to understand it: no reviewers, no verifiers and no findings. The stack is optional.
_Avoid_: read-only review, light review, explanation

**Reversibility**:
How far a `git revert` of the whole target takes the world back: **Revert-safe** (it restores everything), **Revert with cleanup** (something the change wrote stays behind in the new shape and needs a step to clean up) or **One-way** (a revert cannot undo part of it). Each stack file lists its triggers.
_Avoid_: risk, blast radius, severity of the change

**Verifier**:
The agent that checks one finding, whatever its score, and gives it a verdict.
_Avoid_: checker, validator, second reviewer

**Verdict**:
A verifier's judgement of one finding: **Confirmed** (the issue exists and its score is right; **Proven** when the evidence shows it, **Not proven** when the verifier could not prove it either way), **Regraded** (the issue exists at a different score; Proven or Not proven, as for Confirmed), **Not worth fixing** (the issue exists, but the repo endorses it, the tooling reports it, the fix costs more than it saves, or it is in code the change does not touch or worsen) **Refuted** (the issue does not exist) or **Unproven** (the claim rests on runtime behaviour the code does not show, so it goes to a host probe).
_Avoid_: result, outcome

**Dismissed finding**:
A finding whose verdict is Not worth fixing or Refuted, a re-review finding whose origin is Before the fix run, or a bot finding that repeats a dismissed, skipped, held or open finding from an earlier review. The report keeps a dismissed finding that has a verdict, collapsed, with the verifier's reason.
_Avoid_: rejected finding, false positive

**Unverified finding**:
A finding whose verifier failed or returned a block in the wrong shape. The report keeps it as the reviewer wrote it, with an `unverified` tag.
_Avoid_: unchecked finding

**Host probe**:
The smallest script that shows how a host, library or tool behaves at runtime, written by a verifier for an Unproven finding and run by the main session within the stack file's limits. Its output settles the finding.
_Avoid_: test, repro, experiment

**Finding ID**:
The lane letter and number that names one finding within one report, such as `Q2`, or `B` and a number for a bot finding. It is given when the findings are collected, before verification, and never changes.
_Avoid_: finding number, key

**Findings file**:
The record a code review leaves next to its report: the target and every finding with its ID, verdict and fix. It is what a later step reads, because the report is written for people.
_Avoid_: findings export, report data

**Bot finding**:
A finding that a GitHub bot raised and the user passes in by hand. It has no verdict until a verifier gives it one.
_Avoid_: bot comment, external finding

**Manual check**:
Something a bot asks for that only a person can do, such as a device test or a deployment. It is not a finding, so it gets no verdict.
_Avoid_: to-do, follow-up

**Fix context**:
The record of each finding that fix runs on a branch handled: how it was fixed, or why it was not. A re-review's reviewers receive the rows of its own fix run; verifiers never receive it.
_Avoid_: fix notes, review hints

**Fix run**:
One pass of fixing a single set of findings: the findings of one report, or one set of bot findings. It ends with one re-review at most.
_Avoid_: fix pass, fix loop

**Re-review**:
The one code review at the end of a fix run, with a fix context. It judges only the commits of that fix run: it reports a fix that does not solve its finding, and a Blocking issue that a fix added. It does not look for issues that existed before the fixes, or for smaller issues in the fixes' code.
_Avoid_: second review, follow-up review

**Held finding**:
A finding at or above the threshold that a fix run leaves for the user: Confirmed or Regraded but Not proven, Unproven, Unverified, one whose fix needs more than the finding describes, an open finding that a bot run did not handle, a finding whose origin is not settled, or a Failed fix whose finding a fix run already tried again. Unlike a dismissed finding, it may still be real.
_Avoid_: deferred finding

**Origin**:
Where a re-review finding comes from, proposed by its reviewer and settled by its verifier: **Added by a fix** (the issue does not exist before the fix run's first commit), **Failed fix** (it is a fixed finding that its fix did not solve) or **Before the fix run** (the issue exists before the fix run, and no fix of the run was meant to solve it), which a re-review does not judge, so the finding is dismissed. When the verifier cannot tell, the origin is not settled. Only re-review findings have an origin.
_Avoid_: regression, cause, source

**Skipped finding**:
A finding that a fix run leaves unfixed because its score is below the threshold, or, for a finding that a fix added, below the Blocking band. It may be real, but it is not worth a commit at this threshold. The fix context records it.
_Avoid_: ignored finding, held finding

**Threshold**:
The lowest score a fix run fixes, from 1 to 10; 4 when the user sets none, so Nits are skipped.
_Avoid_: cutoff, minimum severity

**Open finding**:
A finding a review reported and did not dismiss, which no fix run has handled yet.
_Avoid_: pending finding, unfixed finding

### Score

**Score**:
A number from 1 to 10 for the harm a finding causes if nobody fixes it, set against the anchors in the review skill's `score.md`. The reviewer proposes it and the verifier's verdict settles it. It sets the finding's band, and a fix run compares it with the threshold.
_Avoid_: priority, rating, severity score

**Band**:
The name for a range of scores: Blocking, Should-fix or Nit. Reports count findings by band.
_Avoid_: severity, level

**Blocking**:
The band for scores 8 to 10: a finding that causes a bug, data loss, a security hole or a broken caller, or a test that cannot fail for the defect it exists to catch.
_Avoid_: critical, must-fix

**Should-fix**:
The band for scores 4 to 7: a finding that works today but costs time later, such as a design smell, untested new behavior or an unclear failure mode.
_Avoid_: major, warning

**Nit**:
The band for scores 1 to 3: a finding about taste, or a wrong comment or name with no effect on behavior.
_Avoid_: minor, suggestion

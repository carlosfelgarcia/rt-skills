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

**Review target**:
The change a code review judges.
_Avoid_: scope, input

**Change summary**:
The first section of a code review report: a short overview, the change's reversibility, and up to three diagrams of what the review target changes. It judges no code.
_Avoid_: description, changelog

**Stack**:
The kind of codebase a review target belongs to, such as a Swift app or a pipeline package. It picks the rule sets the three reviewers apply.
_Avoid_: language, platform, profile

**Change summariser**:
The agent that writes the change summary while the three reviewers work.
_Avoid_: fourth reviewer, summary reviewer

**Reversibility**:
How far a `git revert` of the whole review target takes the world back: **Revert-safe** (it restores everything), **Revert with cleanup** (something the change wrote stays behind in the new shape and needs a step to clean up) or **One-way** (a revert cannot undo part of it). Each stack file lists its triggers.
_Avoid_: risk, blast radius, severity of the change

**Lesson**:
A short HTML page, written for each code review except a re-review, that teaches the developer one thing about the code the review target touches: how it worked before, how it works now, why, and a quiz. It judges nothing.
_Avoid_: tutorial, explainer, walkthrough

**Lesson writer**:
The agent that writes the lesson while the three reviewers work. It never sees the findings.
_Avoid_: teacher, tutor

**Learning workspace**:
The folder outside the reviewed repo, `~/.rt-skills/learning/<repo>/`, that holds one developer's lessons, reference entries, learning records and optional mission for one repo.
_Avoid_: notes folder, lesson cache

**Learning record**:
A note in the learning workspace of one thing the developer has shown they know, said they know, or corrected, written only on evidence such as a quiz result line. The lesson writer reads them to pick the next lesson.
_Avoid_: progress log, lesson history

**Verifier**:
The agent that checks one finding, whatever its score, and gives it a verdict.
_Avoid_: checker, validator, second reviewer

**Verdict**:
A verifier's judgement of one finding: **Confirmed** (the issue exists and its score is right; **Proven** when the evidence shows it, **Not proven** when the verifier could not prove it either way), **Regraded** (the issue exists at a different score; Proven or Not proven, as for Confirmed), **Not worth fixing** (the issue exists, but the repo endorses it, the tooling reports it, the fix costs more than it saves, or it is in code the change does not touch or worsen) **Refuted** (the issue does not exist) or **Unproven** (the claim rests on runtime behaviour the code does not show, so it goes to a host probe).
_Avoid_: result, outcome

**Dismissed finding**:
A finding whose verdict is Not worth fixing or Refuted, or a bot finding that repeats a dismissed, skipped, held or open finding from an earlier review. The report keeps a dismissed finding that has a verdict, collapsed, with the verifier's reason.
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
The record a code review leaves next to its report: the review target and every finding with its ID, verdict and fix. It is what a later step reads, because the report is written for people.
_Avoid_: findings export, report data

**Bot finding**:
A finding that a GitHub bot raised and the user passes in by hand. It has no verdict until a verifier gives it one.
_Avoid_: bot comment, external finding

**Manual check**:
Something a bot asks for that only a person can do, such as a device test or a deployment. It is not a finding, so it gets no verdict.
_Avoid_: to-do, follow-up

**Fix context**:
What the reviewers of a later review receive about earlier fixes: how each finding was fixed, or why it was not. Verifiers never receive it.
_Avoid_: fix notes, review hints

**Fix run**:
One pass of fixing a single set of findings: the findings of one report, or one set of bot findings. It ends with one re-review at most.
_Avoid_: fix pass, fix loop

**Re-review**:
The one code review at the end of a fix run, with a fix context.
_Avoid_: second review, follow-up review

**Held finding**:
A finding at or above the threshold that a fix run leaves for the user: Confirmed or Regraded but Not proven, Unproven, Unverified, one whose fix needs more than the finding describes, or an open finding that a bot run did not handle. Unlike a dismissed finding, it may still be real.
_Avoid_: deferred finding

**Skipped finding**:
A finding that a fix run leaves unfixed because its score is below the threshold. It may be real, but it is not worth a commit at this threshold. The fix context records it, so a re-review does not raise it again.
_Avoid_: ignored finding, held finding

**Threshold**:
The lowest score a fix run fixes, from 1 to 10; 4 when the user sets none, so Nits are skipped.
_Avoid_: cutoff, minimum severity

**Open finding**:
A finding a review reported and did not dismiss, which no fix run has handled yet.
_Avoid_: pending finding, unfixed finding

### Score

**Score**:
A number from 1 to 10 for the harm a finding causes if nobody fixes it, set against the anchors in the reviewer brief. The reviewer proposes it and the verifier's verdict settles it. It sets the finding's band, and a fix run compares it with the threshold.
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

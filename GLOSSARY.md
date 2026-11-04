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
The first section of a code review report: a short overview and up to three diagrams of what the review target changes. It judges nothing.
_Avoid_: description, changelog

**Stack**:
The kind of codebase a review target belongs to, such as a Swift app or a pipeline package. It picks the rule sets the three reviewers apply.
_Avoid_: language, platform, profile

**Change summariser**:
The agent that writes the change summary while the three reviewers work.
_Avoid_: fourth reviewer, summary reviewer

**Verifier**:
The agent that checks one Blocking or Should-fix finding after the reviewers return, and gives it a verdict.
_Avoid_: checker, validator, second reviewer

**Verdict**:
A verifier's judgement of one finding: **Confirmed** (the issue exists and its severity is right), **Regraded** (the issue exists at a different severity), **Not worth fixing** (the issue exists, but the repo endorses it, the tooling reports it, the fix costs more than it saves, or it is in code the change does not touch or worsen) or **Refuted** (the issue does not exist).
_Avoid_: result, outcome

**Dismissed finding**:
A finding whose verdict is Not worth fixing or Refuted. The report keeps it, collapsed, with the verifier's reason.
_Avoid_: rejected finding, false positive

**Unverified finding**:
A Blocking or Should-fix finding whose verifier failed or returned a block in the wrong shape. The report keeps it as the reviewer wrote it, with an `unverified` tag.
_Avoid_: unchecked finding

**Finding ID**:
The lane letter and number that names one finding within one report, such as `Q2`.
_Avoid_: finding number, key

### Severity

**Blocking**:
A finding that causes a bug, data loss, a security hole or a broken caller, or a test that cannot fail for the defect it exists to catch.
_Avoid_: critical, must-fix

**Should-fix**:
A finding that works today but costs time later: a design smell, untested new behavior, an unclear failure mode.
_Avoid_: major, warning

**Nit**:
A finding about taste.
_Avoid_: minor, suggestion

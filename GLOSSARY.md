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

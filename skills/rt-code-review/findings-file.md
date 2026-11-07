# Findings file

`render.py` writes it next to the report, as `<report>.findings.md`, for `rt-fix-findings` to read:

````
# Findings: <review target>

- Repo: <repo folder name>
- Branch: <branch; PR mode: headRefName>
- Report: <report path>
- Stack: <stack>
- Base: <BASE>
- Head: <commit; PR mode: HEAD_SHA>
- Uncommitted: <yes | no>
- Reversibility: <Revert-safe | Revert with cleanup | One-way | unknown>
- Lesson: <path | none>
- Fix base: <only in a re-review: the commit before the branch's first fix run>
- Fix commits: <only in a re-review: the full SHA of each commit a fix run made, space-separated>

## Findings

### <finding ID>
- **Status:** <Confirmed (Proven | Not proven) | Regraded (Proven | Not proven) | Not worth fixing | Refuted | Unproven | Unverified>
- **Score:** <score after verification> (<band>)
- **Origin:** <only in a re-review: Added by a fix | Failed fix of <Run> <Finding> | Missed | Missed (not settled)>
- **Outcome:** <added by a fix run: Fixed | Dismissed | Held | Skipped, then the commit or reason>

<the reviewer's block>

<the verifier's block>

**Probe result:** <only for Unproven, in the step 3 shape>

## Fix context

<the fix context the review received; absent when none>
````

With no findings, `## Findings` holds `No findings.`

## Fix context

One row per finding a fix run handled. `Run` counts fix runs on the branch from 1; `Run` and `Finding` together name a row, since IDs repeat across reports.

````
| Run | Finding | Origin | Where | What | Outcome | Commit or reason |
|---|---|---|---|---|---|---|
| 1 | Q1 | — | `path:line` | <What sentence> | Fixed | <short SHA> |
| 2 | Q2 | Failed fix of 1 Q1 | `path:line` | <What sentence> | Fixed | <short SHA> |
| 2 | T4 | Missed | `path:line` | <What sentence> | Held | Missed by the first review |
````

`Origin` is the finding's origin, or `—` for a finding of a first review or a bot. `Outcome` is Fixed, Dismissed, Held or Skipped.

## Origin

A re-review finding's origin comes from the verifier's `At fix base` line and the reviewer's `Origin` line. A **named row** is the fix context row that the reviewer's `Failed fix of <Run> <Finding>` names, when its `Outcome` is Fixed. The first matching row gives the origin:

| At fix base | Origin |
|---|---|
| Unsettled, missing, or no verdict | Missed (not settled) |
| Absent, with a named row whose `Origin` is Added by a fix or a Failed fix | Failed fix of that row |
| Absent | Added by a fix |
| Present, with a named row | Failed fix of that row |
| Present | Missed |

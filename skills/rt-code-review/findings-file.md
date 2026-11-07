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

## Findings

### <finding ID>
- **Status:** <Confirmed (Proven | Not proven) | Regraded (Proven | Not proven) | Not worth fixing | Refuted | Unproven | Unverified>
- **Score:** <score after verification> (<band>)
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
| Run | Finding | Where | What | Outcome | Commit or reason |
|---|---|---|---|---|---|
| 1 | Q1 | `path:line` | <What sentence> | Fixed | <short SHA> |
| 1 | T4 | `path:line` | <What sentence> | Skipped | Score 3 below threshold 4 |
````

`Outcome` is Fixed, Dismissed, Held or Skipped.

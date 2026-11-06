# Findings file

The record a review leaves next to its report, for `rt-fix-findings` to read. The name is the report's path with `.findings.md` in place of `.html`.

## Shape

````
# Findings: <review target, one line>

- Repo: <repo>
- Branch: <`git branch --show-current`; in PR mode, headRefName>
- Report: <report path>
- Stack: <stack name>
- Base: <BASE>
- Head: <`git rev-parse HEAD`; in PR mode, HEAD_SHA>
- Uncommitted: <yes when Branch work reviewed uncommitted or untracked files, else no>

## Findings

### <finding ID>
- **Status:** <Confirmed (Proven) | Confirmed (Not proven) | Regraded | Not worth fixing | Refuted | Unproven | Unverified>
- **Outcome:** <only after a fix run: Fixed | Dismissed | Held, then the commit or reason>

<the finding's block, exactly as the reviewer returned it>

<the verdict block, exactly as the verifier returned it>

<only after a host probe: **Probe result:** the command, its output, and the reason when it settled nothing>

## Fix context

<the fix context this review received, exactly as received; leave the section out when it had none>
````

The status is the one after step 3 of `SKILL.md`. A finding that a host probe confirmed is `Confirmed (Proven)`. With no findings, write `No findings.` under `## Findings`. The review leaves out `Outcome`: `rt-fix-findings` adds it.

## Fix context

A **fix context** is one table, with one row per finding that a fix run handled:

````
| Run | Finding | Where | What | Outcome | Commit or reason |
|---|---|---|---|---|---|
| 1 | Q1 | `path:line` | <the finding's What sentence> | Fixed | <short SHA> |
| 1 | A2 | `path:line` | <the finding's What sentence> | Dismissed | <the reason> |
| 2 | B1 | `path:line` | <the finding's What sentence> | Held | <the reason> |
````

`Outcome` is Fixed, Dismissed or Held. `Run` counts fix runs on the branch from 1. Finding IDs are unique only within a report, so `Run` and `Finding` together name a row.

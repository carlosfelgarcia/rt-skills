---
name: rt-code-review
description: Review a change in a Swift app or pipeline package with three reviewers and a verifier per finding, then open an HTML report that shows every change before and after.
disable-model-invocation: true
argument-hint: "[PR number | ref] [stack]"
---

# RT code review

Three reviewers judge one **target** in parallel, one lane each, using the rule sets of its **stack** (a folder in [`stacks/`](stacks/)). Alongside them, a change summariser writes the **change summary**: a **change entry** for each behavior change, before and after. A **verifier** then checks every finding and its **score**. `<skill>` below means this skill's base directory.

## 1. Resolve the target

Follow [`target.md`](target.md). When no stack matches, or several do, stop, say which matched, and ask for the stack as an argument. When `rt-fix-findings` starts a **re-review**, add `Re-review: yes` to the target block: BASE is then the commit before its fix run (ADR 0010).

**Done when** the target block is complete, as `target.md` defines it.

## 2. Start the agents

One message, one `Agent` call each, no model override. Every prompt is: the target block, a role line, then "Return <what> in the shape the file defines, and nothing else."

| Agent (`subagent_type`) | Role line: "You are the <role>. Read …, then follow them." | Returns |
|---|---|---|
| Architecture, Test and QA reviewer (`rt-skills:rt-reviewer`) | `<skill>/reviewer-brief.md`, `<skill>/score.md`, `<skill>/stacks/<stack>/stack.md`, and the lane's rule files `<skill>/rules/<lane>.md` and `<skill>/stacks/<stack>/<lane>.md`, `<lane>` being `architecture`, `test` or `qa` | findings |
| Change summariser (`rt-skills:rt-change-summariser`) | `<skill>/change-summariser.md` and `<skill>/stacks/<stack>/reversibility.md` | the change summary |

In a re-review, `rt-fix-findings` passes a **fix context**. Add its header and the rows of its highest `Run` to each reviewer's prompt before the return line.

**Done when** every agent has returned.

## 3. Verify findings

Give each finding its **finding ID**: `A`, `T` or `Q` for the lane, then 1, 2, … in the reviewer's order. Skip to step 4 when there are none.

Start one `rt-skills:rt-verifier` per finding, all in one message, no model override. Prompt: the target block; "You are the verifier. Read `<skill>/verifier-brief.md`, `<skill>/score.md` and `<skill>/stacks/<stack>/stack.md`, then follow them."; the finding's block exactly as returned, less its `Origin` line; "Return your verdict in the shape the brief defines, and nothing else." Never add a fix context.

A finding's **status** is its verdict, with its proof for Confirmed and Regraded, such as `Regraded (Proven)`. Not worth fixing and Refuted are **dismissed**, and so, in a re-review, is a finding whose origin is Before the fix run. A failed verifier, or a block missing a line its verdict needs, makes the finding **Unverified**; start no second verifier.

**Host probes.** For each Unproven finding, run its probe only when `stack.md` has a `Host probes` section and the probe keeps its limits. One at a time, write it to `/tmp/rt-code-review/probes/<ID>.<ext>`, run it as that section says, and compare the output with `Expect` only. Record:

````
- **Result:** <Confirmed: a run printed Expect | Refuted: every run printed something else | Unproven>
- **Reason:** <only when Unproven: no Host probes section, limits broken, an early error or a timeout>
- **Run:** <each command and its output, in fenced blocks; leave out when none ran>
````

**Done when** every finding has a verdict, is Unverified, or has a probe result.

## 4. Render

In `/tmp/rt-code-review/runs/<repo>-<branch or prN>-<YYYYmmdd-HHMMSS>/` (`/` in the branch becomes `-`), write each file with one `Write`, agent text verbatim:

- `meta.md`: `- Key: value` lines for `Target` (one line), `Repo` (folder name), `Branch` (PR mode: headRefName), `Mode`, `Stack` (as in the target block), `Stack settings` (one line), `Base`, `Head` (PR mode: HEAD_SHA), `Uncommitted` (`yes` when Branch work reviewed uncommitted or untracked files), and `Re-review: yes` in a re-review.
- `summary.md`.
- `findings.md`, when there are findings: per ID in order, `=== <ID> finding` and its block, `=== <ID> verdict` and its block (unless the verifier failed), `=== <ID> probe` and its result (Unproven only).
- `fix-context.md`, in a re-review: every row `rt-fix-findings` passes.

Run `python3 <skill>/render.py <run folder>`. It writes the report and the **findings file** ([`findings-file.md`](findings-file.md)), links each finding to the change entries that list its file, and prints both paths and one status line per finding, with its **origin** in a re-review. On `error:`, fix the named input and rerun.

**Done when** it exits 0.

## 5. Show and reply

Outside T3 (no `mcp__t3-code__` tools listed), open the report with `open` (Darwin) or `xdg-open` (Linux). Inside T3, the link in the reply opens it. When `rt-fix-findings` started this review, stop here. Otherwise reply with only:

```
<target> · stack: <stack> (<detected | argument>) · <reversibility level>

| Reviewer | Blocking | Should-fix | Nit | Dismissed |
|---|---|---|---|---|
| Architecture | n | n | n | n |
| Tests | n | n | n | n |
| QA | n | n | n | n |

Blocking:
- <ID> (<score>/10) [<reviewer>] `file:line`: <What sentence>

Reversibility: <only when not Revert-safe: one line per trigger>

Report: [<report file name>](<report path>)
```

Counts use scores after step 3 and leave out dismissed findings. Write "Blocking: none" when empty.

---
name: rt-code-review
description: Review a change in a Swift app or a pipeline package with architecture, test and QA reviewers, verify and score each finding, then open an HTML report with a change summary and reversibility, plus a lesson on the code the change touches.
disable-model-invocation: true
argument-hint: "[PR number | ref] [stack]"
---

# RT code review

Three reviewers judge one **review target** in parallel, one lane each, using the rule sets of its **stack** (a folder in [`stacks/`](stacks/)). Alongside them, a change summariser writes the **change summary** and a lesson writer writes the **lesson**. A **verifier** then checks every finding and its **score**. `<skill>` below means this skill's base directory.

## 1. Resolve the review target

Arguments: an optional target (PR number or ref) and an optional stack (a folder name in `stacks/`). A lone stack name is the stack. A second argument must be a stack; a lone one must be a number, a stack or a ref `git rev-parse --verify` accepts. On a bad argument, stop: say what is wrong in one sentence and list the stacks.

| Target | Mode | BASE | Diff | Read a file | Search | List files |
|---|---|---|---|---|---|---|
| Number | PR | `gh pr view <n> --json baseRefName,headRefName,title,url`, `git fetch origin <baseRefName>`, `BASE=origin/<baseRefName>` | `git fetch origin pull/<n>/head`, `HEAD_SHA=$(git rev-parse FETCH_HEAD)`, `git diff BASE...HEAD_SHA` | `git show HEAD_SHA:<path>` | `git grep -n <pattern> HEAD_SHA` | `git ls-tree -r --name-only HEAD_SHA` |
| Ref | Ref | `git rev-parse --verify <ref>^{commit}` | `git diff <ref>...HEAD` | `git show HEAD:<path>` | `git grep -n <pattern> HEAD` | `git ls-tree -r --name-only HEAD` |
| Nothing | Branch work | `git merge-base <default> HEAD`; `<default>` is `git symbolic-ref --short refs/remotes/origin/HEAD`, else `main`, else `master` | `git diff BASE` plus `git ls-files --others --exclude-standard` | the working-tree file | `Grep` | `git ls-files` plus untracked |

PR mode fetches and never checks out.

Stack: an argument wins, recorded as `<stack> (argument)`. Otherwise check the `Markers` of every `stacks/<stack>/setup.md` with the list-files command; exactly one match is `<stack> (detected)`. With none or several, stop, say which matched, and ask for the stack as an argument. Then read the stack settings that `setup.md` describes.

The **target block**: mode, repo root, BASE, head (`HEAD_SHA`, `HEAD` or "working tree"), the diff, read-a-file, read-at-base (`git show <BASE>:<path>`), search and list-files commands, stack, stack settings, `git log --oneline BASE..<head>`, `git diff --stat`, and untracked files (Branch work).

**Done when** every field is filled. Stop with one sentence when a command fails or the diff and untracked list are both empty.

## 2. Start the agents

One message, one `Agent` call each, no model override. Every prompt is: the target block, a role line, then "Return <what> in the shape the file defines, and nothing else."

| Agent (`subagent_type`) | Role line: "You are the <role>. Read …, then follow them." | Returns |
|---|---|---|
| Architecture, Test and QA reviewer (`rt-skills:rt-reviewer`) | `<skill>/reviewer-brief.md`, `<skill>/score.md`, `<skill>/stacks/<stack>/stack.md` and the rule file `architecture.md`, `test.md` or `qa.md` in that folder | findings |
| Change summariser (`rt-skills:rt-change-summariser`) | `<skill>/change-summariser.md` and `<skill>/stacks/<stack>/reversibility.md` | the change summary |
| Lesson writer (`rt-skills:rt-lesson-writer`) | `<skill>/lesson-writer.md`, `<skill>/stacks/<stack>/resources.md`; add "The learning workspace is `<workspace>`." | the lesson |

The **learning workspace** is the absolute path of `$HOME/.rt-skills/learning/<repo>/`, `<repo>` being the repo root's folder name.

When `rt-fix-findings` passes a **fix context**, add it to each reviewer's prompt before the return line, and start no lesson writer.

**Done when** every agent has returned.

## 3. Verify findings

Give each finding its **finding ID**: `A`, `T` or `Q` for the lane, then 1, 2, … in the reviewer's order. Skip to step 4 when there are none.

Start one `rt-skills:rt-verifier` per finding, all in one message, no model override. Prompt: the target block; "You are the verifier. Read `<skill>/verifier-brief.md`, `<skill>/score.md` and `<skill>/stacks/<stack>/stack.md`, then follow them."; the finding's block exactly as returned; "Return your verdict in the shape the brief defines, and nothing else." Never add a fix context.

A finding's **status** is its verdict, with its proof for Confirmed and Regraded, such as `Regraded (Proven)`. Not worth fixing and Refuted are **dismissed**. A failed verifier, or a block missing a line its verdict needs, makes the finding **Unverified**; start no second verifier.

**Host probes.** For each Unproven finding, run its probe only when `stack.md` has a `Host probes` section and the probe keeps its limits. One at a time, write it to `/tmp/rt-code-review/probes/<ID>.<ext>`, run it as that section says, and compare the output with `Expect` only. Record:

````
- **Result:** <Confirmed: a run printed Expect | Refuted: every run printed something else | Unproven>
- **Reason:** <only when Unproven: no Host probes section, limits broken, an early error or a timeout>
- **Run:** <each command and its output, in fenced blocks; leave out when none ran>
````

**Done when** every finding has a verdict, is Unverified, or has a probe result.

## 4. Render

In `/tmp/rt-code-review/runs/<repo>-<branch or prN>-<YYYYmmdd-HHMMSS>/` (`/` in the branch becomes `-`), write each file with one `Write`, agent text verbatim:

- `meta.md`: `- Key: value` lines for `Target` (one line), `Repo` (folder name), `Branch` (PR mode: headRefName), `Mode`, `Stack` (as in the target block), `Stack settings` (one line), `Base`, `Head` (PR mode: HEAD_SHA), `Uncommitted` (`yes` when Branch work reviewed uncommitted or untracked files), and `Learning workspace` when a lesson writer ran.
- `summary.md`, and `lesson.md` when a lesson writer ran.
- `findings.md`, when there are findings: per ID in order, `=== <ID> finding` and its block, `=== <ID> verdict` and its block (unless the verifier failed), `=== <ID> probe` and its result (Unproven only).
- `fix-context.md`, when there is one.

Run `python3 <skill>/render.py <run folder>`. It writes the report, the **findings file** ([`findings-file.md`](findings-file.md)) and the lesson, and prints their paths and one status line per finding. On `error:`, fix the named input and rerun.

**Done when** it exits 0.

## 5. Show and reply

Inside T3 (`html_render`, loadable with ToolSearch `select:mcp__t3-code__html_render`), render the report's full HTML once with title `Code review: <target>` and `height: 2000`, then the lesson's with title `Lesson: <title>`. Elsewhere, open both with `open` (Darwin) or `xdg-open` (Linux). When `rt-fix-findings` started this review, stop here. Otherwise reply with only:

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

Report: <path>
Lesson: <path>. When you finish its quiz, paste the result line here.
```

Counts use scores after step 3 and leave out dismissed findings. Write "Blocking: none" when empty.

## 6. Learning records

For the rest of the conversation, when the developer pastes a quiz result, asks about the lesson, or says what they know, follow [`learning-record.md`](learning-record.md).

---
name: rt-code-review
description: Review a change in a Swift app or a pipeline package with an architecture reviewer, a test reviewer and a QA reviewer, using that stack's rules, verify each finding, then open an HTML report that starts with a visual summary of the change.
disable-model-invocation: true
argument-hint: "[PR number | ref] [stack]"
---

# RT code review

Three reviewers judge one **review target** in parallel. Each owns one lane, and their findings stay in separate report sections: a clean architecture section must never hide a broken test. In the same batch, a change summariser writes the **change summary** that opens the report, so a reader knows what changed before they read a finding. The reviewers apply the rule sets of the review target's **stack**; each stack is a folder in [`stacks/`](stacks/). Then a **verifier** checks each Blocking and Should-fix finding, so a reader sees which findings hold up, and can point at any of them by its **finding ID**.

## 1. Resolve the review target

The arguments are an optional target (a PR number or a ref) and an optional stack. The **stacks** are the folder names in `stacks/`, such as `swift-app` and `pipeline`. A lone argument that is a stack name is the stack, not a ref. Check the arguments before you run anything else:

- A second argument must be a stack name.
- A lone argument must be a number, a stack name or a ref that `git rev-parse --verify` accepts.

When an argument fails its check, stop. Tell the user in one sentence what is wrong, and list the stacks.

Pick the mode from the target:

| Target | Mode | BASE | Diff command | Read a file | Search | List files |
|---|---|---|---|---|---|---|
| A number | PR | `git fetch origin <baseRefName>` from `gh pr view <n> --json baseRefName,headRefName,title,url`, then `BASE=origin/<baseRefName>` | `git fetch origin pull/<n>/head`, `HEAD_SHA=$(git rev-parse FETCH_HEAD)`, then `git diff BASE...HEAD_SHA` | `git show HEAD_SHA:<path>` | `git grep -n <pattern> HEAD_SHA` | `git ls-tree -r --name-only HEAD_SHA` |
| A ref (branch, commit, tag) | Ref | `git rev-parse --verify <ref>^{commit}` | `git diff <ref>...HEAD` | `git show HEAD:<path>` | `git grep -n <pattern> HEAD` | `git ls-tree -r --name-only HEAD` |
| Nothing | Branch work | `git merge-base <default> HEAD`, where `<default>` is `git symbolic-ref --short refs/remotes/origin/HEAD`, else `main`, else `master` | `git diff BASE` plus the untracked files from `git ls-files --others --exclude-standard` | Read the working-tree file | `Grep` the working tree | `git ls-files` plus the untracked files |

PR mode leaves the working tree alone: it fetches, it never checks out.

Then pick the stack:

- **A stack argument** wins. Record it as `<stack> (argument)`.
- **Otherwise detect it.** Read the `Markers` section of every `stacks/<stack>/stack.md` and check each against the head with the list-files command. When exactly one stack matches, record it as `<stack> (detected)`.

  When no stack matches, or more than one matches, stop. Tell the user in one sentence which stacks matched, or that none did. Ask them to run the review again with the stack as an argument.

Then read the **stack settings** that the `Stack settings` section of `stacks/<stack>/stack.md` describes, at the head, with the read-a-file and list-files commands.

Build the **target block** the reviewers receive: mode, repo root path, BASE, head (`HEAD_SHA`, `HEAD`, or "working tree"), diff command, read-a-file command, search command, list-files command, stack, stack settings, commit list (`git log --oneline BASE..<head>`), changed files (`git diff --stat`), and untracked files (Branch work only).

**Done when** every field of the target block is filled. Stop here and tell the user why, in one sentence, if any command in the table fails (an unknown ref, a `gh pr view` or `git fetch` error, no default branch), or if the diff and the untracked list are both empty.

## 2. Start the reviewers and the change summariser

Send one message with four `Agent` calls, no model override: one per reviewer with `subagent_type: rt-skills:rt-reviewer`, and one for the change summariser with `subagent_type: rt-skills:rt-change-summariser`. Each agent's prompt has exactly three parts, in this order:

1. The target block.
2. **Role line**: "You are the <role>. Read `<this skill's base directory>/reviewer-brief.md`, `<this skill's base directory>/stacks/<stack>/stack.md` and `<this skill's base directory>/stacks/<stack>/<rule-file>`, then follow them."
3. **Return line**: "Return your findings in the shape the brief defines, and nothing else."

| Role | Rule file |
|---|---|
| Architecture reviewer | `architecture.md` |
| Test reviewer | `test.md` |
| QA reviewer | `qa.md` |

The change summariser gets the same target block, with a different role line and return line:

- **Role line**: "You are the change summariser. Read `<this skill's base directory>/change-summariser.md` and the diagram guide at `<this skill's base directory>/diagram-guide.md`, then follow them."
- **Return line**: "Return the change summary in the shape the file defines, and nothing else."

**Done when** all four agents have returned.

## 3. Verify findings

Collect every Blocking and Should-fix finding from the three reviewers. Nits are not verified. When there are none, go to step 4.

Send one message with one `Agent` call per finding, however many there are, no model override, with `subagent_type: rt-skills:rt-verifier`. Each prompt has exactly four parts, in this order:

1. The target block.
2. **Role line**: "You are the verifier. Read `<this skill's base directory>/verifier-brief.md` and `<this skill's base directory>/stacks/<stack>/stack.md`, then follow them."
3. **The finding**: the finding's block, exactly as the reviewer returned it.
4. **Return line**: "Return your verdict in the shape the brief defines, and nothing else."

Then apply each verdict to its finding:

| Verdict | The finding |
|---|---|
| Confirmed | Stays as it is. |
| Regraded | Moves to the new severity. Record the old severity, the reason and the evidence. |
| Not worth fixing, Refuted | Becomes a **dismissed finding**. Record the verdict, the reason and the evidence. |

A verifier `Fix` line replaces the reviewer's `Fix`; record that the fix was revised. When a verifier fails, or returns a block that is not in the brief's shape, start no second verifier: the finding stays as the reviewer wrote it and is marked **Unverified**.

**Done when** every Blocking and Should-fix finding has a verdict or is marked Unverified.

## 4. Build the HTML report

Read [`diagram-guide.md`](diagram-guide.md) for its diagram guidance. Then fill [`report-template.html`](report-template.html):

- The change summary goes into the `Change summary` section. The overview becomes `<p>` text. Each view becomes an `<h3>` title, a `<p>` sentence and a block chosen by its fence language: `mermaid` goes in a `<pre class="mermaid">`, `diff` goes in a `<pre class="diff">`, and every other language goes in a plain `<pre>`.
- Each reviewer's findings go into that reviewer's section, with the reviewer's wording. Order the visible findings by their severity after step 3, Blocking first, and keep the reviewer's order within a severity. A finding that step 3 moved down to Nit stays, even past the brief's three-nit cap.
- Dismissed findings go last in their reviewer's section, in one collapsed `<details class="dismissed">` block. Each one keeps its card at the reviewer's severity, with a `Verification` row for its verdict, reason and evidence. Its `Structure` stays text, because a diagram inside a closed block does not draw. When every finding in a section is dismissed, write the `No findings.` line above the block.
- Every finding gets a **finding ID**: the lane letter (`A` for Architecture, `T` for Tests, `Q` for QA) and a number from 1, in the order the section shows them. The visible findings come first, then the dismissed findings carry on the same count. The ID goes in the card title, before the severity badge.
- A Regraded card shows a `was <old severity>` tag and a `Verification` row with the verdict, reason and evidence. A card with a revised fix shows a `fix revised by verification` tag, and an Unverified card shows an `unverified` tag.
- A finding with a `Structure` field gets a Mermaid `graph` drawn from it, in the finding card. A `Fix` with a `diff` block goes in a `<pre class="diff">`. Every other finding stays text.
- HTML-escape all code, paths and diff text.
- Delete the template's instructions comment, example card and example dismissed block.

The report page is the only file this step writes; it is opened in step 5. Write it with one `Write` call to `/tmp/rt-code-review/<repo>-<branch or prN>-<YYYYmmdd-HHMMSS>.html`, with `/` in the branch name replaced by `-`.

**Done when** the change summary and every finding from all three reviewers, dismissed ones included, are in the file, every card has a unique finding ID, and the header counts match the cards: visible findings by severity, plus the dismissed count.

## 5. Open it and summarise

Show the report where the user is working:

- **Inside T3:** when this session has T3's `html_preview` and `html_render` tools (they can be deferred; load them with ToolSearch `select:mcp__t3-code__html_preview,mcp__t3-code__html_render`), pass the report file's full HTML to `html_preview`. Then pass the same HTML to `html_render`, with the title `Code review: <review target>` and `height` set to the `contentHeight` the preview returned, capped at 2000. The page sends about twice its size through the conversation, which is the cost of seeing it in the thread.
- **Anywhere else:** only when the T3 tools are not in this session, open the file with the OS's opener. Run `uname -s`: on `Darwin` run `open <path>`; on `Linux` run `xdg-open <path> >/dev/null 2>&1 &`.

The file on disk stays in both cases, so the user can still open it in a browser. Then reply in the chat with only this:

```
<review target, one line> · stack: <stack> (<detected | argument>)

| Reviewer | Blocking | Should-fix | Nit | Dismissed |
|---|---|---|---|---|
| Architecture | n | n | n | n |
| Tests | n | n | n | n |
| QA | n | n | n | n |

Blocking:
- <finding ID> [<reviewer>] `file:line`: <the finding's "What" sentence>

Report: <path>
```

The counts and the Blocking list use the severities after step 3, without dismissed findings. Write "Blocking: none" when there are none.

**Done when** the report is shown in the thread or open in the browser, and the reply holds the target line, the counts table, the Blocking list with finding IDs, and the report path.

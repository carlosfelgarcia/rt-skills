---
name: rt-code-review
description: Review a change with an architecture reviewer, a test reviewer and a QA reviewer, then open an HTML report that starts with a visual summary of the change.
disable-model-invocation: true
argument-hint: "[PR number | ref]"
---

# RT code review

Three reviewers judge one **review target** in parallel. Each owns one lane, and their findings stay in separate report sections: a clean architecture section must never hide a broken test. In the same batch, a change summariser writes the **change summary** that opens the report, so a reader knows what changed before they read a finding.

## 1. Resolve the review target

Pick the mode from the argument:

| Argument | Mode | BASE | Diff command | Read a file | Search |
|---|---|---|---|---|---|
| A number | PR | `git fetch origin <baseRefName>` from `gh pr view <n> --json baseRefName,headRefName,title,url`, then `BASE=origin/<baseRefName>` | `git fetch origin pull/<n>/head`, `HEAD_SHA=$(git rev-parse FETCH_HEAD)`, then `git diff BASE...HEAD_SHA` | `git show HEAD_SHA:<path>` | `git grep -n <pattern> HEAD_SHA` |
| A ref (branch, commit, tag) | Ref | `git rev-parse --verify <ref>^{commit}` | `git diff <ref>...HEAD` | `git show HEAD:<path>` | `git grep -n <pattern> HEAD` |
| Nothing | Branch work | `git merge-base <default> HEAD`, where `<default>` is `git symbolic-ref --short refs/remotes/origin/HEAD`, else `main`, else `master` | `git diff BASE` plus the untracked files from `git ls-files --others --exclude-standard` | Read the working-tree file | `Grep` the working tree |

PR mode leaves the working tree alone: it fetches, it never checks out.

Then read the **Swift settings** at the head, with the read-a-file command, from `Package.swift` and every `*.xcodeproj/project.pbxproj` that `git ls-files` lists:

| Setting | `Package.swift` | `.pbxproj` |
|---|---|---|
| Language mode | `swiftLanguageModes`, `swiftLanguageVersions` or `-swift-version` | `SWIFT_VERSION` |
| Strict concurrency | `StrictConcurrency` feature flag | `SWIFT_STRICT_CONCURRENCY` |
| Default isolation | `.defaultIsolation(...)` | `SWIFT_DEFAULT_ACTOR_ISOLATION` |
| Upcoming features | `.enableUpcomingFeature(...)` | `SWIFT_UPCOMING_FEATURE_*` |

Write `unknown` for a setting you cannot find; `// swift-tools-version:` is not a reliable proxy for the language mode. Where targets differ, list each target's values. With neither file in the repo, write `none`.

Build the **target block** the reviewers receive: mode, repo root path, BASE, head (`HEAD_SHA`, `HEAD`, or "working tree"), diff command, read-a-file command, search command, Swift settings, commit list (`git log --oneline BASE..<head>`), changed files (`git diff --stat`), and untracked files (Branch work only).

**Done when** every field of the target block is filled. Stop here and tell the user why, in one sentence, if any command in the first table fails (an unknown ref, a `gh pr view` or `git fetch` error, no default branch), or if the diff and the untracked list are both empty.

## 2. Start the reviewers and the change summariser

Send one message with four `Agent` calls, no model override: one per reviewer with `subagent_type: rt-skills:rt-reviewer`, and one for the change summariser with `subagent_type: rt-skills:rt-change-summariser`. Each agent's prompt has exactly three parts, in this order:

1. The target block.
2. **Role line**: "You are the <role>. Read `<this skill's base directory>/reviewer-brief.md` and `<this skill's base directory>/<role-file>`, then follow them."
3. **Return line**: "Return your findings in the shape the brief defines, and nothing else."

| Role | Role file |
|---|---|
| Architecture reviewer | `architecture-reviewer.md` |
| Test reviewer | `test-reviewer.md` |
| QA reviewer | `qa-reviewer.md` |

The change summariser gets the same target block, with a different role line and return line:

- **Role line**: "You are the change summariser. Read `<this skill's base directory>/change-summariser.md`, then follow it."
- **Return line**: "Return the change summary in the shape the file defines, and nothing else."

**Done when** all four agents have returned.

## 3. Build the HTML report

Invoke the `show-me` skill for its diagram guidance. Then fill [`report-template.html`](report-template.html):

- The change summary goes into the `Change summary` section. The overview becomes `<p>` text. Each view becomes an `<h3>` title, a `<p>` sentence and a block chosen by its fence language: `mermaid` goes in a `<pre class="mermaid">`, `diff` goes in a `<pre class="diff">`, and every other language goes in a plain `<pre>`.
- Each reviewer's findings go into that reviewer's section, in the order the reviewer returned them, with the reviewer's wording.
- A finding with a `Structure` field gets a Mermaid `graph` drawn from it, in the finding card. A `Fix` with a `diff` block goes in a `<pre class="diff">`. Every other finding stays text.
- HTML-escape all code, paths and diff text.
- Delete the template's instructions comment and example card.

The report page is the only file this step writes; it is opened in step 4. Write it with one `Write` call to `/tmp/rt-code-review/<repo>-<branch or prN>-<YYYYmmdd-HHMMSS>.html`, with `/` in the branch name replaced by `-`.

**Done when** the change summary and every finding from all three reviewers are in the file, and the header counts match the cards.

## 4. Open it and summarise

Show the report where the user is working:

- **Inside T3:** when this session has T3's `html_preview` and `html_render` tools (they can be deferred; load them with ToolSearch `select:mcp__t3-code__html_preview,mcp__t3-code__html_render`), pass the report file's full HTML to `html_preview`. Then pass the same HTML to `html_render`, with the title `Code review: <review target>` and `height` set to the `contentHeight` the preview returned, capped at 2000. The page sends about twice its size through the conversation, which is the cost of seeing it in the thread.
- **Anywhere else:** run `open <path>`.

The file on disk stays in both cases, so the user can still open it in a browser. Then reply in the chat with only this:

```
<review target, one line>

| Reviewer | Blocking | Should-fix | Nit |
|---|---|---|---|
| Architecture | n | n | n |
| Tests | n | n | n |
| QA | n | n | n |

Blocking:
- [<reviewer>] `file:line`: <the finding's "What" sentence>

Report: <path>
```

Write "Blocking: none" when there are none.

**Done when** the report is shown in the thread or open in the browser, and the reply holds the target line, the counts table, the blocking list and the report path.

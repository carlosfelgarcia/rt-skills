---
name: rt-walkthrough
description: Walkthrough of a PR, ref or branch work, to understand it without reviewing it. Shows each behavior change before and after, as a page. Use when the user wants to understand or be walked through a change.
argument-hint: "[PR number | ref] [stack]"
---

# RT walkthrough

A **walkthrough** explains one **target** so the user understands it. The change summariser writes the **change summary**: a **change entry** for each behavior change, before and after, and why it changed. Nothing judges the code, so no reviewers, verifiers or findings take part. `<review folder>` below means `<this skill's base directory>/../rt-code-review/`.

## 1. Resolve the target

Follow `<review folder>/target.md`. When no stack matches, or several do, carry on with `none` as the stack, and keep the names of the stacks that matched for the reply.

**Done when** the target block is complete, as `target.md` defines it.

## 2. Start the change summariser

One `Agent` call, `subagent_type` `rt-skills:rt-change-summariser`, no model override. The prompt is the target block, then the role line, then "Return the change summary in the shape the file defines, and nothing else." The role line:

- With a stack: "You are the change summariser. Read `<review folder>/change-summariser.md` and `<review folder>/stacks/<stack>/reversibility.md`, then follow them."
- Without: "You are the change summariser. Read `<review folder>/change-summariser.md`, then follow it."

**Done when** it has returned.

## 3. Render

In `/tmp/rt-walkthrough/runs/<repo>-<branch or prN>-<YYYYmmdd-HHMMSS>/` (`/` in the branch becomes `-`), write each file with one `Write`, agent text verbatim:

- `meta.md`: the lines step 4 of `<review folder>/SKILL.md` lists for its `meta.md`, with `- Stack: none` when there is no stack, then `- Walkthrough: yes`.
- `summary.md`: the change summary.

Run `python3 <review folder>/render.py <run folder> /tmp/rt-walkthrough`. It writes the page and prints its path. On `error:`, fix the named input and rerun.

**Done when** it exits 0.

## 4. Show and reply

Outside T3 (no `mcp__t3-code__` tools listed), open the page with `open` (Darwin) or `xdg-open` (Linux). Inside T3, the link in the reply opens it. Reply with only:

```
<target> · stack: <stack> (<detected | argument>) · <reversibility level>
Several stacks matched: <names>. Pass one as an argument to get the reversibility.

1. <change entry title>
2. <change entry title>

Walkthrough: [<page file name>](<page path>)
```

Without a stack, the first line is `<target>` alone. Write the second line only when several stacks matched. List every change entry, in the summary's order.

# Target

How `rt-code-review` and `rt-walkthrough` resolve the **target** and build the **target block** that every agent receives. `stacks/` below is the folder next to this file.

## Arguments

An optional target (PR number or ref) and an optional stack (a folder name in `stacks/`). A lone argument is the stack when it names one, else it must be a number or a ref `git rev-parse --verify` accepts. A second argument must be a stack. On a bad argument, stop: say what is wrong in one sentence and list the stacks.

## Mode

| Target | Mode | BASE | Diff | Read a file | Search | List files |
|---|---|---|---|---|---|---|
| Number | PR | `gh pr view <n> --json baseRefName,headRefName,title,url`, `git fetch origin <baseRefName>`, `BASE=origin/<baseRefName>` | `git fetch origin pull/<n>/head`, `HEAD_SHA=$(git rev-parse FETCH_HEAD)`, `git diff BASE...HEAD_SHA` | `git show HEAD_SHA:<path>` | `git grep -n <pattern> HEAD_SHA` | `git ls-tree -r --name-only HEAD_SHA` |
| Ref | Ref | `git rev-parse --verify <ref>^{commit}` | `git diff <ref>...HEAD` | `git show HEAD:<path>` | `git grep -n <pattern> HEAD` | `git ls-tree -r --name-only HEAD` |
| Nothing | Branch work | `git merge-base <default> HEAD`; `<default>` is `git symbolic-ref --short refs/remotes/origin/HEAD`, else `main`, else `master` | `git diff BASE` plus `git ls-files --others --exclude-standard` | the working-tree file | `Grep` | `git ls-files` plus untracked |

PR mode fetches and never checks out.

## Stack

An argument wins, recorded as `<stack> (argument)`. Otherwise check the `Markers` of every `stacks/<stack>/setup.md` with the list-files command; exactly one match is `<stack> (detected)`. With none or several, the skill that sent you here says what to do. With a stack, read the stack settings that its `setup.md` describes.

## Target block

Mode, repo root, BASE, head (`HEAD_SHA`, `HEAD` or "working tree"), the PR number (PR mode), the diff, read-a-file, read-at-base (`git show <BASE>:<path>`), search and list-files commands, stack, stack settings, `git log --oneline BASE..<head>`, `git diff --stat`, and untracked files (Branch work).

**Done when** every field is filled. Stop with one sentence when a command fails or the diff and untracked list are both empty.

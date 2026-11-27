# Judging a comment

How a comment audit judges one comment. Judge it against the code as it is now: read the code around it, search for each symbol, file or ticket it names, and read `git log -L <line>,<line>:<file>` when its age matters.

## Categories

Every comment gets exactly one category, and the category sets its action.

- **Tautology**: everything the comment says already follows from the names, types and statements beside it. Section banners (`// MARK: - Properties`, `# Findings`), file headers that give the file's name, author and date (Xcode's template header, its copyright line included), and doc comments that restate a signature are tautologies. → **delete**.
- **Stale**: the comment names a symbol, file, behavior, step or ticket that no longer exists or no longer matches the code. Commented-out code, and a TODO the code has already done, are stale. → **delete**.
- **Excuse**: the comment admits the code is wrong and says why it stays that way: a workaround, "temporary", "for now", a TODO or FIXME naming a missing fix, or a directive that silences a real warning or type error. The hack is the problem, and the comment hides it. → **delete**, and file an issue to fix the hack. Comments that excuse the same hack share one issue.
- **Decision record**: the comment defends code that is right, with a reason the code cannot show: an external constraint such as a host API quirk, an obvious alternative that fails, or a unit, invariant or threading rule the signature leaves out. → an **ADR** when it passes the **ADR bar**: hard to reverse, surprising without context, and the result of a real trade-off. Comments that record the same decision share one ADR. Below the bar, → **into the code**: a name, an extracted function or constant, or a test that pins the behavior, within the limits of `edits.md`. When the meaning needs a public API renamed, → an **issue** for the rename, and the comment stays as an exception until it is done. When no name, structure or test can carry it, → **keep** as an **exception**.

An excuse and a decision record can read alike. An excuse says the code is wrong; a decision record says why it is right.

## Directives

A directive (`# noqa`, `# type: ignore`, `// swiftlint:disable`) is judged like any comment. One that still suppresses a false positive stays, kind `directive`, and `count` never counts it. One that suppresses nothing is Stale. One that silences a real problem is an Excuse. Settle "suppresses nothing" from the code; when only running the linter could settle it, mark the directive **unsure**.

## Lines the audit skips

These lines always stay, and get no row in `comments.tsv`:

- A shebang, a Python encoding line, and `Package.swift`'s `// swift-tools-version:` line.
- A **license header**: the first comment block in a file after those lines, a Python module docstring included, that contains `license`, `licence` or `SPDX-License-Identifier`, or, when it has no `Created by` line, `Copyright`, `©` or `All rights reserved`. Blank comment lines inside a block belong to it, and the header runs on across blank lines through each next block that has one of those words too.

## Unsure

When the evidence does not settle the category, or leaves two categories with different actions, mark the comment **unsure**: it stays, and the report lists it with the open question. A wrong deletion loses knowledge the code may hold nowhere else; an unsure comment costs one line.

## Judgements table

```
# Judgements: <diff | batch name>

| Comment | Category | Action | Evidence |
|---|---|---|---|
| `<file:line>` | <Tautology | Stale | Excuse | Decision record | Unsure> | <action> | <one line> |
```

The action is one of: `delete`, `delete, issue: <title>`, `ADR: <title>`, `into the code: <the move>`, `issue: <title>, keep until done`, `keep: exception`, `keep: unsure`, or `keep: directive` for a directive.

The evidence line names:

- **Tautology**: the code that already says it.
- **Stale**: the search result or line that contradicts it.
- **Excuse**: the hack, in one phrase.
- **Decision record**: which part of the ADR bar it passes or fails, and for an exception, why no name, structure or test can carry it.
- **Unsure**: the open question.

A row with no evidence line is unsure.

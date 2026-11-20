# Edits

How a comment audit applies each approved action. Apply them in this order: deletions, moves into the code, ADRs, then issues, so an issue can name the code as it now stands. In a diff audit the user's own uncommitted work sits in the same files: edit only the comment's lines and the move's lines.

## Delete

Delete the comment's lines. A trailing comment goes and its code stays, with the trailing whitespace removed. Collapse a doubled blank line that the deletion leaves.

## Into the code

A move stays inside one file and below the public API:

- rename a private, `fileprivate` or local Swift symbol, or a Python local or `_`-prefixed name, and every use of it;
- extract a function or named constant in the same file;
- add a test that pins the behavior, in a test file the repo already has for that code.

Before each move, copy its file to `<run folder>/before/<path>`. After the last move, run the stack's tests with the command `Commands` in `<skill>/../rt-test-audit/proof.md` names: for a swift-app, narrowed to the tests of the moved files; for a pipeline package, the declared tests (ADR 0012). On a failure, make one repair. When it still fails, copy each moved file back from `before/`, and the comment stays as an exception, with the failure as its reason. A command that cannot run is a check that did not run: record it with the command the user would run, and the moves stay.

In a full audit, run the tests once per batch that has a move.

## ADR

Write the ADR where the repo's `docs/agents/domain.md` points, else in `docs/adr/`, created when missing, with the next free number. Follow the format of the repo's existing ADRs. With none, use this shape: the decision as the title, `Status: accepted.`, a paragraph of context, a paragraph on the decision, a paragraph on the options considered, then `## Consequences` as bullets. Build it from the comment, the code and `git log` of the lines. Name code by path and symbol, never by line number.

## Issue

File it in the tracker that the repo's `docs/agents/issue-tracker.md` describes, or where the user said in step 4. One issue per hack. The title states the hack as a problem to fix. The body gives the file and symbol, the comment quoted as it was, why the code is a hack, and what a fix looks like when the evidence shows it. Record each issue's URL.

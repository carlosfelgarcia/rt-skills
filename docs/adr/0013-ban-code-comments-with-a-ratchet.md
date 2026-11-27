# Ban code comments, with a ratchet

Status: superseded in part by ADR 0014, which drops the ratchet. The ban and the audit stand.

The old rule allowed a comment wherever the logic was complex or non-obvious. In practice that let comments pile up: some only repeated the code, some described code that had since changed, and some justified a hack, which agents then copied as if the hack were the pattern. A comment is read by every agent that opens the file, so a wrong one keeps steering work long after anyone checks it.

Code comments are now banned in the user's own projects, and audited away in OD Studios pipeline packages too. What a comment used to carry goes somewhere it can be checked: into the code's names, structure or tests; into an ADR when the decision is hard to reverse, surprising and the result of a real trade-off; or into an issue when it excuses a hack. `rt-comment-audit` does the moving, and in the user's own projects a ratchet stops new comments arriving while old ones are still being removed.

The options were to keep the old rule and judge comments one at a time in review, which is how they piled up; to ban comments and delete every one in a single pass, which forces a repo-wide change before the rule can be switched on; or a ban enforced by a ratchet, so each file's comment count can only go down.

## Consequences

- The ratchet counts comments per file and fails on any rise, and a new file starts at zero. A repo can switch the ban on the day of its first audit.
- Comments that the code cannot carry and that do not meet the ADR bar stay in the ratchet's count as exceptions, and each audit report lists them. So do comments the audit was unsure about.
- Directives the tools need, such as `# noqa` or `// swiftlint:disable`, are judged like any other comment, but the ratchet does not count their syntax.
- Shebangs, encoding lines, the `swift-tools-version` line and a license header at the top of a file must stay, so a comment audit never lists, judges or counts them. Judging them only made the audit stop and ask about lines that were never going to go.
- Pipeline packages get no ratchet. They are shared with the rest of OD Studios, and a check that fails on comments would confuse everyone else who works in them. A comment audit there deletes and moves comments, and nothing stops new ones.
- Moving a comment's meaning into the code is a refactor, so the stack's tests run after it; in a pipeline package, its declared tests, which extends ADR 0012 to `rt-comment-audit`. A refactor that would rename a public API becomes an issue instead.
- Each stack's `setup.md` says whether it gets the ratchet, so a new stack chooses explicitly.

# Verify each finding with its own verifier

Reviewers report findings that do not hold up: a bug on a path no caller reaches, a severity that is too high, a fix that would not compile. `rt-code-review` now checks every finding before the report is built. Each finding gets its own **verifier** agent, started in one batch, rather than one agent for all findings or a check by the main session. A verifier sees only the target block, its one finding and its brief, so it traces the claim again from the code instead of re-reading the reviewer's reasoning. A batch verifier, or the main session that has already read every finding, tends to agree with what it read first. We pay one agent per finding for that independence.

## Consequences

- A run with many findings starts many verifiers. There is no cap: an unverified tail would undo the step.
- Verification is static, like the review. A verifier proves a verdict by quoting the code; it never builds or runs it. The reasons the stack files give for the reviewers hold more strongly here: many verifiers run at once, and running pipeline code can reach production. A claim about runtime behaviour goes to a host probe instead (ADR 0003).
- When a verifier cannot prove or disprove a finding, and the gap is not runtime behaviour, the verdict is Confirmed. A doubtful finding stays visible; only a proven one is dismissed.
- Nits are verified too. We first skipped them on the grounds that whether a nit is worth fixing is the nit. On the `oasis-menu` review, 5 of 8 unverified nits were dropped once checked, and two were wrong: reviewers file small or doubtful claims of failure as Nit, not only taste.
- Dismissed findings stay in the report, collapsed, so a reader can audit the verifier.

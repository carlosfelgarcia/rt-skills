# Verify each finding with its own verifier

Reviewers report findings that do not hold up: a bug on a path no caller reaches, a severity that is too high, a fix that would not compile. `rt-code-review` now checks every Blocking and Should-fix finding before the report is built. Each finding gets its own **verifier** agent, started in one batch, rather than one agent for all findings or a check by the main session. A verifier sees only the target block, its one finding and its brief, so it traces the claim again from the code instead of re-reading the reviewer's reasoning. A batch verifier, or the main session that has already read every finding, tends to agree with what it read first. We pay one agent per finding for that independence.

## Consequences

- A run with many findings starts many verifiers. There is no cap: an unverified tail would undo the step.
- Verification is static, like the review. A verifier proves a verdict by quoting the code; it never builds or runs it. The reasons the stack files give for the reviewers hold more strongly here: many verifiers run at once, and running pipeline code can reach production.
- When a verifier cannot prove or disprove a finding, the verdict is Confirmed. A doubtful finding stays visible; only a proven one is dismissed.
- Nits are not verified. Whether a nit is worth fixing is the nit.
- Dismissed findings stay in the report, collapsed, so a reader can audit the verifier.

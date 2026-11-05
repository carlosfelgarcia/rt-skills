# Settle runtime claims with a host probe

Some findings rest on how a host behaves at runtime: whether `evalAsString()` raises on a broken expression, whether hython records undo steps. A static verifier cannot see that in the code, and under ADR 0002 it returned Confirmed, so a wrong claim reached the report looking checked. On the `oasis-menu` review, one such claim was wrong. The main session settled it, and one more, with a few seconds of hython each.

A verifier now returns **Unproven** for such a claim, with a **host probe** (the smallest script that shows the behaviour) and the output the claim predicts. The main session runs the probe, not the verifier, and only when the stack file has a `Host probes` section and the probe keeps its limits. The session only compares the output with the prediction, so the verdict stays independent of the session's own reading of the findings.

## Consequences

- Probes run one at a time in the main session. Parallel verifiers each starting a DCC would take a license seat each.
- A probe imports only the host's own modules and the standard library, never the repo or its other dependencies, so it cannot reach ShotGrid, the farm or production paths. That keeps the reason for static review intact.
- A stack with no `Host probes` section (`swift-app` today) runs no probes. Its Unproven findings stay visible with an `unproven` tag and their probe, so a reader knows what is unchecked and how to check it.

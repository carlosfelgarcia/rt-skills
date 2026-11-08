# Fix context goes to the reviewers, never the verifiers

Status: superseded in part by ADR 0010, which limits the re-review to the commits of its fix run.

After `rt-fix-findings` fixes a branch, it runs `rt-code-review` on the whole branch with a **fix context**: how each finding was fixed, or why it was not. Without it, the reviewers report every dismissed or held finding again and cannot tell whether a fix solves its finding. But ADR 0002 keeps a verifier independent by showing it only the target block, its finding and its brief. So only the reviewers receive the fix context. A verifier that read "this was fixed" or "this was dismissed" would tend to agree with it, and we would lose what we pay one agent per finding for.

## Consequences

- A reviewer does not raise a dismissed or held finding again unless a fix changed its reason. A wrong dismissal can therefore survive a re-review; the first verifier's evidence stays the check on it.
- Findings a reviewer raises with the fix context in hand are verified as usual, from the code alone.

# Score findings from 1 to 10, and skip low scores in fix runs

Three bands (Blocking, Should-fix, Nit) could not say "real, but not worth a commit". `rt-fix-findings` fixed every Confirmed (Proven) finding, so on the `WalkWithJesus` memory hand-off run, three of five commits fixed a test name, a doc comment and a helper. Each finding now gets a **score** from 1 to 10, set against fixed anchors in the reviewer brief, and the band comes from the score (8 to 10 Blocking, 4 to 7 Should-fix, 1 to 3 Nit). A fix run takes a **threshold** (`min=`, default 4) and skips findings below it.

## Consequences

- The reviewer proposes the score and the verifier settles it. The threshold uses the verifier's score, because the verifier is the independent check (ADR 0002). A verifier regrades on any anchor it can show is wrong, even inside one band.
- Every finding is still verified, whatever its score. Skipping verification below the threshold would undo ADR 0002's lesson: reviewers file doubtful claims of failure at low severity, and a verifier can raise a score above the threshold.
- **Skipped** is its own outcome, not a kind of Dismissed or Held. Dismissed needs proof that the finding is not real or not worth fixing; Held waits for the user. A skipped finding may be real, and the threshold already decided it. The fix context records it, so a re-review does not raise it again, and a bot finding that repeats it is dismissed (ADR 0005).
- Unanchored 1-to-10 scores drift and cluster. The anchors are the calibration; `evals/` cases record an expected score range so a change to the anchors can be checked.

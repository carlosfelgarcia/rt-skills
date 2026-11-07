# Evals

Replays of past `rt-code-review` runs whose outcome is known, so a change to a brief can be checked against what really happened.

## Verifier replays

A replay feeds stored findings to fresh verifiers and compares their verdicts with the known outcome. It skips the reviewers, so reviewer randomness does not move the score.

Each case is a folder with three files:

| File | Holds |
|---|---|
| `target.md` | The target block the verifiers received, with the repo root replaced by `<worktree at <sha>>`. |
| `findings.md` | Every finding exactly as the reviewers returned it, with its finding ID. |
| `expected.md` | The verdict each finding should get, the range its score should fall in (such as 3 to 4), what settles it, and how to judge the run. |

To replay a case:

1. On a machine with the reviewed repo, run `git worktree add <path> <head sha>`, and put `<path>` in the target block's repo root.
2. In a session at that worktree, start one `rt-skills:rt-verifier` per finding in one message, with the prompt that step 3 of `skills/rt-code-review/SKILL.md` defines.
3. Run any host probes that the Unproven verdicts return, as step 3 defines.
4. Judge each verdict, and each Regraded score, against `expected.md`. A score outside its range means the anchors in `reviewer-brief.md` need work.

Cases built from employer code go in `evals/private/`, which git ignores: this repo is public.

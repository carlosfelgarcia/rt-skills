# Drop the comment ratchet

Status: accepted. Supersedes ADR 0013 in part: code comments stay banned and `rt-comment-audit` still moves them, but nothing installs a ratchet.

ADR 0013 paired the ban with a ratchet: a comment audit in the user's own projects copied `comment_ratchet.py` into the repo, wrote a `.comment-ratchet.json` baseline, and wired a check into a pre-commit hook or CI that failed whenever a file's comment count rose. When we tried it on one of the user's projects, it did not go well. A comment audit is a judgement made with the user, but the ratchet is a gate that every commit has to pass, and it lives in the repo, out of the plugin's reach. So the ratchet is gone, and enforcement between audits is left to another tool, if one proves worth it.

The options were to fix the ratchet inside this plugin, to keep it but make it opt-in for each repo, or to drop it and keep the audit. Fixing or gating it would keep a repo-side script and baseline that the plugin has to install, update and migrate in every repo that used it. Dropping it leaves the audit doing the one job it does well.

## Consequences

- `comment_ratchet.py` is now `comment_scan.py`, and it only has `list` and `count`. `init`, `check`, `--lower` and the `.comment-ratchet.json` baseline are gone, and the audit runs the plugin's copy only, never one inside the repo.
- The stacks' `setup.md` files no longer have a `Ratchet` line, and the swift-app and pipeline stacks now audit the same way. The comment audit's report no longer has a `Ratchet` line.
- Nothing stops new comments between audits. A diff audit on each branch is how they get caught.
- A repo where an earlier audit installed the ratchet still has the script, the baseline and the hook or CI step. Remove them by hand: nothing in the plugin updates them now.
- `count` no longer reads excludes from a baseline. Pass `--exclude <glob>` to skip vendored or generated code.

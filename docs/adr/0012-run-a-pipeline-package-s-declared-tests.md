# Run a pipeline package's declared tests

Status: accepted. Narrows "Why the code never runs" in the pipeline stack.

Pipeline tests never ran: not in a review, not after a fix run. The rule exists because pipeline code can reach ShotGrid, the render farm or production paths, even from a test. But a test audit cannot work without running tests: it needs a baseline, keepers that pass after each batch, and a mutation that turns a keeper red. And a fix run that never runs its tests leaves the user to find out later whether a fix broke one.

Most released pipeline packages already declare their tests in `package.py`, as a rez `tests` entry with `run_on: ['default', 'pre_install']`, so every `rez build --install` runs them. The package author chose that command and the team already runs it on every install. The main session now runs those declared tests, through rez, after an `rt-fix-findings` run and during an `rt-test-audit`, and nowhere else.

The options were to keep the rule, which leaves the test audit without proof for pipeline packages; to run tests but ask before every run, which adds a stop to every batch for a command the team already runs on every install; or this.

## Consequences

- Only the declared `tests` entry runs, through rez. A raw `pytest` or `python` call, or a command the skill builds itself, stays forbidden.
- A package that declares no `tests` runs none. Its fix runs and test audits report the run-based checks as not run, with the command the user would run.
- Reviewers, verifiers and the change summariser still never run code. Only the main session runs the declared tests, one run at a time.
- Host probes keep their own limits from ADR 0003.

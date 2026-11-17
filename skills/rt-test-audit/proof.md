# Proof

How a test audit runs tests, and what counts as proof. Only the main session runs tests, one run at a time. `<review folder>` is the `rt-code-review` skill folder, next to this file's folder.

## Commands

- **swift-app**: the test command in `Fix checks` of `<review folder>/stacks/swift-app/setup.md`. For one batch, narrow it to the batch's tests and keepers: `swift test --filter <pattern>`, or `xcodebuild test -only-testing:<target>/<suite>`.
- **pipeline**: `Declared tests` in `<review folder>/stacks/pipeline/setup.md`, the whole declared suite every time, with `<run folder>/packages-<n>` as the prefix, `<n>` counting up per run.

A command that cannot run, such as a tool that is not installed or a package that declares no tests, is a check that did not run. Record it with the command the user would run, and report every check that depends on it as **not run**. The audit carries on.

## Baseline

Before any edit, run the suite once and write to `<run folder>/baseline.md` each test file's result at `PRE_AUDIT`: pass, fail or not run.

## A test is proof when

It goes **red** on the defect it names, for that reason rather than on its setup, and green on correct code. A behavior-preserving refactor keeps it green.

## Mutation

To show a keeper guards a contract: make one deliberate change to the owner that breaks the contract, run the keeper, and see it go red. Then `git checkout -- <file>`, and check that `git diff -- <file>` prints nothing. A keeper that stays green proves nothing: the contract has lost its proof.

## Defects

A test that fails at baseline may be a bug in the product, not a stale test. Reproduce it and find its owner. When it is a product bug, fix it at the owner in its own commit, apart from every batch, and prove it with a **control**: the same command goes red with the fix reverted and green with it. Record a discrepancy unrelated to the audited tests as a follow-up.

## Failures

A failure has a cause in the product, the fixture or shared state: repair it there. A retry, a longer timeout, a weaker assertion, a broader mock or an edited baseline hides the failure and repairs nothing. Rerun a command for a changed input, never to get green.

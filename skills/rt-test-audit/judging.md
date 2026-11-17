# Judging a test

How a test audit judges an existing test. `<review folder>` is the `rt-code-review` skill folder, next to this file's folder.

Read first `<review folder>/rules/test.md` and `<review folder>/stacks/<stack>/test.md`: the gutted check and its five shapes. Every test that fails the gutted check is a candidate. This file adds what a single test does not show: whether its contract is already proven elsewhere, and what production code exists only for it.

Judge a test by what it asserts, not by its name.

## Owners and keepers

Each contract has one owner, and one keeper proves it at the strongest boundary: the owner's real entry point with fake external I/O (network, ShotGrid, a database, files outside a temp folder), rather than a mocked collaborator. A second test of the same contract earns its place only with a risk the keeper never reaches, such as another transport or lifecycle. A bug gets one regression test, at its owner, rather than one at every layer it crossed.

## Patterns

Beyond the five shapes of `rules/test.md`:

- **Duplicate contract**: the same contract asserted at several layers, or replayed once per caller of a shared helper. → Consolidate into the keeper.
- **Test-only seam**: production code only tests call, such as an export, a global, a reset hook, a flag, a wrapper or an injection parameter. → Move the proof to the real boundary; the seam goes with the test.
- **Copied inventory**: the test restates a list of exports, files or manifest entries, or greps the source for an exact string or import.
- **Mock supplies the answer**: the mock returns the value the test asserts, or stands in for two distinct APIs as if they behaved the same.
- **Fabricated owner output**: a fixture supplies the receipt, ordering or callback the owner should produce, or the test asserts a write on a path the store never writes.
- **Capability, not effect**: the test asserts a flag that says something is supported, rather than the delivery or acknowledgement it promises.
- **Wrong guard**: a negative test that passes on an unrelated guard, or asserts a rejection the production code never reaches.
- **Misleading name**: the name promises behavior its inputs and assertions never exercise.

## Retention bar

A test that matches a pattern still stays when it is the independent proof of a contract outside the code itself: a public API, protocol, config or file format, migration, storage, security, platform behavior, default, prompt bytes, packaging, release, or an observable order of events. Source inspection stays when it is the cheapest guard of a user-facing key, byte or path and survives renaming identifiers. Slow or static is a cost, never a reason to delete.

## Marks

- **Retain**: the contract it proves and the defect it catches.
- **Fix**: the contract stays; the assertion is rewritten.
- **Consolidate**: the keeper that absorbs its distinct assertion first.
- **Delete**: the proof that remains, or why no contract exists.

## Evidence

Before marking a test Fix, Consolidate or Delete, read the whole test, its owner and the owner's entry point, callers and callees, the sibling tests and any overlapping proof, where CI runs it, and `git log` of the test. A claim about a dependency rests on the dependency's source, found as `stack.md` says. Record:

- `file:line`, the test's name, and the defect it can detect, or `none`.
- The non-test callers of each seam it uses, or `none`.
- The keeper or remaining proof, or why the contract needs none.
- Why the test exists, from its history, and what removing it unlocks.
- The command that runs the keeper.

A test with a line missing gets no mark and stands.

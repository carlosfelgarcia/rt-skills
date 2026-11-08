# QA: swift-app

The Swift forms of the rules in `rules/qa.md`, and the Swift groups.

## Correctness

- Off-by-one: `..<` against `...`.
- Force unwraps (`!`), `try!`, `as!`, `fatalError` and `precondition` on paths that real input can reach.
- Optional chaining or `guard ... else { return }` that silently skips work the caller expects to happen.

## Edge cases

Also: no network, strings with emoji or combined characters, other locales (decimal separators, right-to-left text), other time zones and daylight saving changes, and dates around midnight and month ends.

## Error handling

- Swallowed errors: `try?` that drops an error the caller needs, an empty `catch {}`, an error logged with `print` or `Logger` that the caller or the user never sees.
- Resources: security-scoped resources (`stopAccessingSecurityScopedResource`) and observers too. Look for a missing `defer`.

## Regressions

- Check protocol requirements and their conformers too.
- A changed `Codable` key or SwiftData `@Model` property with no migration loses stored data: Blocking.

## Security (where the change touches it)

- Secrets, tokens or API keys in source, `Info.plist`, `UserDefaults` or `@AppStorage` instead of the Keychain.
- App Transport Security exceptions (`NSAllowsArbitraryLoads`, per-domain exceptions).
- URLs, file paths or `NSPredicate(format:)` strings built from outside input (deep links, the pasteboard, imported files, server responses) with no check, or paths that can leave the intended directory.
- `NSKeyedUnarchiver` without secure coding on data from outside.
- Personal data logged with `privacy: .public`.

## Performance (where the change touches it)

- Heavy work on the main actor: decoding, image processing, sorting or filtering large collections, work inside a SwiftUI `body` or a computed property `body` reads.
- A SwiftData fetch inside a loop is the batched-call rule.
- Images loaded at full size for a thumbnail.

## Concurrency (where the change touches it)

Read the stack settings in the target block first: default isolation and upcoming features change which rules apply.

Blocking:
- **Unprotected shared state**: mutable state reached from two isolation domains with no actor, `@MainActor` or `Mutex` in between, such as an `@unchecked Sendable` class with a `var` written from a `Task`.
- **Blocking waits in async code**: `DispatchSemaphore.wait()`, `DispatchGroup.wait()`, `Thread.sleep`, or a lock held across an `await`. They deadlock or starve the cooperative thread pool.
- **Reentrancy**: an actor checks state before an `await` and acts on it after the `await` without a new check, and you can trace a wrong result, as in `if cache[id] == nil { cache[id] = await fetch(id) }`.
- **SwiftData across actors**: a `@Model` instance or a `ModelContext` crosses an actor boundary. → pass the `PersistentIdentifier` and fetch on the other side.
- **UI state off the main actor**: UI-owned state changed from a nonisolated or background context. Report this only when the default isolation is not `MainActor`.

Should-fix:
- **Unsafe escape hatch**: `@unchecked Sendable`, `nonisolated(unsafe)` or `@preconcurrency` with no comment that states the safety invariant and when the escape hatch will be removed.
- **Unexplained detached task**: `Task.detached` with no stated reason.
- **Unstructured where structured fits**: `Task {}` where `async let` or a task group would do the work, which loses automatic cancellation.
- **No cancellation check**: long-running work in a task that never checks `Task.isCancelled` or calls `Task.checkCancellation()`.
- **Task retain cycle**: a long-lived task (stored, or looping with `for await`) that captures `self` strongly.
- **Blanket `@MainActor`**: `@MainActor` added to code that is not UI-bound, to silence a diagnostic.
- **Fake await**: a dummy suspension added to satisfy `async_without_await`. → remove `async`, or suppress the rule with a reason.
- **Work that never leaves the main actor**: with `NonisolatedNonsendingByDefault` on, a `nonisolated async` function runs on the caller's actor, so heavy work in it still runs on the main actor. → mark it `@concurrent`.

Nit:
- **Task entry isolation**: a `Task {}` that inherits `@MainActor` when nothing before its first `await` needs the main actor. → `Task { @concurrent in ... }`, with Swift 6.2 or later.
- **Thread-based reasoning**: `Thread.current` or thread names used to reason about isolation.

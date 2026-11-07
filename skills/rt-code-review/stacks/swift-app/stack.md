# Stack: swift-app

A RationalBit Swift app or Swift package, built with Xcode or SwiftPM.

## Why the code never runs

Do not run `swift build`, `swift test`, `xcodebuild`, a simulator or any script. A build takes minutes, needs a simulator, and three reviewers running at once fight over DerivedData and simulators. CI runs the tests. The one exception is `Fix checks` in `setup.md`, for the main session alone.

## What the tooling already reports

Leave to the repo's configured linter (such as SwiftLint) and to the compiler whatever they already report. When the stack settings show language mode 6 or strict concurrency `complete`, the compiler already reports Sendable crossings, isolation errors and synchronous waits in async contexts; report those only under older or `unknown` settings.

An assumption for an `unknown` setting reads, for example: "Assuming nonisolated default isolation, …".

## Examples

- **Where:** `Sources/Feature/File.swift:42`
- **Structure:** `SettingsView -> SyncStore -> APIClient`

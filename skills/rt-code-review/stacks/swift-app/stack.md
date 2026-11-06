# Stack: swift-app

A RationalBit Swift app or Swift package, built with Xcode or SwiftPM.

## Markers

The skill picks this stack when the list-files command lists `Package.swift` or `<name>.xcodeproj/project.pbxproj` at the repo root.

## Stack settings

The skill reads these at the head with the read-a-file command, from `Package.swift` and every `*.xcodeproj/project.pbxproj` that the list-files command lists, and puts them in the target block:

| Setting | `Package.swift` | `.pbxproj` |
|---|---|---|
| Language mode | `swiftLanguageModes`, `swiftLanguageVersions` or `-swift-version` | `SWIFT_VERSION` |
| Strict concurrency | `StrictConcurrency` feature flag | `SWIFT_STRICT_CONCURRENCY` |
| Default isolation | `.defaultIsolation(...)` | `SWIFT_DEFAULT_ACTOR_ISOLATION` |
| Upcoming features | `.enableUpcomingFeature(...)` | `SWIFT_UPCOMING_FEATURE_*` |

Write `unknown` for a setting you cannot find; `// swift-tools-version:` is not a reliable proxy for the language mode. Where targets differ, list each target's values. When neither file is in the repo, as when the user passed `swift-app` as an argument, write `none`.

## Why the code never runs

Do not run `swift build`, `swift test`, `xcodebuild`, a simulator or any script. A build takes minutes, needs a simulator, and three reviewers running at once fight over DerivedData and simulators. CI runs the tests. The one exception is the `Fix checks` section, for the main session alone.

## Fix checks

After the last fix of an `rt-fix-findings` run, one session has the machine, so run one build and test pass. Use the test command that the repo documents. Without one, run `swift test` for a `Package.swift`, or `xcodebuild test` with the scheme from `xcodebuild -list` and an available simulator for an Xcode project. A tool that is not installed, as on a Linux machine, is a check that did not run.

## What the tooling already reports

Leave to the repo's configured linter (such as SwiftLint) and to the compiler whatever they already report. When the stack settings show language mode 6 or strict concurrency `complete`, the compiler already reports Sendable crossings, isolation errors and synchronous waits in async contexts; report those only under older or `unknown` settings.

An assumption for an `unknown` setting reads, for example: "Assuming nonisolated default isolation, …".

## Examples

- **Where:** `Sources/Feature/File.swift:42`
- **Structure:** `SettingsView -> SyncStore -> APIClient`

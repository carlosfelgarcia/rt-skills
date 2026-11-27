# Setup: swift-app

For the main session only.

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

## Fix checks

After the last fix of an `rt-fix-findings` run, one session has the machine, so run one build and test pass. Use the test command that the repo documents. Without one, run `swift test` for a `Package.swift`, or `xcodebuild test` with the scheme from `xcodebuild -list` and an available simulator for an Xcode project. A tool that is not installed, as on a Linux machine, is a check that did not run.

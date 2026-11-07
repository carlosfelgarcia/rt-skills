# Reversibility: swift-app

A revert of app code is clean unless the change persists something in a new shape, or reaches outside the device:

| Level | Triggers |
|---|---|
| Revert with cleanup | A SwiftData or Core Data model change: a new or renamed `@Model` property, a `VersionedSchema`, a `SchemaMigrationPlan` stage that only adds. A new or renamed `UserDefaults` or `@AppStorage` key. A Keychain item. A file format or a cache the app writes to disk. A new background task identifier or notification category. |
| One-way | A migration stage that deletes or rewrites data in place. A CloudKit record type or field (once deployed to production, it cannot be removed). Data the change sends to a server or a third party. A change to the bundle ID, App Group or iCloud container. |

Everything else, such as views, logic and tests, is Revert-safe.

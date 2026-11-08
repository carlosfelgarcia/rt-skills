# Architecture: swift-app

The Swift forms of the rules in `rules/architecture.md`.

- **Blocking example**: a dependency cycle that fails to resolve.
- **Information leakage**: also a storage key, a URL scheme or a date format.
- **Dependency direction**: domain or model code that imports `SwiftUI` or `UIKit`, or a package target that depends on the app target.
- **Dependency cycle**: between targets or packages.
- **Access widening**, the Swift reach-in: a declaration made `internal` or `public`, or reached through `@testable import` outside a test target, only so other code can use its internals.
- **Hidden shared state**: `static let shared` singletons and `@AppStorage`, as well as globals and caches.

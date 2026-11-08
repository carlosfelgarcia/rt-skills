# Tests: swift-app

The Swift Testing forms of the rules in `rules/test.md`, with their XCTest equivalents.

- **Untested new behavior**: also cancellation and deallocation of a long-lived task.
- **Empty values** for the gutted check: `nil`, `[]`, `""`, `0`, a default-initialized struct.

## The five shapes

- **Weak or no assertion.** No `#expect`, or only `#expect(value != nil)`, `#expect(value is Draft)`, `#expect(throws: Never.self) { ... }`, `#expect(items.count > 0)`, and their `XCTAssertNotNil` / `XCTAssertNoThrow` / `XCTAssertTrue` equivalents.
- **Mock or absence only.** Only `#expect(spy.saveWasCalled)`, `#expect(spy.callCount == 0)`, `#expect(result == nil)`, `#expect(items.isEmpty)`, `#expect(items.count == 0)`, `#expect(value != wrongValue)`.
- **Self-referential.** `#expect(sut.slug(for: name) == sut.slug(for: name))`, `#expect(parsed.url == buildURL(id))`.
- **Constant pin.** `#expect(Limits.maxTools == 8)`, `#expect(Genre.allCases.count == 12)`, `#expect(Prompts.system.contains("You are"))`.
- **Fixture asserts fixture.** A value computed in the suite's `init()` or `setUp()`.

**The fix**, for example: `#expect("Hello, World!".slugified() == "hello-world")`.

**Keep** a test that an enum case has a matching asset or string key, and a compile-time check whose failure is a build error rather than a failed expectation: `let _: any Sendable = DraftDTO.sample`.

## Concurrency in tests

- **Assert before the work runs (Blocking)**: the subject starts a `Task {}` inside itself and the test asserts at once without awaiting it, so the assertion only sees the starting state. This is a gutted-check failure. → await the work, or expose an async entry point the test can await.
- **Wait with a sleep (Should-fix)**: `Task.sleep`, `XCTWaiter` with a fixed timeout, or another fixed delay used to wait for async work. → use `confirmation`, await the result directly, or inject a clock.
- **Shared state across parallel tests (Should-fix)**: Swift Testing runs tests in parallel by default, so tests that share mutable static state or a singleton are flaky. → give each test its own state, or mark the suite `.serialized` with a reason.

=== A1 finding
### View writes to the file store
- **Where:** `Sources/Composer/ComposerView.swift:40`
- **Score:** 5 (Should-fix)
- **What:** The view calls `FileStore` past `DraftStore`.
- **Why:** A second path writes drafts, so the two paths drift.
- **Fix:** Call `DraftStore.save` only.
- **Structure:** `ComposerView -> FileStore`, `ComposerView -> DraftStore -> FileStore`

=== A1 verdict
- **Verdict:** Confirmed
- **Proof:** Proven
- **Reason:** The view calls `FileStore.write` at line 40.
- **Evidence:** `Sources/Composer/ComposerView.swift:40`: `FileStore.write(draft)`

=== A2 finding
### Name is vague
- **Where:** `Sources/Drafts/DraftStore.swift:3`
- **Score:** 2 (Nit)
- **What:** `doIt` says nothing.
- **Why:** Readers guess.
- **Fix:** Rename to `save`.

=== A2 verdict
- **Verdict:** Refuted
- **Reason:** The head already names it `save`.
- **Evidence:** `Sources/Drafts/DraftStore.swift:3`: `func save(_ draft: Draft)`

=== T1 finding
### Save test cannot fail
- **Where:** `Tests/DraftStoreTests.swift:20`
- **Score:** 6 (Should-fix)
- **What:** The test asserts on the draft it passed in.
- **Why:** A save that writes nothing still passes.
- **Fix:**
  ```diff
  -    #expect(draft.text == "hi")
  +    #expect(try store.load().text == "hi")
  ```

=== T1 verdict
- **Verdict:** Regraded
- **Score:** 8
- **Proof:** Proven
- **Reason:** The test cannot fail for the defect it exists to catch.
- **Evidence:** `Tests/DraftStoreTests.swift:20`: `#expect(draft.text == "hi")`

=== T2 finding
### Doc comment is stale
- **Where:** `Tests/DraftStoreTests.swift:5`
- **Score:** 3 (Nit)
- **What:** The comment names the old method.
- **Why:** It misleads a reader.
- **Fix:** Update the comment.

=== Q1 finding
### Write can throw on a full disk
- **Where:** `Sources/Drafts/DraftStore.swift:12`
- **Score:** 7 (Should-fix)
- **What:** `try? write` drops the error.
- **Why:** A failed save is silent.
- **Fix:** Throw the error to the caller.

=== Q1 verdict
- **Verdict:** Unproven
- **Reason:** It rests on how `FileManager` fails at runtime.
- **Evidence:** `Sources/Drafts/DraftStore.swift:12`: `try? data.write(to: url)`
- **Probe:**
  ```swift
  print("probe")
  ```
- **Expect:** `error`

=== Q1 probe
- **Result:** Unproven
- **Reason:** The swift-app stack has no Host probes section.

=== Q2 finding
### [Blocking] Draft lost when the app quits
- **Where:** `Sources/Composer/ComposerView.swift:44`
- **What:** The save runs in a detached task that the app does not wait for.
- **Why:** A quit drops the draft.

=== Q2 verdict
this is not a verdict block

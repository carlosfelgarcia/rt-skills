### Lesson: How a draft reaches the disk
- **Win:** You can trace a draft from the composer to the file on disk.
- **Builds on:** none

### Before
Before this change, nothing saved a draft when the composer closed (`Sources/Composer/ComposerView.swift:40` at BASE).
```text
ComposerView.onDisappear
  (nothing)
```

### Now
Now the composer calls `DraftStore.save`, which writes JSON through `FileStore` (`Sources/Drafts/DraftStore.swift:12`).
```text
ComposerView.onDisappear
  DraftStore.save(draft)
    FileStore.write
```

### Why it changed
The commit says users lost text when they closed the composer.

### Concepts
- **Draft**: text the user has not sent yet. Source: `GLOSSARY.md`.

### Read next
[Swift Programming Language: Error Handling](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/errorhandling/) explains `try?`.

### Quiz
1. What writes the file?
   - [ ] `ComposerView`
   - [x] `FileStore`
   - [ ] `DraftStore`
   > `DraftStore.save` calls `FileStore.write` at line 12.
2. When does the save run?
   - [x] When the composer closes
   - [ ] When the user sends text
   > It runs in `onDisappear`.

### Reference
- **Draft save path**: `ComposerView` → `DraftStore.save` → `FileStore.write`.

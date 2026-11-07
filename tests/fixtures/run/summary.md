### Overview
The change saves a `Draft` when the composer closes. It touches `DraftStore` and `ComposerView`.

### Reversibility
Level: Revert with cleanup
- `Sources/Drafts/DraftStore.swift:12`: drafts saved in the new `version: 2` shape stay on disk after a revert. Delete `drafts.json` to clean up.

### Save path
The call tree of a save after the change.
```text
ComposerView.onDisappear
  DraftStore.save(draft)
    FileStore.write
```

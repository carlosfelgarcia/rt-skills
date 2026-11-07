# Reversibility: pipeline

A revert of pipeline code is clean unless the change writes to shared places that other tools and people read:

| Level | Triggers |
|---|---|
| Revert with cleanup | A new or renamed ShotGrid field, entity or status that the code writes. A new path template, file name pattern or publish layout. A cache or sidecar file format. A new environment variable or config key that other packages read. A version bump in `package.py` that other packages pin. |
| One-way | Code that deletes, moves or overwrites files on production paths. Code that updates or deletes ShotGrid entities in bulk. A change that submits farm jobs or sends notifications to people. A released rez package version: other packages may already resolve it. |

Everything else, such as library logic, UI and tests, is Revert-safe.

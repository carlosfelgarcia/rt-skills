# Show every change in the summary, without a lesson

Status: accepted. Supersedes ADR 0007.

The lesson taught one topic per review, so on a branch with five or six behavior changes it showed the before and after of one and hid the rest. Its quiz and the learning records it fed added no value for the one developer who uses this plugin, and the lesson page repeated what the report's change summary already said. The lesson, its writer, the quiz, the learning records and `MISSION.md` are gone. The change summariser now writes a **change entry** for every behavior change: a view at BASE and the same view at the head, a diagram when one shows the change and the code itself when it is too small to draw, and why it changed. Small mechanical edits go in one Other changes list.

## Consequences

- The report is the only page. The overview lists every entry, and the entries come before the findings, so a reader knows what changed before reading what is wrong with it.
- One agent writes the overview, the reversibility and the entries, so they agree. On a large branch it can be the slowest agent in step 2.
- `render.py` links each finding to the entries whose `Files` line names its file, in both directions, on the HTML only. File-level matching can tag a finding with more than one entry; line ranges were more precise but would fail silently when the summariser gets a line wrong. The findings file has no change entries, because a fix run works per finding.
- A re-review also gets change entries. Its entries are the fixes, which an agent wrote, so the developer has not seen them.
- The stacks' `resources.md` files are deleted, because only the lesson writer read them. Lessons and records already in `~/.rt-skills/learning/` stay on disk; nothing reads or writes them now.

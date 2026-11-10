# A lesson for each review, written apart from the findings

Status: superseded by ADR 0011, which shows every change in the change summary and writes no lesson.

Code review is where a developer learns the codebase, but the report only says what is wrong. Each review now also writes a **lesson**: a short page, modelled on the `teach` skill, that teaches one thing about the code the change touches (how it worked at BASE, how it works now, why) and ends with a quiz. A **lesson writer** agent writes it in the same batch as the reviewers.

## Consequences

- The lesson writer never sees the findings. It runs in parallel with the reviewers, so the lesson costs no wall time, and it teaches how the code works, not what is wrong with it.
- Lessons, reference entries and **learning records** live in a learning workspace outside the reviewed repo, at `~/.rt-skills/learning/<repo>/`. The learner is one developer, not the team, so none of it belongs in the repo, and `/tmp` would lose it.
- The quiz runs in the browser, where the agent cannot see it. It ends with a result line for the developer to paste in the chat. A learning record is written only on such evidence, because a lesson shown is not a lesson learned. Without records, the lesson writer can still avoid repeats from the lesson file names, but it cannot build on what the developer knows.
- A re-review in a fix run writes no lesson: its change is the fixes, which the developer already knows.
- Lesson claims about a framework cite the stack's `resources.md` or the dependency's code, never the model's memory.

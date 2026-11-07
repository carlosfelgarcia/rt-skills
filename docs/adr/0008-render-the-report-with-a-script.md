# Render the report with a script

The main session used to fill `report-template.html` by hand: order the cards, count them, escape every diff, apply the verdict table and write the findings file. On the `WalkWithJesus` memory hand-off run it wrote its own 238-line Python renderer to do it, and every run did it a little differently. `render.py` now does all of it from a **run folder** that holds what the agents returned, verbatim. Step 4 is a few `Write` calls and one command.

## Consequences

- The verdict table, the ordering, the counts and the findings file shape now live in code. `SKILL.md` and `findings-file.md` still define them, and `tests/test_render.py` checks the script against a fixture, in CI.
- A verifier block that is not in the brief's shape makes its finding Unverified in the script, not by the main session's judgement.
- The script uses only the Python 3 standard library, so it runs on the pipeline machines and on a Mac with no setup. It runs from the skill folder, never from the reviewed repo, so it keeps the pipeline stack's rule that no repo code runs.

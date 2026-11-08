# QA reviewer

You judge whether the production code in the change works. These rules hold for every stack; the stack's `qa.md` adds its forms to each group, and its own groups. Tests are the test reviewer's lane: when an edge case breaks, report the break in the production code, not which test should catch it.

Work through every group here and in the stack file for every changed function.

## Correctness

- The code does what its name, doc comment and commit message say.
- Inverted conditions, wrong operators, off-by-one errors in ranges, wrong variable used.

## Edge cases

Trace each input the change accepts through these values, and the stack file's: empty, null, zero, negative, a boundary value, very large, duplicates, and a missing file or directory.

## Error handling

- Swallowed errors: an error dropped, caught and ignored, or only logged where the caller or the user never sees it.
- Errors that hide their cause: a re-throw that drops the original error, a vague message, a wrong error type.
- Partial state after a failure: a multi-step operation (save, then upload, then notify) that leaves earlier steps done when a later step fails.
- Resources not released on failure: open files, connections, locks, and the stack file's resources.

## Regressions

For every changed signature, return value, default or side effect, find its callers with the target block's search command and check each still works. Quote the caller that breaks.

## Performance (where the change touches it)

- A query, fetch or network call inside a loop that one batched call could replace.
- Repeated disk or network reads of the same data inside a loop.

## Security and concurrency (where the change touches them)

The stack file lists what to look for.

# QA: pipeline

The pipeline forms of the rules in `rules/qa.md`, and the pipeline groups.

## Correctness

- Off-by-one in frame ranges too.
- Return values on every path, including early returns.

## Edge cases

Also: paths with spaces, non-ASCII characters or a leading `-`.

## Error handling

- Swallowed errors: bare `except:`, `except Exception: pass`.
- Resources: temp directories too.

## Security (where the change touches it)

- Outside input reaching `subprocess` with `shell=True`, `os.system`, `os.popen`, or a command built with string formatting.
- `eval`, `exec`, `pickle` or `yaml.load` on data from outside.
- Paths built from outside input with no check that they stay inside the intended root.
- Hard-coded secrets, tokens, passwords or API keys.
- SQL or query filters built by string formatting.

## Performance (where the change touches it)

- A ShotGrid, database or API call inside a loop is the batched-call rule.
- Quadratic loops over frames, assets, shots or files.
- Loading a whole large file where streaming would do.

## Concurrency (where the change touches it)

- Mutable state shared across threads or processes with no lock.
- Check-then-act on the file system (`if not exists: write`) where another process can act between the two.
- Non-atomic writes to a shared file that a reader can see half-written.

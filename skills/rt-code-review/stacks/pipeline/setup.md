# Setup: pipeline

For the main session only.

## Markers

The skill picks this stack when the list-files command lists `package.py` at the repo root.

## Stack settings

The skill reads these at the head with the read-a-file command and puts them in the target block:

| Setting | Where to read it |
|---|---|
| Python version | The `python-…` entry in `requires` in `package.py` |
| DCC hosts | The `requires` entries in `package.py` whose name is `houdini`, `maya`, `nuke`, `rv` or `usd`, with their version ranges |
| Linters and type checkers | `[tool.ruff]`, `[tool.pyright]`, `[tool.mypy]` and `[tool.pylint]` in `pyproject.toml`, and the files `ruff.toml`, `.ruff.toml`, `pyrightconfig.json`, `mypy.ini`, `.flake8`, `.pylintrc` and `pylintrc`, where the list-files command lists them at the repo root |

Write `none` for DCC hosts or for linters when there are none. Write `unknown` for a value you cannot read. Pass every `requires` entry through unchanged when you are not sure which ones are DCC hosts.

## Fix checks

After the last fix of an `rt-fix-findings` run, run each linter and type checker in the stack settings on the files the fixes changed, with the repo's config. These read the code and execute none of it. A tool that is not installed is a check that did not run. Then run the declared tests.

## Declared tests

The only way pipeline tests run (ADR 0012): the `tests` entry in `package.py`, through rez, in the main session, one run at a time. `<prefix>` is a new empty folder under `/tmp`.

1. At the repo root, `rez build --install --prefix <prefix>`. It builds the working tree, runs the tests whose `run_on` lists `pre_install`, and cancels the install when one fails.
2. For each declared test whose `run_on` leaves out `pre_install`: `rez test --paths "<prefix>:<packages path>" "<name>==<version>" <test>`, with `name` and `version` from `package.py`, and `<packages path>` the paths `rez config packages_path` lists, joined with `:`. The exact version keeps rez on the build in `<prefix>` rather than a higher release.

A package that declares no `tests` runs none: its tests did not run, and the summary says so.

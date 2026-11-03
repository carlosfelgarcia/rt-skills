# Stack: pipeline

A rez package of OD Studios pipeline code: Python libraries, tools and DCC integrations that can reach ShotGrid, the render farm and production paths.

## Markers

The skill picks this stack when the list-files command lists `package.py` at the repo root.

## Stack settings

The skill reads these at the head with the read-a-file command and puts them in the target block:

| Setting | Where to read it |
|---|---|
| Python version | The `python-…` entry in `requires` in `package.py` |
| DCC hosts | The `requires` entries in `package.py` whose name is `houdini`, `maya`, `nuke`, `rv` or `usd`, with their version ranges |
| Linters and type checkers | `[tool.ruff]`, `[tool.pyright]` and `[tool.mypy]` in `pyproject.toml`, and the files `ruff.toml`, `.ruff.toml`, `pyrightconfig.json`, `mypy.ini` and `.flake8`, where the list-files command lists them at the repo root |

Write `none` for DCC hosts or for linters when there are none. Write `unknown` for a value you cannot read. Pass every `requires` entry through unchanged when you are not sure which ones are DCC hosts.

## Why the code never runs

Pipeline code can reach ShotGrid, the farm or production paths, even from a test or a scratch directory. Do not run `python`, `pytest`, `rez env`, `rez build` or any script from the repo.

## What the tooling already reports

Leave to the linters and type checkers in the stack settings whatever they already enforce: formatting, import order, unused names, and type errors where pyright or mypy is configured. When the stack settings list no linter, report these problems only when they hide a defect.

## Examples

- **Where:** `python/dailies/submit.py:42`
- **Structure:** `publish -> manager -> store`

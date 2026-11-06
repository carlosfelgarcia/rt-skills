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
| Linters and type checkers | `[tool.ruff]`, `[tool.pyright]`, `[tool.mypy]` and `[tool.pylint]` in `pyproject.toml`, and the files `ruff.toml`, `.ruff.toml`, `pyrightconfig.json`, `mypy.ini`, `.flake8`, `.pylintrc` and `pylintrc`, where the list-files command lists them at the repo root |

Write `none` for DCC hosts or for linters when there are none. Write `unknown` for a value you cannot read. Pass every `requires` entry through unchanged when you are not sure which ones are DCC hosts.

## Why the code never runs

Pipeline code can reach ShotGrid, the farm or production paths, even from a test or a scratch directory. Do not run `python`, `pytest`, `rez env`, `rez build` or any script from the repo. The one exception is a host probe, which only the main session runs. This holds for `rt-fix-findings` too.

## Dependencies

When a claim rests on how a package in `requires` behaves, read its released source under `/software/packages/<name>/<version>/`, at the highest installed version the `requires` range allows. A dev checkout of the same package can be ahead of or behind the release, so quote the release.

## Host probes

A probe settles how a DCC host behaves at runtime. It imports only the host's own modules (`hou`, `pxr`, `maya`, `nuke`) and the standard library, reads and writes nothing outside `/tmp`, and builds its scene from scratch. It never imports the repo or a package from `requires` other than the host.

Run it with the host's batch interpreter (`hython` for Houdini, `mayapy` for Maya, `nuke -t` for Nuke) in a rez env of the host alone, once per major version in the DCC hosts range: for `houdini-21+<23`, run `timeout 300 rez env "houdini-21+<22" -- hython <probe>`, then the same with `"houdini-22+<23"`. Run probes one at a time: each one takes a host license.

## Fix checks

After the last fix of an `rt-fix-findings` run, run each linter and type checker in the stack settings on the files the fixes changed, with the repo's config. These read the code and execute none of it. A tool that is not installed is a check that did not run. Tests stay unrun: the summary says so.

## What the tooling already reports

Leave to the linters and type checkers in the stack settings whatever they already enforce: formatting, import order, unused names, and type errors where pyright or mypy is configured. When the stack settings list no linter, report these problems only when they hide a defect.

## Examples

- **Where:** `python/dailies/submit.py:42`
- **Structure:** `publish -> manager -> store`

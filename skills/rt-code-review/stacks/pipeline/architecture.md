# Architecture: pipeline

The pipeline forms of the rules in `rules/architecture.md`.

- **Blocking example**: an import cycle that fails at import time.
- **Information leakage**: also a path layout or a protocol.
- **Dependency direction**: a core library that imports a UI or a tool script, or any module that imports a DCC module (`hou`, `maya`, `nuke`, `rv`, `pxr`) whose host the target block's stack settings do not list under DCC hosts. A DCC import is correct in a package that lists that host.
- **Dependency cycle**: an import cycle between modules.
- **Private reach-in**: code outside a module uses its private names (`_attr`, `_helper`) or its internal layout.

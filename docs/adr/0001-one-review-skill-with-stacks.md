# One review skill with per-stack rule sets

`rt-code-review` serves both Swift apps and OD Studios pipeline packages. It does this with one skill that detects the review target's **stack** and loads that stack's rule sets from `stacks/<stack>/`, rather than with two skills (`swift-app-review`, `pipeline-review`). About 80% of the skill is shared: the steps, the reviewer brief, the change summariser, the report template and the agents. Two copies of it already drifted apart once, as `od-code-review` and `rt-code-review`. One skill means a fix to the shared parts lands once, for every stack.

## Consequences

- Stack detection can guess wrong. It reads root markers only. A repo with no marker stops the review and asks for the stack; it does not fall back to a general rule set.
- Adding a stack means adding a `stacks/<stack>/` folder, not a new skill.
- Reviewer rules that hold for every stack live once, in `rules/<lane>.md`. A stack's rule file holds only their forms in its code and the rules particular to it, because the copies in each stack had started to drift.

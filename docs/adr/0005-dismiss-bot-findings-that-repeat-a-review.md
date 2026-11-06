# Dismiss bot findings that repeat an earlier review

ADR 0002 dismisses a finding only on proof from a verifier. Bot findings are an exception. GitHub bots often read one file, so they lack the context of an `rt-code-review` run, which saw the whole branch and verified what it found. In a fix run, a bot finding that makes the same claim about the same code as an earlier dismissed, held or open finding is dismissed with no verifier, and points to the earlier finding ID. A second verifier would pay again for a question that a better-informed review already answered.

## Consequences

- A bot finding that repeats a finding that was fixed still goes to a verifier. The bot read the fixed code, so it may show that the fix did not work.
- A bot finding that repeats a held or open finding is dismissed. The earlier finding keeps its state, and the fix run's summary notes that a bot raised it too. A bot run then records an open finding as held, so it stays in the record after the re-review.
- The main session decides the match, which is the one place it judges a finding. It matches only on the same claim about the same code, sends any doubt to a verifier, and shows each match in the summary so the user can check it.
- A bot finding that no earlier review mentions always goes to a verifier. With no findings file, that is every bot finding.
- One bot's opinion of another bot's finding, such as "real" or "already fixed", never reaches a verifier, for the reason ADR 0002 gives. Its location and fix details do.

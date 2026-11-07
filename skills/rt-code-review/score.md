# Score

A finding's **score**, 1 to 10, is the harm it causes if nobody fixes it. Use the highest anchor it fully meets:

| Score | Anchor |
|---|---|
| 10 | Data loss or a security hole on a path users reach. |
| 9 | A crash, a hang or corrupt saved data on a common path. |
| 8 | A wrong result or a broken caller on a path users reach; a test that cannot fail for the defect it exists to catch. |
| 7 | A bug on a rare path (an error case, an edge input); a silent failure. |
| 6 | New behavior with no test; one decision in two places that will drift. |
| 5 | A design smell that makes the next change harder: a wrong dependency direction, a leaky boundary. |
| 4 | An unclear failure mode; a name, comment or test name that is false about code callers depend on. |
| 3 | A wrong comment, doc or test name with no effect on behavior. |
| 2 | Naming, ordering or duplication a reader notices but that costs nothing. |
| 1 | Taste. |

**Bands**: 8–10 Blocking, 4–7 Should-fix, 1–3 Nit. When a rule file names a band, score inside it. A claim that code fails, runs slow, or puts one decision in two places scores at least 4. A finding that rests on an `unknown` stack setting names its assumption in `What` and scores at most 7.

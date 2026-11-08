# Architecture reviewer

You judge the structure of the change. These rules hold for every stack; the stack's `architecture.md` names their forms in its code and adds its own. Every rule is a judgement call: name it as a possible problem ("possible Feature Envy"), quote the hunk, and score it with `score.md`. Most structure findings are Should-fix; a structure problem is Blocking only when it already breaks something, as in the stack file's example.

## Deep modules (Ousterhout, *A Philosophy of Software Design*)

- **Shallow module**: a new type or module whose interface is nearly as large as its implementation, so callers gain little. → merge it into its caller or callee, or give it a real job behind a small interface.
- **Information leakage**: one design decision (a file format, a naming scheme, or a decision the stack file names) is known by more than one module in the change. → hide the decision in one module; others call it.
- **Temporal decomposition**: code split by the order things happen (read, then decode, then save) rather than by the knowledge each part owns. → group by knowledge, so each module owns one decision end to end.
- **Complexity pushed up**: callers must handle special cases, defaults or configuration the module could handle itself. → pull the complexity down into the module; define errors out of existence where you can.
- **Special-purpose leak**: flags or parameters added to a general interface for one caller's case. → give that caller its own function on top of the general one.

## Coupling and cohesion

- **Dependency direction**: a low-level or core module depends on a high-level one, as the stack file defines them. → invert the dependency: pass the high-level piece in, or move the code up.
- **Dependency cycle**: the change makes two modules depend on each other, directly or through others. → move the shared part into a third module both depend on.
- **Reach-in**: code outside a module uses its internals, in the form the stack file names. → add a deliberate operation to the module's interface and call that.
- **Hidden shared state**: singletons, module-level globals or caches reached from deep inside the code, coupling callers who never reference each other. → pass the state in explicitly, or give it one owner.

## Design smells (Fowler, *Refactoring*, ch. 3)

- **Feature Envy**: a method that reaches into another type's data more than its own. → move the method onto the data it envies.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstractions, generics, parameters or hooks added for needs nothing in the change has. → delete it; inline back until a real need shows.
- **Middle Man**: a type or function that mostly just delegates to another. → cut it and call the real target directly, or give it real work.

## ADRs

If the change contradicts an ADR in the reviewed repo's `docs/adr/`, report it, name the ADR in the title, and quote the line of the ADR it contradicts. The author may reopen the decision; the review only surfaces the conflict.

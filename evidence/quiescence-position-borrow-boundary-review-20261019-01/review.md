# Q parent Position borrow: bounded feasibility

The split is feasible at source level. On frozen47, the only mutable whole-parent Node use after Q’s snapshot is non-check selection (quiescence.rs274–282). Every other parent use is immutable; recursive calls mutate distinct owned children. Unlike ordinary47’s single full call, Q needs the selector and its fast/full observer adapters split too. This is an interface refactor question, not a selected experiment or speed claim.

Saved exact47 generic Q text confirms node+0x10→rsp+0x290, length0xa0, memcpy at3ad4a (source246). Its recorded frame is0x4c8 with existing outgoing adjustment. This is an entry parent snapshot, separate from the rejected28 child-return transport. No PGO extent, dynamic frequency, or removable CPU cost is inferred.

## Parent access and lifetime

The snapshot follows charge_node and PV initialization (243–246). Check calculation, observer.enter’s Position/arrival Retained, and early_draw retain their current order (247–253). The ply63 leaf calls fast/fast_stage through immutable Node references (255–264); it does not require a mutable parent. On a non-check node the selector is the sole conflicting mutable call. Checked nodes skip it entirely.

After selection, generation/ordering/projection and capture estimates read the same unchanged Position. Capture allowance reads the parent’s *refreshed* retained values (354–355), so an independent copied Retained substitute would be wrong. Destination support must retain the existing lazy closure demand and geometry permission (369–374). Neither map construction nor evaluation returns a borrow of Evaluator: map lifetime is the local scratch’s lifetime. No extra map, eager build, or permission creator is needed.

Node::child receives &self at408/443. The prepared-reply child stays at its earlier site, and the lazy child remains after the existing safety screen. History/repetition/reply and candidate effects remain in exact order. Mutable recursion at459/462 is on a distinct child; the parent’s Position and retained fields are not replaced. The observer samples current parent retained at458. The outer leave runs only after the closure returns Ok (487–493); Err continues to skip partial leave output. An immutable Position field borrow can end with the closure, before this final read.

## Minimal interface breadth

Keep all public Node signatures. One existing select_noncheck_impl must accept &Position plus &mut Retained instead of &mut Node, retaining its OBSERVE/STAGES const choices and *all* conditions. Its public default/detailed/stage wrappers split the same Node fields; the private Search default route needs a split-field entry too. Share its default no-op observer literal site rather than duplicating closure types in Q and public wrappers.

The selector calls three evaluation forms. Default full already has47’s full_parts and one numerical full_impl; reuse it. Detailed full needs a private split adapter shared by the public full_detailed wrapper and selector. The private full-stage adapter must take split fields and keep before→full→after→callback exactly. Components-observed and forced-FRESH public full routes already pass split fields to the same numerical owner and need no new selection policy.

Fast numerical fast_impl currently takes &Node (537–563). Make that single owner consume &Position and &Retained, with a shared private default adapter and private detailed/stage adapters. Public fast, fast_detailed_observed and fast_stage_observed keep their Node signatures and delegate. The terminal Q leaf can continue using its existing immutable public Node calls; only selector consumers force the split. Do not synthesize a Node or copy Retained to feed old adapters. Existing intentional stage before/after value snapshots remain, const-gated exactly as today.

This spans Q plus evaluator fast/default/detail/stage and selector adapters; it is materially broader than ordinary47. Full numerical formulas, selection conditions and Q recursion can each retain a single owner. No NodeCell, unsafe aliasing, new fields, new recursion policies, or stage algorithm duplication is necessary.

## Preserved semantics and risks

EVAL-QUIESCENCE-ENTRY39–76 requires sparse immediate-full without fast, otherwise the *finished* fast score and strict refresh window/capture exception; full consumes live PawnCache, fast does not and charges no R. EVAL-RETAINED-SEQUENCE39–65/67–86 and SEARCH-QUIESCENCE-TREE51–99 require retained replacement/preservation, siblings inheriting parent state, draw before terminal evaluation and checked bypass. Sharing the exact policy/body satisfies these obligations only if the adapter chronology above is preserved. Raw/custom Influence stays caller-supplied, public default geometry permission stays false, and public forced-FRESH wrappers retain their existing policy.

Callbacks receive Position by immutable reference or evaluation/retained snapshots by value. Safe callers cannot concurrently mutate the exclusively borrowed parent through these interfaces. Its address would change from a stack snapshot to the actual Node field, but these contracts specify state observations, not pointer identity. No stronger guarantee for unsafe external aliasing is claimed. Existing panic behavior is not upgraded to rollback: full writes Retained before later component/finish observation, and callback panic must not introduce restoration or reordered writes.

Typing remains untested. Split &Position/&mut Retained carries different alias information and an extra field pointer through fast/selector/helper ABIs; closure types and inlining may change code size, frames, register lifetimes and observed/default sharing. Compiler evidence must show the160-byte entry copy removed without relocation or a reconstructed Node, while preserving actual default Q, full/fast, sparse/refresh and observed routes. Static source feasibility alone settles none of those costs.

No files in frozen47 were changed. No build, Rust parse, native test, engine, ELF/binutils, profiling or timing work was performed. This audit is not experiment48 selection or broad conformance evidence.

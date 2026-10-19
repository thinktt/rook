# Ordinary Position reborrow without evaluator changes

**Source-feasible; no escaping pre-full Position reference found.** Canonical43 can conceptually use one immutable Node.position loan for the pre-full work, end that loan before its unchanged full(node,map,checked) call, then create a fresh immutable Node.position loan immediately after the call. This is a source lifetime audit, not a compiler result, selected trial, or performance claim.

The first binding belongs at ordinary.rs743, leaving Q delegation719–736, node charge738 and PV initialization742 untouched. Its last use on the full path is ensure_influence_for_search811. A later binding that shadows the first immediately after full812 makes every remaining Position use refer to the second loan. The name being in lexical scope does not itself require a live borrow once it has no later use; safe NLL still must be verified by an actual build if selected. No explicit drop, scope-wide Position copy, unsafe alias, or evaluator field split is necessary in this source plan.

| Pre-full consumer | Returned state crossing full |
| --- | --- |
| Check fallback744–746 | bool; unwrap_or_else consumes its short closure |
| TT group/query/probe750–759 | Query stores group/identity/ply/target/window scalars; ProbeResult stores score/bound/move/depth/flag values, no references (remembered.rs25–58) |
| Current phase/selectivity771–777 | owned i32 adjustment |
| Fast gate/pressure/threat780–807 | scalar gates, Evaluation values and i32 threat; successful cutoff returns before full |
| Influence at798/811 | reference to local scratch, not to Position |

The influence lifetime is the decisive interface fact: evaluator.rs316–321 explicitly returns &'a Influence from scratch: &'a mut Option<Influence>, while position: &Position has an independent elided input lifetime. Its producer stores an owned Influence value in scratch (322–330) and returns scratch.as_ref() (335). Supplied Some is preserved. Therefore keeping map for full and later Predecessor does not extend the Node.position loan. The analogous public ensure_influence306–311 has the same separation.

The current Predecessor—which deliberately retains the parent Position reference through later children—is not constructed until821–826. It can take the second loan. The incoming previous is caller-supplied ancestor context, not newly derived from the current binding. Its existing safe signature does not enable a simultaneously mutable aliased current Node. No pre-full source closure or stored local otherwise captures the current Position for later use.

The unchanged canonical full_impl389–483 reads Node.position and writes only node.retained.positional461, pawn_progress462 and age463. It does not replace or mutate Position. Thus re-reading Position after successful full gives the same state value as the old snapshot, while later retained consumers see the real updated fields. On panic/early return the newly proposed post-full binding is never evaluated; existing partial-state/error behavior is neither restored nor otherwise changed. No operation needs to move across full: map construction, cache/query charging, late retained reads, stats, no-op observer/finish and all tail code remain in their existing order.

After full, remaining whole-parent calls are immutable: threat, child/null_child, and ordering_phase. Recursive mutable calls use distinct owned children. Parent chronology, current Predecessor lifetime, history push/pop, retries, public API, default closure types and the sole evaluator numerical body can remain exact43. All189 old test bodies can stay byte-identical; no new runtime witness is implied by this audit.

This differs from47:47 kept the loan live through full by splitting Position/Retained and changing the private evaluator ABI/owner adapters. This alternative ends the loan and retains the exact canonical full Node API and implementation.47’s own-PGO fixed70 failed its frozen gates:0.0137518% lower,4/7 lower,ratio0.99986248; its decision parks47 and explicitly forbids causal attribution of that failure to frame/ABI. Those results neither qualify nor reject this unimplemented lifetime alternative. Rejected28 concerned child-return aggregate transport and remains separate from this parent snapshot.

No source changes were made. A future compiler discriminator would need to establish that the entry160-byte snapshot actually disappears without a new copy, that the unchanged full path does not induce other relocation or alias/codegen costs, and that normal fast/TT early-return paths and post-full users retain their original behavior. This audit does not predict that result or estimate speed. Q split remains unselected and unnecessary to this ordinary-only question.

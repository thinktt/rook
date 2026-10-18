# Retained evaluation — unexecuted one-route proposal, 2026-10-18

Prepared by `/root/score_context_transport` for `/root`. Requested Sol6.1 High / Normal; native runtime speed controls/readback unavailable. Predecessor is `/tmp/imp2-full-fresh-proposal-20261018-92x348cj`, which the parent reports passed 137 native tests and 4637 DIAG cases/92 units; that source remains isolated while root79 is committed. New proposal: `/tmp/imp2-retained-evaluation-proposal-20261018-uz57d6p0`. All writes are limited to this new copy and this evidence directory. Prior proposals/review and live root are unchanged. No Herdr, advisors, subagents, builds, tests, rustc, engines or profilers were used. All shell housekeeping ran with affinity `0-5,8-13`, respecting the parent's own-PGO CPU pilot82282.

## Scope and exact artifacts

Only `evaluation.retainedSequence` is added. There are five changed source files: native evaluator.rs; cold diagnostic main.rs and fresh_evaluation.rs; new evaluation_common.rs and retained_evaluation.rs. No move/quiescence routes, selection/disposition helpers, native pawn cache APIs, or complete session behavior were added.

`proposal.patch` combines `native.patch` then `transport.patch`, all relative to the named fresh81 predecessor. `source-hashes.json` records per-file before/after SHA-256, complete proposed Rust-source manifest, three exact patch hashes, relevant released spec hashes, and source comparisons. `plan.json` extends the exact predecessor selection with the complete retained-evaluation-v1.json fixture and all 84 case IDs. These are proposals/inventories, not child pass evidence. Parent owns formatting/review, integration, execution and promotion.

## Native owners and observations

Cold FullDetails now includes the actual selected.reused Boolean. New full_detailed_observed calls the existing full_impl with FRESH=false, using actual ordinary cache probe/replacement and current full evaluation. The old full_observed/fresh_observed Components APIs, callback point before finishing, and ordinary Evaluation return remain unchanged. Fresh transport ignores the additional cold flag and still uses FRESH=true.

New FastDetails exposes actual computed base and the single actual native Finished. Both old fast and fast_detailed_observed call the same generic fast_impl; ordinary fast supplies a statically dispatched no-op. Its existing statistics, tempo/base arithmetic and finish arguments are unchanged. The obsolete private no-op finish wrapper is removed because both full and fast now reach the already shared finish_observed. That finishing function's source is byte-identical to the predecessor. No finishing call or arithmetic is duplicated in transport.

Fast receives only the immutable node and check flag. Its core contains no pawn probe/population/clear, Influence construction, pair/age mutation, or R charge. It preserves the node while producing a new current score/bounds; the only existing evaluator metric effect is fast-call counting under DIAGNOSTICS. FullDetails reuse is directly from selection, not inferred from statistics.

Evaluation, Retained, Node, Position and Evaluator field declarations are byte-identical to the predecessor and their hashes are recorded. No callback or observation record is stored in any hot structure. Position and native pawn source files are untouched.

## Cold controlled lifetime and shared formatting

Request parsing validates exact top-level settings and every position's exact fields, scalar domains and complete pawn order before creating native evaluation state. First-full and first-side=rootSide checks occur after every position schema/order is parsed. Numerically unused king percentages, fast pawn orders, and hit orders remain validated. Broad bounded placements are admitted without requiring a legal transition history; no phase, identity, clear, prior retained score, per-position personality or material substitute is accepted.

Exactly one evaluator is configured and begin_search is called once before the position loop. First placement fixes root phase/counts/values, root-side ownership, percentages, averageDepth, draw preference and variation range. Each controlled current placement builds a new Node::root under those same root values, recomputing current nonking squares. Only the prior produced positionalSubtotal/pawnProgress pair is carried. Node::root supplies age zero; ordinary full resets it and actual fast preserves it. These arbitrary placement changes are not moves and do not advance age.

Full alone constructs current influence, invokes actual nonfresh full selection and updates the produced pair. Fast never constructs influence and calls the actual native fast observer. Native full returns actual per-call pawn+activity R even on classification hits; fast returns zero and pawnEntryReused:null. Every step emits actual current phase, geometric check, identity, base, Finished, retained pair/age and exact selected reuse. No finalScore +/-10000 supplied-input gate is applied to produced values. Neither finished score nor bound replaces the pair.

The unchanged percentage/order admission and actual-native-value record formatting were moved from fresh_evaluation.rs into evaluation_common.rs. Both fresh routes now share those helpers with the new route. This shares parsing/serialization, not evaluation arithmetic. Existing fresh fixture/unit rechecks are necessary because their cold plumbing moved.

## Inventory and focused source tests

The whole released retained fixture adds **1 route / 84 cases / 1818 result records**. Proposed selection becomes **82 routes / 4721 cases**, from 81/4637. Source-declared tests become **139 native /99 diagnostic**, adding two native and seven diagnostic tests. No test was executed.

Native tests observe actual initial-zero/group-replacement/hit flags and exercise fast details under both DIAGNOSTICS monomorphs. They check one observer call, parity with old fast, immutable node including age 19, no nonfast metrics/R, and no eviction of a warmed same-group entry. Diagnostic tests cover published full-identity collision values, fast pair preservation and absence of cache eviction, initial zero versus replacement behavior, hit order versus first-miss order, fixed root through current phase/nonking-square changes with exact base 1888/R0, current reversible finishing without storing its zero result, independent repeated requests, and strict entire-request/order/initial admission.

## No-op monomorph and production cost caveats

There is no native dynamic callback, heap allocation, runtime observer flag or layout expansion. The computation portion of fast and the complete finish_observed source compare byte-identical; the manifest records this textual evidence. Generic wrapper/closure instantiation, adding the cold reuse flag, removing the private finish wrapper, and changed inlining can nevertheless affect code layout, registers, stack materialization or instruction cost. Optimized removal of no-op detail records is expected, not demonstrated. Source declaration equality is not an executed layout/ABI check. Parent should compare all 84 new cases separately, run full native/diagnostic checks, recheck shared fresh behavior, and assess relevant production codegen/cost controls after the live CPU pilot permits execution. No performance neutrality or promotion is claimed.

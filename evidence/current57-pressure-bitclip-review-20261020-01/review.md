# Conditional GO: one coherent pressure-clipping compiler discriminator

Source feasibility only; no candidate, source rewrite or runtime selected. Current57's exact own-PGO profile35 is the evidence basis, not experiment32's costs. The prospective discriminator is removal of per-target mailbox/tag/offset termination work, while retaining every admitted mark lookup/addition. The narrow envelope warrants a compiler-first question, not an expectation of a meaningful native gain.

Current source/spec: `src/activity.rs:453–498` implements released `/home/legolas/king-spec/spec/activity.md:162–182`: start one step from the defending king; include empty squares and the first defender occupant; exclude the first attacker occupant and stop. Orthogonal R/Q and diagonal B/Q inventory gates precede their traversal. Knight occupancy admission is separate. Static `PRESSURE_VALUES` at activity.rs:429–450 remains the numerical owner. Pressure adds no R charge (spec:210–222).

## Exact coherent mask lemma

Borrow the actual four planes through `Position::attack_planes` (position.rs:175–178); do not copy a new placement view. Existing `attacks::influence_rays` (71–72) provides the immutable eight rays and scan polarities. Canonical coherent tags give occupancy O=a|b|c and attacker occupancy from color plane d intersected with O. For each admitted ray R, find its nearest occupied bit b in R&O. If none, select R. Otherwise select the ray prefix through b, then remove b exactly when it is an attacker. The source/king bit is absent from R. This is exactly the scalar target set: every prior square is empty, the first defender endpoint contributes, and the first attacker endpoint does not. All occupants are opaque here: no slider transparency, source vacancy, check legality or Influence-map authentication is involved. An adjacent attacking king blocks without contributing. The proof imports the existing native placement/list/plane coherence permission; arbitrary public/stale Position values cannot use it.

Keep orthogonal and diagonal sets distinct. They may each union their four disjoint rays and iterate set bits because each target occurs once in that family. Applying one combined 0xfc mask to the union is wrong: bishop marks on orthogonal squares or rook marks on diagonal squares would spuriously count. Queens contribute in both families with the existing 0xf0/0xcc masks. Empty-ray and no-blocker cases must avoid shifts by64 or unguarded leading/trailing-zero indices. Both scan polarities and bits0/63 matter. Leave knight traversal unchanged in this discriminator.

Reordering integer additions is safe: each masked slider target contributes at most48, at most8*7 targets; each of at most8 knight targets contributes at most40. Every nonnegative partial sum is <=3008, and the final single `(sum-12).max(0)` is <=2996, comfortably i32. Weak/strong coexistence remains additive. Do not clamp per family/ray. Marks are still freshly produced from the actual supplied Influence by the unchanged activity owner; geometry permission does not replace map authority or change R/order of activity production.

## Current57 cost evidence and replacement costs

Closed `/home/legolas/rook2-private/current57-callgrind-20261020-01/selected-activity.stdout` has whole profile35 total43,940,740,008 simulated user Ir, independently replay-verified. Its exclusive source-line attribution is:

| Activity source row | Simulated Ir | Interpretation |
|---|---:|---|
|473 direction iteration|81,703,518|Mixed retained iteration/setup; not all removable|
|475 offset/loop|39,830,619|Candidate mixed loop/coordinate attribution|
|476 mailbox load|113,525,288|Candidate target-classification attribution|
|477 attacker stop test|43,267,682|Candidate target-classification attribution|
|480 mark lookup/add|84,152,868|Required admitted mark work|

Rows475–477 sum196,623,589 (0.44747% of the program). This is a targeted attribution envelope, not a proven removable instruction count or predicted CPU saving; inlining/line placement mixes operations. No line0, whole Activity, global type/offset costs, ordinary_policy::king_pressure or inclusive callee rows are borrowed. Knight rows490–493 stay outside the proposed removal. Only this one workload was profiled here; no frequency or current08 cost is inferred.

New work includes borrowed-plane decoding, up to eight guarded nearest-bit queries, prefix/end-point arithmetic, attacker-color tests once per blocked ray, lsb iteration, and possibly family unions. Mark loads/table loads/additions remain. Inventory gates must precede unnecessary plane/ray setup; no eager eight-ray work on pawn/king-only or knight-only activity. Occupied-heavy short rays may lose against scalar early termination. Frame/register spills, helper calls, code size and scalar fallback coexistence can dominate this small envelope.

## Permission plumbing is part of the mechanism gate

There is no permission parameter in current `Evaluator::full_impl` (381–401), and activity::compute is public. Ordinary captures permission at779 and ensures the map at798/811 but calls public full at812. Root preparation does likewise at quiescence.rs:149–157. Q selection already has coherent_geometry (evaluator.rs:651) but its full branches678/700 discard it. Thus a pure pressure helper alone cannot safely activate on native calls. A possible minimal later seam is private `full_for_search(...,coherent_geometry)` and a shared-body private Activity entry that branches only at the pressure tail; public/full/fresh/observed/custom entries stay scalar. Thread existing Search permission at every actual ordinary/root/Q full site. Do not infer permission from Some(map), checkedness or build success. Avoid duplicating the large Activity/full owners with new const-bool monomorphs solely for this tail. A live bool/possible sixth Activity argument, inlining and spill costs must be priced, not called free. No new permission field/state or validation is proposed.

## History, falsifiers and decision boundary

Parked32 (`docs/decisions/0023-pressure-table-traversal-trial.md`, own-PGO backend review) replaced coordinate walks with precomputed target lists while retaining per-target board stops. Its own-PGO failed (+0.239039%,4/7); historical Activity code+175B/frame unchanged/+8 static stack references is not current57 evidence. It also preceded the current static pressure-value owner. This proposal is distinct because classification is once per ray and intermediate targets require no mailbox decoding. It must not become a retry of table iteration,52's full coherent activity consumer or a second pressure arithmetic experiment.

If root later selects a source discriminator: compare independent old coordinate pressure versus the clipped helper for every king/color/direction, empty/first blocker distances, both blocker colors/all canonical kinds, edge bits, adjacent kings, inventory family gates, and supplied all-bit/coexisting marks. Put nonzero marks on an excluded attacker endpoint and beyond every first blocker. Include wrong-family B-on-orthogonal/R-on-diagonal marks and Q in both families; otherwise union bugs can pass. Compare complete Activity/shelter/R and public stale/custom-map fallback, not helper versus its own mask machinery.

Conditional GO only for this bounded compiler discriminator: actual private native paths must remove inner mailbox/kind/offset tests, retain exact lookup targets and public scalar fallback, and expose all new decoding/bit iteration/argument/frame/call costs. Reject if work merely relocates, setup is eager for inactive families, owner duplication/frame growth overwhelms the narrow mechanism, or authority cannot stay explicit. Static success would still require root's separately selected matched native experiment. No gain/adoption/qualification claim.

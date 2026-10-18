# Current117 evaluation hotspot recommendation

Read-only interpretation, 2026-10-18, score_context_transport. **First choice: a stateless activity destination-input trial, binding oriented/flattened value tables once per color/piece rather than repeatedly deriving target coordinates. Second choice: fuse the duplicated selected-pawn forward scans. Do not start another persistent evaluation/material cache from this evidence.** Neither proposal is implemented or predicts CPU improvement.

## Bound profile and attribution limits

The parent closed fixed profile35 then08 on own-PGO image `6a5ce6e27b74490e623fbb705f70c770ec12ff7e88f761fb0c7119ca2aee4a50`: outer97618/4dc405→dd7870 exit0, independent b30ef5 exit0. Existing `complete117-callgrind-20261018/independent-verification.json` records total simulated whole-lifetime user Ir **48,746,346,838 / 4,163,216,998**, native exits0 and strict original raw-byte equality. This is two fixed lifetimes, not native PMU instructions/cycles, a call census, or a representative weighted54/12 CPU result.

`displayed-owner-rows.json` preserves every counted file:function row and original table line. Its groups sum disjoint **exclusive** displayed rows sharing exactly the named function owner, including inline standard-library attribution. Threshold99 omits some rows, so these are threshold-limited attribution lower bounds, not complete inclusive function costs. Repeated function tables in the different annotation outputs are not additional events. No source-line subset below is added to these groups.

| Exact function-owner group | profile35 Ir (% program) | profile08 Ir (% program) |
| --- | ---: | ---: |
| activity::compute | 11,324,462,593 (23.2314%) | 469,043,926 (11.2664%) |
| influence::Influence::build | 4,389,525,713 (9.0048%) | 158,310,998 (3.8026%) |
| shelter::compute | 2,128,366,852 (4.3662%) | 393,997,010 (9.4638%) |
| pawn_progress::selected | 737,032,118 (1.5120%) | 584,170,242 (14.0317%) |
| pawn_terms::structure_terms | 1,209,131,421 (2.4805%) | 117,036,574 (2.8112%) |
| pawn_terms::raw_piece_terms | 1,279,348,346 (2.6245%) | no row displayed |
| pawn_structure::fresh_with_order | 1,058,485,967 (2.1714%) | 3,594,881 (0.0863%) |

An absent row is not zero execution. The own-source rows alone are activity.rs:compute **6,202,242,820 / 252,483,486**, and pawn_progress.rs:selected **427,465,827 / 367,633,692**. Inlining is why these differ from the grouped ownership figures.

Original relative-path source requests produced “No information has been collected”; they are preserved request failures, not line evidence. This review uses the parent's corrected absolute displays in `complete117-callgrind-absolute-annotation-20261018-02`, actual fcc68e/0, independent b38fcf/0 (159 inputs/16 streams). `exclusive-source-lines.json` extracts only numeric source rows after the source marker, excluding `=>` callee costs. Unidentified line attribution remains unallocated. For activity, identified source events plus unidentified are **5,088,896,358 + 1,113,346,462** in35 and **202,875,737 + 49,607,749** in08; these reconcile its own-source function rows exactly. They do not include all inline code in other source files.

## Why activity destination inputs are the next useful trial

Current frozen producer: `complete117-pgo-use-build-20261018/source-before/src/activity.rs`, especially `relative_rank:137`, `destinations_kind:223–307`, and `piece_score_kind:310–350`.

| Exclusive activity source row/range |35 Ir|08 Ir|
| --- | ---: | ---: |
| relative_rank137: color orientation |592,226,863|17,050,099|
| destinations223–307, entire identified range |2,102,824,850|52,786,194|
|263: ray target iteration (subset of preceding range) |314,613,436|7,419,524|
|265: Square(target &63) (subset) |273,740,013|7,095,387|
|266: board victim read (subset) |182,493,342|4,730,258|
|290: destination value indexing (subset) |241,582,384|8,707,472|
|297: weighted mobility accumulation (subset) |141,993,958|8,015,438|
|195–196: mark bit computation/update |451,707,312|13,317,708|
|388–440: pressure machinery, entire identified range |1,045,555,763|85,513,806|

These rows put the largest case's activity work in destination traversal/value preparation, with real additional pressure work; they do not show a material-cache opportunity. Line137 includes every inlined relative_rank use attributed there, not only the destination call, and debug attribution is not a count of branches or removable instructions.

The bounded trial is to bind an immutable physical-square-indexed value view once for each color, and select the normal versus rook-seventh value view once per eligible piece. This can reuse the exact destination constants and side orientation across all its targets, rather than repeatedly forming relative rank/file and selecting a two-dimensional row. The same approach can cover LOW_MOBILITY's per-piece coordinate lookup if it remains one coherent private change. Use exact existing constants/geometry, not fixture values; preserve the rook-seventh admission based on the enemy king. Knight/bishop/rook/queen specialization already exists and should remain.

This needs no Node/Retained/Position fields, recursive argument, identity, runtime memo table, allocation or eager evaluator. It changes neither which destinations count nor the separate direct/additional ray transparency policies. Direct-category shortcuts, marks, pressure ownership, all arithmetic/rounding and relation-work increments remain unchanged. Additional-ray relation computations can be physically avoided only if a separately proved pure result shortcut applies; their semantic charges cannot disappear. Do not bundle such a change into the first table-orientation trial.

Generated code may already hoist portions, a new table reference can increase register pressure, and more tables/code can hurt cache use. Therefore the trial's first backend question is actual default activity code/calls/frame/load/coordinate lowering, followed by its own matched CPU comparison if functional/codegen gates support it. The source-row totals are not a predicted saving. This is distinct from already parked activity widths, profile_sum lookup, pressure_value lookup, and previously adopted geometry/static-kind changes (`docs/research/remaining-performance.md`, items1/10/11/14/15).

## Concrete second choice: remove one pawn forward traversal

`pawn_progress::candidates:106–151` walks each selected pawn's forward file to obtain path and protection, then calls `raw:13–91`, which walks the same forward file again for its influence/occupancy measure. A shared private native scan could return the raw contribution and path/protection summary together, reusing each forward square's board and influence reads with O(1) locals. Preserve raw's separate backward-rook/queen scan, immediate-front exception, terminal rank weighting, all integer operation boundaries, selected descriptor order/ties, top-two scores and ending/fallback rules. The public raw helper can retain its current API; there is no need to cache progress across positions or add fields.

This is a concrete algorithmic duplicate, and the08 grouped owner is its largest displayed evaluation owner. There is **no corrected pawn_progress source annotation in this closed set**, so no allocation of its 584M Ir to the two scans and no saving percentage is claimed. This bounded source shape is enough to justify a later isolated proposal without another broad census. It is not a claim that the entire selected owner can be eliminated.

## Why the other reuse ideas do not take priority

`evaluator.rs:355–453` FULL computes current material, selects pawn descriptors, then computes current pawn terms, activity, shelter and progress, writes P/G/age and charges pawn+activity R. FAST:500–524 computes material/square balance plus retained P/G and one finish, with no activity, influence construction or pawn-cache probe. Sparse noncheck selection invokes FULL; other noncheck selection uses FAST with conditional FULL refresh (`601–658`). Consequently these Ir rows cannot be converted into FULL/FAST counts, and removing FULL because it is costly is not a valid optimization.

The cache at `pawn_structure.rs:98–144` already obtains production pawn chronology/builds fresh descriptors only on full-identity misses. Its retained identity can preserve earlier ordered/colliding descriptors. Current `pawn_terms` and `pawn_progress` still read current placement/map/phase/kings/material: extending this cache to those outputs based solely on pawn identity would be wrong. Small displayed08 fresh-construction attribution does not justify changing admission/probe order or dropping current work.

Influence construction remains material at9.00% /3.80% displayed owner attribution, but it already uses typed lists and shared rays. Its semantics differ from legal attacks and activity continuation, so the 128-byte map cannot be replaced by attack planes or shared ray traversal without a new proof. Corrected influence source row208 (profile_sum) is **936,962,069 /25,753,383 Ir across consumers**; those are source subsets, not extra Influence::build costs, and the exact lookup was already tried and parked under own PGO. Repeating that microtrial is not the recommended next step.

Parent-material transport remains a conditional opportunity, as documented in `parent-material-transport-review-20261018`. These annotations do not isolate RootContext::material cost or count inherited first-demand hits, invalidations or zero-demand edge tax. Its source purity and i16 final-value representation do not supply those missing denominators. Prior same-produced-node FULL caching had only0.050058% age0 FULL entries on historical79; null influence and Q material endpoint caches were also parked. None proves current uselessness, but this profile gives stronger immediate support to a stateless activity algorithm than to adding transport/caches.

## Closure

All work used existing closed profile/source text on housekeeping0–5,8–13. No engine, profiler, build, test, binary scan, Git, shared-source edit or extra annotation was launched. Offline parsers and their exact counted rows are retained here. Table grouping actual e5d060/0; corrected-line extraction0483e4/0; focused row read67a18c/0. All helpers returned actual terminal results; zero owned background jobs. Parent retains implementation selection and any later execution authority.

# Next ordering cost: defer binary insertion

**Do not select a new binary-insertion trial from this evidence.** The final permutation can be preserved, and sorting is a real cost, but gap6 has already shortened the later backward walk. Binary search retains the required shifting work and may add comparisons and two variable-size memmoves for small/partially ordered prefixes. No implementation, threshold, tuning or numbered28 trial is proposed. Direct child initialization remains a separate backup.

## What is actually attributed

Current exact51529 profiles record45,762,253,122/3,967,850,732 simulated lifetime Ir for35/08. The cited1,474,856,599 Ir under ordinary`'2` and tactical.rs is a file:function partition, not an ordering-algorithm saving. Across both recorded ordinary and Q variants, the following **exclusive, disjoint tactical source rows** reconcile exactly to1,717,404,439/56,561,370:

| Selected current tactical.rs owner |35 Ir|08 Ir|
|---|---:|---:|
| Insertion priority load250 |155,535,866|5,791,674|
| Comparison/bounds/cursor control252, both passes |594,007,851|11,220,753|
| Move/priority shifts253–254, both passes |309,788,348|6,121,958|
| Final item stores257–258, both passes |140,247,692|4,133,988|
| Preferred/low partition322–330 |289,809,312|19,428,280|
| Q preference callback209–241, mapped portion |79,911,411|3,638,945|
| Direct final-copy setup336, mapped portion |5,853,759|964,359|
| Unidentified tactical line0, unassigned |142,250,200|5,261,413|

The four insertion rows sum1,199,579,757/27,268,373 (2.621330%/0.687233%). Even **all comparison/control252 across both passes** is1.298030%/0.282792%; it is not an achievable saving. It includes required bounds/cursor/branch work, and binary insertion needs its own search/comparison work. Movement/final stores and gap6 stay required. Positive source coverage is not a full dynamic instruction-cost bound: compiler inline/core/line0 instructions are deliberately not redistributed to make a larger opportunity.

Ordinary's first-applicable callback is defined in ordinary_policy and includes relation/material/category work beyond this tactical source partition. It cannot be charged wholesale to priority_sequence; nor can every ordinary_policy row be treated as callback cost. Q preference has only its directly mapped portion above. The final preferred/deferred list copies remain required by this alternative (saved ordinary0x33e19/0x33e64 are the two memcpy sites); bulk-copy libc cost and other core-source setup are outside this table, not secretly counted as insertion traffic. Noncheck tactical generation is a separate function and excluded completely. `attribution.json` retains individual function/raw-row ownership and proves the table partition, rather than adding inclusive call arcs to self costs.

## Gap-specific evidence and its limit

The saved exact51529 ordinary body contains separate unrolled loops: gap6 near0x33cf8–0x33d79, then gap1 near0x33da3–0x33e0a. Each source-line profile likewise retains two disjoint ordered row clusters, A then B. Their positive tactical costs are:

| Raw cluster, consistent interpretation |35 Ir|08 Ir|
|---|---:|---:|
| A, consistent with gap6 |460,393,804|2,801,028|
| B, consistent with gap1 |739,185,953|24,467,345|

**The cluster costs are exact; assigning them to instruction addresses is an inference.** Raw `positions: line` does not carry instruction addresses. Serialization/source order and the two matching saved loop structures support A→gap6/B→gap1, but this report does not upgrade that correspondence to address-counter proof. The conservative unconditional result is the combined-pass table above; unknown/core/line0 rows are not assigned to either phase. No new binutils, annotation or simulation ran.

The conditional gap1 interpretation is also evidence against a blind binary replacement. Ordinary`'2` clusterB's priority-shift store254 is41,386,567/1,080,474 Ir versus final-priority store258 at17,909,164/805,970: ratios2.31/1.34. These are source-row ratios, **not function-entry counts**. With the saved single-store instruction correspondence, they are consistent with only about2.31/1.34 element shifts per insertion after gap6. Its main comparison row is232,981,932/6,664,100; correspondence to the four-instruction load/compare/branch block is consistent with about3.25/2.07 comparisons per insertion. These derived operation estimates remain conditional on the same mapping and are not CPU predictions. A logarithmic search can easily lose on such short walks; a mean does not establish the full length/shift distribution.

## Exact semantic boundary

Released tactical-capture-order.md defines the result, not a mandatory implementation: stable descending within each modulo-six position class, restore those class positions, then stable descending over that combined sequence. Equal keys are stable **after gap6**, not necessarily in original order. `[1,1,1,1,1,1,2]` must yield indices`[6,1,2,3,4,5,0]`; sorting the original list globally stable would be wrong.

Keeping gap6 exactly and using stable binary insertion for gap1 is mathematically sound if each insertion finds the first strictly lower priority in the descending sorted prefix, placing the new item **after existing equals**. Move and u32 priority arrays shift together and retain identity; unsigned full-domain keys, including0/1/u32MAX, stay exact. No re-evaluation of callbacks during binary comparisons is allowed.

search-candidate-order.md separately requires low0/1 items in original order and preferred>1 items reversed before this permutation. tactical::order_by315–336 evaluates priority_for exactly once per original candidate in original order, writes reversed preferred/forward low partitions into the existing search-wide scratch, sorts only the preferred suffix, then copies preferred followed by low to the produced row. Preserve all category/wrapping precedence, callbacks and charges (ordering adds no relation units), masks, and final copies. Q shares this owner for quiet evasions/underpromotions as well as captures. Scratch is consumed before recursion and must not become per-child storage or persistent sorted state.

Current tests already compare the actual permutation against an independent modulo-six/stable mathematical model for all ternary sequences through length9 and a full-capacity mixed/u32MAX sequence; fixed tie and shared-evasion witnesses remain. No test was run or weakened. A bounded search of decisions/research and prior review notes found no existing binary-gap1 trial; the existing search-wide scratch is completed work, not a new suggestion.

## Recommendation and closure

Defer binary insertion. The targetable comparison work is smaller than the whole sorting owner, gap6 and shifting bytes survive, and current conditional operation evidence favors the cheap existing linear walk. Precise gap-address counters plus preferred-prefix length/backward-distance distributions would discriminate the alternative if parent later revisits it; current line-only totals cannot settle that. This is a missing-evidence statement, not a request for a new census or profiler run. No automatic controls or implementation follow.

All inputs are our own frozen candidate25 source, saved51529 assembly/raw profiles and released king-spec. Image/source/assembly hashes match the existing identity/function-capture records and current root at read time. Full SHA pins are in input-pins.json; originals rechecked unchanged. Normal-speed policy has no runtime readback available. All helpers were pinned0-5,8-13 with HOME TMPDIR during the live27 quiet window. Only small source/raw parsing/report work ran: no binutils, native/build/test/profiler/annotation/timing/Git/archive. Primary offline analysis ACTUAL43e872/0, all owned jobs terminal. The initial read-only normative path miss (d482d2/2) was resolved to the actual search-candidate-order.md/tactical-capture-order.md files; no runtime/source repair occurred.

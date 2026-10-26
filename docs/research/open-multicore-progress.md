# Open multicore research: current assessment

2026-10-26, imp2-lead. Continuing under the
[mission](../deterministic-multicore-mission.md); this is a progress assessment,
not research closure or release approval.

The strongest retained result now uses three threads. One coordinator preserves
King's search, pawn-cache accesses, state updates and logical work. Two helpers
compute independent color Activity/opposite-Shelter chains at actual FULL demand.
One immutable input is shared until both readers retire; each owns its output.
The reviewed epoch protocol removed serialized reader copies and result locking.
The numerical split alone had lost: the transport change made it useful.

The [own-PGO full54 survey](../../experiments/multicore-feasibility/epoch-own-pgo/report.md)
records 60.763786s search wall for this candidate, versus 64.092876s preserved
two-thread and 67.973988s accepted serial in that window. Gains are 5.19% and
10.61%, respectively. Whole CPU is 1.422x the two-thread cost and 2.679x serial.
The same new binary's one-thread mode is a descriptive 0.15% above accepted
serial. These are single observations per case/configuration, with separate
repeated generic evidence. They are not a matched KingWCR comparison.

The gain spans 48/54 cases against preserved two-thread and 45/54 against serial;
case43 still loses 4.56% to serial. Active helpers can consume CPU while the
coordinator is blocked in a callback. Short idle probes show zero ticks at 10ms
resolution after parking. These costs matter when choosing a thread budget.

## What the experiments distinguish

| Question | Evidence and current judgment |
|---|---|
| Can exact branches simply become parallel jobs? | Actual wide 1/2/4/8 execution found real work and descendant reuse, but state/order validation and replay cost exceeded useful reuse. This does not establish a general impossibility. See [wide replay](../../experiments/multicore-feasibility/wide-internal/report.md). |
| Can pure results survive failed branch speculation? | Yes, but the same-fixture [census](../../experiments/multicore-feasibility/coarse-pure-salvage/report.md) found only 5.596ms of newly unavailable first-demand kernel proxy; its current pool construction cost already exceeded that. Those representation costs are not universal lower bounds. |
| Was the failed color split inherently too small? | The original three-thread graph lost, but [direct epoch transport](../../experiments/multicore-feasibility/epoch-colors/report.md) improved it enough to beat two threads. This is a net architecture result, not isolated mutex nanoseconds. |
| Does adding move generation supply useful fourth-thread work? | [Conditional inventory4](../../experiments/multicore-feasibility/epoch-inventory-four/report.md) supplied exact lists at substantial actual demand, but the measured implementation was 0.81% slower than preserved3 and used 1.344x CPU. It remains parked. |
| Does direct epoch transport also help one helper? | The [generic whole-FULL trial](../../experiments/multicore-feasibility/whole-full-epoch/report.md) improves mode2 by 2.62%, but [own-PGO/full54](../../experiments/multicore-feasibility/whole-full-own-pgo/report.md) reduces that to a descriptive 0.317%. Three threads remain faster. Keep the tested alternative without replacing the retained candidate or extrapolating generic gains. |
| Was research accounting hiding an inventory4 gain? | The fixed [observer-free comparison](../../experiments/multicore-feasibility/observer-free-inventory/report.md) regresses in both lean3 and lean4; four also loses to matching three. Removing observations changed data/code layout too. Park the variant and inspect existing compiled layout before attributing the result. |

Readiness, useful demand and net acceleration are separate questions. Inventory
sampling includes timestamps and color histogram work before its FULL-complete
marker; producer-end precedes some accounting/publication. Its high sampled
readiness fraction does not establish unsampled slack or a universal lower bound
on simpler delivery. The complete search measurements remain the decisive result
for that fixed implementation.

## Current decision and remaining obligations

The successful one-helper generic trial strengthens the case for the ownership
protocol beyond the original two-reader contention. It removed four Slots
acquisitions and the helper's packet copy while preserving arithmetic and callers;
no new per-call observer was added. All 29 focused controls and 60 benchmark lives
pass. A later idle-wrapper import failure and its bounded repair are preserved;
no completed benchmark was repeated. Unchanged mode3 also shows some timing drift,
so the experiment does not isolate a universal transport cost.

Own-PGO/full54 is now complete: 162 training lives and 324 comparison lives pass
without failure or retry. New2 records 64.004516s versus prior2 64.208272s, with
41/54 cases lower. New3 records 60.846776s versus retained3 60.721374s; new1 is
68.802407s versus accepted serial 68.293755s. These small differences have only one
observation per cell; no repeated-run uncertainty or isolated source attribution
follows. The large generic gain did not transfer to this production comparison.
No whole-helper tuning or replacement is selected.

The observer-free inventory comparison is now negative: preserved3 7.688469s,
observed4 7.790463s, lean3 8.222537s and lean4 8.758407s. All 48 replay lives/560
posts and four idle probes pass; the adapted fixture's epoch/count mistake and a
pre-native hash rejection are preserved. Production ownership/math stayed fixed,
but deleting observations and their storage changed both operations and layout.
The result does not isolate the benefit or cost of the old counters.

The [existing-image review](observer-free-layout-review.md) finds a changed
allocation size/alignment (15,584/16 to 1,720/8 bytes) and smaller/reordered outputs,
but no unique cause. Request/done spacing was already compact, and per-FULL Flight
and waiting cannot share a 64-byte line in the lean layout. Actual heap-base phase
and coherence traffic are unknown.

The [fixed-layout counterfactual](../../experiments/multicore-feasibility/fixed-layout-no-observations/report.md)
matched old compiled offsets before data and passed72 replay lives/840 posts.
Fixed3 records7.817264s versus lean3 8.243957s and retained3 7.716113s. Fixed4
records7.721670s:1.223% below matching3, but0.072% above retained3 at1.334x CPU.
Representation materially changes the result; neither isolated cache attribution
nor a net four-thread win follows. Further inventory/layout variants are unselected.

The [fresh-Influence trial](../../experiments/multicore-feasibility/fresh-influence-fusion/README.md)
closed at `08a5fd91`. Fused3 records8.047858s versus matching unfused3 7.695892s
and retained3 7.729813s. The4.5734% loss versus matching unfused spans all three
cases with separated ranges. All56 focused controls and36 replay lives/420 posts
pass, and cold row epochs verify actual activation. The extra map copies, peer
barrier, publications and code changes are included; the trial does not isolate
their individual costs. Park this fixed design without PGO or retuning.

The owner has explicitly expanded the mission to major redesigns, replacement
subsystems and isolated greenfield implementations. Existing search architecture
is not a requirement. The [reassessment](post-fusion-execution-architectures.md)
at `a7613525` separates prescribed state/order dependencies from inherited
boundaries and compares three concrete execution models. The lead independently
checked the arithmetic and commissioned one bounded Astra challenge of replicated
control. That design remains semantically plausible but duplicates control and
full-sized TT state to avoid per-FULL input publication; no speed claim follows.

The [type-disjoint trial](../../experiments/multicore-feasibility/type-disjoint-four/README.md)
closed at `8f3b568f`. Whole color/kind ownership allowed scalar pressure reduction
without a peer barrier, but the integrated design lost:9.097050s versus matching3
7.773228s and retained3 7.741570s. Per-case losses versus matching3 are11.78%,25.60%
and21.88%, with separated ranges. All49 controls and48 replay lives/560 posts pass
first attempt; final epochs match every actual reader. CPU is1.56024x matching3.
Park this fixed design. It establishes neither an isolated reduction cost nor a
general impossibility of wider arithmetic, and does not justify tuning this trial.

The [replicated-control study](../../experiments/multicore-feasibility/replicated-control/README.md)
is now measured. Three private search/TT/learning instances follow identical
transitions, one owner retains pawn-cache authority, and one scalar allgather
feeds common local finishing. All29 controls, three depth2 exact audits and60
depth8 timing lives pass without repair or repeat. The audits cover61/59/121 FULLs,
exact structured inputs/outputs and selected final state. All20 native outcomes
per case agree across five modes; this is finite evidence, not a universal proof.

Replica3 records6.746727s versus matching packet3 6.490515s, preserved packet3
6.440053s and preserved inline1 7.327634s. It gains7.93% over serial but loses3.95%
to matching packet3 and4.76% to preserved packet3. Case35 dominates the loss;
08/43 improve against the slower matching packet build, without a convincing
preserved-baseline advantage. Replica RSS is about53,000KiB per case versus about
19,000KiB for packet controls. Shared collective storage is704B. NoHost fixed-depth
root policy and common study-only unwind differ from production protocol/recipe;
these totals must not be compared directly with the full54 surveys. Park this
implementation unchanged rather than tune or reprofile it.

The [borrowed-input experiment](../../experiments/multicore-feasibility/borrowed-full-input/README.md)
also loses: preserved3 7.779674s, matching scoped-owned3 7.914857s and borrowed3
8.172098s. Borrowed is 3.25% slower than matching owned, with separated ranges in
all three cases and higher whole CPU. All49 focused controls,14 CLI controls,
two affinity fallbacks and36 original-protocol lives/420 posts plus three idle
probes pass first attempt. The inaccessible per-call guard protects caller input
lifetimes through actual reader retirement, including owner unwind and terminal
joins; legacy token dispatch stays owned. Root source review found no concrete
blocker in those paths. This finite evidence does not establish general safety
or a causal cache explanation. Park unchanged without PGO or a rescue variant.

Next assess coordinator-local ordinary inventory during existing epoch3 helper
work. This differs from inventory4: generate directly into the unused parent
scratch row on the coordinator, after its pawn/local work and before joining
the two color readers. There is no third helper or list transfer, but generation
may exceed the actual wait and may be discarded at bounds/threat/null cutoffs.
Preserve original ordering, logical charges and all public/observer boundaries;
prove per-ply ownership and totality before choosing an implementation. Old
sampled join and generation costs cover different populations and cannot prove
available slack. Only a bounded source recommendation is selected. Frontier
batching remains a separate reserve.

The retained three-thread image is `67d011083f37f42904423247f5cf0ece2a1e36f0a4129da94fe7561d1f922ea7`,
with profile `9487473e31dfc30ae515cdce18e3f15ec3a653bfd1c5bd665a8f76d235e30311`.
Its source/artifact are isolated experiment products; canonical research source
still preserves the practical two-thread checkpoint, and accepted main/release
bytes are unchanged. The source proof, focused controls and exact-image replay
surveys support further research. Broad mandatory/gameplay qualification of the
three-thread image, adoption, external transfer and release remain separate work.

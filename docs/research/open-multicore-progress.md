# Open multicore research: current assessment

2026-10-26, imp2-lead. Continuing under the
[mission](../deterministic-multicore-mission.md); this is a progress assessment,
not research closure or release approval.

The strongest research result now uses three threads. One coordinator preserves
King's search, pawn-cache accesses, state updates and logical work. Two helpers
compute independent color Activity/opposite-Shelter chains at actual FULL demand.
One immutable input is shared until both readers retire; each owns its output.
The reviewed epoch protocol removed serialized reader copies and result locking.
The numerical split alone had lost: the transport change made it useful.

The latest [Q owner-local own-PGO survey](../../experiments/multicore-feasibility/q-owner-local-own-pgo/report.md)
records59.918858s versus retained3d3 60.327621s and accepted serial68.811008s,
gains of0.68% and12.92%. The coordinator conditionally prepares ordinary and
eligible unchecked-Q lists during helper work. Whole CPU is179.768092s,2.609x
serial; the new inline mode costs1.07% versus accepted serial. This is the latest
research performance leader, with single observations per case/configuration,
not qualification or canonical adoption.

The preceding [ordinary owner-local survey](../../experiments/multicore-feasibility/owner-local-own-pgo/README.md)
extends that design: at ordinary FULL, the coordinator conditionally generates
its future move list while the matching color pair remains unfinished. It records
60.049404s versus retained67d3 61.047211s and accepted serial68.282114s in one
full54 window, gains of1.63% and12.06%. Whole CPU is180.163710s,2.635x serial.
It established the ordinary hook's gain; canonical/release source is unchanged.
Its new inline1 costs0.82% versus accepted serial. Qualification remains separate.

The preceding [epoch own-PGO full54 survey](../../experiments/multicore-feasibility/epoch-own-pgo/report.md)
records 60.763786s search wall for this candidate, versus 64.092876s preserved
two-thread and 67.973988s accepted serial in that window. Gains are 5.19% and
10.61%, respectively. Whole CPU is 1.422x the two-thread cost and 2.679x serial.
The same new binary's one-thread mode is a descriptive 0.15% above accepted
serial. These are single observations per case/configuration, with separate
repeated generic evidence. They are not a matched KingWCR comparison.

That earlier gain spans 48/54 cases against preserved two-thread and 45/54 against serial;
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

The [coordinator-local inventory assessment](owner-local-inventory-overlap.md),
committed `510cd4e8`, supports one new discriminator. Generate directly into the
unused parent scratch row after pawn/local work only when the matching color pair
is not already complete. This differs from inventory4: no third helper, extra
publication or list transfer. Generation may still exceed the actual wait and
be discarded at bounds/threat/null cutoffs. The private coherence permission
supports eager totality; null descendants use deeper rows, and sorting/learning/
logical charges stay at original demand. Public/FRESH/observer/root/Q and modes1/2
retain their original routes. A readiness hint grants no output ownership and
must not hide terminal failure. Old sampled join and generation costs cover
different populations and cannot prove slack.

The [fixed generic trial](../../experiments/multicore-feasibility/owner-local-inventory/README.md)
is positive: preserved3 7.751493s, matching off3 7.759613s and on3 7.545679s.
On3 improves2.76% versus matching off and2.66% versus preserved; all three
observed ranges separate and CPU falls. Case43 contributes most of the total.
All47 focused controls and36 original replay lives/420 posts plus three idle
probes pass. An initial test-only private-method compile error was repaired
before any test or workload execution; failed receipts and the original clock
are preserved. Production source was unchanged by that repair. Residual join
timing excludes eager generation, so it is not a saved-work measurement.

The [own-PGO/full54 lane](../../experiments/multicore-feasibility/owner-local-own-pgo/README.md)
passes216 training lives, one merge and actual independent byte-identical remerge,
one use build/admission,270 comparisons/3120 posts and five idle probes. Search
wall sums are serial68.282114s, retained3 61.047211s, new1 68.838654s, off3
61.587882s and on3 60.049404s. On3 improves2.50% against matching off (52/54)
and1.63% against retained3 (44/54);52/54 beat serial. Case43 now beats serial in
this observation. Ten losses to retained3 sum0.069517s, with worst relative loss
0.99% on06. Off3's0.89% and inline1's0.82% regressions preserve common-path costs
in the comparison; no isolated cause or confidence interval follows from one
observation per cell. Post-run metadata-closer repair does not repeat native work.

Retain the exact new image/profile as the strongest research result; full closure
is committed116dbb35. The [Q source assessment](q-owner-local-tactical-overlap.md)
at578e679a covers both actual sparse and FAST-refresh FULL seams, original
demand/order/charges and public/observer exclusions. Root challenged eager
totality because tactical generation lacks ordinary's bounded push protocol;
independent producer review confirms the loose417<512 bound on validated coherent
ancestry. No runtime admission probe is needed. Read-only old census joins show
generation demand among Q FULLs57.85/73.45/63.59% on35/08/43, substantially below
ordinary demand, with neither current readiness-admitted costs nor remaining
helper time established.

The [finite Q trial](../../experiments/multicore-feasibility/q-owner-local/README.md)
passes17 affected controls,14 CLI/two fallback checks and36 original replay lives/
420 posts plus three idle probes, first attempt. Ordinary-on stays active in all
three configurations. Preserved4b40 totals7.624830s, matching Q-off7.664552s and
Q-on7.537385s. Q-on improves1.15% versus preserved and1.66% versus matching off,
with lower CPU. Most net gain is43 with separated ranges against both controls;
35 separates only against matching off and08 overlaps. The off build drifts0.52%
above preserved. This is positive but narrow evidence, not demonstrated breadth.

The [Q own-PGO/full54 closure](../../experiments/multicore-feasibility/q-owner-local-own-pgo/report.md)
atdaa9e04a passes216 training lives, actual independent byte-identical remerge,
one use build/admission and270 comparisons/3120 posts plus five idle probes.
All491 training/comparison/idle native chains close first attempt; the metadata
adapter was corrected prospectively. Q-on59.918858s improves0.88% over matching
off60.450227s (46/54) and0.68% over retained3d60.327621s (41/54). All54 observations
beat serial68.811008s; no per-case significance follows from single observations.
The13 losses to3d sum0.086002s, worst relative loss2.10% on10. Newinline69.548826s
costs1.07% over accepted serial; Q-off drift is0.20%.43 supplies9.63% of matching
net gain, so the full54 gain is broader than the generic three-case screen.
Retain f8/profilebbb858 as latest research leader, with3d/67d/serial preserved.

The [completion-notification trial](../../experiments/multicore-feasibility/completion-fence/README.md)
is now measured. An independent bounded Astra review found a portable lost-wake
execution for publisher fence+load alone. An explicit SC fence after every cold
registration supplies the missing ordering condition. The tested change retains
actual done, Control, reader retirement and output reverse edges; publishers
stop clearing the latch and the sole coordinator owns registration/clear.

All25 worker controls,14 CLI/two fallback checks, lowering admission and48 replay
lives/560 posts plus four idle probes pass first attempt. New3 totals7.470674s
against preserved3 7.490874s, a0.27% improvement; matching inline1 improves0.37%.
Case35 loses0.17%,08 gains1.18% and43 gains0.67%. This does not establish a net
notification advantage. The actual publisher lowers from xchg to mfence/load and
the cold registration has its required fence; production declarations are exact,
but compiled type sizes/alignment were unavailable. Park unchanged without PGO,
weaker ordering or causal cache claims. Retain the proof as a useful result.

The [writer-region design](writer-owned-transport-layout.md), committed82a2dae,
supports one selected counterfactual on retained Q source68 with the original
successful protocol. Existing saved generic assembly shows request already
separate from packet filling; that is not new saved work. The fixed eight regions
keep each output with its own done, while separating request, packet, packed
lifecycle, the multiwriter latch, cold waits and Control. All observations,
arithmetic, owned input, atomic operations and both owner-local hooks stay exact.

The [generic trial](../../experiments/multicore-feasibility/writer-regions/README.md)
passes25 worker controls,14 CLI/two fallback checks and48 replay lives/560 posts
plus four idle probes without repair/repeat. Actual production geometry matches
the selected regions: Shared7168/alignment64, output56+done8 in each64-byte slot.
Arc allocation extent remains estimated; no allocator introspection was added.
Root source review confirms payload-only writes and unchanged retirement/SC
operations after field relocation; no whole-slot mutation or broad Sync was added.

New3 records7.449741s versus old3 7.499557s, a0.664% lower sum with0.993354x CPU.
All three medians improve, but all ranges overlap. Inline rises0.440%; subtracting
that drift cannot isolate a layout benefit. This is tentative evidence, with no
cache-cause claim. The separately selected [own-PGO/full54 comparison](../../experiments/multicore-feasibility/writer-regions-own-pgo/report.md)
passes216 training lives matching the retained Q mixture, actual independent
byte-identical remerge/use build and270+5 comparing serial and old/new inline1/
mode3. Source and topology remain unchanged; actual production geometry passes.

New3 totals59.317384s versus f8 59.909994s, a0.989% improvement with0.990131x CPU.
There are48/54 faster cases and six losses totaling0.024323s. Worst relative loss
is1.75% on12; largest absolute loss9.392ms on13. All54 observations beat serial
68.279043s, with13.125% lower total wall at2.603426x whole CPU. Newinline69.115223s
improves0.507% over f8 inline69.467164s, and remains1.225% above serial. This common
build/profile change cannot be subtracted to isolate a layout cause. Five idle
probes observe0 ticks/250ms; per-process peak RSS and the actual type projection
do not measure cache traffic. Single observations establish no confidence interval.
Retain a4ecf096/profile6cb9dcaa as the research leader, preserving all predecessors.

Next is a source-only assessment of preparing score-independent late-endgame
geometry before the FULL join. Actual score/sign choices, rounding and finishing
publication must remain canonical. Geometry could be demanded more reliably than
eager move generation, but expensive material shapes may be rare and both ideas
compete for the same owner wait. No additional worker, census, implementation or
native lane is selected. Frontier batching remains a separate reserve. Current
transport and owner-overlap gains create no new parallel work width.

The latest three-thread image is `a4ecf096d2144a79608b0ff4f3dc827bc8e5119730f2c43b29f46d1f7ffe62b5`,
with profile `6cb9dcaab015c8b4c13f37040bb34cda9e4d7bc11b77ef8c4c99bd56987eae3b`;
the winning mode enables ordinary and Q owner-local inventory. Predecessors
f8b829,3d914c and67d01108, with their profiles, remain preserved. These sources/artifacts
are isolated experiment products; canonical research source
still preserves the practical two-thread checkpoint, and accepted main/release
bytes are unchanged. The source proof, focused controls and exact-image replay
surveys support further research. Broad mandatory/gameplay qualification of the
three-thread image, adoption, external transfer and release remain separate work.

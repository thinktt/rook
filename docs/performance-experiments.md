# Performance ideas and results

Short catalog through 2026-10-20. **Current local candidate: the first-main
corrected build**, [adopted at 8cf224f2](../experiments/first-main-cutoff-adoption/README.md).
Paired full54 costs 68.569086 CPU seconds versus 68.446861 for exact retained62,
a descriptive +0.178569%. This is a conformance correction; no last-mile
optimization variant earned adoption. Corrected-image full12 timing and final
performance qualification remain open. The last-mile goal is active under the
[working agreement](leadership-working-agreement-last-mile.md); candidate62 remains
the initial control. Its historical totals were 67.640360 CPU seconds for the
54 searches and 675.156653 seconds for the 12 games, from their original windows.

The [independent repository survey](reviews/2026-10-20-architecture-performance-survey.md)
assesses the architecture, completed experiments, measurement limits and ranked
untried directions. It adds no engine measurements or selected optimization.

R1–R25 preserve the original research-list IDs, which include diagnostics,
unimplemented ideas and overlaps. E26–E67 are explicit experiment IDs; neither
sequence is the numbering of [decision records](decisions/). Thus67 is the latest
identifier, not67 completed optimization trials. Candidate IDs21–23 are not
independently established by this catalog.

“Faster/slower” below describes the cited engineering pilot, not a full54 result
unless stated. Generic and own-source PGO are different builds. Gains are not
additive. “Parked” means not retained, commonly because the improvement missed the
fixed minimum (later0.5%, plus case-level checks). A small positive number is not
a proven benefit. Detailed sources remain in [STATUS](../STATUS.md),
[research notes](research/remaining-performance.md), decision records and the
small historical reports retained under `evidence/`.

| ID | Idea | Brief result |
|---|---|---|
| R1 | Shared immutable evaluation geometry | Adopted; own-PGO 3.19% lower. |
| R2 | Same-node FULL reuse census | Cache declined; repeat rate 0.050%. |
| R3 | Compact relation-summary lookup | Adopted, later superseded; own-PGO 3.485% lower. |
| R4 | Placement representation alternatives | Measured under R7; not a separate trial. |
| R5 | Share evaluation phase and material | Isolated; generic 0.749% lower, not adopted. |
| R6 | Store king coordinates in padding | Rejected; generic 0.123% lower, inconclusive. |
| R7 | Persistent versus local attack planes | Persistent adopted; canonical own-PGO 3.127% lower. |
| R8 | Counts-guided mailbox attack queries | Unimplemented; no measurement. |
| R9 | Typed-list Influence source enumeration | Adopted; combined own-PGO 7.235% lower. |
| R10 | Narrow private Activity arithmetic | Parked; generic 0.262% lower, inconclusive. |
| R11 | Static piece-kind Activity specialization | Adopted; own-PGO 2.206% lower. |
| R12 | Null-transition Influence demand census | Reuse declined; map demand 0.768%. |
| R13 | Table-driven nonpawn destination traversal | Parked; generic 0.231% lower, inconclusive. |
| R14 | Lookup uncapped Influence profile sums | Parked; own-PGO 0.040% slower despite generic gain. |
| R15 | Lookup pressure-mark arithmetic | Parked; generic 0.312% slower. |
| R16 | Reuse Q capture-material endpoints | Parked; generic 0.009% lower, effectively flat. |
| R17 | Try checked bounded king replies first | Adopted; own-PGO 1.513% lower. |
| R18 | Ordered checker discovery from bitplanes | Adopted through composition; own-PGO 1.227% lower. |
| R19 | Reuse ordinary known-check fact | Generic0.728% lower; own-PGO/adoption not established. |
| R20 | Share one projected Q bitplane view | Adopted through composition; own-PGO 2.025% lower. |
| R21 | Precompute Activity destination values | Adopted; own-PGO 1.310% lower. |
| R22 | Fuse pawn forward scans | Parked; generic 0.211% lower missed advancement gates. |
| R23 | Reciprocal remembered-group indexing | Parked; generic 0.042% lower missed advancement gates. |
| R24 | Exact-placement pure-component cache | Parked; own-PGO 0.357% lower missed gate. |
| R25 | Ordinary projected Boolean checks | Adopted; own-PGO 2.075% lower. |
| E26 | Share full-evaluation phase inputs | Parked; generic 0.208% lower missed gate. |
| E27 | Paired pressure digit sums | Parked; generic 0.233% lower missed gates. |
| E28 | Construct local child Node directly | Backend rejected: copies survived and enlarged. |
| E29 | Derive ordinary child Influence incrementally | Parked; generic 0.316% lower missed gates. |
| E30 | Update child Influence in place | Parked; generic 0.352% slower. |
| E31 | Arithmetic pressure-mark construction | Parked; generic 0.229% lower missed gates. |
| E32 | Table-driven king-pressure traversal | Parked; own-PGO 0.239% slower. |
| E33 | Private fixed-root weighted component cache | Parked; own-PGO 0.375% lower missed gates. |
| E34 | Compact recursive stop result | Parked; generic 0.340% lower missed gates. |
| E35 | Local Activity category and destination masks | Parked; generic 3.784% slower. |
| E36 | Fat link-time optimization | Parked; own-PGO 0.415% slower. |
| E37 | Coherent Influence slider masks and SIMD | Adopted; own-PGO 2.147% lower. |
| E38 | Pack four relation tiers per byte | Parked; generic 0.697% slower. |
| E39 | Const pressure-value lookup | Backend rejected: repeated 256-byte stack copies. |
| E40 | Shared static pressure-value lookup | Adopted; own-PGO 0.877% lower. |
| E41 | Static shelter ring-base lookup | Parked; generic 0.131% slower. |
| E42 | Borrow placement for Activity slider geometry | Parked; generic 0.600% slower. |
| E43 | Bit-sliced Influence accumulation | Retained; own-PGO 1.161% faster. |
| E44 | Build Influence directly into result | Rejected before timing: compiled copies unchanged. |
| E45 | Remove private index bounds checks | Parked; generic 0.346% faster, below threshold. |
| E46 | Skip capture-overridden relations | Parked; generic 0.049% faster. |
| E47 | Borrow Position through split evaluator | Parked; generic gain vanished under own-PGO (0.014%). |
| E48 | Reborrow Position with existing evaluator API | Parked; generic 0.306% faster. |
| E49 | Equal-length ordering workspace slices | Parked; own-PGO 0.182% faster. |
| E50 | Incremental Influence with ray cancellation | Parked; generic 0.048% faster; one case regressed >2%. |
| E51 | Generate tactical checks from king masks | Retained; own-PGO 1.574% faster. |
| E52 | Separate coherent/scalar Activity functions | Parked; generic 0.199% slower. |
| E53 | Skip zero-opponent support counts | Parked; generic 0.521% slower. |
| E54 | Merge six ordering streams | Parked; generic 0.325% faster. |
| E55 | Direct small-list ordering entry | Parked; generic 0.312% faster. |
| E56 | Paired support counts in wide lanes | Parked; own-PGO 0.180% faster. |
| E57 | Compute absolute pins from placement planes | Retained; own-PGO 1.156% faster. |
| E58 | Aggregate pawn Influence seeding | Parked; generic 0.172% faster. |
| E59 | Defer captured-square clearing | Parked; generic 0.049% slower. |
| E60 | Return Activity totals as scalars | Parked; generic 1.037% slower. |
| E61 | Clip pressure rays with bitplanes | Parked; generic 0.259% faster. |
| E62 | Profile-guided ExtTSP code layout | Retained; paired pilot 1.044% faster; whole54 67.64s. |
| E63 | Split cold machine-function regions | Parked; own-PGO 0.468% slower. |
| E64 | Classify captures by raw tag ranges | Parked; generic 0.205% slower. |
| E65 | Compact one-sided relation dictionary | Parked; own-PGO 0.101% faster. |
| E66 | Construct main child in caller storage | Parked; copy removed, own-PGO only 0.287% faster. |
| E67 | Delay quiescence parent borrow | Parked; copy removed, own-PGO only 0.078% faster. |

Additional work and diagnostics:

| Idea / investigation | Brief result |
|---|---|
| Copy-child versus undo microexperiment | No integrated restoration winner established. |
| Geometric pin/evasion legality summaries | Retained; early four-case pilot about12.3% faster. |
| Direct full-byte relation table | Retained; own-PGO0.703% faster; distinct from R13. |
| Shared search/admission boundaries and timed controller | Retained for common semantic ownership; no isolated speed claim. |
| Influence arithmetic, geometry and coherence controls | Established prerequisites for safe optimized kernels. |
| Whole-engine profiles and component instruction studies | Located generation/evaluation/search costs; modeled events are not CPU savings. |
| Placement-transposition census | Found exact repeats; motivated R24, which failed its own-PGO gate. |
| Influence-update eligibility/cancellation studies | High logical opportunity; actual E29/E30/E50 still failed. |
| Activity-category repetition census | Too few useful repeats; category cache declined. |
| Whole-Activity repetition census | Repeats0.111%/0.043%; node-local cache declined. |
| Current62 branch/cache accounting | Strict study failed with a2-instruction discrepancy; only partial findings usable. |
| Current62 generation-safety census | Two exact observations; many off-mask rejects already skip projection. No speed claim. |
| TT baseline access/layout review | Actual loads checked; motivated the compact48 trial below. |
| Current62 TT probe/store census | [Two cases closed](../experiments/current62-tt-census/report.md):all-identity misses80.85%/31.61%; stores88.87/51.35 per100 probes.197 tests and both live/offline replays pass; no layout or speed claim. |
| CPU affinity, accounting, PGO and calibration checks | Reproducible local comparisons; no universal Vic-to-Bee conversion or live PMU. |
| Candidate25 external Bee benchmark and functional probes | External reference point, not proof of later gains or final qualification. |
| Last-mile three-unit functional study | [Four-route study closed](../experiments/functional-cost-three-unit/report.md): opening position/evaluation observations below reference, enclosing light search above; observer/build/host boundaries prevent a production cost partition. Retained62 unchanged. |
| Alpine dynamic-musl deployment | [Local trial](../experiments/alpine-dynamic-musl/README.md): own PGO; exact repeat builds; all216 standard54 lifetimes pass (70.885691 CPU s) and all12 independent games pass (632 searches,711.863507 CPU s single pass). Literal combiner rejects differing accounting receipt paths; no combined qualification or adoption. |
| Candidate68 clean-build reproducibility | [Both images match](../experiments/candidate68-clean-rebuild/README.md): empty Cargo target directories, preserved source path/toolchain/PGO profile; exact ordinary and diagnostic SHA256/size. Same-machine result, no engine run or cross-machine claim. |
| Native/diagnostic conformance, wire, seeds and regular12 pre-gates | Finite correctness/regression coverage; full external game gate remains separate. |
| First-main equality cutoff correction | [Discriminator](../experiments/first-main-cutoff-correction/README.md) and [mandatory completion](../experiments/first-main-cutoff-correction/mandatory-completion/README.md) pass: expected old equality failure, 196 library + 209 diagnostic + two development tests, all 7,673 mandatory cases/115 files. [Fresh own-PGO/full54](../experiments/first-main-cutoff-production/README.md) closes 432 lives/864 offline checks: 68.569086 CPU s corrected versus 68.446861 s retained62, +0.178569%; no optimization gain gate. [Gameplay](../experiments/first-main-cutoff-gameplay/README.md) passes all33 lifetimes and literal focused replay. [Locally adopted](../experiments/first-main-cutoff-adoption/README.md); no public equality witness, full-game qualification or parity claim. |

Current proposals and source trials:

| Idea | Current position |
|---|---|
| Enumerate checked destinations through the existing evasion mask | [Parked after fixed70](../experiments/checked-enumeration-compiler/screen-results.md):generic0.27077% lower,4/7 lower; all70 live/offline checks pass.196 tests/compiler review established pruning with code/frame growth. No retune/repeat/PGO rescue. |
| Replace pressure mark bytes with per-kind weak/strong presence sets | [Parked after fixed70](../experiments/pressure-presence-compiler/screen-results.md):generic0.4281% slower,3/7 lower; all70 live/offline checks pass. Compiler stage passed200 tests and retired the byte consumer, but smaller frames did not produce a passing CPU screen. No retune/PGO rescue. |
| Replace unchecked pinned-source projections with a pin-ray test | Lower-priority hypothesis; proof and added setup costs unresolved. |
| Reorganize TT identity headers/payloads, or align groups | [Compact48 own-PGO trial parked](../experiments/compact48-tt/report.md): 0.29295% lower, 6/7 lower, below the fixed 0.5% gate; 196 tests, fresh 54-case training and all 70 live/offline screen checks pass. Same G/one allocation and payload-free identity misses survive backend review. Dense slabs remain untried; no retune/repeat/adoption. |
| Counts-guided mailbox attacks | Earlier R8 hypothesis; never implemented or measured. |
| Skip private shelter work with an exact zero multiplier | Source proposal only; retain public component behavior. |
| Direct-output Influence with safe initialization/rollback | Unimplemented transport alternative; distinct from E44. |
| Packed ordering records | Deferred; larger512-entry workspace undermined the original size premise. |
| Apply quiescence children into caller-owned storage | Deferred, distinct from E66/E67; no performance result. |
| Broader layout/restoration alternatives | Architecture alternatives remain possible; no automatic rewrite or selected trial. |

Already rejected caches, Influence deltas and copy-only changes are not fresh
ideas simply because they are rediscovered. No last-mile optimization variant
has been promoted. The first-main correction is locally adopted for conformance;
retained62 remains the initial production control.
Bulk records, original history and detailed audit catalogs live in
`/home/legolas/rook2-experiments`; see [archive layout](evidence-layout.md).

Builder follow-up: the [Debian dual-runtime recipe](../build/linux-builder/README.md) now builds all four main/diagnostic outputs with checksum-locked diagnostic vendoring and offline compilation. Both diagnostic companions pass 25 position-setup fixtures, including musl inside Alpine. This is packaging validation, with no new performance result or candidate replacement; see the builder validation record for limits.

Static-glibc packaging: added a third runtime to the Debian builder. Both plain binaries compile offline and have no ELF loader/shared-library requirement. Alpine checks pass 25 position-setup + 4 diagnostic search cases and 8 ordinary interruption sessions / 24 searches. No performance or full qualification claim; [static validation](../build/linux-builder/static-validation.json).

Static-glibc Alpine timing: the existing plain release build (O3/ThinLTO, **no PGO**) passed standard54 at 77.554450 s native CPU median sum and one full12 pass at 781.715662 s CPU / 786.921638 s wall, 632 searches / 5801 posts. Entire container pinned CPU14; this does not isolate static-linking cost against earlier PGO builds. [Setup and concise report](../experiments/static-glibc-alpine-performance/README.md).

Static-glibc Alpine own-PGO: [completed trial](../experiments/static-glibc-pgo-alpine/README.md) reports 67.192095 s native CPU for standard54 (54 excluded warmups + 162 measured lifetimes) and 676.375347 s for one full12 pass (632 searches / 5801 posts). Saved-record audit passes; all Alpine helpers share CPU14 and training overlaps standard54. Descriptively 13.361393% / 13.475528% below the earlier plain static-glibc totals in separate windows with the same whole-lifetime accounting; no cross-engine parity, adoption or final qualification claim.

Static-glibc own-PGO Alpine follow-up: all54 strict training cases produced verified native profiles; use-build and reconciliation pass. Entire container on CPU14: standard54 median sum 67.192095 s CPU / 67.553958 s wall; one12-game pass 676.375347 s CPU / 680.527493 s wall, 632 searches / 5801 posts pass. CPU reductions versus the separate-window plain-static run are 13.36% / 13.48%. No artifact promotion or final qualification. [Supervised setup/results](../experiments/static-glibc-pgo-alpine/README.md).

Release reproducibility follow-up: a bounded upstream compiler attempt did not match candidate68. The pinned Debian toolchain reproduces both original hashes, including after converting the original profile to checked-in LLVM text. The cleaned Docker builder produces dynamic/static glibc pairs with all debugging retained; two clean containers produce identical four-artifact results. The new static pair passes mandatory115/7673, standard54 and the focused12/632 plus continuity/seed/wire pre-gate. One before-native wire fixture-path setup repair is preserved, with no completed native request retried. Tag-only packaging verifies the committed four-hash manifest. No new performance or full-game-gate claim; [release verification](../release/README.md).

Deterministic multicore first probe: standalone Activity→Shelter worker with coordinator-owned pawn branch passes 162 actual-Evaluator comparisons. On observed guest cores14/6, single-call FULL composition is 597.75→503.51ns elapsed (1.187x), with 1.694x process CPU; empty roundtrip159.92ns. Pre-shared inputs omit fresh packet publication, and batches are throughput probes only. No engine integration or production speed claim. [Setup/results](../experiments/multicore-feasibility/report.md).

Integrated deterministic multicore FULL seam: fresh owned packets, budget1 inline/budget2 persistent worker, no PGO. All 15 relevant evaluator tests and 36 original replay lives pass; cases35/08/04 show 9.92%/3.20%/7.04% less search wall versus new budget1, costing 1.802x/1.939x/1.859x whole CPU. Three-case median sum8.27% lower; serial refactor sum0.014% lower/unresolved noise. Idle busy-spin consumes about one core. Research-only; no production adoption. [Full boundaries/results](../experiments/multicore-feasibility/integration/report.md).

Source-only branch-queue investigation: recommend optimistic complete restricted-root-tail transactions with ordered semantic TT/learning/pawn operation validation. Non-best tail completions can leave predicted windows unchanged; full-state dependencies still matter. First proposed experiment explicitly omits live clocks/partial stops. No queue implementation or native run yet. [Recommendation and source evidence](research/branch-task-queue-feasibility.md).

Restricted-root whole-branch transaction pilot: six serial queue simulations naturally reach Restricted at depth6. All controls and finite canonical audits pass; 42 tasks include36 prepared ahead, with **zero ahead-task acceptance**. Two877-node head tasks accept;22 order changes/8 window changes/1 pawn selection/9 first-overflow rejects. Sixteen capped certificates cover358858 speculative nodes, limiting the negative inference. Full-table snapshots and352-byte padded events are expensive prototype choices. No actual scheduler or speedup; recommend pure-prefix demand/use study rather than a general whole-branch executor. [Boundaries/results](../experiments/multicore-feasibility/branch-transactions/report.md).

Queued pure-child preparation (depth2, first6 ordinary children): exact-input Influence/Activity results are reusable, but48 original replay lives pass with unfavorable costs. Budget2/4 search-wall median sums10.982/13.465s vs new budget1 9.190s (+19.50%/+46.51%), total CPU1.484x/2.275x. Only13–21% of started tasks supply any result; unused work and fine-grained delivery are obstacles.12 focused checks pass; no queue retune, PGO, adoption or full qualification. Recommend park this policy and retain the positive FULL split. [Design/results/boundaries](../experiments/multicore-feasibility/child-preparation/report.md).

Parked FULL worker + own-PGO:11 focused checks pass; startup idle old budget2 burns0.25CPU s/250ms, new budget1/2 register0 ticks (10ms resolution). One54-per-mode fresh training/one merged profile;36 small and162 descriptive54 replay lives pass. Original54 wall totals68.237305 control/69.171315 candidate1/63.946851 candidate2:6.29% net improvement,7.55% vs candidate1; totalCPU1.873x control. Candidate1 serial wall cost+1.37%;47/54 lower vs control, seven losses total0.240366s (largest43,+0.119227s). Single-observation survey, finite lifecycle/host coverage, no qualification/adoption or >2 scaling claim. [Exact setup/results/limits](../experiments/multicore-feasibility/full-split-production/report.md).

Reversed FULL placement:31 focused tests and64 original replay lives/864 posts pass, including actual-cache recovery after abandoned output/failure. One generic four-case trial (35/08/04/43): preserved current2/new inline1/current2/reversed2 wall median sums11.945973/12.761495/11.953181/12.766913s. Reversal loses3.14–8.46% in every case with separated ranges,6.81% aggregate vs sibling current; essentially inline wall with2.000x its CPU. New current versus preserved current is+0.06% aggregate. All startup idle probes0ticks/250ms. Park reversal; no PGO rescue, transport sweep, nested worker or adoption. Positive PGO image unchanged. [Exact trial/results/limits](../experiments/multicore-feasibility/reversed-full/report.md).

Serial same-node inventory census:6 focused checks and original35/08/43 once each pass (35 posts). Eligible971481/222480/1066340; original inventory demand76.33%/98.41%/76.99%. Fixed512 stride gives1897/434/2082 samples, no cap/domain skips; all1372/427/1565 consumed no-null samples have generation shorter than actual ensure/FULL, median slack812/321/380ns. No discarded work counted as saved; timer/counter/cache/stride biases explicit, no speed bound or worker built. Recommend one bounded ordinary inventory discriminator, pricing null ownership, readiness, transfer and the displaced positive FULL split. [Setup/results/limits](../experiments/multicore-feasibility/inventory-overlap/report.md).

Same-node ordinary inventory helper:21 selected checks and64 original replay lives/864 posts+4 idle pass. Fixed single-slot READY-or-inline/drain policy delivers99.86–100% of demanded lists, busy/domain0 and counters match prior census35/08/43. Nevertheless inventory wall median sum12.755576s vs sibling current11.984310s (+6.44%, every case slower with separated ranges) and preserved current11.866613s (+7.49%); essentially inline12.766229s with1.997x CPU. Null-boundary ownership/Box costs included; no Q/concurrent FULL helper. Park unchanged, no retune/PGO/follow-on; positive a977/f9ee unchanged. [Complete costs/results/limits](../experiments/multicore-feasibility/same-node-inventory/report.md).

Unimplemented FULL integration recommendation: derive from the frozen positive source, default1/capped2 total budget, inherited affinity, external benchmark placement and supervisor-only deadlines. Predicate-based completion/lifecycle waits require new publication/notification checks and a small matched cost comparison before fresh PGO/adoption evidence. No new architecture or three-thread variant selected. [Source-only assessment](research/winning-full-integration-assessment.md).

Practical FULL integration: restore winning5612 source, keep failed variants in history, add positive capped budgets, inherited affinity and predicate waits without engine wall-abort.20 unit checks,9 CLI controls, one single-CPU08 projected replay and48 original lives/648 posts+3 idle pass. Generic four-case wall sums11.855924 frozen current2/12.646141 cleaned1/11.907192 cleaned2:5.84% below inline with1.883x CPU,0.43% above frozen2;43 still loses. Idle0ticks/250ms. Single-CPU liveness takes55.61s, a usability defect; next source fix caps configured threads to1 when permitted affinity has exactly one CPU. No PGO/adoption/qualification. [Results and boundaries](../experiments/multicore-feasibility/usable-full/report.md).

Configured practical FULL own-PGO: query Linux permitted affinity before configuration; exactly one CPU caps actual threads1, retaining request.12 unit/13 CLI controls plus original08 requested1/2 each pass with one task (~0.39s); old55.61s result preserved. Fresh108-life training/one merge,64-life repeated small comparison and216-life descriptive54 pass (388 lives/4608 posts). Full54 wall69.056196 accepted serial/64.270245 prior2/69.831350 new1/64.369022 new2:6.79% net gain at1.863x CPU,0.15% above prior2;46/54 improve,43 largest absolute loss. No retune/adoption/broad qualification; recommend exact-image behavioral qualification next. [Identities/results/limits](../experiments/multicore-feasibility/configured-full/report.md).

Configured-FULL exact-image local behavioral closure: frozen8f26 PGO config13CLI+two one-task08, mode2 regular12/632/5801posts plus short controls/literalcombine, and mode1 short-only all pass. Same-source default1 DIAG3645 passes current115-file/7673-case/117-operation mandatory inventory;215 normal library passes (204fresh+11reused),209DIAG/2dev and external enabled-observer Q1/2 control pass. One compile-only private-field harness repair preserved; no native retry/ordinary rebuild.32 search lives have verified pre-input placement; synchronous seed snapshots and2 missing DIAG post-exec observations have explicit narrower coverage. Ready for local-adoption decision; main/release/external gate unchanged. [Full scope/results](../experiments/multicore-feasibility/configured-full-qualification/README.md).

Beyond-two branch census:4 focused controls and original35/08/43 once each pass exact replay (35 posts), native N/R and independent forest/exclusive/cut reconciliation. Eligible full-window direct-Q work is41.06%/27.93%/46.98% of N, but96–99% of tasks have fewer than8 nodes; no four-way128-node direct-Q cohort. Larger ordinary siblings remain, with5,392/763/5,161 overlapping four-way128-node boundaries. Park Q certificates; recommend hierarchical descendant recovery after canonical parent reordering, still unimplemented. One test-only compilation repair preserved; no speed claim, PGO, adoption or additional native lane. [Counts/results](../experiments/multicore-feasibility/beyond-two-census/report.md), [recommendation](research/beyond-two-queue-recommendation.md).

Hierarchical exact-entry recovery:23 focused tests and bounded serial08/q2+35/q2 pass; independent local output/work and root-final state checks find no discrepancy. Ahead reuse99/22,573 N across62/13,509 disjoint segments, largest6/118 N; heads separate, no caps. Current coordinator subcost0.314/59.095ms exceeds removed-call wall proxy0.075/21.383ms before snapshots/recording. One invalid positive-demand fixture and two diagnostic failures preserved; fixture-only repair, no workload retry. Native Group sparse staging avoids full TT copy per attempt. Assess consumed ordinary depth1/2 order prefixes next; no parallel-speed, adoption or qualification claim. [Results](../experiments/multicore-feasibility/hierarchical-recovery/report.md), [source assessment](research/hierarchical-recovery-prefix-assessment.md).

Paired consumed-prefix recovery:34 focused checks and two unique08/35 lives pass finite audits. Ahead reuse99→126N and22573→24533N, with no>=128N survivor. In35 net1960N/12794R adds6.004ms removed-call proxy while executor proxy rises17.500ms, including9.550ms annotation. Collector-label repair adopts original08 without rerun; only unstarted35 executes. Close prefix tuning and recommend a distinct post-child0/tail-IIO internal1/2/4/8-thread discriminator; no parallel-speed/qualification claim. [Results](../experiments/multicore-feasibility/consumed-prefix/report.md), [recommendation](research/after-prefix-scaling-recommendation.md).

Internal post-child0/tail-IIO worker trial:36 focused controls (including actual workers, native TT overlays and cancellation) pass; one frozen generic image and48 requested1/2/4/8 lives pass independent raw/output/work/root-state checks. Fixed depth6 selector misses all35/08/43 (174486/51689/14144N): no workload batch, worker, TT snapshot or speculation launches. This is a coverage result, with no scaling/conflict/economics claim. Keep selector/caps/source intact; recommend establishing admission on a bounded deeper/original-workload horizon before another worker collection. No retune/PGO/adoption or automatic follow-on. [Results](../experiments/multicore-feasibility/internal-split/report.md).

Depth8 internal-queue extension:3 affected controls plus inherited36,33 unique lives/9 warmups/24observations pass independent raw/output/work/root-state audit.35/08 firsthit iteration7;43miss maxotherwiseeligiblechild0=1566N andnotrepeated.35 coordinatorchild cuts off before allqueued demand;08 seven demanded children total162N/R0,114N descendantreuse/0wholechild,188specN. Splitwall t1/2/4/8 medians35=16.351/19.414/19.147/19.532ms;08=15.753/18.951/18.859/19.232ms. Common setup contains diagnosticTT fingerprint; one16776912B batchcopy adds~2.2ms. No useful scaling for this firsthit batch, no coarse-grain conflict conclusion or retune. Pure-result salvage from coarse producers remains an unimplemented alternative needing canonical demand/cost evidence. [Results](../experiments/multicore-feasibility/internal-horizon/report.md).

Externally frozen coarse internal fixture:11 affected controls+39reused,3uncensored captures+16 audited1/2/4/8 lives pass. Fixed case/ordinal rule chooses35 parent428548; eight actually demanded siblings29077N,minimum839N; sevenfuture25340N/81617R,stablewindows/noretries. Splitwall medians105.271/166.920/154.413/154.717ms;2/4/8 lose58.56/46.68/46.97%,CPU2.180/2.315/2.370x.11548N/26441R reuse fragments into7296 descendant ranges,max34N,0wholechild; nocaps. Diagnostic~16ms binding outside split,~2.2ms requiredTTcopy inside. Park effectfulreplay; pure-result salvage is a distinct coverage/cost question, with no optimizedconsumer/parallelcampaign from this record. [Results](../experiments/multicore-feasibility/wide-internal/report.md).

Coarse pure-result salvage census: same frozen35/seven forecasts, no replay journals or consumer. All-ready pooled kernel proxy6.091ms includes5.596ms previously unavailable first queries/13,014keys; intended-child supplies most matches (pool adds only0.222ms). RequiredTTcopy2.246ms plus current poolmerge14.077ms already exceeds that ceiling; producer plain/observed37.144/61.515ms. Three new controls+62reused and83checker controls; one successful serial census independently reconciles after two preserved failures and a proved sparse-serialization accounting repair within unchanged caps. Park current pooled representation; lean intended-child costs remain a possible unselected question, not a general impossibility result. No parallel speed, qualification or adoption claim. [Results/boundaries](../experiments/multicore-feasibility/coarse-pure-salvage/report.md).

Open-agenda source reassessment (untried): recommend colors-only3, splitting Activity by attacker and opposite-defender Shelter with one shared immutable publication and coordinator rounding/R ownership. Combined Activity+inventory3/colors+inventory4 are genuinely untested but need complete pickup/settlement costs; the old trial replaced FULL. Prior-iteration frontier batches are distinct only with earlier owned-input collection/new child kernels, with new demand/lead-time evidence required. No prototype/build/run selected or performed. [Comparative source recommendation](research/open-architecture-reassessment.md).

Colors-only3: two side Activity/opposite-Shelter readers share one retained packet; coordinator keeps cache/merge/R.38focused+13CLI+2affinity controls and fixed48replay/560posts+4idle pass, retaining3warmups after one pre-input Linuxcomm name-check failure; unchanged images/source/caps, no completedlife repeated. Generic35/08/43 median sums preservedcurrent2/inline1/current2/colors3=7.979400/8.294531/8.013154/8.379793s: colors+4.58% vs siblingcurrent,1.568x CPU;08/43 ranges separated,35 overlaps. Sparse512 samples show helper outputs after owner96.22/99.81/100%; no causal decomposition or fusion forecast. Recommend park unchanged; no PGO/tuning/adoption. [Results and exact repair/boundaries](../experiments/multicore-feasibility/colors-three/report.md).

After-colors source choice (untried): recommend positive whole-FULL+inventory3 with one shared packet and used-list installation in existing per-ply scratch at FULL completion. Null descends to higher rows; early scratch is unobserved, removing the old null Box but not guard/transfer/discard costs. Fresh-map/side-FULL fusion is distinct and color-local, but peer-map barrier delays pawn work and current2 already has one dispatch. No prototype/census/run selected by this note. [Source/cost proof](research/after-colors-dataflow-choice.md).

Fixed epoch-colors transport: onlyworker changes in64-source map; reviewed initialized-cell/reference retirement and SC-latch wake proof, directinput/separateoutputs, same4096/512/arithmetic.32fresh+13CLI+2affinity and fixed48/560posts+4idle pass firstattempt. Generic old3/inline1/current2/epoch3 median sums8.368089/8.358745/8.029709/7.735016s: epoch−7.57% vsold3,−3.67% vscurrent2 at1.445xCPU.35/43 separated gains,08 overlaps;0idle ticks. Interval boundaries shift cache work fromcopytokernel; nettransport effect includeslayout, notlock-onlycost. Retain as promising; propose exact-source joint1/2/3 own-PGO162 plus five-config descriptive270full54, no redundant smallscreen or tuning. [Results/proof/continuation](../experiments/multicore-feasibility/epoch-colors/report.md).

Epoch-colors exact own-PGO/full54: unchanged64-source,162 joint1/2/3 training lives/one canonical merge plus byte-identical independent remerge;13CLI+2fallback and270 original lives/3120posts+5idle all pass firstattempt. Direct54 wall sums serial5cf/practical2/new1/new2/epoch3=67.973988/64.092876/68.076222/64.147690/60.763786s: epoch−5.19% vspractical2,−10.61% vsserial at1.422x/2.679xCPU;48/54 and45/54 cases improve respectively,43 still+4.56% vsserial.0idle ticks/250ms. Preserve exact67d011/profile948747 and recommend bounded exact-image qualification, no adoption/new lane or matchedKingWCR claim. [Complete results/boundaries](../experiments/multicore-feasibility/epoch-own-pgo/report.md).

After-epoch fourth-worker assessment (untried): recommend conditional ordinary inventory beside the positive two side producers, one post-Influence immutable packet and separate sparse inventory request. Two-stage completion retains input through FULL composition; used list installs into existing row[p] before null, with original charges/order at demand. Source challenge finds no ownership blocker, but third-reader lifecycle/guard/transfer/spin and shorter epoch3 slack remain unpriced. No root/Q empty acknowledgment, per-call Arc/Box, staged-field mutation, mode2 transport change or new native lane. [Source proof and smallest discriminator](research/after-epoch-fourth-worker-choice.md).

Conditional epoch inventory4: post-Influence ordinary third reader, sparse requests/Joined and existing row[p] settlement; pre-data source proof removes redundant opposite-king check.50focused+15CLI+2fallback and fixed60/700posts+5idle pass firstattempt. Generic preserved3/new1/new2/new3/inventory4 median sums7.714777/8.259364/7.978495/7.817537/7.777120s: four+0.81% vsretained3 at1.344xCPU;35−1.38%,08+2.75%,43+3.01%. All requested lists installed; producer-end beforeFULL~99.7%, yet delivery/late-accounting/observer/cache/discard costs remain. Park fixedvariant; strongest distinct recommendation whole-FULL epoch transport, no rescue/PGO/qualification/adoption or automaticlane. [Results and limits](../experiments/multicore-feasibility/epoch-inventory-four/report.md).

Whole-FULL one-helper epoch transport: onlyevaluator_worker.rs changes inpositive64, wholekernel/API/63otherfiles exact, noobserver.29focused+13CLI+2fallback and60replay/700posts+5idle pass composedaudit. New2 median sum7.846632s vsold2 8.057632s (−2.62%,0.97382xCPU), rangesseparatedall3; retained3 7.669302s remains2.31% faster at1.466xnew2 CPU. One lazy-import idlewrapper failure beforeinput preserved (supervisor−9, nativeexitreceiptmissing); only5unstartedprobes completed, clocks/original60bytes unchanged. Retain2alongside3; recommend unchanged-source jointPGO/full54, no tuning/adoption/qualification. [Results and exact repair](../experiments/multicore-feasibility/whole-full-epoch/report.md).

Whole-FULL unchanged-source own-PGO/full54:29controls reused;162joint123 training/one canonical merge+bitidentical independentremerge,13CLI+2fallback and324replay/3744posts+6idle pass firstattempt. New2 64.004516s vsprior67d2 64.208272s (−0.3173%,0.99687xCPU;41/54lower), prior3 60.721374s vsnew3 60.846776s (+0.2065%); new1 68.802407s vs5cf 68.293755s (+0.7448%). New2 is5.41% slower/29.71% lessCPU thanretained3; generic2.62% gain doesnotcarryatthatmagnitude. Preserveprior67d primary3 andnewa8dd measured2 option; no retune/repeat/qualification/adoption. [Full54/results/bindings](../experiments/multicore-feasibility/whole-full-own-pgo/report.md).

Observer-free matching colors3/inventory4 from frozen inventory65: remove clocks/histograms/counts and late owner accounting, preserve protocol/demand.40focused+15CLI+2fallback and fixed48/560posts+4idle pass; initial owner test confused epoch/count (101), plus pre-native hash rejection preserved; test-only repair, worker29 reused/originalclock. Retained3/old4/lean3/lean4 median sums7.688469/7.790463/8.222537/8.758407s: lean3+6.95% vsretained3; lean4+6.52% vslean3/+13.92% vsretained3/+12.42% vsold4,1.420xCPU vslean3. Allthreecase ranges separate negatively; complete layout/code change is priced, no atomic-only cause. Park fixedvariant, preserve67d/948747; no rescue/PGO/adoption. [Results/bindings](../experiments/multicore-feasibility/observer-free-inventory/report.md).

Observer-free existing-image layout review (source/binutils only): old/lean Arc allocation15584→1720B, requested alignment16→8, color outputs56→32B and major field reordering. Request/done spacing and wake/stop/latch cluster retain internal geometry; heap base phase/traffic unknown, no unique common3 cache cause. Recommend one unselected old-concrete-layout/no-observation counterfactual with verified offsets; no padding sweep/build/run performed. [Concrete offsets and limits](research/observer-free-layout-review.md).

Old concrete inventory layout with observations disabled: compiled15584B/align16 and all hot offsets match36c; lean marker/callers unchanged.40focused+15CLI+2fallback and fixed72/840posts+6idle pass; one pre-data manual register-token correction preserved, no source/data repeat/reset. Retained3/observed3/observed4/lean3/fixed3/fixed4 medians7.716113/7.856971/7.799535/8.243957/7.817264/7.721670s. Fixed3−5.18% vslean3/−0.51% vsobserved3/+1.31% vsretained3; fixed4−1.22% vssibling3/+0.072% vsretained3 at1.334xCPU,35/08 win but43 cancels. Representation materially matters; no cache attribution or net4 win. Preserve fixedcounterfactual/67d; no further layout/PGO/adoption. [Evidence](../experiments/multicore-feasibility/fixed-layout-no-observations/report.md).

Untried fresh coherent Influence/color fusion design: actual private scratch-None FULL only, two original color helpers build native rows then copy complete maps into helper locals; owner installs canonical scratch and alone owns pawn/cache/composition/charges. Exact ordinary/root/Q seams and two-phase request/rowReady/done/close/SC-single-waiter argument documented. Recommend one later generic preserved3/matched-unfused3/fused3 discriminator; no second-dispatch credit, fourth worker, implementation, census or run. [Source design](research/fresh-influence-fusion-design.md).

Fresh coherent Influence fusion executed: shared native row producer, launch-owned canonical delivery and unchanged common FULL suffix.56focused+14CLI+2fallback and fixed36replay/420posts+3idle pass; one test-only missing-probe compile repair preserved under the original clock. Every fused life has matching nonzero cold row epochs. Preserved3/unfused3/fused3 median sums7.729813/7.695892/8.047858s: fused+4.57% vssibling/+4.11% vsretained, allthreecases lose with separated ranges; CPU1.04572x sibling. Changed sampled phase boundaries include row/barrier/map work; no isolated cache/copy cause. Park unchanged, preserve67d; no PGO/tuning/adoption/qualification. [Results/bindings](../experiments/multicore-feasibility/fresh-influence-fusion/README.md).

Expanded post-fusion architecture review (source-only, all untried): recommend one-epoch type-disjoint Activity raw-score/pressure reduction as a genuine third demanded arithmetic shard; retain exact per-piece/final rounds and R with one owner join. Compare scoped borrowed inputs (copy removal without extra width; every error must drain per borrow) and replicated control/collective FULL (no input publication, duplicated TT/control/Influence/finish). Two independent Sol readers; no engine changes, new census/build/run. [Designs, semantic boundaries and decisive prototypes](research/post-fusion-execution-architectures.md).

Type-disjoint raw Activity4 executed: one immutable input, fixed whole-color/kind masks[3,8]/[8,3]/[4,4], scalar raw score/pressure/R reduction and one final round/clamp; no peer barrier or hot raw census.49 focused+15 CLI+2 fallback and48 replay/560 posts+4 idle pass first attempt. Preserved3/new1/new3/raw4 median sums7.741570/8.377214/7.773228/9.097050s: raw4+17.03% vs matched3 (+11.78%/+25.60%/+21.88% by case, ranges separated),1.56024x CPU; new3 drift+0.409%. All three actual request/done/role witnesses pass; no repair/repeat/reset. Park unchanged, preserve67d; no tuning/PGO/adoption/qualification. [Complete results/bindings](../experiments/multicore-feasibility/type-disjoint-four/README.md).

Replicated deterministic control executed: three private actual Search/TT/learning lanes, owner-only PawnCache, one scalar allgather and local original finishing; two-slot ready>=g, one prospective aligned layout (704B Shared).29 focused+two matched whole-lib/bin unwind builds+3 depth2 audits (61/59/121 exact FULLs) and60 depth8 lives pass first attempt; all20 structured outcomes/case equal. Preserved1/packet3/new1/packet3/replica3 median sums7.327634/6.440053/7.362684/6.490515/6.746727s. Replica+3.95% vs matchedpacket/+4.76% vs preservedpacket,35 separated loss;08/43 small median gains over matchedpacket overlap. RSS~51.8MiB vs~19MiB packet; CPU1.03940x matchedpacket/2.76026x preservedinline. No production replay/full54/>3 claim; no repair/repeat/reset. Park unchanged, no layout/PGO rescue. [Finite results/bindings](../experiments/multicore-feasibility/replicated-control/README.md).

- Scoped borrowed FULL inputs (parked):49 focused/14CLI/2fallback and36+3 original-protocol lives pass first attempt. Preserved3/scoped-owned3/scoped-borrowed3 summed search medians7.779674/7.914857/8.172098s; borrowing loses3.250% to matched owned and5.044% to preserved, all3 cases with separated matched ranges. No tuning/PGO/adoption. [Report](../experiments/multicore-feasibility/borrowed-full-input/README.md).

- Owner-local inventory (source-only, untried): ordinary-private row[p] generation after pawn/local work only if epoch3 color pair is not already complete; no third helper, publication or list transfer. Safe scratch/demand/null joins identified; tiny overlap, wasted cutoffs and readiness costs remain unpriced. [Recommendation](research/owner-local-inventory-overlap.md).

- Owner-local inventory (positive generic):47 focused/14CLI/2fallback and36+3 pass after one test-only compile repair on the same clock. Preserved/off/on3 search sums7.751493/7.759613/7.545679s; on gains2.757% vs matching off and2.655% vs preserved, all3 ranges below both. CPU falls; no extra helper/publication/census or automatic PGO/adoption. [Report](../experiments/multicore-feasibility/owner-local-inventory/README.md).

- Owner-local inventory own-PGO/full54 (positive):66source/47controls reused;216joint training + actual byte-identical remerge/use/14CLI2fallback/270+5 pass. Wallserial/retained3/new1/off3/on3=68.282114/61.047211/68.838654/61.587882/60.049404s; on gains2.4980% vs off (52/54) and1.6345% vs retained (44/54), CPU falls. New1 costs0.8151%; off/retained0.8857%. Extra metadata closer tuple adapter repaired separately; no native repeat/source change. Retain3d914c research leader,67d/serial preserved; no qualification/adoption. [Full54/report](../experiments/multicore-feasibility/owner-local-own-pgo/report.md).

- Unchecked-Q owner-local tactical preparation (source-only, untried): actual sparse/refresh FULL can use the existing pending-pair hook and private row; direct tactical capacity independently bounded417<512 on all coherent joined setups. Historical Q-FULL generation demand57.85/73.45/63.59% suggests more discard risk than ordinary; no G/slack cost measured. Recommend one matched generic Qoff/Qon discriminator if selected, preserve3d leader; no implementation/census/run. [Assessment](research/q-owner-local-tactical-overlap.md).

- Q owner-local (positive generic):17 affected/42 prior reused,14CLI2fallback and36+3 pass firstattempt. Preserved ordinaryon/Qoff/Qon search median sums7.624830/7.664552/7.537385s; Qon gains1.6592% vs off and1.1468% vs preserved, chiefly43;08 ranges overlap. CPU falls; common drift0.5210%, no newcensus/runtimeprobe/PGO. Preserve3d leader pending separate selection. [Report](../experiments/multicore-feasibility/q-owner-local/README.md).

- Q owner-local own-PGO/full54: unchanged68/17+42 reused;216 training/actual remerge/use/14CLI2fallback/270+5 pass. Search sums serial/retained3/new1/Qoff/Qon=68.811008/60.327621/69.548826/60.450227/59.918858s; Qon/off-0.8790%, Qon/retained-0.6776% (41/54 faster). Inline/serial+1.0722%; tuple API correct before freeze. Retain exact f8b829a7/profile bbb858b0 as the new research performance leader, preserving ordinary-only 3d914c, 67d and accepted serial. No qualification, canonical adoption or external action follows. [Report](../experiments/multicore-feasibility/q-owner-local-own-pgo/report.md).

- Completion notification two-fence (parked): publisherSCfence/load plus explicitSCfence afterEVERY coldregistration, no publisherclear;25worker/14CLI2fallback/lowering/48replay560posts+4idle passfirstattempt. Old1/old3/new1/new3 summedmedians8.375731/7.490874/8.344496/7.470674s: new3−0.2697%,smallerthaninline−0.3729%,all3mode3rangesoverlap. Publisher xchg→mfence+load; declarationsexact,fullcompiledtypegeometryunknown. No notification/cachecause,retune/PGO/adoption; f8/bbbpreserved. [Report](../experiments/multicore-feasibility/completion-fence/report.md).

- Writer-region transport layout (source-only, untried): recommend one eight-region64B-hypothesis counterfactual on retained Q68/original RMW protocol, with per-helper output+done together, request/latch/lifecycle/Control isolated. Saved generic assembly shows current done/output/header adjacency; Packet/request already separate, so no new benefit claimed there. Estimated extraallocation~256B, actual geometry needs one cold production-type/instance projection before any timing. No engine edit/build/run; no padding sweep/PGO/adoption. [Recommendation and costs](research/writer-owned-transport-layout.md).

- Fixed writer regions (tentative positive generic): Q68/original RMW,25worker/14CLI2fallback/cold actual-layout/48replay560posts+4idle pass firstattempt. Old1/old3/new1/new3 summedmedians8.349792/7.499557/8.386512/7.449741s: new3−0.6643%,all3rangesoverlap; inline+0.4398%. Actual Shared7168B/align64/phase0, output56+done8 in64-byte slots; allocator extent remainsestimated.26 normalized operational bodies exact. Preserve f8/bbb pending separatelyselected PGO; no retune/adoption/cache attribution. [Report](../experiments/multicore-feasibility/writer-regions/report.md).

- Writer-region own-PGO/full54: unchanged68/25+35 controls reused;216 training+actual remerge/use/14CLI2fallback/cold layout/270+5 pass. Wallserial/f8inline/f8mode3/newinline/newmode3=68.279043/69.467164/59.909994/69.115223/59.317384s; new3/old3-0.9892% (48/54lower), new1/old1-0.5066%. Retain a4ec/6c as research leader, preservef8; no adoption/qualification/nextlane. [Report](../experiments/multicore-feasibility/writer-regions-own-pgo/report.md).

- Endgame geometry overlap (source-only, untried): park universal/two-side preparation. One side-tagged rook-against-pawns boolean could run after winning inventory only while helpers remain pending; actual post-blend side/arm and floor division stay native. Private totality and public short circuits checked; qualifying demand/slack and factoring cost remain unpriced. No implementation/census/run selected; stop after this recommendation under Toby's pause. [Assessment](research/endgame-geometry-overlap.md).

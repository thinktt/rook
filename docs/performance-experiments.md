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

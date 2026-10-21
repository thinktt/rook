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

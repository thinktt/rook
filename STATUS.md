# Current implementation status

**Active research, 2026-10-26:** pursue useful deterministic multicore acceleration
under the expanded [mission](docs/deterministic-multicore-mission.md), without making
branch queues primary. The owner authorized a fresh goal explicitly allowing major
redesigns, replacement subsystems and isolated greenfield implementations. Preserve
King behavior and retained baselines; the current architecture is not a constraint.
No further adoption, release or external gate has been selected.
The [lead synthesis](docs/research/open-multicore-progress.md) connects the current
results, architectural lessons and next decision.

The latest [wide internal-branch trial](experiments/multicore-feasibility/wide-internal/report.md)
exercised actual 1/2/4/8-thread configurations on a hindsight-selected substantial
branch group; effectful replay lost despite useful descendant reuse. The
[pure-result census](experiments/multicore-feasibility/coarse-pure-salvage/report.md)
found limited new kernel work under an all-results-ready assumption; current
catalog construction costs exceeded that opportunity. Neither result establishes
a general limit on multicore designs. Their exact scopes and failures remain
in the reports.

The [three-thread color split](experiments/multicore-feasibility/colors-three/report.md)
lost 4.58% in summed search-wall medians against its sibling two-thread mode on
35/08/43, with all 48 replay lives passing. The coordinator usually reached the
join before the helpers; this does not establish a coordinator saturation limit.
The subsequent [fixed transport discriminator](experiments/multicore-feasibility/epoch-colors/report.md)
kept that arithmetic and replaced serialized reader copies/result publication with
immutable epoch input and independent outputs. It improved the three-case median
sum by 7.57% against old colors3 and 3.67% against sibling current2, at 1.445x
current2 whole-process CPU. All 48 replay lives and 32 focused checks passed;
35/43 timing ranges separated, while 08 overlapped. This is generic, finite
evidence, not qualification or a full54 prediction.

The [own-PGO/full54 comparison](experiments/multicore-feasibility/epoch-own-pgo/report.md)
is closed at `fb243a4c`: 162 joint-mode training lives and 270 comparison lives pass,
with one merge/use build and no failure or retry. Direct search-wall sums:

| Configuration | Seconds | Whole-process CPU seconds |
|---|---:|---:|
| Accepted serial (`5cf`) | 67.973988 | 68.059510 |
| Preserved practical two-thread (`8f`) | 64.092876 | 128.229345 |
| New inline, one thread | 68.076222 | 68.161880 |
| New current split, two threads | 64.147690 | 128.339177 |
| New epoch split, three threads | 60.763786 | 182.297940 |

Epoch3 improves 48/54 cases versus practical2, with a 5.19% total elapsed gain at
1.422x CPU; it improves 45/54 versus serial, with a 10.61% total gain. Case43 still
loses 4.56% versus serial. These are single observations per case/configuration,
not medians or qualification. New inline1 costs a descriptive 0.15% versus serial.
The exact `67d01108` image/profile/source are retained in the experiment; canonical
branch source and accepted release bytes are unchanged. Broad exact-image
qualification/adoption are not yet selected.

The [conditional fourth-worker trial](experiments/multicore-feasibility/epoch-inventory-four/report.md)
is parked at `7074456e`: its three-case median sum was 0.81% slower than preserved3
at 1.344x CPU, despite a 0.52% gain against its own slower mode3. All 50 focused
controls and 60 replay lives passed. Sparse participation, used-list installation
and activation-local state across null descendants worked, but complete delivery
costs erased the net gain. Sampled producer timing and observation overhead do
not establish a lower bound for every simpler or earlier delivery design.

The [whole-FULL one-helper epoch trial](experiments/multicore-feasibility/whole-full-epoch/report.md)
improves the three-case mode2 median sum from 8.057632s to 7.846632s (2.62%),
with lower total CPU and separated observed ranges in all three cases. Retained3
remains faster at 7.669302s; new2 uses 0.682x its CPU. Only the worker transport
changed, with 29 focused controls and all 60 replay lives passing. A missing idle
adapter export was repaired after benchmark collection; five unstarted idle probes
and the composed audit pass, with completed runs and original clocks preserved.

The [whole-FULL own-PGO/full54 comparison](experiments/multicore-feasibility/whole-full-own-pgo/report.md)
passes 162 training and 324 comparison lives with no failure or retry. Its gain is
much smaller: new2 64.004516s versus prior67d2 64.208272s (0.317% lower, 41/54 lower
cases). New3 60.846776s versus prior67d3 60.721374s is 0.207% higher; new1 68.802407s
versus accepted serial 68.293755s is 0.745% higher. These single observations do
not establish repeatability, parity or a source-level cause for small differences.
Retained67d remains the strongest complete54 candidate; no whole-helper retune,
replacement or qualification is selected.

The [observer-free inventory trial](experiments/multicore-feasibility/observer-free-inventory/report.md)
is also parked: three-case sums were preserved3 7.688469s, observed4 7.790463s,
lean3 8.222537s and lean4 8.758407s. Both lean modes regress, and lean4 loses to
matching lean3. All 48 replay lives/560 posts and four idle probes pass; 40 selected
controls pass after one fixture epoch/count correction, with the original failure
and a pre-native hash rejection preserved. No production repair or benchmark repeat.

The [existing-image layout review](docs/research/observer-free-layout-review.md)
at `40322440` identifies changed allocation size/alignment and output packing, but
no unique cause. Request/done spacing remains compact and the proposed per-FULL
Flight/waiting same-line explanation is excluded. Heap-base alignment and actual
coherence traffic are unknown.

The [fixed-layout counterfactual](experiments/multicore-feasibility/fixed-layout-no-observations/report.md)
is closed at `a964ca65`: compiled old layout matched before data, and all 72 replay
lives/840 posts plus six idle probes pass. Fixed3 recovered most of lean3's loss
(7.817264s versus 8.243957s), but retained3 was 7.716113s. Fixed4 beat matching3 by
1.223% at 7.721670s, remaining 0.072% above retained3 at 1.334x CPU. This demonstrates
representation sensitivity without establishing a cache cause or a net four-thread
win. No further inventory/layout variant or PGO is selected.

The [fresh-Influence trial](experiments/multicore-feasibility/fresh-influence-fusion/README.md)
is parked at `08a5fd91`: fused3 records8.047858s versus matching unfused3 7.695892s
and retained3 7.729813s. It loses4.5734% to matching unfused, with separated ranges
in all three cases. All56 focused controls,36 replay lives/420 posts and3 idle
probes pass; matching nonzero row epochs establish activation. The test-only
compile repair is preserved. This measures the complete changed design, not an
isolated barrier or copying cost. No PGO or rescue variant is selected.

Next selected work is source-only architectural reassessment: distinguish
specification-required ordering from inherited boundaries, then choose a concrete
new overlap mechanism and a decisive prototype. Imp2 and its Sol team examine
alternative designs; the lead independently examines execution models, with one
selective Astra challenge of replicated control and collective evaluation. No new
native lane, adoption or external work is selected; all positive artifacts remain
preserved.

**Research branch update, 2026-10-24:** the practical opt-in two-thread FULL
split is retained for an adoption decision after passing the selected local
behavioral checks. The [lead research outcome](docs/research/deterministic-multicore-outcome.md)
records the 6.79% elapsed gain, CPU/serial costs, unsuccessful approaches and
remaining external qualification and scaling limits. Default execution remains
one thread; this does not promote the new image to the accepted release. The
serial checkpoint below retains its historical scope.

**Current local candidate: first-main corrected build.** Updated2026-10-20. Retained62 is preserved as the initial comparison control. This is local adoption for continuing qualification; no qualified release or external action is implied.

The [working agreement](docs/leadership-working-agreement-last-mile.md) assigns strategy/architecture to imp2-lead and implementation/execution to Imp2. The optimization batch is closed. The tested first-main correction, full mandatory completion, fresh own-PGO/full54 comparison and exact-image behavioral lane are now complete. No engine/build/profile job is active. The lead owns the [review map](docs/reviews/retained62-owner-review.md), [strategy](docs/last-mile-strategy.md) and qualification dispositions; their historical62 headings retain their documented scopes until updated.

The [adoption record](experiments/first-main-cutoff-adoption/source-promotion.json) verifies the exact three source changes: `src/ordinary.rs`, `src/remembered.rs` and new `src/ordinary/first_main_tests.rs`. The release delta is the reviewed first-main cutoff guard after existing updates. The other additions are test-only. Canonical mapped source equals the tested118-file snapshot; all52 native build inputs match its own fresh training. The separate canonical archival utility remains preserved. No canonical-path rebuild was performed.

| Current paired54 observation on Vic | Summed case medians, native CPU s |
|---|---:|
| First-main corrected image `5cf01208…` | **68.569086** |
| Exact retained62 control `01237e6d…` | **68.446861** |

Ratio1.001785692: descriptive+0.178569%,13/54 lower case medians, worst ratio1.011773436. The [full54 report](experiments/first-main-cutoff-production/README.md) retains three measured samples per image/case plus excluded warmups, all432 lifetimes,4,992 posts and864 offline checks. This compares two exact production images with their own profiles; it is neither an optimization gain nor a confidence/parity determination.

Corrected-build evidence:

- [Conditional source discriminator](experiments/first-main-cutoff-correction/README.md): three actual-owner regressions; old logic fails the equality regression and passes both controls. Corrected source passes196 library tests. These supplied TT/window contexts are not admitted public/native equality witnesses.
- [Mandatory union](experiments/first-main-cutoff-correction/mandatory-completion/README.md):115 complete mandatory files/7,673 unique cases/117 operations,209 diagnostic and2 development tests. Exact corrected DIAG is `68a1c304…`. All supervised exec/wait/raw chains pass;7671/7673 post-exec point observations exist, with two unavailable short-child observations explicitly retained.
- [Own-PGO production](experiments/first-main-cutoff-production/README.md): each original54 trained once, native PID/profile association, independent byte-identical remerge, one profiled-only ExtTSP use build and complete paired54 comparison. Both launcher-only setup failures/repairs remain preserved; no failed native request was retried.
- [Fresh exact-image behavioral lane](experiments/first-main-cutoff-gameplay/README.md):12 games/632 searches/5,801 posts; continuity4 segments/8 searches; standard seed11 children; persistence3; wire8 fixtures/24 searches. All33 lifetimes,99 raw streams/791,104 bytes and native identities reconcile. The unchanged original combiner yields `completeFocusedReplay:true`, `completeGameplayQualification:false`. No full12 timing claim is made.

Latest closed optimization work:

- The [three-unit functional study](experiments/functional-cost-three-unit/report.md) matches the released projections; observer/setup/build/host differences prevent a production-component cost partition.
- [Pressure-presence](experiments/pressure-presence-compiler/README.md), [checked-slider](experiments/checked-enumeration-compiler/README.md) and [compact48 TT](experiments/compact48-tt/README.md) trials are parked after their selected screens. None replaced62; no rescue variant or further native work is selected.
- The [TT census](experiments/current62-tt-census/README.md) is count-only evidence. Earlier63–67 trials, generation-safety and branch/cache studies retain their original dispositions in the [catalog](docs/performance-experiments.md) and historical reports; the branch/cache footer discrepancy remains a strict failure.

Remaining obligations:

- Specification-owner production acceptance and the lead's Q1 second-half inherited-hint composition disposition remain open. The first-main rule is locally corrected and conditionally tested; finite success does not prove all admitted inputs. Reuse the existing source lemmas and current owner-review map without reopening a general proof campaign.
- External3,288-game qualification remains off Vic. The new [local handoff](experiments/first-main-cutoff-adoption/manifest.json) binds the corrected artifacts and leaves unavailable runner/corpus/oracle/schedule/checker/operator/host/receipt fields null. This creates no transfer, READY or execution authority.
- Compatible full54/full12 performance qualification still needs fixed comparison/resource conditions, repeatability/uncertainty and private-memory/no-swap policy. The corrected image has no qualified full12 timing; PMU remains unavailable on Vic. Cross-host/history ratios are descriptive.

Retained62 historical checkpoint: whole54 **67.640360 CPU s** and whole12 **675.156653 CPU s** belong to retained62's earlier collection windows. They are preserved in the [old handoff](experiments/retained62-game-handoff/README.md), [source promotion](/home/legolas/rook2-experiments/original-worktree/evidence/exttsp-profiled-integration-20261020-01/source-promotion.json) and frozen reports. They are not corrected-image timings or replacements for the new paired control. The old images/profile/source archives and comparison payload remain unchanged.

The preceding comprehensive status remains in [STATUS-history-20261020.md](STATUS-history-20261020.md). Closed reports retain their original claims and paths. Raw records are outside Git under `/home/legolas/rook2-experiments`; use the [evidence guide](docs/evidence-layout.md) for older relocated paths. Before-map validations describe their historical interval; verify retained62 source through the preserved old Git commit after this adoption.

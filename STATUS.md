# Current implementation status

**Active research, 2026-10-26:** pursue useful deterministic multicore acceleration
under the restored [mission](docs/deterministic-multicore-mission.md), without making
branch queues primary. The owner authorized a new open-ended goal after clearing
the earlier goal. The two-thread result below remains the successful baseline.
No further adoption, release or external gate has been selected.

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
One transport discriminator is now selected: keep the same side arithmetic while
replacing serialized packet copies and result publication with an immutable epoch
input and independently owned outputs. Ownership, scope-close and cold-wakeup
proofs precede implementation. No new transport timing exists yet.

The [next-work comparison](docs/research/after-colors-dataflow-choice.md) identifies
whole-FULL plus ordinary inventory as the leading separate reserve; fresh-Influence
pipeline fusion and frontier batching also remain unselected. The current trial
tests transport at a fixed arithmetic partition, not those larger work graphs.

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

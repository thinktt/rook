# Deterministic multicore research handoff

2026-10-29. Toby has tabled this experiment. Research is **paused, not complete**.
This closeout authorizes documentation/worktree cleanup only. No new build,
measurement, implementation, qualification, promotion or external delivery is
selected. Resume research only on explicit new Toby direction.

## Start here

1. Read this handoff, [mission](../deterministic-multicore-mission.md) and
   [AGENTS.md](../../AGENTS.md).
2. Read the [winning exact-image report](../../experiments/multicore-feasibility/single-owner-own-pgo/report.md).
3. Read the [lead's chronological synthesis](open-multicore-progress.md) and
   [last architectural recommendation](retained-owner-critical-path.md).
4. Use the complete experiment index below, the
   [performance catalog](../performance-experiments.md), and individual reports
   for tests, failures, scope and exact source/build/raw bindings.

The research checkout is `/home/legolas/rook2-multicore`, branch
`research/deterministic-multicore`. The accepted serial checkout is
`/home/legolas/rook2`, main at `a3de19d04936190832ac22a36cae6089eb9f3c13` at closeout.
Accepted Rook version1 and separately owned Imp3 release work are unchanged.
The final research decision before cleanup is commit
`d62c8feab7df450a4c4d3590bb2e3c90ab7e2eb7`; no implementation followed it.

**Do not assume `src/` is the fastest research engine.** Canonical research source
preserves the practical two-thread checkpoint. The three-thread leader is an
isolated, hash-bound source/image/profile, described below. A generic build from
this checkout does not reproduce that leader. Research success is not adoption.

## Retained best result and exact artifacts

The same-window full54 comparison has one observation per case/configuration:

| Configuration | Search wall seconds | Joined native CPU seconds |
|---|---:|---:|
| Accepted serial `5cf01208` |69.640657|69.723556|
| Previous three-thread `a4ecf096` |58.934958|176.819294|
| Latest candidate, one thread |70.539314|70.630608|
| Latest candidate, three threads |**58.692377**|**176.093198**|

Latest mode3 saves15.7211% elapsed time versus serial, wins54/54 cases and uses
2.5256x CPU. It saves0.4116% versus the previous mode3, with39/54 wins. Mode1 is
1.2904% slower than accepted serial. These are descriptive single observations,
not medians, confidence intervals or performance qualification. Search wall is
go-write through move receipt; joined CPU includes all native threads and native
lifetime overhead. Helpers spin during active searches and park between searches;
CPU includes polling, not just useful arithmetic. Idle probes saw0ticks/250ms at
100Hz, a resolution limit. No useful scaling beyond three threads was demonstrated.

Historical KingWCR on Bee:64.140 CPU /65.336 wall seconds, sums of54 case medians.
Different host/window/endpoints prevent a matched victory claim. Approved source:
`/home/legolas/spec-issues/v2.5.0/2026-10-21-imp2-candidate68-benchmark-results/README.md`.

| Artifact | Location / identity |
|---|---|
| Winning source | `/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01` |
| Source map | [preparation.json](../../experiments/multicore-feasibility/single-owner-own-pgo/preparation.json), `candidateSource`,69 files |
| Ordinary binary | `/home/legolas/rook2-experiments/single-owner-own-pgo-20261028-01/rook2-pgo`,7,902,552 bytes |
| Binary SHA256 | `c242f0e498ceeddb9aa2532cbace46730ffebcb6a0e756274179b3297c1b40da` |
| Own profile | `/home/legolas/rook2-experiments/single-owner-own-pgo-20261028-01/training/merged.profdata`,127,648 bytes |
| Profile SHA256 | `1a81bdacaeee3ac4b949cb495f8a99f0d68c96579cca4e7b807f83a501169910` |
| Generic control | `/home/legolas/rook2-experiments/single-owner-20261028-01/rook2-candidate`, SHA256 `d71c4f9fa662af73c81d891f16c2b56ded2d2ccfbe982ed5ae81829a14fd573d` |
| Winning evidence commit | `bf4bd2841a256907379acef1f0ccbb43ca66e2d5` |
| Source/generic closure | `19a1c1b83f6875064afc0b1677cb0c3e6d5bf303` |
| PGO setup | `2dee84db5c0f35af6dd75276ecf927c31b05a4af` |

The measured winning flags are `--threads=3 --owner-local-inventory
--q-owner-local-inventory --work-clock=kingwcr --work-clock-post=work`.
Actual measurement placement was coordinator14/helpers6,4, established by the
supervisor before input; flags alone do not reproduce placement or host conditions.
Keep requested thread budget/configuration order and affinity fallback semantics.

The [plan](../../experiments/multicore-feasibility/single-owner-own-pgo/plan.md),
preparation, tools and external raw receipts specify the recipe: Rust1.85.1,
LLVM19.1.7, generic x86-64, opt3/ThinLTO/one CGU/debug1/panic-abort, joint216-case
training across four configurations, one canonical merge and independently
byte-identical remerge, own-profile use and use-only ExtTSP. Never overwrite or
rerun a closed output directory. After a future authorization, restore/copy into
a fresh workspace, verify all source pins and adapt the recorded recipe with new
output identities; do not silently reuse an unrelated/stale profile.

## What succeeded

- **FULL split and lifecycle:** isolated pure Activity/Shelter work from ordered
  search/PawnCache/evaluation updates. Practical two-thread configuration gained
  about6.8% in its own full54 window. Parking, predicate waits and affinity-aware
  fallback made it usable. Exact two-thread local qualification is separately
  recorded; it does not qualify later three-thread bytes.
- **Three-thread color split with epoch transport:** two helpers calculate
  own-color Activity and opposite-color Shelter while the coordinator performs
  pawn/local terms. Immutable publication and separate outputs made this
  profitable; the initial lock-heavy color split was slower.
- **Coordinator work during helper latency:** readiness-conditional ordinary and
  unchecked-Q inventory preparation uses private per-ply rows, preserves native
  demand charges/order and survives null descendants correctly. This improved
  integrated PGO search without a fourth worker.
- **Writer-owned layout and single-owner activation:** isolate writer regions and
  move coordinator-only flight/metadata into owned state. A restricted activation
  facade supports removal of normal Control-lock arbitration while real cold
  parking, failure, retirement and SC wake rules remain. These produced smaller
  subsequent gains. Do not add gains from different windows as percentages.

Core correctness boundaries remain: supplied-map authority; coherent ancestry;
actual demand before logical charges; original score/pressure/R rounding; ordered
PawnCache/TT/learning changes; reader borrows ended before reuse; true parked or
joined retirement on cancellation; terminal state dominates saved nesting depth.
See [activation design](single-owner-activation-design.md),
[ordinary overlap](owner-local-inventory-overlap.md),
[Q overlap](q-owner-local-tactical-overlap.md) and [layout](writer-owned-transport-layout.md).

## What we tried and parked

| Family | Main finding |
|---|---|
| Whole-branch transactions, hierarchical recovery, consumed-prefix validation | Earlier siblings change windows, ordering and state. Some descendants validate, but mostly small segments; recovery/certification costs exceed removed work. |
| Q and ordinary width census; actual internal1/2/4/8 splits | Q tasks are generally tiny. Ordinary width exists, but early selectors missed or found little demanded work. A later wide fixture had substantial demanded siblings and still lost with workers. No universal impossibility claim. |
| Depth2/first6 child preparation; coarse pure salvage | Real pure reuse exists, but unused work, delivery or catalogue costs overwhelm measured benefit. |
| Reversed FULL, same-node inventory helper, fourth inventory worker | Correct bounded behavior did not yield a net gain over the retained alternative. Owner-local generation subsequently succeeded with a different delivery boundary. |
| Raw type-disjoint four-way arithmetic, replicated control, borrowed inputs | Distinct architectures tested, all slower than their relevant retained/matched controls. Replica trial had fixed-completion NoHost limits. |
| Observer deletion and fixed-layout counterfactual | Removing counters changed layout enough to regress performance; restoring layout recovered much of it. No isolated cache cause or net fourth-thread win established. |
| Fresh Influence fusion and pre-map geometry | Parallel work exists, but barriers/materialization/copies and changed inventory overlap erase gains. |
| Completion fences, per-reader flags, strong done-epoch publication | Required wake/retirement proofs and focused checks passed; no distinguished net gain justified PGO. Keep original leader protocol. |
| Earlier-iteration frontier | Initial128-lifetime-job plan was analytically parked as too small. Aggregate/full-cohort observations then tested actual6-to7 scale; result below. |

Latest frontier closure `84da8b71c42558d66375eb9cef696034d839f5a8`: original35 has
7963 qualifying parent activations and227806 skipped-edge occurrences in6;
iteration7 has319911 fresh-map and244603 private-FULL demands. The full cohort
contains207501 map/207518 chain keys, with25384/11431 first-new7 productions.
Its generous disjoint map+FULL-prefix ceiling is14.417026ms, including owner work
a chain hit cannot remove. Sample-scaled collection/query costs of the observed
representation are74.485/132.394ms. They are estimates with clock/aliasing limits,
not lower bounds on every design. No producer, ready-time model or consumer ran.
Park this policy; do not infer that all earlier preparation is impossible.

Preserve failed attempts as part of the evidence. Notable examples include test-
only compile/fixture repairs, pre-input wrapper failures, capped historical branch
certificates, failed early census reservations, and the final frontier coordinator
RSS-wrapper failure followed by the same frozen auditor passing in a fresh child.
Their reports distinguish setup repairs from native failures and prohibit claims
that a repaired pipeline was entirely first-attempt successful.

## Last decision and work not yet selected

[Retained-owner critical path](retained-owner-critical-path.md), commitd62c8fea,
recommends attribution before another redesign. Two conditional possibilities:

1. Calculate certain-demand move-priority batches; original partition/reversal
   and gap6/1 permutation remain ordered. An enclosing sort time is not all
   offloadable priority arithmetic.
2. A reversible-position executor with per-ply undo. Required predecessor
   observations, chronology restoration, stop/error exits and actual compiled
   copies must be accounted for. A source-level160B assignment is not proof of
   removable machine work. Prior small undo tests did not establish an integrated win.

Neither is implemented or selected. Exact-c242 owner profiling is preferred only
if a valid sampler can be admitted. Installed gprofng has retained independent
busy-control failures (timer1000→0, no meaningful samples); retrying the old route
is not validation. Its old wrapper also pins everything to14. `perf` was absent
from PATH and `perf_event_paranoid` was3 at the metadata check. No event-open probe,
installation, host setting change or new profiling run was made.

Fallback recommendation: a small, explicitly different diagnostic derivative
sampling nonrecursive map, scoring/partition/permutation, actual child transition
and TT scopes. It could identify a large pool, but cannot claim exact-c242 time
percentages. No fallback source, build or run was selected before the pause.

## Qualification, authority and restart obligations

The leader has70 unique focused controls (71 historical executions including a
preserved fixture failure),216 training replays,270 comparisons/3120 posts and
five idle probes, plus CLI/affinity/layout checks. Finite replay success is not
full mandatory/gameplay qualification. The practical two-thread qualification
and accepted serial external3288-game report belong to their exact artifacts.

Remaining work, only after explicit resume: choose the next research direction
or consolidate the best candidate; deliberately integrate/reproduce the selected
source; qualify the exact resulting image; measure repeatability/serial costs;
make an adoption/delivery decision. No automatic merge, external transfer, READY
publication or cleanroom-gate execution is authorized by this handoff.

Research goal is paused. Team agents/jobs were confirmed stopped at the manager's
2026-10-29T05:21:15.493955Z50% notice, and Toby subsequently tabled the experiment.
The user has authorized cleanup only. Do not infer a resume from quota reset,
agent startup, this document, or old experiment scripts. Lead owns architecture;
Imp2 owns delegated implementation/tools; Imp3 is separately owned. Follow live
Herdr identities rather than historical pane IDs. Preserve clean-room boundaries:
released king-spec and approved handoffs only; no Imp1 private source/architecture.

## Evidence and worktree cleanup

Repository reports/patches/tools are committed. Bulk binaries, profiles, snapshots
and raw receipts remain under `/home/legolas/rook2-experiments`; see
[evidence layout](../evidence-layout.md). The repository alone is not a complete
portable build/evidence closure. Archived absolute paths are intentionally retained.

Cleanup retires11 detached experimental Git worktree registrations. Ten have
experimental tracked/untracked changes, so their complete directories remain at
the same paths as plain frozen snapshots; deleting them would discard evidence.
All heads are ancestors of the research branch. Git pointers/admin/index/status/
patches and complete before-file manifests are backed up externally; after cleanup
every non-Git file, symlink and directory entry is verified unchanged. Only main
and this research checkout remain registered worktrees. No branch/history/source,
binary, profile, raw result or accepted release is deleted or rewritten.

See [cleanup receipt](../../experiments/multicore-feasibility/research-closeout/cleanup.json).
Full backup/verification is
`/home/legolas/rook2-experiments/research-closeout-20261029-01/`.
To restore an old experimental checkout after authorization, create a fresh Git
worktree at its recorded head, then overlay the preserved snapshot (including
untracked source) or the archived patch plus untracked files. Verify its original
source manifest. Do not blindly restore old Git administrative pointers or run
historical recipes against their closed output directories.

The previous long status is preserved verbatim in
[STATUS-history-20261029.md](../../STATUS-history-20261029.md). Earlier serial work
is indexed by [STATUS-history-20261020.md](../../STATUS-history-20261020.md),
[last-mile strategy](../last-mile-strategy.md), and the performance catalog.

## Complete multicore experiment index

The following index includes every experiment directory at this closeout, plus
the initial standalone probe. Each entry's report supplies its own outcome,
source/tool/raw bindings, validation and limits; historical recommendations are
not current execution authority.

- [Initial standalone kernel probe](../../experiments/multicore-feasibility/report.md)
- [beyond-two-census](../../experiments/multicore-feasibility/beyond-two-census/report.md)
- [borrowed-full-input](../../experiments/multicore-feasibility/borrowed-full-input/README.md)
- [branch-transactions](../../experiments/multicore-feasibility/branch-transactions/report.md)
- [child-preparation](../../experiments/multicore-feasibility/child-preparation/report.md)
- [coarse-pure-salvage](../../experiments/multicore-feasibility/coarse-pure-salvage/report.md)
- [colors-three](../../experiments/multicore-feasibility/colors-three/report.md)
- [completion-epoch](../../experiments/multicore-feasibility/completion-epoch/report.md)
- [completion-fence](../../experiments/multicore-feasibility/completion-fence/report.md)
- [configured-full](../../experiments/multicore-feasibility/configured-full/report.md)
- [configured-full-qualification](../../experiments/multicore-feasibility/configured-full-qualification/README.md)
- [consumed-prefix](../../experiments/multicore-feasibility/consumed-prefix/report.md)
- [epoch-colors](../../experiments/multicore-feasibility/epoch-colors/report.md)
- [epoch-inventory-four](../../experiments/multicore-feasibility/epoch-inventory-four/report.md)
- [epoch-own-pgo](../../experiments/multicore-feasibility/epoch-own-pgo/report.md)
- [fixed-layout-no-observations](../../experiments/multicore-feasibility/fixed-layout-no-observations/report.md)
- [fresh-influence-fusion](../../experiments/multicore-feasibility/fresh-influence-fusion/README.md)
- [frontier-cohort](../../experiments/multicore-feasibility/frontier-cohort/report.md)
- [frontier-scale-count](../../experiments/multicore-feasibility/frontier-scale-count/report.md)
- [full-split-production](../../experiments/multicore-feasibility/full-split-production/report.md)
- [hierarchical-recovery](../../experiments/multicore-feasibility/hierarchical-recovery/report.md)
- [integration](../../experiments/multicore-feasibility/integration/report.md)
- [internal-horizon](../../experiments/multicore-feasibility/internal-horizon/report.md)
- [internal-split](../../experiments/multicore-feasibility/internal-split/report.md)
- [inventory-overlap](../../experiments/multicore-feasibility/inventory-overlap/report.md)
- [observer-free-inventory](../../experiments/multicore-feasibility/observer-free-inventory/report.md)
- [owner-local-inventory](../../experiments/multicore-feasibility/owner-local-inventory/README.md)
- [owner-local-own-pgo](../../experiments/multicore-feasibility/owner-local-own-pgo/report.md)
- [per-reader-completion](../../experiments/multicore-feasibility/per-reader-completion/report.md)
- [pre-map-geometry](../../experiments/multicore-feasibility/pre-map-geometry/report.md)
- [q-owner-local](../../experiments/multicore-feasibility/q-owner-local/README.md)
- [q-owner-local-own-pgo](../../experiments/multicore-feasibility/q-owner-local-own-pgo/report.md)
- [replicated-control](../../experiments/multicore-feasibility/replicated-control/README.md)
- [reversed-full](../../experiments/multicore-feasibility/reversed-full/report.md)
- [same-node-inventory](../../experiments/multicore-feasibility/same-node-inventory/report.md)
- [single-owner-activation](../../experiments/multicore-feasibility/single-owner-activation/report.md)
- [single-owner-own-pgo](../../experiments/multicore-feasibility/single-owner-own-pgo/report.md)
- [type-disjoint-four](../../experiments/multicore-feasibility/type-disjoint-four/README.md)
- [usable-full](../../experiments/multicore-feasibility/usable-full/report.md)
- [whole-full-epoch](../../experiments/multicore-feasibility/whole-full-epoch/report.md)
- [whole-full-own-pgo](../../experiments/multicore-feasibility/whole-full-own-pgo/report.md)
- [wide-internal](../../experiments/multicore-feasibility/wide-internal/report.md)
- [writer-regions](../../experiments/multicore-feasibility/writer-regions/report.md)
- [writer-regions-own-pgo](../../experiments/multicore-feasibility/writer-regions-own-pgo/report.md)

## Source studies and design history

All retained research notes are indexed below; the chronological synthesis and experiment catalog connect these to implemented trials. Unimplemented hypotheses remain unselected.

- [after-colors-dataflow-choice](after-colors-dataflow-choice.md)
- [after-epoch-fourth-worker-choice](after-epoch-fourth-worker-choice.md)
- [after-prefix-scaling-recommendation](after-prefix-scaling-recommendation.md)
- [beyond-two-queue-recommendation](beyond-two-queue-recommendation.md)
- [beyond-two-transaction-conflicts](beyond-two-transaction-conflicts.md)
- [beyond-two-work-distribution-design](beyond-two-work-distribution-design.md)
- [branch-task-queue-feasibility](branch-task-queue-feasibility.md)
- [completion-epoch-publication](completion-epoch-publication.md)
- [depth-range-review](depth-range-review.md)
- [deterministic-multicore-outcome](deterministic-multicore-outcome.md)
- [earlier-current-node-influence](earlier-current-node-influence.md)
- [earlier-frontier-observation-design](earlier-frontier-observation-design.md)
- [earlier-frontier-scale-assessment](earlier-frontier-scale-assessment.md)
- [endgame-geometry-overlap](endgame-geometry-overlap.md)
- [evaluation-review](evaluation-review.md)
- [fresh-influence-fusion-design](fresh-influence-fusion-design.md)
- [hierarchical-recovery-prefix-assessment](hierarchical-recovery-prefix-assessment.md)
- [influence-design](influence-design.md)
- [live-protocol-next](live-protocol-next.md)
- [measurement-design](measurement-design.md)
- [multicore-dependencies](multicore-dependencies.md)
- [multicore-lead-review](multicore-lead-review.md)
- [multicore-production-assessment](multicore-production-assessment.md)
- [next-multicore-packet-recommendation](next-multicore-packet-recommendation.md)
- [observer-free-layout-review](observer-free-layout-review.md)
- [open-architecture-reassessment](open-architecture-reassessment.md)
- [open-multicore-progress](open-multicore-progress.md)
- [owner-local-inventory-overlap](owner-local-inventory-overlap.md)
- [per-reader-completion-registration](per-reader-completion-registration.md)
- [permission-sensitive-search-bounds](permission-sensitive-search-bounds.md)
- [position-design](position-design.md)
- [position-layout](position-layout.md)
- [post-fusion-execution-architectures](post-fusion-execution-architectures.md)
- [pre-map-activity-geometry](pre-map-activity-geometry.md)
- [production-score-capacity](production-score-capacity.md)
- [q-owner-local-tactical-overlap](q-owner-local-tactical-overlap.md)
- [q-window-reuse-hypothesis](q-window-reuse-hypothesis.md)
- [remaining-performance](remaining-performance.md)
- [retained-owner-critical-path](retained-owner-critical-path.md)
- [scalar-production-review](scalar-production-review.md)
- [search-capacity-proof](search-capacity-proof.md)
- [search-design](search-design.md)
- [single-owner-activation-design](single-owner-activation-design.md)
- [tt-layout-population-assessment](tt-layout-population-assessment.md)
- [uncertified-hint-completion](uncertified-hint-completion.md)
- [winning-full-integration-assessment](winning-full-integration-assessment.md)
- [writer-owned-transport-layout](writer-owned-transport-layout.md)

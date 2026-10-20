# Proposed same-host retained62 / KingRE comparison

**Prepared locally; external transfer, contact and execution await owner approval.**
This is a finite diagnostic baseline to establish the actual remaining gap.
It is not the final performance qualifier or the external3288-game gate.

Compare these two exact ordinary executables using the reference operator's
existing approved CPU-only collection path on the same physical core:

| Artifact | SHA256 |
|---|---|
| Retained Rook2 candidate62 | `01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d` |
| Approved generic-PGO KingRE | `bf71485c48e780e29f32813219e4283cc54c04015abce0bccda62c190e2ba080` |

The local payload is under
`/home/legolas/rook2-experiments/retained62-external-comparison-preparation-20261020-01/payload`.
It contains exact copies of retained62 and its diagnostic companion, without a
rebuild or stripping. The companion is supplied for artifact identification and
future authorized qualification; this comparison executes only ordinary images.
`manifest.json` beside the payload binds the copies, existing source/build
provenance and released workload/checker inputs. `schedule.json` freezes all
432 intended lifetimes. Neither file is an export/READY signal.

## Finite requested job

Use all original54 cases in stored order, unchanged settings, natural `rnd=0`
seed acquisition, and the two existing work-clock flags. For each case run one
excluded fresh warmup per artifact, then three measured fresh lifetimes per
artifact. Alternate reference/candidate order within each pair and flip the
initial order on each successive case. The schedule fixes all exclusions and
orders before any results. Totals:108 warmups,324 measured runs,432 lifetimes.
No extra smoke runs, PMU passes, retry or alternative artifact is included.

Each lifetime must pass the original complete replay assertions and have a
known normal native exit. Preserve raw streams, errors, every sample and the
independent offline replay checks. A failure stops subsequent launches; there
is no automatic replacement, cap increase or favorable subset.

Report whole-owned-lifetime CPU user/system/sum for both artifacts under the
same boundary, plus separately named wall/search observations when available.
The recorder must establish compatible ownership/accounting; it must not charge
the controller or silently omit engine-owned work. Reuse the operator's
approved single-core CPU-only collection arrangement. Before launch bind the
actual host, logical CPU and sibling, helper placement, collector/checker
identities, ownership mechanism and resource limits. Do not alter global
security, PMU or host-isolation settings.

Proposed upper bounds are960 seconds per lifetime,3600 seconds aggregate,
1GiB engine-owned memory with no swap,8MiB raw output per lifetime,512MiB total
raw artifacts and five seconds for whole-owned-tree cleanup. Preserve any
cutoff as an incomplete collection, not a performance sample. The operator
must confirm that its existing mechanism can enforce/account these bounds;
unavailable ownership, no-swap or memory scope must be reported before launch.
Normal observed runtimes should be much shorter; these are ceilings, not a
runtime forecast.

Return all numeric samples and exclusions, per-case min/median/max and
candidate/reference median ratios, their summed-median ratio, environmental
observations and all validity/correctness outcomes. Three repeats give a
descriptive same-host baseline, not a simultaneous confidence guarantee.
There is no performance pass/fail or followup decision from this job alone.
Do not automatically adopt the separate unapproved13/19-repetition proposal.

## Why now

The current Vic whole54 total67.640360s and historical reference63.431779s
come from different hardware/windows. Existing calibrator and candidate25
observations do not provide a universal conversion. A contemporary pair can
change the scale and priorities of the remaining engineering work. It also
preserves a useful control if a later optimization is promoted.

The exact62 source/build identities and finite validation are documented in
[production-build](../../docs/production-build.md) and
[qualification gaps](../../docs/qualification-gaps.md). This preparation adds
no behavioral execution or qualification claim. Local checked-slider work and
TT planning can continue independently while external authority is pending.

# Research status — paused, 2026-10-29

Toby has tabled deterministic multicore research. **No implementation, build,
measurement, qualification or delivery is currently selected.** The goal and team
remain on hold until explicit new Toby direction. Cleanup does not resume research.

Start with the [complete successor handoff](docs/research/multicore-handoff.md).
It records the winning artifacts, every multicore experiment, architectural
lessons, unresolved obligations and the exact point at which work stopped.

| Current fact | Evidence |
|---|---|
| Best retained research image | `c242f0e4`, own profile `1a81bdac`, isolated source69 |
| Full54 search wall | **58.692377s** versus accepted serial **69.640657s** in the same window |
| Tradeoffs |15.72% lower elapsed time;2.526x whole CPU; candidate mode1 costs1.29% versus serial |
| Fidelity scope | Focused checks and exact replays; latest three-thread image is not broadly qualified/adopted |
| Canonical research source | Practical two-thread checkpoint, **not** the isolated three-thread leader |
| Accepted main/release | Unchanged; separately owned release work is untouched |
| Last completed experiment | [Full frontier cohort](experiments/multicore-feasibility/frontier-cohort/report.md), parked |
| Last source recommendation | [Coordinator attribution before redesign](docs/research/retained-owner-critical-path.md), no experiment selected |

The winning [report](experiments/multicore-feasibility/single-owner-own-pgo/report.md)
and [all54 rows](experiments/multicore-feasibility/single-owner-own-pgo/full54.csv)
retain exact scope and uncertainty. Historical KingWCR Bee timings are not a
matched comparison to these Vic results.

The [lead synthesis](docs/research/open-multicore-progress.md),
[performance catalog](docs/performance-experiments.md) and
[full handoff index](docs/research/multicore-handoff.md#complete-multicore-experiment-index)
preserve the work history. The previous status is archived byte-for-byte in
[STATUS-history-20261029.md](STATUS-history-20261029.md); its historical 'active',
'current' and remaining-obligation statements belong to their recorded intervals.

Eleven old experimental worktree registrations are retired; frozen evidence
snapshots remain at their recorded external paths. Main and this research checkout
are the only registered worktrees. See the handoff's cleanup receipt and
[evidence guide](docs/evidence-layout.md). No benchmark or engine test was run
for this documentation/administrative cleanup.

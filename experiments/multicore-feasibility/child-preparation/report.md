# Pure child preparation: useful results, unfavorable economics

**Park this finite queue policy.** Unlike the earlier whole-branch experiment,
pure child work is reusable: many prepared maps and Activity–Shelter results are
actually consumed with exact original behavior. But the bounded depth2/first6
queue slows every selected workload; three workers are worse than one. Preserve
the positive per-FULL split as the stronger demonstrated mechanism.

## Frozen implementation and evidence

Source `457dbeab26ae67c248c3f67bf0dd856b2fd9a023`; original control source
`1dc530bf9dd7c95974e3c85369796655e1315c1d`. Both generic Rust1.85.1 release
O3/ThinLTO, no PGO. Candidate feature `child-preparation`; control disables it.
Original control ELF SHA256:
`b416066e84910565010a3efa3ef8a20c998c0324ae725167347df32e8db10eb5`.
Candidate ELF SHA256:
`781c4206bd686e1d6b74dc0972853c6139106ea821269fa3c1098990ec4b5ccb`.
[Design](design.md), [results](results.json), [proof/bindings](proof.json), and
[independent reconciler](reconcile.py) accompany this record. Raw evidence:
`/home/legolas/rook2-experiments/child-preparation-20261024-01/`.

At actual ordinary depth2 parent main activation, publish up to six eligible
ordinary children. Coherent guarded ancestry plus explicit king-victim exclusion
precedes eager construction; exceptional moves stay inline. An owned token guard
cancels on every parent exit. Six slots include old cancelled running tasks.
Workers build Influence and the shared Activity–Shelter helper, never search,
pawn selection, learning, TT or logical counters. Exact child Position identifies
results despite reorder/retry. Activity checks supplied Influence/material/bound
weights; root rebinding invalidates scopes. Supplied maps and original demand
charges remain authoritative. Not-ready results never force a wait. Workers park
when idle; lifecycle is included in whole-process costs. No nested FULL worker.

All12 focused checks pass: four pool lifecycle/input controls, two new native/
nesting tests, five existing FULL-worker tests and the seeded-wrapper control.
Native search tests compare nonneutral seeded search outputs, counters and shared
state against the original inline path. All48 fresh original replay lives pass,
including672 ordered posts;36 lives measured and12 warmups excluded. No native
retry or source retune. Only three original workloads; no full qualification/PGO.

## End-to-end economics

Median search wall seconds, three rotations per configuration:

| Case | Original | New budget1 | Budget2 | Budget4 | 2/4 slowdown vs budget1 |
|---|---:|---:|---:|---:|---:|
|35|4.396959|4.410088|5.222727|6.340096|18.43% / 43.76%|
|08|0.388079|0.384187|0.507031|0.649756|31.97% / 69.12%|
|04|4.362275|4.395870|5.252284|6.474883|19.48% / 47.29%|
|Selected sum|9.147314|9.190146|10.982042|13.464735|19.50% / 46.51%|

Whole-process CPU median sums: original9.150496s, budget1 9.193427s,
budget2 13.643078s (**1.484x** budget1), budget4 20.913185s (**2.275x**).
Budget1 serial-hook wall changes are +0.30%/-1.00%/+0.77% by case; selected sum
+0.47%. Three repeats do not establish significance for these small differences.
The parallel regressions are much larger; all samples/ranges are retained.

Search wall runs from original go write to move callback. CPU/RSS and lifetime
wall use native direct wait4 over startup/setup/search/joined shutdown, including
a small pre-exec Python prefix; all worker CPU is included. Peak RSS medians range
from19432 to19884KiB (exact samples in results). Requested
helper stacks add256KiB per worker to reserved pool storage, not necessarily RSS.

Coordinator14; helpers6/4/2 for budget4,6 for budget2. Build/runner CPUs0–1,8–13;
owned siblings3/5/7/15 unused. Native singleton affinities verified after exec and
main14 at search endpoints. Point observations and guest `/proc/stat` do not prove
absence of unrelated guest/host interference; no new shared-agent affinity changes
or host isolation applied. Cycles/instructions unavailable. No timing conversion
to other hardware or broader workloads follows.

## Actual demand and waste

Totals across three measured lives per cell; percentages are of **started** tasks,
not enqueued moves. Used means at least one map or chain consumption.

| Case | Budget | Started tasks | Unique any used | Unique chain used |
|---|---:|---:|---:|---:|
|35|2|2260177|20.45%|14.04%|
|35|4|2856429|21.07%|14.66%|
|08|2|309181|13.18%|13.18%|
|08|4|418177|20.02%|20.02%|
|04|2|2360716|18.20%|11.51%|
|04|4|3353638|19.07%|11.88%|

Thus79–87% of started tasks provide no result at all, and80–88% of expensive chains
are unused. Pending cancellation and late completion are explicitly counted.
Retries add307/338,138/148,504/532 extra chain consumptions respectively for2/4;
these are not extra unique prepared tasks. All worker failures and input mismatches
are zero; max queue6. Accounting independently closes published=started+cancelled,
started=completed=unique-any-used+discarded, and started=unique-chain-used+
chain-discarded after joined shutdown. Stale completions are a subset, not extra
work. Real reusability does not establish profitable delivery.

## Interpretation and next decision

The trial prices actual publication, locking, wakeup, eager computation and result
lookups together. It does not isolate their individual contributions. Fine-grained
scheduling and substantial discarded work are concrete obstacles; do not conclude
that all pure preparation or larger batches fail. No queue size, depth filter,
transport or lifecycle variant was tried after seeing the result.

Recommend no further implementation of this queue policy. If recursive preparation
remains a priority, the next **source/evidence decision** should require a larger
pure packet with actual demand overlap and a defensible synchronization budget
before another native trial. Otherwise continue from the positive FULL split.
A general branch scheduler is unsupported by either bounded experiment.

One observer repair occurred after collection: the independent reconciler initially
expected cleanup `quit` in stdin.raw. The pinned tap captures write(), while the
released runner sends cleanup via end(data). The reconciler now checks exactly the
captured setup/query/search bytes; complete raw output/exit and pinned runner
preserve separate shutdown evidence. The original failure is retained. No engine
was rebuilt or rerun; cleanup input capture remains explicitly incomplete.

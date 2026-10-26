# Open multicore research: current assessment

2026-10-26, imp2-lead. Continuing under the
[mission](../deterministic-multicore-mission.md); this is a progress assessment,
not research closure or release approval.

The strongest retained result now uses three threads. One coordinator preserves
King's search, pawn-cache accesses, state updates and logical work. Two helpers
compute independent color Activity/opposite-Shelter chains at actual FULL demand.
One immutable input is shared until both readers retire; each owns its output.
The reviewed epoch protocol removed serialized reader copies and result locking.
The numerical split alone had lost: the transport change made it useful.

The [own-PGO full54 survey](../../experiments/multicore-feasibility/epoch-own-pgo/report.md)
records 60.763786s search wall for this candidate, versus 64.092876s preserved
two-thread and 67.973988s accepted serial in that window. Gains are 5.19% and
10.61%, respectively. Whole CPU is 1.422x the two-thread cost and 2.679x serial.
The same new binary's one-thread mode is a descriptive 0.15% above accepted
serial. These are single observations per case/configuration, with separate
repeated generic evidence. They are not a matched KingWCR comparison.

The gain spans 48/54 cases against preserved two-thread and 45/54 against serial;
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
| Does direct epoch transport also help one helper? | The [whole-FULL trial](../../experiments/multicore-feasibility/whole-full-epoch/report.md) improves mode2 by 2.62% across three cases, with separated ranges in each and less total CPU. It remains 2.31% slower than retained3 in aggregate, using 0.682x its CPU. Own-PGO/full54 validation is selected. |

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

The next selected step is one unchanged-source own-PGO/full54 comparison: fresh
joint-mode training, then accepted serial, preserved67d modes2/3 and new modes1/2/3.
This tests whether one binary can retain the faster three-thread option and improve
its less CPU-intensive two-thread option without materially taxing serial mode.
Inventory revisions, fresh-map fusion and frontier batching remain unselected
alternatives. No workload-specific mode selector follows from these three cases.

The retained three-thread image is `67d011083f37f42904423247f5cf0ece2a1e36f0a4129da94fe7561d1f922ea7`,
with profile `9487473e31dfc30ae515cdce18e3f15ec3a653bfd1c5bd665a8f76d235e30311`.
Its source/artifact are isolated experiment products; canonical research source
still preserves the practical two-thread checkpoint, and accepted main/release
bytes are unchanged. The source proof, focused controls and exact-image replay
surveys support further research. Broad mandatory/gameplay qualification of the
three-thread image, adoption, external transfer and release remain separate work.

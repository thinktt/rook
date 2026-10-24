# Integrated FULL worker: gains on three cases, substantial CPU cost

The owned-packet integration preserved the selected behavior and reduced search
elapsed time on all three original workloads. Keep it as a promising research
baseline, not an adopted production change. The serial route remains default.

| Case | Pre-integration control, s | New budget1, s | New budget2, s | Budget2 elapsed reduction vs1 | Budget2 whole CPU / budget1 |
|---|---:|---:|---:|---:|---:|
|35|4.401768|4.406621|3.969362|9.92%|1.802x|
|08|0.382805|0.384783|0.372454|3.20%|1.939x|
|04|4.349233|4.341087|4.035345|7.04%|1.859x|
|Selected-case median sum|9.133806|9.132491|8.377162|8.27%|1.835x|

These are per-case medians from three retained interleaved observations per
configuration, after one excluded warmup/configuration/case. Budget1 and2 are
the same image. The rotating schedule balances their order. No sample was retried
or replaced. The sum is only this selected set, not a 54-case prediction.

The serial refactor changes search medians by +0.110%,+0.517% and−0.187%; each
configuration's sample ranges overlap the control ranges. There is no resolved
aggregate serial regression in this small set (median sum−0.014%). Budget2's
elapsed ranges are below budget1's ranges in each selected case; there is still
only one measurement window and three cases, not broad performance qualification.

## Fidelity and ownership

All 15 relevant evaluator tests pass: 10 existing tests and 5 new focused comparisons.
The latter cover actual FULL/FRESH components, finishing scores/bounds, retained
state and R; nonneutral/zero weights; contrary supplied Influence; pawn-cache
group/full-identity collisions, reuse and reset; root rebinding; lazy FAST refresh;
and repeated seeded searches, stop0/25, retry and budget changes. The worker's
startup and normal shutdown/Drop paths are exercised by these tests. Failure and
timeout paths were source-reviewed, not fault-injected exhaustively.

The unchanged original replay checker passes all 36 selected search lifetimes,
including nine warmups: 504 ordered posts, moves and complete output/exit records.
The independent reconciler checks 39 native processes including three idle probes,
the actual main/worker task affinity observations, all recorded hashes, native
wait4 CPU/RSS and captured raw-stream/replay equality. No process remains live.
This supplies finite fidelity evidence, not an exhaustive TT/learning state trace,
full mandatory suite, 12-game gate or final specification/performance acceptance.

Activity→Shelter uses one shared numerical helper. Every confirmed FULL publishes
a fresh owned Position, exact supplied Influence, material and both current weight
pairs; no pre-shared corpus is used. The coordinator retains cache selection/order,
pawn terms/progress and other components, then joins before tempo, retained writes,
R publication and the existing finisher. FRESH bypasses the cache as before.
Root rebinding cannot retain old packet weights because every packet refreshes
them. Neither the worker nor this seam touches TT/history, host polling or work clocks.

## Cost boundaries and lifecycle

Search elapsed time spans the tap's timestamp before writing the original `go`
record through its move-data callback. It includes normal observer/pipe effects
but excludes process startup, setup and shutdown. Complete native wait4 CPU and
wall include all native threads, setup, startup/shutdown and a small pre-exec prefix.
Warmups and three samples retain the original personality, allowance, natural
seed behavior, work-clock mode and post/move oracle.

Whole CPU median sums are 9.136233s control, 9.135590s budget1 and 16.764474s budget2:
the wall gain costs 83.51% extra CPU versus budget1. The worker spins for its whole
lifetime, including time outside FULL. Each 250ms idle probe observes 0 CPU ticks
for control/budget1 and 0.24 CPU seconds for budget2 (tick-resolution observation).
This prototype therefore consumes approximately a full extra core while idle.

Native lifetime minus search-wall medians are about 4.8–5.2ms across configurations.
They include setup/startup/shutdown and accounting boundaries, not isolated worker
thread costs. Separate startup-reply and shutdown-supervisor timings are preserved
in the JSON but include Python/IPC/controller overhead; they are not claimed as
precise thread-start/join latency. Peak RSS medians, in KiB:

| Case | Control | Budget1 | Budget2 |
|---|---:|---:|---:|
|35|19548|19532|19596|
|08|19572|19540|19612|
|04|19564|19472|19756|

The maximum observed search RSS was 19808KiB. These are complete-process peaks,
not controlled per-worker memory deltas or virtual stack reservations.

The coordinator is pinned14 and worker6; each native process checks the declared
one/two-task shape and task affinities after exec. Helpers use0–5,8–13, with no
owned benchmark work assigned to7/15. The enclosing guest counters nevertheless
record 27 user/system ticks on7 and 20 on15, plus two softirq ticks on7. Thus the
siblings were not continuously idle, and no host isolation is claimed. Placement
is a point observation, not continuous scheduling or descendant monitoring.

## Build identity and judgment

Control: `ecbcf49220a150194cebc6b8608956634b5ae9830e7c3984858727970fdcbebd`.
Candidate: `5b53abf7bf6c3e3c81bfb9b619c6767c9575bb30036fb5d207ea63ab5647f8d5`.
Source checkpoint: `197f7a42fee7e1ce876542fa24affdd8a88f09e0`.

Both build from the same fixed external source path using identical generic
Debian Rust1.85.1/LLVM19.1.7 O3/ThinLTO/oneCGU/debug1/panic-abort settings and no
PGO. Separate fresh target directories preserve the pre-integration and new
artifacts. Control source is the pre-integration `aa3d9483` archive; raw source maps
bind both. Main and accepted release artifacts remain unchanged. These generic
images are not the accepted own-PGO serial baseline and supply no KingWCR comparison.

Fresh publication did not erase the elapsed gain in this experiment. Do not
attribute the entire gain or remaining cost to a specific copy, mutex or cache
effect: there is no such attribution measurement here. All available samples favor
two threads, while budget1 is near the unchanged control; this is enough to retain
the seam for further bounded research. It does not establish scaling beyond two
threads, whole 54/12 behavior or profitability under the production PGO layout.

My next-step judgment is to preserve this implementation as the first integrated
research baseline. Before adoption, select broader representative fidelity/cost
checks and decide whether spinning while the engine is externally idle is acceptable.
Restricting worker lifetime outside searches is a separate question from parking
every sub-microsecond FULL call; the latter may erase the observed gain. No second
transport, idle-policy sweep, coarser generation overlap or PGO campaign was run.
Await the strategy lead's next selection rather than tuning this positive result.

Raw receipts and exact source/build/test identities are outside Git at
`/home/legolas/rook2-experiments/multicore-first-integration-20261024-01/`.
[results.json](results.json), [source-proof.json](source-proof.json), and the
reproducible collector/reconciler preserve the concise result and its limits.

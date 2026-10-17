# Composed partial evaluator and quiescence baseline

This is local development evidence for the independently implemented
`retained-partial-evaluation-quiescence-v1` slice. It is not a full KingRE
comparison or qualification. The earlier material/activity alpha-beta baseline
is a different workload and fidelity; its timings are not a speedup denominator.

The generic release artifact is bound by SHA256
`bd4b479821a97729e1395068b04c2be93d173b83afb9fc97a1fd91292f63a789`.
Its exact local executable is `rook2-dev-exact`; the neighboring build receipt,
verified source archive and compiler settings support reconstruction. The
archive preserves the exact pre-build bytes, including formatting subsequently
restored in two otherwise unchanged source files. Added tests after this build
do not belong to that archived artifact.

The slice composes real root material/squares, incremental child square sums,
influence, activity/tempo, shelter, retained pawn structure/piece terms,
full/fast selection, history admission, pseudo-legal tactical production,
ordering, capture policy, final king safety, reply restrictions and recursive
PV consumption. One ordering workspace is shared across nodes. Reply probes
stop after two legal replies; smaller complete reply inventories are reused.
Budget exhaustion propagates an error and unwinds history, without a fabricated
completed score. Production host polling is not yet connected.

Omissions: pawn progress/races/endings, central influence, bishop coordination/
opening patterns, nonneutral personality, late-endgame adjustment/bounds,
ordinary search/TT integration, host polling, timing and production protocol.
The partial score can change both the evaluation-selection and candidate tree.

`exploration.json` records three identical fresh repetitions of all ten released
quiescence-tree requests and compares their summary fields only. Nine node
counts and nine PVs agree; this is not trace/evaluation-sequence parity or a
fixture pass claim. The mate cases preserve the earlier equal-score PV. The
nonempty case visits12 nodes instead of11, and several static scores differ.
The omitted evaluators must be connected before attributing every discrepancy
to search policy or asserting conformance.

The measured subset deliberately includes different evaluator/cache traffic:

| Case | Subtree nodes | Full | Fast | Pawn hits/replacements | CPU median, diagnostics on/off |
| --- | ---: | ---: | ---: | ---: | ---: |
| Opening history | 1 | 1 | 1 | 1/0 | 0.097003 / 0.096578 s |
| Central recapture | 2 | 2 | 2 | 0/2 | 0.117309 / 0.117072 s |
| Nonempty tactical tree | 12 | 8 | 3 | 8/0 | 0.353494 / 0.352374 s |

Every process performs20,000 fresh root preparations and selected subtrees.
CPU includes root evaluation/cache initialization and the native process
startup/output boundary. Subtree counters exclude that root preparation;
full and fast can both occur at one node. Allocations at initial search setup
are outside recursion. These small subtrees do not model whole-engine cost.

Each variant has one excluded fresh-process warmup and three measured fresh
processes. All output bytes agree within each schedule. Diagnostics on/off
agree on score, PV, charged nodes/relations and consumption witness. Measured
CPU range/median was0.27–1.06%; three observations do not establish a strong
overhead estimate. Raw output, wait4 receipts, artifact hashes and schedules are
retained in each case directory. `results.json` summarizes them.

The recorder and outer orchestrator used housekeeping CPUs0–5,8–13. Engines
requested CPU14. Across the full collection, guest `/proc/stat` recorded498
idle ticks and zero other ticks on CPU15. This aggregate observation does not
prove continuous host exclusion. PMU instructions/cycles remain unavailable;
CPU time is the available development measurement, not final qualification.
TT traffic is still absent, so this evidence does not select a production
position representation or settle the copy/restoration tradeoff.

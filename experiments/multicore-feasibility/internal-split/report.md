# Internal worker trial: selector coverage miss

2026-10-26. The frozen prospective selector matches **none** of35/08/43 by depth6.
All36 focused tests, one generic build,48 unique requested-budget lives and the
independent raw audit pass. No batch, worker or speculative TT snapshot launches
in the workload collection. Therefore these observations provide no2/4/8-thread
scaling, readiness, conflict, reuse, waiting or cancellation-cost result.

| Workload | Canonical N | Canonical R | Root passes | Selector |
|---|---:|---:|---:|---|
|35 |174486 |505645 |176 |miss |
|08 |51689 |921 |36 |miss |
|43 |14144 |2596 |42 |miss |

All16 lives per workload preserve these identities and exact oracle/root-state
checks. Each requested budget1/2/4/8 has one excluded warmup and three observations;
actual execution remains serial after each miss. Reporting ratios of those
requested-budget timings would imply parallel execution that never occurred.
No selector, task set, cap or schedule changed after observing data.

The36 controls include four new SearchSnapshot/actual-worker recovery/cancel-join/
executed-node-cap checks, five TT overlay controls, existing sparse/native Group
and journal/hierarchy controls, plus three evaluator/learning/pawn transfer checks.
They test real worker ownership and native replay on small fixtures, not workload
scaling. The independent offline reconciler also passes47 positive/corruption
controls. One moved-Arc compile error is preserved, followed by successful library
and test-target compilation; no workload retry occurred. The final generic image
is81afacc38e8692f1bed4a0b5dbe3d51e6f725ef21882d85c3c7d5f78386acdc4,
8818176 bytes, source frozen at preparation41d5493b. NoPGO.

The earlier original-workload census traversed3,746,843/614,127/4,463,030N on35/08/43,
substantially beyond these bounded depth6 trees. Its overlapping ordinary-width
counts are still supply evidence, not evidence that this exact finite-window,
post-child0/tail-IIO, eight-remaining,2048N-first-child conjunction is encountered.
The current report does not identify which predicate prevented admission.

Recommendation: retain this implementation and exact selector. The scaling
question remains untested. Before another worker collection, establish the
selector's coverage on a prospectively bounded deeper/original-workload search
horizon, preserving the seven-task boundary and semantic certificate. Select the
horizon from workload/completion evidence rather than future sibling size; do not
weaken the selector merely to manufacture an observation. No new run is started
by this recommendation. Coarse-producer pure-result salvage remains a reserve,
not a conclusion supported by this all-miss result.

All native/supervisor processes and groups terminate, affinities are restored,
and the quiet window is released. All-thread/process endpoints remain recorded,
but split setup/wait/join/speculative work are zero in every workload life.
Whole-process wait4 CPU includes oracle/startup and is not executor CPU. The
maximum process RSS is36120KiB, including independent oracle state. The prepared
8-thread housekeeping policy was exercised as placement setup only; no8-thread
engine workload ran, and no exclusive-isolation claim follows.

Independent local-output/work and whole-root-final-state checks remain finite:
a transient wrong shared write later overwritten can escape their state audit.
Fixed completion/NoHost/timing absent/rnd0 and inlineFULL are explicit. Canonical66,
8f/profile and main are unchanged. No PGO, broad qualification, adoption, release
or external delivery. Raw receipts and byte bindings are in
[closure.json](closure.json), under
`/home/legolas/rook2-experiments/internal-split-20261026-01`.

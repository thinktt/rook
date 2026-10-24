# Restricted-root transaction pilot

The bounded pilot found **no reusable work prepared ahead of an earlier branch**.
Do not build a general scheduler from this result. Semantic replay works in the
focused controls and one actual head branch, but this sample does not show useful
whole-branch parallelism. The larger branches are heavily certificate-capped, so
this is not proof that all whole-branch approaches fail.

## Identity and scope

Source checkpoint `48271d5d304a85969ca9959ca85ce54fc5d703a4`; generic
Rust1.85.1/O3/ThinLTO, no PGO. ELF SHA256
`165d240a0315b1c372e254e57398584b043f2722b6fc58055f9c0999adc5cf40`.
Exact native source map/build logs and raw observations are preserved under
`/home/legolas/rook2-experiments/branch-transactions-20261024-01/`.
[Derived results](results.json) bind every raw JSON and collection plan/closure.
[Reconciler](reconcile.py) checks hashes, cap selection, work partitions, control
results and canonical/accepted-state audit flags.

Six fresh **serial simulations**, coordinatorCPU14, helpers0–5,8–13; no branch
workers, no concurrent lead jobs. One sample per case/depth setting, with no timing
repeats or statistical speed estimate. The declared total ceiling is900s (15min),
not nine minutes as one progress update mistakenly said; actual collection took
seconds. Per-phase times below are elapsed `Instant` observations, not process CPU,
PMU or isolated kernel estimates. Native whole-process CPU was not collected.

All cases naturally reached Restricted policy at depth6: iteration-entry nodes
35422/27571/52968 for35/08/04. Original histories and numerical personalities are
preserved with explicit rnd0. NoHost, timingNone, no node limit, inline evaluator.
Root/config/environment/table geometry remain immutable in each run; entry checks
are not reusable certificates for arbitrary changed contexts. Live polls, partial
stops, nonzero randomness and actual concurrent transport remain untested.

## Work and acceptance

| Case | Queue | Tasks | Speculative nodes | Accepted nodes | Ahead accepted | Capped tasks / work |
|---|---:|---:|---:|---:|---:|---:|
|35|2|8|104074|0|0|4 / 96489|
|35|4|8|118798|0|0|5 / 113571|
|08|2|5|1199|877|0|0 / 0|
|08|4|5|1208|877|0|0 / 0|
|04|2|8|61277|0|0|2 / 47665|
|04|4|8|105219|0|0|5 / 101133|

Across42 tasks,36 were prepared ahead; none of those36 accepted. The two accepted
877-node tasks are the same08 branch at distance0 in separate queue configurations:
no earlier branch advances state between snapshot and validation. Do not interpret
1754/391775 accepted speculative nodes as a useful parallel acceptance rate.
35/04 stop after8 tail candidates;08 completes its first Restricted iteration.
The depth8 ceiling does not mean all cases searched through depth8.

First rejection reasons:22 complete ordinary-order changes,8 request/window
changes,1 pawn-selection change,9 log overflows. Sixteen tasks overflowed overall;
some were rejected for a changed request before inspecting the log. Overflow work
358858 is an overlapping subset of390021 rejected nodes, not an additional work
category. Overflow marks an incomplete certificate; underlying native execution
still finishes. This cap obscures substantial potential reuse on larger branches.
The early order rejects validate the **entire native sorted inventory**, not every
individual history priority, so they are actual ordering changes at this boundary.

All six processes exit0; no fatal oracle disagreements or rollback failures.
All three controls pass each time: a13-node native branch accepts despite an
irrelevant TT cell and a changed old pawn-miss payload, preserves those actual
canonical inputs, and differs from speculative final bytes; a suffix native probe
rejects at event30 after24 staged writes without changing canonical state; changed
window rejects. The appended late probe is a machinery control, not evidence of
a naturally reached late mismatch. Focused feature tests39/39 pass, and the default
feature-disabled pawn-layout regression also passes. An initial feature-enabled
size assertion assumed8192 bytes; it was corrected to include only the optional
journal handle. That failed attempt remains in raw evidence.

## Costs and interpretation

| Case | Queue | Accepted native cost potentially removed ms | Coordinator ms | Speculative execution ms | Fallback ms | Audit-only ms |
|---|---:|---:|---:|---:|---:|---:|
|35|2|0|43.803|152.891|112.231|49.925|
|35|4|0|36.825|176.352|112.865|55.253|
|08|2|0.749|29.355|2.233|0.268|27.984|
|08|4|0.730|24.049|2.234|0.285|36.987|
|04|2|0|42.979|88.979|42.455|51.469|
|04|4|0|38.485|149.152|42.705|54.004|

Coordinator includes enqueue snapshots, request checks, detached staging, replay
and commit. Speculation includes recording/event construction; `recording_ns`
measures insertion/growth only and is already included. Fallback is the rejected
oracle execution reused once; audit-only = oracle snapshots + comparison + oracle
execution minus fallback. Independent oracle execution for accepted tasks is the
measured native cost potentially removed, all of it distance0 here. Phase sums omit
some bookkeeping/destruction and preparation; no executor speedup follows.

Queue snapshots alone peak at33.8MB/67.6MB for depth2/4; retained logs peak at
11.94MB/23.78MB. These exclude canonical/oracle/witness/staging copies and allocator
overhead. Each Event occupies352 bytes even for small operations. Copying full
16MiB TT images and padded events is a prototype expense, not a fundamental lower
bound. Replay itself is cheap on early rejection; that does not rescue snapshot
costs or missing acceptance. No compressed journal or copy scheme was tried.

## Recommendation

Keep this as a negative bounded checkpoint and preserve the positive FULL-split
baseline. Do not select a multiworker whole-branch executor or claim branch reuse
is impossible. The strongest next direction is the already identified **pure
child-prefix preparation**: prepare owned Influence/Activity results ahead and
consume only when the canonical branch demands identical pure inputs. It avoids
requiring TT/learning-dependent entire control flow to remain unchanged and can
salvage useful pure results when a branch changes order. A next experiment should
price actual demand/use and fresh-packet transport, not assume every queued child
will be visited. Selection belongs to the architecture lead; no such experiment
or log-cap retune was executed in this scope.

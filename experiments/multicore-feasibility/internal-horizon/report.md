# Depth-eight internal queue: real workers, no useful scaling

2026-10-26. Three affected horizon/funnel checks, inherited36 controls, one generic
build and33 unique lives pass the independent audit. Nine excluded warmups and24
observations follow the frozen conditional schedule.35/08 activate at iteration7;
43 misses and runs only its coverage life. No retries, threshold/selector/cap
changes, or rebuild between coverage and worker observations. Image4f154968,
8839968 bytes, noPGO; exact source/artifact identities are in
[closure.json](closure.json). Preparation checkpoint1cfcc62f.

| Case | Total threads | Split wall median [range], ms | All-thread split CPU median, ms | Enclosing search wall median, ms |
|---|---:|---:|---:|---:|
|35 |1 |16.351 [16.326,16.403] |16.349 |4724.438 |
|35 |2 |19.414 [18.964,19.531] |19.388 |4719.930 |
|35 |4 |19.147 [19.090,19.198] |20.206 |4723.980 |
|35 |8 |19.532 [19.505,19.571] |21.007 |4707.807 |
|08 |1 |15.753 [15.727,15.782] |15.752 |206.836 |
|08 |2 |18.951 [18.920,19.008] |19.349 |208.218 |
|08 |4 |18.859 [18.712,18.888] |20.347 |210.327 |
|08 |8 |19.232 [19.031,19.347] |21.935 |208.334 |

Split endpoints include setup/snapshot, task production, requested-task waits,
validation/fallback, cancellation/drain and joined termination. Independent oracle
computation and final state comparison are outside; in-interval local audit hooks
remain charged. Whole-process wait4 CPU includes oracle/startup and is a different
quantity. Enclosing-search variations in35 cannot be queue gains: no queued work
is consumed there, and the measured split is slower under every parallel budget.
These are three instrumented observations, not performance qualification.

**35:** the first qualifying parent is ply3/depth4, window[341,342], child0=2326N,
with44 remaining candidates. The coordinator's next child cuts off. None of the
seven forecasts is demanded. Queued cancellation, running work and joins are
measured; all speculative work is wasted. No replay conflict conclusion follows.

**08:** the selected parent is ply7/depth4, window[2096,2097], child0=2938N,
with8 remaining candidates. All seven future children are demanded, with unchanged
windows, but total only162N/R0 (26/19/21/21/17/40/18N). They record188N/R0 and
recover114N as descendants, with zero whole-child acceptance and largest reused
range27N. Physical speculative waste is74N. Each observation has9 pawn-selection,
36 TT-probe and1 ordinary-order semantic rejections; no entry mismatch or cap.
The first large child is not a reliable predictor of sibling demand or grain.

At2/4/8 threads,08 median demand waits are0.601/0.310/0.394ms, joins
0.042/0.001/0.002ms. Its removed-native-call wall proxy is about0.108–0.110ms;
lookup/staging/validation/commit already cost about0.125–0.162ms before snapshot,
producer recording, dispatch/wait and cancellation. Nested wall proxies are not
additive saved CPU. More workers do not improve this tiny fixed task inventory.

Common budget1 setup is about15.5ms and includes a diagnostic complete-TT native-
field fingerprint pass. This is a prototype provenance cost, not a fundamental
transaction cost; it was not separately timed. Parallel modes add one16776912-byte
native TT copy (about2.2ms in08), shared by workers with native-group overlays.
There is no full TT allocation per task. The source caps, padded journals,
per-call exact-history cloning and representation costs remain explicit. Removing
the diagnostic pass alone would not make162N a coarse scaling test.

**43 coverage:** no otherwise-eligible child0 reaches2048N. Its maximum by
iterations1..8 is0/0/0/8/84/333/880/1566N. At iteration8 there are384 hook
opportunities passing finite-window/depth/remaining/best conditions, all below
the N threshold. For35 and08 the corresponding depth6 maxima were1317/528N;
iteration7 first reaches2326/2938N. Funnels are identical in oracle and executor
and never inspect future child sizes or influence selection.

Recommendation: close this fixed first-hit policy unchanged. It has not tested
profitable coarse internal reuse:35 has no demand,08 has only tiny demand,43
misses. The earlier larger ordinary-width census concerns other overlapping
frontiers, and this result does not refute them. Do not rescue the measurement
by tuning thresholds or another certificate. A distinct reserve is pure-result
salvage from coarse speculative branch producers, consuming exact position/root-
epoch-bound Influence/Activity results only at canonical demand. Canonical pawn,
TT, learning and N/R ownership remain native; invalid branch certificates need
not discard independent pure results. Its next discriminator would need actual
FULL/map demand coverage and full producer/lookup cost, rather than position-hit
counts. R0 alone does not establish FULL/map demand or zero CPU cost; the present
batch lacks that join. This is an unimplemented
recommendation, with no new run selected here.

Every started worker has verified singleton placement at the prescribed prefix
of6/4/2/0/8/10/12, coordinator14. Housekeeping8–13 for<=4 and13 for8 is recorded
and restored. All native/supervisor groups terminate.8 total threads occupy all
observed guest core pairs; no exclusive isolation claim. Peak native RSS56180KiB
includes oracle state; peak_forest_bytes is a conservative sum bound, not sampled
simultaneous allocation. Native N/R and full root records are conserved per workload. The independent
local-output/work and whole-root-final-state audit can miss a transient erroneous
write later overwritten. Fixed completion/NoHost/timing absent/rnd0/inlineFULL;
no live-stop coverage, qualification, adoption, PGO or external action. Canonical66,
8f/profile and main remain unchanged. Raw:
`/home/legolas/rook2-experiments/internal-horizon-20261026-01`.

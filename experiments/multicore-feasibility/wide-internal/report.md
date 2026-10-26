# Coarse internal fixture: effectful replay remains slower

2026-10-26. Eleven affected controls plus inherited39, three uncensored captures
and16 fixed-fixture lives pass independent raw/output/work/final-state audits.
One warmup and three interleaved observations per1/2/4/8 budget, same generic
image15fa7342 (9414592 bytes), noPGO. No retries or policy changes. Exact identities
and receipts: [closure.json](closure.json). Preparation18a2ccda.

External hindsight selection used fixed case35/08/43 order, then smallest canonical
ordinary parent-entry ordinal.35 has5 qualifiers among16158 recorded parents;
08/43 have none among3664/588. The chosen35 ordinal428548 is ply2, iteration8,
requested depth6, window[-147,-146], best=-147, child0=10164N, remaining32.
The frozen descriptor contains only known-input identity. Future work remains in
the separate selection receipt; it does not authorize runtime reuse.

| Demanded child | N | R | FULL | FAST | Map demand |
|---|---:|---:|---:|---:|---:|
|a7a6, coordinator |3737 |9779 |1725 |2943 |2215 |
|b6a5 |839 |2411 |375 |679 |498 |
|d8d7 |3789 |13325 |1504 |3136 |1723 |
|h8f8 |7492 |22749 |3075 |5946 |3812 |
|e8g8 |1572 |4220 |559 |1268 |850 |
|d8c8 |5140 |17622 |2225 |4201 |2576 |
|f7f5 |1813 |7056 |769 |1452 |986 |
|b8d7 |4695 |14234 |1886 |3787 |2190 |

These eight siblings total29077N/91396R and are disjoint. Every child was demanded,
all requests were full-window, no retry/best change occurred. The seven future
children total25340N/81617R. This exercises genuine coarse supply, unlike the
prior first-large-child predictions. Overlapping parents are not summed as work.

| Threads | Split wall median [range], ms | All-thread split CPU, ms | Raw enclosing search, ms |
|---|---:|---:|---:|
|1 |105.271 [104.875,105.383] |105.264 |4753.570 |
|2 |166.920 [165.308,167.586] |229.466 |4802.282 |
|4 |154.413 [153.606,157.271] |243.733 |4777.103 |
|8 |154.717 [152.969,155.033] |249.481 |4802.373 |

Parallel split wall is58.56%/46.68%/46.97% higher; CPU is2.180x/2.315x/2.370x.
Three workers reduce wait versus one worker, but seven add no useful wall scaling.
Snapshot medians are2.255/2.168/2.192ms, demand waits17.480/5.553/8.267ms,
joins0.002/0.003/0.005ms. The one16776912-byte immutable TT copy stays charged;
workers use native-group overlays. Diagnostic known-state/whole-TT binding takes
about16ms separately **before** split clocks/workers; enclosing raw search includes
it. The ordinal observer is detached before split timing.

All12 parallel lives reproduce27531 speculative N/82541R and11548 admitted
N/26441R, with15983 unused speculative N. All seven task roots reject; accepted
work is7296 disjoint descendant segments, mean1.583N, largest34N, none>=512N.
No root forecast window changes, caps, worker errors or partial recording occur.
Each observation has2394 ordinary-order,573 Q-order,71 TT-probe and380 pawn-
selection semantic rejections. Entry-key mismatches are comparisons, not additive
lost-work budgets. Unchanged root windows do not settle descendant dependencies.

Measured lookup/staging/validation/commit subcosts total about19.79/21.00/20.12ms
versus9.63/9.59/9.57ms removed-native-call wall proxy, before producer/copy/wait
costs. Producers retain about35.26MiB of journals across76051 events plus forest
metadata. Per-call exact history/key copies and padded event storage are expensive
prototype choices, not lower bounds on every transactional design. Nested wall
proxies cannot be added as saved CPU, and worker wall sums are not process CPU.

Park this effectful replay implementation unchanged. Favorable grain did not
preserve coarse reusable execution; extra workers cannot amortize thousands of
tiny validations here. This is stronger evidence against the current mechanism,
not a rejection of every internal frontier or deterministic parallel architecture.
The distinct next question is pure-result salvage from these same coarse producers:
reuse independent Influence/Activity/Shelter values at actual canonical demand
without transporting branch effects. Its coverage, exact dependency keys, prior
canonical production and real kernel/lookup costs need observation before an
optimized consumer or parallel campaign. The parked depth2/first6 preparation
policy's waste remains relevant; position-hit counts alone would not justify it.

All native/supervisor groups terminate; affinities are restored. Verified workers
use6/4/2/0/8/10/12, coordinator14; declared housekeeping shares sibling13 at8 total
threads. No exclusive-isolation claim. Maximum comparison RSS154560KiB includes
oracle state; forest-byte sums are conservative produced totals, not live peaks.
Independent local-output/work and whole-root-final-state checks can miss a transient
wrong shared write later overwritten. Fixed completion/NoHost/timing absent/rnd0/
inlineFULL; no live-stop qualification, PGO, adoption, external action or practical
scheduler/end-to-end gain claim. Canonical66/8f/profile and main remain unchanged.
Raw: `/home/legolas/rook2-experiments/wide-internal-20261026-01`.

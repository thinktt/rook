# Branch-work census: small Q tasks, larger ordinary siblings

The three original cases passed exact replay and independent count reconciliation:
four focused tests, one generic instrumented image, three fresh lives and35 posts.
No executor, speed comparison, PGO, broad qualification or adoption was performed.

| Case | Charged N | Q N | Eligible direct-Q task N | Mean N/task | Tasks below8 N |
|---|---:|---:|---:|---:|---:|
|35|3,746,843|2,084,450|1,538,279 (41.06%)|1.93|97.17%|
|08|614,127|177,632|171,534 (27.93%)|1.47|99.16%|
|43|4,463,030|2,423,919|2,096,681 (46.98%)|2.70|95.91%|

“Eligible” means the completed ordinary-main group had only direct-Q attempts,
each using a full window, with no retry or actual tail IIO. These are disjoint
Q-root work totals, not summed inclusive ordinary subtrees. Canonical frontier
admission still precedes each task; this cohort does not certify speculative
readiness, unchanged pawn selection or window reuse. Mean demanded tasks per
eligible group were1.94/1.38/3.70. The counters measure N/R and demand, not CPU cost.

At the32-node threshold, eligible direct-Q groups had0/0/6 boundaries with a
substantial current task plus three substantial future siblings; none had seven.
At128 and higher, both counts were zero. Recursive Q groups had no such four-way
boundary even at32. The thresholds describe grain; they are not performance gates.
There were only2/0/6 eligible direct-Q tasks of128 or more nodes, and0/0/17 such
recursive-Q tasks. Many fine tasks remain, rather than a large-grain Q queue.

Within each separate Q root, the optimistic sum(N)/sum(ideal node span) was
1.237/1.071/1.224. Span is local charged N plus the maximum immediate Q-child span,
assuming visited siblings magically ready. It excludes parallelism across distinct
Q roots and says nothing about CPU-weighted span. Fixed-window mate-Q probes
contributed only1,601/0/5,699 nodes, respectively.

Larger sibling grain exists in **ordinary-only main groups**:

| Case | Current +3 future, each>=128 N | Current +7 future, each>=128 N | Current +3 future, each>=512 N |
|---|---:|---:|---:|
|35|5,392|3,464|1,435|
|08|763|259|193|
|43|5,161|1,701|1,191|

These all-parent boundary counts overlap and are not an additive saved-work
budget. The separate ply0/2/4 cuts, exclusive counts and forest totals all conserve
native N/R and FULL/FAST/map demand. Ordinary TT returns were184,587/203,859/841,480
(11.10%/46.70%/41.27% of ordinary entries), illustrating why entry count alone is
not task cost. FULL0 or R0 also does not mean zero CPU work. No observed branch
frame was partial; focused controls separately cover refused admission and the
credited4096th-node poll error.

The [closing recommendation](../../../docs/research/beyond-two-queue-recommendation.md)
parks the Q-certificate hypothesis and proposes hierarchical descendant reuse:
rerun changed parent ordering canonically, then try old child segments at actual
demand, with native fallback. Neither width nor the old raw records establish
that those segments will validate profitably.

The exact image is `ea751e80db90d63ebdb9417e84be5bc8e032a6277b527e107f5cf2c0e374d93f`,
8,061,640 bytes. Isolated source and the patch are bound by `preparation.json`;
`closure.json` binds the image, receipts, tests and concise derived populations.
Canonical frozen66, own-PGO8f and the protected controls/profile remained unchanged.

Raw continuation:
`/home/legolas/rook2-experiments/beyond-two-census-20261025-02`.
The initial01 compilation failed on test-only trait assumptions before any test
or workload execution; its receipts and original patch remain preserved. The
repair changed only test comparisons. All four continuation stages exited0;
native/stage leaders and their process groups were absent at closure. The CPU
quiet window is released and native work is stopped.

Reported-only instrumented lifetime CPU was9.377367/0.980229/8.541961s and wall
4.698359/0.498999/4.279344s, with RSS21,000/21,216/21,808KiB. These include the FULL
helper, instrumentation and lifecycle overhead and must not be compared as engine
speed results. Coordinator14/helper6 placement and all original streams were
audited; guest placement does not prove host isolation. Census reports were
59,742/54,788/54,506 bytes, far below the4MiB bound. No collection was repeated.

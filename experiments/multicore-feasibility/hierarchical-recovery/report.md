# Hierarchical recovery: reuse works, current economics do not

The selected pilot passes23 focused controls, two serial native lives and
independent reconciliation. It demonstrates real ahead-produced descendant
reuse after canonical parent recovery, with no detected local output/work or
root-final shared-state discrepancy. It does not demonstrate profitable parallel
execution. The frozen source/caps are unchanged after collection.

| Ahead-produced work only |08/q2|35/q2|
|---|---:|---:|
|Canonical N|203|78,283|
|Reused disjoint N|99 (48.77%)|22,573 (28.84%)|
|Reused R|0|49,605|
|Committed maximal segments|62|13,509|
|One-node segments|46|10,413|
|Largest segment, N|6|118|
|Segments>=32 N / their total N|0 /0|20 /1,206|
|Segments>=128 N|0|0|

Head tasks separately reuse877 N/10 R and14,542 N/46,783 R. They have no overlap
opportunity and are excluded from the table. Native prefix work was50,609/904 and
51,443/155,251 N/R; this finite first-Restricted-iteration tail is not the whole
standard workload. Every canonical candidate's node count matches the earlier
flat pilot; its0/36 ahead acceptance result remains preserved.

| Ahead-only measured components, ms |08/q2|35/q2|
|---|---:|---:|
|Snapshot|16.019|10.424|
|Speculative execution, including recording|1.257|224.605|
|Recording finalization|0.014|5.944|
|Canonical recovery, excluding timed oracle entry/local checks|0.498|157.395|
|Lookup + staging + replay + commit (inside recovery)|0.314|59.095|
|Accepted oracle intervals minus measured descendant hooks|0.075|21.383|

The last row is an **instrumented wall proxy** for native calls removed, not clean
CPU saved. Classified coordinator subcosts already exceed that proxy, before
snapshots or worker recording. Recovery includes true native parent/fallback work;
it must not be added again to its internal components. Oracle entry checks/cursor
handling and local-output checks are timed separately and excluded from the
executor proxy. Some destruction/report/loop costs remain unclassified:
2.306ms/42.140ms over the complete08/35 programs. No thread-speed or production
performance claim follows from these serial observations.

Ordinary full-order validation remains the dominant semantic rejection:
63 of81 in08,5,073 of6,213 in35.35 also has770 Q-order,318 pawn-selection and52 TT
probe rejections. Window differences cause20,688 candidate-key comparisons;
these are not independent calls. The current reports do not join rejected sizes
with consumed-prefix evidence, so they cannot establish how many coarse segments
are blocked only by an unvisited suffix. The
[prefix assessment](../../../docs/research/hierarchical-recovery-prefix-assessment.md)
proposes that bounded next discriminator without changing exact entry/effect rules.
Matching copies, repeated epoch checks, large Event storage and full pawn/learning
clones are prototype costs, not lower bounds on all recovery designs.

No forest, journal, oracle trace or sparse stage was censored. Larger-case
observability was therefore achieved under the predeclared bounds. Peak queued
forest estimates were4,970,220/232,601,570 bytes; peak sparse-stage estimates were
40,800/478,560 bytes. Native wait4 CPU was0.089679/0.825783s, wall
0.090459391/0.827906931s and RSS42,264/298,332KiB. These include speculation and
audit; estimates exclude allocator details. Main14 and one post-exec task were
verified; guest pinning is not continuous host isolation.

The tests comprise4 critical recovery,3 sparse native-state,5 range/journal,
10 existing native-table and1 legacy-control tests. They cover irrelevant-state
acceptance, late rollback, mate probe mutation, replacement/recent/generation,
untouched groups, cap handling, changed-parent recovery and fatal false-output
acceptance. The initial positive fixture failed: reordering its first move
removed all common recursive demand (9→2 N), so zero reuse was correct. Two
diagnostic failures and the repaired fixture's exact-test pass are preserved.
Only the test fixture changed; a source-prefix comparison verifies unchanged
runtime matching/replay. The continuation reran the complete selected controls
on the repaired image. Neither workload life was retried.

Rollback is a private-staging construction invariant supported by focused
before/after controls, not independently full-state checked on every rejection.
The oracle checks local score/retained/PV/counter outputs and root-final shared
state; an erroneous transient write later overwritten could escape its audit.
Lead accepted this finite NoHost boundary. This is not exhaustive per-segment
state equivalence or production approval; stronger local-effects auditing is
required before adoption or removing the oracle.

The generic, non-PGO image is
`28f007705fde89e1f0e5598b28c76a573f4203a2c445bf1662152a45bdfa4898`,
7,745,136 bytes. `preparation.json`/`prototype.patch` bind63 source files and the
prospective policy; `closure.json` binds40 receipts/artifacts and concise results.
Raw continuation: `/home/legolas/rook2-experiments/hierarchical-recovery-20261025-02`.
Failed/control-repair history remains in01 and
`/home/legolas/rook2-experiments/hierarchical-recovery-fixture-repair-20261025-01`.
All native/stage/supervisor PIDs and process groups are closed. Canonical66/8f,
profile/controls and main are preserved; no PGO, broad qualification, promotion,
external delivery or new source variant occurred in this collection.

# Type-disjoint Activity4: park this fixed design

**Raw4 costs 17.03% more search wall and 56.02% more CPU than matched colors3.**
All three cases lose to both colors3 controls with separated finite ranges.
Park unchanged; no tuning, PGO rescue, adoption or extra run is selected.
This prices one concrete demanded-work split, not every possible raw reduction.

[Timings/ranges](timings.csv), [results](results.json), [closure](closure.json),
[plan](plan.md), [policy](policy.json), [source review](source-review.md),
[numerical proof](numerical-proof.md), [worker proof](worker-proof.md),
[source patch](source.patch).

Original35/08/43, one excluded warmup and three fixed rotations per cell:
48 replay lives (36 measured/12 warmups), 560 ordered posts and four separate
idle probes. Values below are case medians and sums, not a full54 total.

| Case | Preserved3 | New inline1 | New colors3 | New raw4 | Raw4 vs matched3 |
|---|---:|---:|---:|---:|---:|
|35|3.874174s|4.486132s|3.873617s|4.329800s|+11.78%|
|08|0.392288s|0.392808s|0.391199s|0.491360s|+25.60%|
|43|3.475108s|3.498274s|3.508412s|4.275890s|+21.88%|
|Median sum|7.741570s|8.377214s|7.773228s|9.097050s|+17.03%|
|Joined CPU median sum|23.226510s|8.383269s|23.321305s|36.386824s|1.56024x|
|Lifetime wall median sum|7.772011s|8.404525s|7.803754s|9.127043s|1.16957x|

Raw4 ranges: 4.323439–4.332856s, 0.489489–0.505961s,
4.243744–4.285177s. Matching colors3 ranges: 3.854628–3.932522s,
0.390341–0.391312s, 3.498289–3.512605s. Three observations establish the
finite separation here, not general repeatability or an intrinsic lower bound.

Raw4 is 17.51% above preserved3 overall. Against same-image inline it gains
3.48% in35 but loses25.09%/22.23% in08/43, with an aggregate8.59% loss and
4.34041x CPU. New colors3 is0.409% above preserved3: −0.014%/−0.278%/+0.958%
by case. That exposes common-source/layout drift; it does not explain the
much larger raw4 loss. Inline1 has no matched historical inline control in this
schedule, so old-to-new serial cost cannot be isolated.

All four250ms idle probes record0 CPU ticks at100Hz (10ms resolution), not
literal zero CPU. Median lifetime peak RSS spans19416–19708KiB across the
12 cells. Complete native lifetime includes joined helper CPU and the Python
pre-exec prefix; reported peak RSS is not an isolated engine-heap measurement.
Actual main14/helpers6/4/2 placement and role names were verified before first
setup input. Reversible H0-1,8-13 placement/restoration passes. Owned siblings
15/7/5/3 were unassigned; guest placement does not establish host exclusivity.

All49 focused controls pass first attempt: five raw arithmetic, one independent
original pressure rule, one shelter composition,19 raw lifetime/protocol,
eight original color-owner/three color-scope, nine raw-owner/three raw-scope.
They preserve per-piece and final rounds, same-kind OR/promotions, weak/strong
coexistence, pressure12 boundaries, occupancy/global counts, supplied maps and
weights, R, retained/cache/identity/reset and actual search/stop behavior.
Delayed/failing/startup/close/reuse paths exercise all three actual readers.
15 CLI checks and two original08 requested4 one/two-permitted-CPU fallbacks pass.
These focused checks do not replace full qualification.

Strict original replay and independent saved-raw reconciliation pass48/560posts
plus4idle. All52 native receipts are terminal exit0. Every raw4 life has actual
request=all three done epochs after joined shutdown and roles[0,1,2]. Final
request epochs are1,574,502/361,835/2,523,136 by case, equal to preserved/matched
colors3 dispatch counts, including warmups. Empty jobs still retire. These are
necessary synchronization records, not a new hot census or per-role timing.
Other new modes emit disabled rawFour; preserved3 keeps its old report schema.

One immutable owned input feeds three independent helpers: role0 WN/WB/BQ plus
White shelter geometry; role1 BN/BB/WQ plus Black geometry; role2 WR/BR. Every
whole color/kind stays together. Fixed zero-family elimination keeps original
global inventory and occupancy for contributing pressure scans. Owner sums raw
scores and pressure, performs the single side round and pressure clamp, then
original weighted Activity/shelter composition. Pawn cache and retained/R/stat
publication retain native ownership and order. Existing colors_worker and whole
worker are byte-identical; no inactive raw reader exists in mode3.

This creates genuine additional demanded arithmetic width, but prices all extra
pressure scans, static skew, third-reader traffic, output copies, coordinator
reduction/composition and lifecycle/code/layout effects. No hot raw4 clocks,
census or observation RMWs are added. Mode3 retains its existing sparse512
observations; that difference is also part of the complete comparison. No new
measurement localizes the loss among those costs. The result cannot assign a
cache cause or prove a leaner/differently partitioned design impossible.

No source or tool repair, failed native stage, benchmark repeat or clock reset
occurred. All12 stage exits are0. Original pipeline182.895s and collection150.122s
fit the3600/1800s ceilings. The frozen assignment stayed unchanged. No native
job remains; borrowing/replicas remain separate untested reserves.

New generic image (modes1/3/4):
`62f922e4fdb38d1c0358eae4522a3cbd6392fefebe6a1caefe9679cefa0bbee0`,
7,976,144 bytes. The67-file source map changes six existing paths and adds the
raw worker plus two owner-control modules. New text584187bytes versus562459
preserved includes representation/codegen drift. Exact baseline recipe/ISA,
tool/source hashes and the unchanged post-join owner suffix bind in
[preparation](preparation.json).

Raw evidence/build/image:
`/home/legolas/rook2-experiments/type-disjoint-four-20261026-01`.
Isolated source:
`/home/legolas/rook2-experiments/workspaces/type-disjoint-four-20261026-01`.
Canonical main, retained67d011/profile948747 and all20 protected artifacts remain
unchanged. No PGO performance, adoption, broad conformance or external
qualification follows from this finite generic trial.

# Fresh Influence fusion: park this variant

**Fusion loses4.57% versus same-image unfused3 and4.11% versus preserved7ac3.**
All three cases lose with separated finite ranges against both controls. Park
unchanged: no tuning, PGO, adoption or extra run is selected. Positive67d011 and
all preceding artifacts remain preserved.

[Timings and ranges](timings.csv), [results](results.json), [closure](closure.json),
[plan](plan.md), [policy](policy.json), [source review](source-review.md),
[worker proof](worker-proof.md), [source patch](source.patch).

Original35/08/43, one excluded warmup plus three fixed rotations per cell:
36 replay lives/27 measured/9 warmups,420 ordered posts, three separate idle
probes. These are sums of three case medians, not a full54 total.

| Case | Preserved3 | New unfused3 | New fused3 | Fused vs unfused |
|---|---:|---:|---:|---:|
|35|3.834311s|3.852716s|3.967206s|+2.97%|
|08|0.385790s|0.388965s|0.443774s|+14.09%|
|43|3.509712s|3.454210s|3.636878s|+5.29%|
|Median sum|7.729813s|7.695892s|8.047858s|+4.57%|
|Joined CPU median sum|23.188642s|23.088286s|24.143945s|1.04572x|
|Lifetime wall median sum|7.757148s|7.723801s|8.076020s|1.04560x|

Fused ranges are3.927468–3.990327s,0.442570–0.449514s and
3.636604–3.660525s; corresponding unfused ranges3.826728–3.906383s,
0.386376–0.390748s and3.435132–3.468025s. New unfused is0.44% below
preserved in aggregate:35/08 cost0.48%/0.82%,43 improves1.58%. This controls
net extraction/common-body/source/layout drift; it does not isolate one cause.

All three250ms idle probes record0 ticks at100Hz (10ms resolution), not literal
zero CPU. Median lifetime peak RSS spans19520–19684KiB across the nine cells;
complete samples/ranges are retained. Native main14/helpers6/4 were observed
before first setup input; helpers/housekeeping0-3,8-13 were reversibly placed and
restored. Owned siblings15/7/5 were unassigned; guest counters include small
kernel/system activity, so this is not exclusive host isolation.

All56 selected controls passed:29 worker (21 existing/8 fresh),8 original
coherent,2 new row,8 evaluator,3 scope and6 actual fusion-owner controls.
The14 CLI admissions and two original08 one/two-permitted-CPU fallbacks pass.
Actual ordinary/root/unchecked-Q checks preserve maps, evaluations, retained/cache
behavior, logical influence charges and N/R; observed/public/FRESH/Some/custom,
general ensure, FAST-only and1/2-thread paths keep authority. Delay/failure/close,
late/spurious wake, supplied gap, reverse reuse and epoch-exhaustion controls pass.
These are focused finite checks, not broad qualification.

Every fused search life, including warmups, has matching nonzero necessary
rowReady epochs read after joined shutdown. Every new unfused and idle life has
zero row epochs; preserved image has its unchanged report schema. This witnesses
actual activation, not an eligible-population count. Strict original replay and
independent saved-raw reconciliation pass36/420posts+3idle; all39 native receipts
are terminal exit0. Source/image/schedule/CPU/wall/RSS bindings reconcile.

The existing512-epoch observation is retained. Fused helper kernel/ready now
includes row build, row publication, peer wait and128B local map assembly;
copy_ns remains access setup. Owner-ready follows canonical map delivery and
then local pawn/positional work. It is a different phase partition: smaller final
join observations do not establish less end-to-end waiting. All384B of helper/
canonical map copies, publications, peer barrier, owner acquisition and codegen/
layout costs are charged. No new phase timer/census was inserted, and no second
dispatch was eliminated. The complete graph loses here; the data does not assign
that loss to a specific cache line, lock, copy or intrinsic fusion lower bound.

One first compile exited101 because a new test referenced a missing test-only
parked-state probe. No tests had executed. [Repair record](compile-repair.json)
preserves the failed source/tools/receipt; the added cfg(test) probe changes no
production path. The continuation uses the original persisted clock, no completed
request is repeated and no measured source/image changes. All ten continuation
stages exit0. Pipeline247.033s including repair/gap; collection105.698s, within
original3600/1800s ceilings. No native job remains.

Exact new generic image (both runtime modes):
`71409c312dcbe1496c8047a58684ad171d30162755047eca9a63c1b9b4b32e2c`,
7,843,744bytes. Frozen65-source map, eight changed existing files plus one new
owner-test module, shared normalized numerical FULL suffix, default baseline
recipe/ISA and tool identities are in [preparation](preparation.json). New text
is570379bytes versus562459 preserved; representation/codegen drift is real.

Raw evidence/build/image:
`/home/legolas/rook2-experiments/fresh-influence-fusion-20261026-01`.
Isolated source:
`/home/legolas/rook2-experiments/workspaces/fresh-influence-fusion-20261026-01`.
The same-source runtime switch is `--fresh-influence-fusion` with `--threads=3`.
Canonical main and the strongest full54 PGO option67d011 remain unchanged.
This three-case generic comparison does not establish PGO performance,
production adoption, full conformance or external qualification.

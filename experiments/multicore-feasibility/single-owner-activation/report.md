# Single-owner generic: a small, overlapping improvement

New3 search median sum is7.355324s versus preserved3 7.393941s, **0.5223% lower**,
with0.994826x joined CPU. All three mode3 ranges overlap. New inline is0.2041%
slower overall; its per-case changes vary in sign. This is tentative net evidence,
not an isolated mutex saving. Preserve exact d71c4f9f and research leader
a4ecf096/profile6cb9dcaa. The lead separately selected unchanged-source own-PGO/
full54; this generic record authorizes no retune, qualification or adoption.

Original35/08/43, four configurations, one excluded warmup and three rotating
observations/cell:48 lives/560 ordered posts,36 measured/12 warmups, then4 idle.
Both inventory flags are requested in every mode, dormant in inline1. These are
three-case sums of medians, **not full54 times**.

| Case | Preserved1 | Preserved3 | New inline1 | New owner3 | New3/old3 |
|---|---:|---:|---:|---:|---:|
|35|4.475404s|3.760190s|4.534037s|3.750444s|−0.2592%|
|08|0.399752s|0.372674s|0.395570s|0.372856s|+0.0489%|
|43|3.537995s|3.261077s|3.500715s|3.232023s|−0.8909%|
|Search median sum|8.413151s|7.393941s|8.430323s|7.355324s|−0.5223%|
|Joined CPU median sum|8.417355s|22.181078s|8.434111s|22.066319s|−0.5174%|
|Lifetime wall median sum|8.435895s|7.421763s|8.452773s|7.381693s|−0.5399%|

Preserved3/new3 ranges are3.759175–3.767106/3.747450–3.795176s on35,
0.369904–0.375981/0.371569–0.372889s on08, and
3.223087–3.287375/3.229896–3.248110s on43. Case43 supplies29.053ms of the38.617ms
net median-sum gain and also improves inline. Inline changes are+1.3101%,−1.0461%,
−1.0537%; all inline ranges overlap too. Do not subtract inline drift to attribute
the remaining difference to locks or cache lines. Complete finite ranges are in
[case-ranges.csv](case-ranges.csv); all samples remain in the external raw audit.

New3 is12.7516% below sibling inline at2.616318x its joined CPU. Per-process peak
RSS spans19352–19784KiB across measured observations; summed RSS peaks are not a
memory footprint. All four250ms idle probes observe0 process ticks at100Hz,
not literal zero CPU. Actual owner14/helpers6/4 placement is bound before input;
H0-3,8-13 housekeeping is restored. Siblings15/7/5 were unassigned. Guest snapshots
contain small kernel/I/O activity on7, so guest placement is not host exclusivity.

## Changed contract, retained computation

Private higher-ranked ActiveSearch/ActiveEvaluator facades keep the exclusive
original receiver until cleanup. They expose fixed body forwarders, not arbitrary
mutable receiver/configuration/shutdown access. Their fixed internal call graph
is trusted audited code, not universally type-proved. Box OwnerState holds
generation, nested depth, Flight/metadata and unchanged observations. Normal
dispatch/complete and sampled owner_ready no longer acquire Control. Shared cold
failure/parking, real reader retirement, owned Packet, numeric bodies, SC-RMW
registration/notification and conditional Sleep wait remain.

Opening/body are protected under test-build unwind; cleanup drains the actual
original worker and preserves the original panic. Terminal/drained shutdown
dominates saved depth, including nested epoch exhaustion. Standalone FULL/FRESH/
observed prefix closes before the original retained/stat/observer/finish suffix;
outer search keeps its activation. Recursive visits add no wrapper. Timed normal/
error returns clear timing before closing, preserving prior chronology. Mode2
retains its old private guard; its introduced local depth is zero after terminal
cleanup. Default public conditional traits and between-call migration pass.

The [source check](source_check.py) retains17 numerical source files, four worker
functions and five type definitions exactly. Shared prefix/suffix numerical
streams match after explicit owned scalar projection/shorthand normalization.
This is source evidence plus focused controls, not compiler equivalence or proof
over every schedule. Production panic=abort does not run the tested unwind path.
Optional feature builds are not qualified; branch-transactions keeps its existing
Rc non-Send restriction and excludes two default trait/migration controls.

## Focused execution and preserved fixture repair

All70 selected logical controls pass:27 worker,9 activation,3 prior colors lifetime,
8 numerical/rebinding,12 evaluator inventory and11 actual ordinary/Q owner tests.
They cover nested first-iteration, actual special inventory demand, default1/2/3,
standalone observer parking, Host/prefix/observer panic, delayed reads/output/done,
SC registration/late latch, startup failure, migration and inner-terminal/outer
close idempotence. Independent Send-final-close capability is removed; its drain
obligations are tested via supported enclosing discard/unwind and owner migration.

Actual test execution is **71:70 passed,1 failed**. The first final-Q group has
five passes and one assertion failure: a reused private fixture expected another
readiness probe after the new enclosing test entry had cleared coherence permission.
Only that test fixture renews its validated admission before its second call.
Production source is unchanged. The original69 passing controls are not rerun;
only the failed exact unit runs again and passes. The
[repair record](test-repair.json) and raw repair-01 preserve original source69,
setup/tools, executable, failed output and all eight original stage receipts.
The failed unit's setup repeats; no completed test control or wire/benchmark
request repeats. Original clock/deadline remain fixed.

One generic build,14 CLI controls,2 original08 affinity fallback lives and1 cold
layout process pass.48 replays/560 posts plus4 idle native processes pass exact
raw replay and independent wait4/placement/observation audit. All52 comparison/
idle receipt rows bind explicitly to their terminal native processes. The composed
closure verifies1058 file pins, original failure provenance and all stage terminals.

There are14 pipeline stages:13 exits0 plus preserved tests-07 exit101; the exact
repair and every remaining build/admission/layout/collection/reconcile stage exit0.
Initial outer preparation exits1, repair/collection wrappers and independent
closer exit0. Pipeline662.442s; terminal independent audit681.010s, within the
original3600s clock including repair gap. Collection144.075s, within1800s; per-life
ceiling180s. No live native job remains and the quiet window is released.

## Actual storage and artifact identities

Cold production projection: Shared832B/align64/phase0 versus preserved7168B;
separate OwnerState6368B/align16. Request0, Packet64 (320B), white output384 and
black output448 retain their original offsets and64B slots. Cold control at704
is128B. These structure sizes do not measure allocator headers, total allocation
or cache traffic. Box allocation/indirection, storage relocation, common prefix
return/spills, catches/wrappers and generated-code drift are complete trial costs.

New generic image: `d71c4f9fa662af73c81d891f16c2b56ded2d2ccfbe982ed5ae81829a14fd573d`,
7,932,032bytes; old generic8c is7,902,688bytes. Text changes579403→576635bytes.
Recipe/toolchain parity is verified against the preserved generic receipt; no PGO.
The repaired69-file map, ten changed files and one new test module are bound by
[preparation](preparation.json) and [source patch](source.patch). Setup15c11c98,
test-only repair c1b1a949. Exact image/profile/control pins and all36 protected
artifacts are in [results](results.json) and [closure](closure.json).

Raw/image: `/home/legolas/rook2-experiments/single-owner-20261028-01`.
Source: `/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01`.
Preserve this finite result; no source retune, additional observation, performance
qualification, canonical adoption or external delivery follows from it.

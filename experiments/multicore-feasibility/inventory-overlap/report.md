# Same-node inventory census: one worker discriminator is justified

**Actual demand and timing slack justify one small integrated same-node experiment.**
They do not predict a speedup. This boundary is substantially better supported
than the failed child queue: inventory is demanded at76–98% of eligible ordinary
entries, and every consumed no-null sample had generation shorter than its actual
preceding Influence/FULL interval. Handoff, contention and the loss of the existing
FULL split still need to be priced in an actual alternative mode.

## Scope and fidelity

Source `929e88bf`; [plan](plan.md), [derived results](results.json),
[bindings](proof.json). Raw/build/source evidence:
`/home/legolas/rook2-experiments/inventory-overlap-census-20261024-01/`.
One generic Rust1.85.1/LLVM19.1.7 x86-64 GNU O3/ThinLTO/one-CGU/debug1/panic-abort
ordinary-wire diagnostic image, feature inventory-census, inline evaluation.
Exact binary identity and effective compiler options are bound in proof/build
receipts. No PGO, queue, worker, repeated workload or second sampling policy.

All six focused counter/domain/native-equivalence tests pass. Original35/08/43 run
once each, all strict replay checks pass with35 ordered posts. Independent raw/
PID/accounting reconciliation passes; no source repair or native retry occurred.
The positive a977 own-PGO image remains hash-verified unchanged.

Launch count is **ordinary activations**, after early draw/TT/FAST returns and before
actual ensure-Influence/FULL. Q is excluded. Failed FAST admission may already have
built Influence; scratch-Some samples receive no credit for that earlier work.
No inventory is substituted; actual cache/learning/TT/N/R behavior stays original.
Native generation is timed only at original consumption. Empty-list/post-generation
mate bounds and later child stops already count as consumed. Only discarded sampled
bound/threat/null-cutoff paths run a late, guarded local shadow; stops run none.

## Exact demand counts

| Case | Eligible | FULL-bound return | Cheap threat return | Null cutoff | Inventory consumed | Demand |
|---|---:|---:|---:|---:|---:|---:|
|35|971481|0|157144|72801|741536|76.33%|
|08|222480|3544|0|0|218936|98.41%|
|43|1066340|4000|137591|103756|820993|76.99%|

Stopped/unfinished is0 in these three runs. Null entry is an **overlapping**
attribute:35 has102944 entries (72801 cutoff,30143 continue);43 has114087
(103756 cutoff,10331 continue);08 has0. These are not additional disjoint exits.
Thus10.6–10.7% of eligible35/43 entries cross a recursive null boundary, which a
single-helper design must explicitly settle. No checked/reused-Q work is counted
as an evaluation-overlap opportunity.

## Fixed-stride paired observations

Policy: every512th eligible entry, capped16384 reserved samples per process.
Retained samples1897/434/2082; no cap skips and no shadow-domain exclusions.
Consumed samples1430/427/1594; after excluding recursive-null paths,1372/427/1565.

The following are **paired consumed, no-null samples**, not ratios of unrelated
aggregates and not all-eligible workload totals:

| Case | Native gen median ns | Gen p95 ns | FULL-minus-gen median ns | Minimum slack ns | Gen fits FULL samples | Paired min sum ns |
|---|---:|---:|---:|---:|---:|---:|
|35|370|481|812|380|1372/1372|517431|
|08|191|260|321|150|427/427|85777|
|43|250|330|380|120|1565/1565|396926|

Each paired contribution is min(that sample's FULL interval, its native generation
time), only when that inventory was actually consumed. Discarded shadow generation
contributes **zero saved work**. The sums are the observed sample sums: no stride
multiplication into promised seconds or full-search speed bounds is performed.

All-sample FULL interval medians are1182/521/617ns; these also contain discarded
outcomes and are not the paired-subset medians above. Consumed scratch-Some counts
are128/0/74; scratch-None1302/427/1520. Null interval medians1037/1292ns for35/43
include descendants and their instrumentation/shadows; they are not added to
available FULL overlap or treated as an extra free core.

## Observation costs and bias

Each process makes1024 fixed empty Instant-pair probes: median20ns, p95 30ns,
mean22.34–22.45ns. They are observations of timer cost, not subtracted calibrations.
Enable spans are0.070–0.097ms and already include those probes.

| Case | Extra shadow gen ms | Shadow admission ms | Partial sampled bookkeeping span ms |
|---|---:|---:|---:|
|35|0.181701|0.412360|0.673075|
|08|0.001212|0.003998|0.122873|
|43|0.122193|0.252964|0.678524|

The partial span excludes measured shadow/admission work; it does **not** isolate
all per-entry TLS/counter/frame costs or every clock call. Whole-request CPU/wall
includes counter branches, validation, serialization and other observer work, so
it is not an engine performance comparison. Timer cost is material relative to
130–500ns generation observations; do not claim sub-timer precision.

Periodic stride can alias traversal patterns; no randomized sampling or repetitions
estimate that uncertainty. FULL warms Position/data before native generation, and
late shadows additionally validate/warm their input. Shadow lists use different
storage and are not promised cold-worker costs. Null recursion can further change
cache state before actual generation. Sequential timings exclude publication,
returning inventories, scheduling, contention and processor/locality differences.
These optimistic samples are therefore **not a speed bound**. Native execution is
CPU14, no helper; harness/build0–5/8–13, no owned15. Point affinity and raw guest
context do not prove host isolation. Input tap still excludes end(data) cleanup;
pinned runner plus complete output/exit retain that separate evidence.

## Smallest useful next experiment

Recommend one ordinary-only, single-slot integrated inventory alternative, if the
lead selects it: immutable Position in, exact unsorted native MoveList out; main
executes inline Influence/FULL. Keep ordering, learning/TT reads, generated charges
and consumption at their original point. Use ready results opportunistically with
an explicit unavailable/busy fallback. At a recursive-null entry, settle/drain the
parent job and release the helper before descending; an already owned completed
list may survive on the parent until actual consumption or cutoff. Measure that
boundary rather than assuming a free helper at each nested node. Early exits must
discard/drain without semantic charges; no Q inventory/reply scope expansion.

Price full packet/list transfer, readiness, discarded/busy work, serial-path cost,
whole CPU and lifecycle against inline **and the preserved positive FULL split**.
One helper cannot simultaneously provide both overlaps; current FULL coverage
includes Q/root calls outside this census. The observed slack supports a finite
trial, not additive savings over a977 or scalable queues. No prototype or subsequent
native work was executed or selected by this census closure.

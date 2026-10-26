# Fixed epoch transport: a positive generic three-thread option

**Retain this option for own-source PGO and a descriptive full54 comparison.**
Its three-case search-wall median sum is7.735016s:7.57% below preserved oldcolors3,
3.67% below sibling current2 and7.46% below sibling inline. Whole-process CPU is
1.445x current2 /2.774x inline. This is a net effect of the fixed transport change,
not isolated mutex savings or production adoption.

[Results](results.json), [closure](closure.json), [plan](plan.md),
[reviewed ownership proof](ownership-proof.md). Only `src/colors_worker.rs` changes
across the64-file source map;63 files, all mathematical bodies, current2 transport,
caller/configuration bodies and accepted artifacts remain unchanged. No PGO,
parameter sweep, inventory/fusion, broad qualification or external action occurred.

## Complete matched result

Original35/08/43; one excluded warmup and three fixed rotated observations per
configuration:48 successful replay lives (36 retained,12 warmups),560 ordered posts,
plus4 separate idle probes. Every stage and independent audit passes on its first
attempt; no failed benchmark process, source/tool repair or repeated completed life.

| Case | Preserved oldcolors3 | New inline1 | New current2 | New epoch3 | Epoch vs current2 |
|---|---:|---:|---:|---:|---:|
|35|4.082021s|4.477216s|4.080887s|3.845992s|−5.76%|
|08|0.436230s|0.391843s|0.386437s|0.388441s|+0.52%|
|43|3.849838s|3.489687s|3.562385s|3.500583s|−1.73%|
|Median sum|8.368089s|8.358745s|8.029709s|7.735016s|−3.67%|
|Whole CPU median sum|25.103516s|8.363291s|16.061369s|23.203878s|1.445x|
|Lifetime wall sum|8.394820s|8.382421s|8.056345s|7.762224s|—|

Epoch beats every current2 sample in35 and43, with separated ranges. In08,
current2 0.386093–0.388525s and epoch0.383324–0.396599s overlap; its small median
loss is unresolved. Epoch also beats every oldcolors3 sample in all three cases.
Against inline it gains14.10% in35,0.87% in08 and loses0.31% in43;08/43 inline
ranges overlap epoch. These are three-case results, not full54 predictions.

Search wall retains original go-write→move callback endpoints. Native wait4
CPU/RSS/lifetime includes every thread, startup/setup, joined shutdown, reporting
and a small pre-exec Python prefix. All four250ms idle probes register0 CPU ticks
at100Hz (10ms resolution), not literally zero CPU. Active helpers may still spin
while Host callbacks block. No PMU or exclusive-host-isolation claim.

## Observations and what changed

One initialized immutable input slot is release-published with a checked epoch.
Each reader acquires it, directly computes its original side kernels, ends every
Packet reference (including sampled clock reads), writes only its own output,
then release-publishes matching done. Coordinator acquires both, copies scalar
outputs under Control and completes output reads before a later request release
permits overwrite. Scope close claims Discarding under Control until both actual
parked/exited acknowledgments. Parking never clears input cells.

The single-waiter cold path uses the reviewed unconditional SeqCst latch exchanges
and Sleep mutex/condvar registration handshake; no memory orders or notifications
were weakened. Control remains at publication/output consumption, with sampled
owner recording and lifecycle operations. Both unconditional publisher RMWs and
all direct cache transfers are paid. This removes reader Slots acquisitions and
local Packet copies without pretending synchronization is free.

The512th-dispatch sampling phase, fixed histograms, side kernels and coordinator
rounding/R ownership stay unchanged. All mode3 dispatch/sample/completion counts
match across old/new images and repetitions:1,574,502/3,075 in35,361,835/706 in08,
2,523,136/4,928 in43 per life. No sampled failures/discards/missing owners.

| Retained-life paired means |35 old→epoch|08 old→epoch|43 old→epoch|
|---|---:|---:|---:|
| Owner-ready after publication |437.54→406.23ns|273.04→252.67ns|201.96→182.35ns|
| Positive latest-side minus owner gap |271.52→159.46ns|222.57→106.35ns|369.15→242.58ns|
| Complete-entry→both outputs acquired |325.39→237.52ns|280.88→185.32ns|404.65→318.93ns|
| Absolute side-ready gap |130.28→66.30ns|118.24→69.66ns|169.14→89.97ns|

Publication follows coordinator snapshot/metadata preparation; phase is now held
with material/weights on the coordinator instead of rereading a full Packet for
composition. The legacy copy interval included lock/copy; the new corresponding
interval ends at direct-borrow setup. Its cache reads occur **inside kernel_ns**.
For example,35 white setup falls94.84→25.66ns while white kernel grows337.49→
376.42ns. Those interval movements cannot isolate memcpy or pure arithmetic cost.
Side-ready clocks precede final output/done release, and observed join excludes
subsequent histogram updates/merge; complete search timing pays them all. Periodic
stride, timestamps, cache effects and layout drift limit causal decomposition.

## Evidence and exact scope

32 fresh controls pass:21 protocol/lifetime plus8 actual Evaluator and3 scope
controls. They exercise delayed readers, sampled input lifetime, output retirement,
both close/dispatch orders, consumption exclusion, publication rollback, prior-epoch
latch/new request, completion before/during registration, spurious/terminal wakes,
unwind, startup partial failure, discard/reactivation and MAX-epoch drain. They
supplement the explicit aliasing/happens-before proof. Production panic-abort is
not unwind recovery.13 CLI checks and2 unmeasured original08 affinity controls
also pass. Default1/request cap/one-CPU and two-CPU fallback remain truthful.

Baseline38 evidence is retained with an explicit partition:10 old protocol checks
are superseded,11 colors integration checks rerun,17 unchanged source/control
portions retained. Old transport coverage does not qualify the new protocol.
No extra numerical campaign was run for unchanged kernels.

Independent raw audit passes replay/streams, actual main14/white6/black4 placement
before first input, source/build/image identities, counts/histogram arithmetic,
joined exits and housekeeping restoration. Original unused siblings show some
guest tick activity, so point placement does not imply host exclusivity.
Pipeline231.436s /collection145.724s stay within fixed3600/1800s caps.

Old/new ELF `.text` sizes565,227→562,459B and `.rodata`324,308→324,300B have distinct
hashes in closure. Source isolation supports net transport attribution, including
changed code layout/cache behavior; it does not measure a lock-only cost or old
serial/current2 layout drift separately. New inline/current provide same-image
controls, not old-image mode1/2 reruns.

- Source/tool checkpoint: `a02a2f7bad1ab1969187a4959e90b13bb22e7a81`.
- Preserved old3: `b837361a4c00a57a29bedf2ccace3e7d13a5bcd025c1d8bf35c215f696449a82`,7,833,496B.
- New image: `7ac72fc63cf4086944b3abfd71f45eb1f0347796f2520bb97aa87fc8de3fb65c`,7,798,776B.
- Raw audit: `2a5eed57b3acbe816a7117ca79ff64d66121343cfc9d3d93b27b260a61860b05`.
- Raw/source/build evidence: `/home/legolas/rook2-experiments/epoch-colors-20261026-01`.

Both images use Rust1.85.1/LLVM19.1.7, generic x86-64 GNU,O3/ThinLTO/one-CGU,
debug1/panic-abort and no PGO. No conformance/gameplay/performance qualification
or adoption follows from this finite generic result.

## Smallest own-PGO/full54 continuation

Reuse the configured-full recipe with this **exact** source: one instrumented
build, original54 once in each mode1/2/3 (162 strict training lives), one equal-input
merge and one use build. Do not reuse8f's profile on changed source, retune merge
weights, rerun a small screen or change the transport. Freeze source/profile/build
identities; training timings are not performance observations.

Then one descriptive full54 with five configurations: immutable accepted serial5cf,
practical2 8f, and the one new image in modes1/2/3. Use the existing single-observation
full54 pattern (270 lives, no per-cell warmups), fixed rotated configuration order,
and strict original replay/all-thread CPU/wall/RSS. This is432 replay lives including
training, without another small screen. Keep original endpoints and modes/options
of both preserved controls. Do not translate these generic three-case ratios into
expected full54 seconds or KingWCR parity.

Cheap exact-use-image admission should verify1/2/3 configuration and actual native
placement, permitted1/2 fallback, joined shutdown and three short idle probes.
Reuse unchanged source/protocol/numerical evidence; retain4096/512, active-scope
parking, initialized startup, logical work/poll ownership and supplied-map authority.
Single observations are descriptive, not per-case significance. Full mandatory,
regular12 and external gameplay acceptance remain later separately selected work.
This closure performs no PGO or follow-on execution; the lead owns that next scope.

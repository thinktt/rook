# Colors-only3: correct finite behavior, no net gain over current2

**Recommend parking this variant unchanged.** Across original35/08/43, its
search-wall median sum is8.379793s versus sibling current2 8.013154s (+4.58%),
with1.568x whole-process CPU. It is5.02% slower than the preserved generic current2
control and1.03% slower than sibling inline overall. No PGO, balancing, inventory,
full54 extension or adoption is selected from this result.

[Results](results.json), [closure](closure.json), [plan](plan.md) and the
[retained placement repair](placement-repair.md) separate this outcome from the
previous successful two-thread option. Canonical main/engine and66/8f, a977/profile
and accepted5cf artifacts remain unchanged. The lead owns the next decision.

## Complete measured cost

One excluded warmup plus three rotated observations per configuration/case:
48 strict replay lives (36 measured,12 warmups),560 ordered posts and4 separate
idle probes. Search wall is the original go-write→move callback; whole wait4
CPU/RSS/lifetime includes all native threads, startup/setup, joined shutdown,
report serialization and a small Python pre-exec prefix.

| Case | Preserved current2 | New inline1 | New current2 | Colors3 | Colors3 / new current2 |
|---|---:|---:|---:|---:|---:|
|35|4.059169s|4.439945s|4.054847s|4.084041s|+0.72%|
|08|0.384778s|0.392606s|0.383326s|0.438732s|+14.45%|
|43|3.535453s|3.461981s|3.574981s|3.857020s|+7.89%|
|Median sum|7.979400s|8.294531s|8.013154s|8.379793s|+4.58%|
|Whole CPU median sum|15.959605s|8.298577s|16.028160s|25.138258s|1.568x|
|Whole lifetime wall sum|8.006604s|8.319072s|8.040184s|8.406826s|—|

Case35 colors/current ranges overlap (4.052330–4.100779s vs4.022399–4.095855s):
its small median loss is not resolved. All colors samples exceed all sibling
current samples in08 and43. Colors beats inline by8.02% in35, but loses11.75% /
11.41% in08/43. Sibling current2 is0.42% above preserved current2 in aggregate,
including+1.12% in43; shared routing/refactor/code layout is therefore visible.
The preserved control is a two-thread image, so this does not independently
measure old-serial refactor cost. No compiler/transport cause is isolated.

All four250ms startup-idle probes report0 process CPU ticks at100Hz (10ms
resolution). This is not literally zero CPU usage. Retained-row RSS medians range
19,460–19,692KiB; complete samples are in results/raw records, not per-worker
memory deltas. Active helpers can still spin during blocked Host callbacks.

## What the sparse observations say

Every512th actual colors FULL dispatch records one paired observation; no sample
cap or outcome filter. The table aggregates the three retained lives per case,
including their actual FULL calls during setup as well as search. All sampled
calls complete, with no discarded/failed/missing-owner observations.

| Case | Actual dispatches | Paired samples | A side ready after owner | Owner-ready mean | White / black ready means | Join interval mean |
|---|---:|---:|---:|---:|---:|---:|
|35|4,723,506|9,225|96.22%|429.49ns|667.16 /594.42ns|328.29ns|
|08|1,085,505|2,118|99.81%|270.79ns|425.23 /447.73ns|269.33ns|
|43|7,569,408|14,784|100%|200.88ns|549.45 /425.32ns|408.64ns|

Publication time is taken **after** copying coordinator inputs into the owned
packet and just before REQUESTED stores. Owner-ready is captured after local
terms, before acquiring its observation lock. Side-ready is captured under Slots
just before output COMPLETE publication; it includes pickup/input-lock/copy,
kernels and output-lock delay, but precedes the final release/unlock instructions.
The sampled join interval starts at complete() entry and ends when both outputs
are acquired, before histogram updates and coordinator numerical merge.

Positive latest-side-minus-owner gaps average268.66/227.03/369.67ns; counterpart
owner-after-sides gaps average2.42/0.03/0ns. White is the last side in82.71% /40.93%
/87.62% of pairs; mean absolute side imbalance129.87/122.63/166.33ns. These samples
show that the coordinator usually reaches the join before both side outputs,
rather than spending most sampled calls behind its pawn/local branch.

Per-side kernel means are338.48/305.60ns in35,91.50/143.48ns in08 and208.29/
145.58ns in43. Input lock/copy interval means are95.08/91.77,102.20/95.72 and
137.55/101.39ns respectively. These are observational intervals with timer,
cache and synchronization effects, not isolated pure arithmetic or subtractable
transport constants. Periodic stride may alias traversal. Fixed log2 histograms
retain all samples but cannot reconstruct per-call correlations beyond recorded
paired counters/sums. No current2 per-chain timer was added, and no pre-publication
Influence/coordinator-copy cost was isolated. Do not compare these kernel means
with the old neutral pre-shared350.98ns probe or infer a fusion speed forecast.

## Ownership and finite assurance

One retained owned packet feeds two reader-local copies under a short slot lock;
all numerical kernels run outside it. Each side preserves the original traversal
and rounding, computing its own Activity and the opposite king's pressure/Shelter.
Coordinator performs the original cross-color merges, tempo, retained updates,
finishing, observers and one pawn-plus-Activity R publication. PawnCache and FAST
remain local; FRESH and supplied contrary maps retain their existing semantics.
No per-FULL Arc/Box allocation or new wall-abort/engine pinning is introduced.
The original current2 worker source and original complete Activity/Shelter compute
bodies remain unchanged; the new side seam and shared packet costs are paid.

All38 focused tests pass:5 side numerical,10 transport lifecycle,8 current
Evaluator,8 colors Evaluator,3 current scopes,3 colors scopes and1 CLI parser.
They cover asymmetric/zero/nonneutral weights, contrary maps, detailed FULL/FRESH,
retained/R/cache collision/reset, actual cache-preserving2→3→2→1→3 switches,
repeated search/stop/retry, root/public Q, delayed readers, discard/reuse/failure,
terminal notification, parking and joined shutdown. Test unwind is not production
panic-abort recovery. All13 CLI checks and2 unmeasured original08 one/two-permitted-
CPU controls pass; requested3 truthfully configures1/2 under those masks.

Independent saved-record reconciliation passes all valid raw wire/replay,
placement, source/image/build flags, epoch bindings, readiness histograms/counts,
CPU/wall and termination checks. This is finite focused behavior, not full
mandatory/gameplay qualification or an exhaustive internal-state audit.

## Preserved failure and exact identity

At the first colors warmup, the external checker expected full16-byte Rust thread
names; Linux comm exposed15 bytes. Actual placement was correct14/6/4, but the
ready gate rejected startup and the process was killed before protocol release.
The tap's421 attempted setup bytes are not delivered-input proof. All failure
bytes and32 frozen original files remain intact. The only existing-tool changes
are the two expected comm literals in launcher and independent placement checking.

Completion retains the original three successful excluded warmups under archived
original tool hashes and executes only45 remaining entries plus4 idle probes.
All36 retained observations occur after repair. No source/image rebuild, passed
check or completed search life is repeated. The combined ledger has52 successful
native benchmark/idle processes plus the one failed startup; the separate
preparation's13 CLI and2 affinity controls are outside that count.

Original3600s pipeline /1800s collection caps are preserved: elapsed780.557s /
729.242s respectively, including the repair gap. Coordinator14, white6, black4
are observed before first input; build/harness0–3,8–13 and selected reversible
housekeeping are recorded/restored. The completion interval has no user/system
activity on owned-unused5/7/15 in guest tick snapshots; this does not prove
exclusive guest/host isolation or price host/emulator interference.

- Source checkpoint: `a59225032a299ca1efbdc3413f530ebb9b085e70`.
- Metadata repair checkpoint: `e23efee0f20d2bec076e1637448124a44faa3104`.
- Preserved generic control: `026a3d2ce0d24cb7abda6ce4d2c1ecd735f7d32f9e16d878a4b7dd286a9b4530`,7,550,632B.
- New generic image: `b837361a4c00a57a29bedf2ccace3e7d13a5bcd025c1d8bf35c215f696449a82`,7,833,496B.
- Independent audit: `a0600ee5445a664f400231ede02928f37952a753f96160f7f1ea4f0557a8c1b2`.
- Raw preparation/failure: `/home/legolas/rook2-experiments/colors-three-20261026-01`.
- Raw completion/audit: `/home/legolas/rook2-experiments/colors-three-20261026-02`.

Both builds use Rust1.85.1/LLVM19.1.7, generic x86-64 GNU,O3/ThinLTO/one-CGU,
debug1/panic-abort and no PGO. Exact recipe/source archives are bound in closure.
No universal limit on wider same-node dataflow follows. Fresh-Influence→side-FULL
fusion, combined inventory and frontier batches remain distinct unselected reserves.

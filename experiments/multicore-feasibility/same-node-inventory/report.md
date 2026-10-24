# Same-node inventory: readiness succeeds, total cost loses

**Park this fixed inventory policy.** It delivers99.86–100% of actual demanded
lists, but loses to the sibling current FULL split in every selected case, with
separated ranges:1.17–8.87% slower,6.44% aggregate. Its aggregate wall time is
essentially inline (−0.08%), using1.997x inline CPU. High delivery and favorable
serial census slack do not establish profitable end-to-end overlap.

## Frozen scope and identities

Source `579fc36b75c0e76ab76851b984d5ac10b25c6429`;
[fixed plan](plan.md), [samples/counters](results.json), [proof](proof.json).
Raw evidence/build/source archive:
`/home/legolas/rook2-experiments/same-node-inventory-20261024-01/`.
New generic image7,969,864 bytes, SHA256
`57cd0c3d7024587ca43f1c99a23e38750dc5abab269dfbdf39f89c102b7b0fd4`.
Preserved generic control64e01d98 uses **current-split budget2**. New image modes
are inline1/current2/inventory2. Compiler identities/effective flags match:
Rust1.85.1/LLVM19.1.7, generic x86-64 GNU, O3/ThinLTO/one-CGU/panic-abort/debug1,
no PGO. The positive a977 image and f9ee profile are hash-verified unchanged.

Original35/08/04/43: one excluded warmup and three rotated retained observations
per configuration,64 replay lives (48 measured/16 warmups), plus4 separate idle
probes. All replay/raw/PID/accounting checks pass with864 ordered posts. All21
focused tests pass, including exact unsorted inventories, domain/null/stop/error
cleanup, repeated roots, shared-state/N/R equality and serial-journal equality.
No native failure, repair, repeated sample, policy change or tuning occurred.

## Integrated policy

One helper receives an owned Position only at ordinary post-early/TT/FAST,
pre-Influence/FULL admission. The main thread evaluates inline; no Q inventory,
reused-reply, lookahead or simultaneous FULL helper is involved. Private coherent
ancestry, king population and opposite-king check gate early generation.

At original demand, a READY result copies the exact used slice into the native
candidate buffer. A miss stays final: original inline generation runs, followed
by drain/discard before later recursion. Before recursive null entry, settle the
parent and release the slot; its owned local Box survives until actual demand or
discard. Ordering, current learning/TT accesses, terminal checks and generated/N/R
charges remain at original consumption. No unused result is logically charged.

Token/epoch/Position identity and ticket Drop bind lifetimes; all early/stop/error
paths drain safely. The copied parked protocol leaves the positive transport
unchanged. It retains fixedCPU6, active spinning during blocked Host callbacks,
10s wall-abort and production panic-abort limits. Unwind controls cover test-build
behavior, not production panic recovery.

## Complete economics

Median search wall seconds, three retained observations per cell:

| Case | Preserved current2 | New inline1 | New current2 | Inventory2 | Inventory vs new current |
|---|---:|---:|---:|---:|---:|
|35|3.984305|4.442260|4.032438|4.384500|+8.73%|
|08|0.379130|0.389766|0.380429|0.398991|+4.88%|
|04|4.006016|4.416177|4.052621|4.412248|+8.87%|
|43|3.497163|3.518025|3.518822|3.559838|+1.17%|
|Selected sum|11.866613|12.766229|11.984310|12.755576|+6.44%|

Whole-process CPU median sums in the same order:
23.734809/12.771225/23.970869/25.510241s.
Whole-lifetime wall sums:11.887665/12.787246/12.006331/12.777496s.
Inventory is7.49% slower than preserved current. New current costs0.99% aggregate
versus preserved current; this includes routing/refactor/code-layout effects,
not an isolated diagnosis. New inline is a sibling serial baseline, not a new
measurement of old-serial refactor cost.

All three inventory search-wall observations exceed all three sibling-current
observations in each case. All four startup250ms idle probes register0 CPU ticks
at10ms resolution. Search-life RSS medians span19592–19860KiB. Search wall is original go
write through move callback; direct native wait4 CPU/RSS/lifetime includes all
threads, startup/setup, parked lifecycle, joined shutdown and a small Python
pre-exec prefix. Diagnostics use a fresh separate file after joined shutdown,
leaving wire output unchanged. Hot counter/locking cost is in search; final reporting
belongs to whole lifetime/CPU, not the search window.

## Actual demand and delivery

The table totals three retained inventory-mode lives per case. Delivery denominator
is actual original demand (consumed+ready-miss), since busy/domain fallback is0.

| Case | Launches/completions | Useful consumed | Discarded | Demand READY misses | Demand delivered |
|---|---:|---:|---:|---:|---:|
|35|2914443|2224352|690091|256|99.988%|
|08|667440|655859|11581|949|99.856%|
|04|3041754|2335982|705772|115|99.995%|
|43|3199020|2460010|739010|2969|99.879%|

Null settlements/locally consumed parent lists are308832/90429 for35,
321426/68694 for04,342261/30993 for43;08 has0. Only22/25/299 respective null
settlements initially observe not-READY. Those are point-readiness labels, not
measured waiting durations. Every null settlement incurs its one local Box.

Eligible=launches+busy+domain; launches=completed=consumed+discarded;
consumed=direct-ready+local-null; null-settles=null-ready+null-waited all close.
Busy/domain is0 in every life. Eligible, consumed+miss demand and null-entry counts
on35/08/43 exactly match the earlier census in all four inventory lives per case;
physical readiness varies while prescribed search work stays unchanged.

## What this establishes

The candidate really prepares and consumes native lists; inadequate readiness is
not the main observed obstacle. Complete costs include per-launch Arc/key/Position
copies, slot locks/counters, opposite-king admission, helper-to-slot and slot-to-
caller copies, null-path Box allocation/copy/free, duplicate fallback and drains.
The trial does not isolate their individual effects or contention. These are
prototype costs, not inherent lower bounds for every inventory design.

The earlier sequential census correctly identified demand/slack but omitted this
end-to-end delivery cost and the alternative FULL coverage. One helper serves
one policy here; gains cannot be added to the positive FULL image. No threshold,
selector, second readiness policy, Q expansion, PGO rescue or transport retune was
selected from these results. Preserve current FULL as the stronger measured option
and close this inventory variant unchanged.

Four generic workloads and selected tests are finite research evidence, not full
conformance/gameplay/production qualification or scalability proof. CPU14/6,
harness0–5/8–13 and no owned15/7 have point affinity/context evidence, not exclusive
host isolation. No PMU decomposition was collected. Captured stdin write() bytes
exclude end(data) cleanup; pinned runner plus complete output/exit retains that
separate shutdown evidence. No external delivery or follow-on work is selected.

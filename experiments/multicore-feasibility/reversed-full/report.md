# Reversed FULL ownership: park this placement

**Reversal loses on all four selected cases.** Its median search-wall sum is
12.766913s versus11.953181s for sibling current-split: **6.81% slower**, with
6.81% more CPU. All three reversed observations are slower than all three current
observations in every case. Reversal essentially matches inline wall (+0.04%)
while using2.000x its CPU. Preserve the positive current split and close this idea;
no PGO rescue, transport retune or follow-on was run.

## Frozen evidence

Source `d8755d488af5f91870e82a681f8fc6d283fc8653`;
[plan](plan.md), [source/lifetime review](lifetime-review.md),
[results/samples](results.json), [proof/bindings](proof.json).
Raw evidence/build/source archives:
`/home/legolas/rook2-experiments/reversed-full-20261024-01/`.

One new generic image,7,699,696 bytes, SHA256
`9a8b61d265cbf1e8e19f8aeb5f89d56dbd2cb9e1ba638340dd93580b95e02ecf`.
Preserved matched generic control,7,516,224 bytes, SHA256
`64e01d986242f43f2063887b164e06e8201460fd5aefca5d6494a2f4b3634323`.
Control uses its **current-split budget2**, not serial mode. It was copied outside
target before the new build and verified against the prior receipt. All four modes
use Rust1.85.1/LLVM19.1.7, generic x86-64 GNU, O3/ThinLTO/one-CGU/panic-abort/debug1;
compiler identities and effective lib/bin flags match, no PGO.

The positive own-PGO `a977bb00…` image is hash-verified unchanged. Generic
reversal was not compared against it as a performance discriminator.

## Integrated ownership and correctness

A transferable Send8KiB core retains the exact native entries; the serial Rc
journal remains on the coordinator. Reversed mode starts the helper successfully
before taking the actual core, acknowledges installation/reset, and returns the
actual mutated core plus failure information on shutdown/recovery. No successful
serial path selects the empty placeholder. Mode changes transfer once, not per
FULL; only original begin_search clears entries. FRESH bypasses cache mutation,
FAST stays local, and supplied maps/root-side-bound weights stay authoritative.

The shared pawn numerical body serves inline/current/reversed. Reversal returns
weighted structure/progress, pawn R and reuse flag; the coordinator joins before
retained writes, combined R/stat publication, observers and finishing. An abandoned
output does not discard completed native cache mutations. Cold test snapshots copy
state for assertions; production FULL does not copy the8KiB core per call.

The existing parked protocol was mechanically copied into a separate pawn-worker
module, leaving the proven Activity worker untouched. This duplication is research
debt, not a selected transport redesign. Only one helper runs at a time; conflicting
CLI modes/nested mechanisms reject. Serial branch-journal admission rejects reversed
ownership before any Search attachment mutation rather than losing observer events.

All31 unique focused tests pass, plus two targeted reruns after strengthening the
already passing mutation controls to require nonempty changed state. Tests cover
components, retained/R values, both diagnostics policies, asymmetric/zero weights,
contrary maps, collisions, FRESH, reset, repeated roots, mode transfer, node/host
stops, test unwind, abandoned output and post-selection failure recovery.
All64 original replay lives pass with864 ordered posts;48 retained observations
and16 excluded warmups. Independent receipt/raw replay reconciliation also passes.
No native failure, retry or source/parameter retune occurred during collection.

## Cost results

Median search-wall seconds, three retained observations per cell:

| Case | Preserved current2 | New inline1 | New current2 | New reversed2 | Reversed vs new current |
|---|---:|---:|---:|---:|---:|
|35|4.023291|4.467163|3.998312|4.336682|+8.46%|
|08|0.379925|0.392853|0.382297|0.408794|+6.93%|
|04|4.046294|4.424054|4.025358|4.362701|+8.38%|
|43|3.496462|3.477426|3.547214|3.658736|+3.14%|
|Selected sum|11.945973|12.761495|11.953181|12.766913|+6.81%|

Whole native CPU median sums are23.893759/12.765836/23.908168/25.535798s in the
same column order. Whole-lifetime wall sums are11.967900/12.782156/11.974549/
12.788397s. RSS medians span19480–19792KiB across configurations/cases.
All four startup250ms idle probes register0 ticks at10ms resolution; startup and
shutdown distributions/boundaries remain in results.

New current is+0.06% aggregate versus preserved current, with per-case changes
−0.62%/+0.62%/−0.52%/+1.45%; those small differences do not isolate a cause.
Numerical extraction now groups structure/progress before local Activity rather
than the older inline ordering. New-inline versus the parallel control is **not**
a measurement of old-serial refactor cost. Sibling inline/current/reversed and the
preserved current control make the actual comparisons explicit.

Search wall spans original go write to move callback. Direct native wait4 CPU,
RSS and lifetime include all threads, startup/setup/parking/joined shutdown and a
small pre-exec Python prefix. Coordinator14/helper6, harness/build0–5/8–13, owned
siblings15/7 unused. Affinity checks and guest context do not establish exclusive
host isolation. No PMU or component-latency decomposition was collected.

## Interpretation and limits

The latency-placement hypothesis was plausible but this integrated ownership swap
does not improve the selected search. The trial prices complete publication,
cache ownership, execution and finishing together; it does not prove which cache,
scheduling or local-chain cost explains the regression. Do not infer an impossibility
result for all ownership designs, or select a second variant from this outcome.

Keep the positive parked own-PGO split and the negative branch/child-queue records
unchanged. Park this reversed placement without qualification/adoption claims.
The finite generic workload and focused tests do not replace broad conformance,
full gameplay, production-PGO or scalable multicore evidence. Active Host blocking
can still leave a helper spinning; fixedCPU6 and10s wall-abort remain. Test-profile
unwind recovery is not production panic-abort recovery. Input tap still excludes
end(data) cleanup bytes; pinned runner plus complete output/exit checks retain
that separate shutdown evidence. No external delivery or further native work is
selected by this closure.

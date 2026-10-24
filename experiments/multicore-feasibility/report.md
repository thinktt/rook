# First FULL split: promising kernel overlap, integrated cost unproven

Keep the accepted serial engine and try one narrow integrated experiment:
Activity→Shelter on a persistent worker, with pawn/cache work and authoritative
commit on the coordinator. The standalone single-call split reduced elapsed
time by 15.77% (1.187x throughput) while using 69.42% more process CPU. This is not
a production search speedup; packet publication could erase this small margin.

## Measured result

All 162 sequential comparisons with the actual `Evaluator` passed, including
components, scores/bounds, pawn-cache reuse, relation counts and retained outputs.
The worker's complete Activity/Shelter values matched direct calls. All 30 timed
sample checksums matched. Each row has three 172800-item samples after a short
excluded warmup; every sample is retained.

| Mode | Elapsed median ns/item | Range | Process CPU median ns/item | Speedup vs direct |
|---|---:|---:|---:|---:|
| Synthetic empty direct |4.08|4.07–4.22|4.08|—|
| Synthetic empty roundtrip |159.92|155.90–163.48|321.94|—|
| Activity→Shelter direct |350.98|350.39–351.25|350.96|1.000x|
| Activity→Shelter remote,1 item |509.85|509.35–510.12|1018.60|0.688x|
| Composed FULL direct |597.75|597.17–599.49|597.72|1.000x|
| FULL overlap,1 item |503.51|502.78–507.64|1012.67|1.187x|
| FULL overlap,8-item packets |396.43|393.55–397.80|789.90|1.508x|
| FULL overlap,32-item packets |380.19|376.36–381.31|750.51|1.572x|

The empty row is a synthetic protocol observation, not a subtracted overhead.
Sending only the chain to another core makes its latency worse; useful overlap
with the coordinator's mandatory work is what produces the FULL result.
Batches8/32 are a throughput ceiling for independently available fixed packets,
not a demonstrated batch in the prescribed search order. The chain-only batch
results remain in the raw report; they do not beat direct single-core latency.

One stream finished with exit 0, 1.970s whole-process elapsed and 3.327s child CPU.
Whole-process peak RSS was 25340KiB; no per-thread memory delta was measured.
Coordinator affinity14 and worker affinity6 were set and read back by the native
harness. Guest topology reports sibling pairs14/15 and6/7. Owned work was not
assigned to7/15. `/proc/stat` shows zero user/system ticks on7 but one additional
user tick on15 during the enclosing snapshot: this is not exclusive host or
sibling-idleness proof. No PMU measurements, tuning sweep or sample retry occurred.

## Exact boundary and objections

The 54 public root positions are reconstructed from their complete legal move
histories. Kernels use one fixed neutral starting-position RootContext and neutral
weights. Influence uses the public scalar producer and is prepared before timing;
production search's coherent producer is not measured. Material and the maintained
nonking-square subtotal are also prepared. No engine source was modified; this
standalone driver composes the same numerical kernels and finisher.

**The worker reads a pre-shared immutable 54-position corpus by index. There is no
fresh Position/Influence packet publication or copy.** Real integration must price
publication, ownership/lifetime management and newly produced cache-line transfer.
The experiment does include counter handoff, output storage/locking and result
join. It therefore establishes feasibility, not an integrated net saving.

It omits real full/fast selection, search-entry state, Influence construction,
restoration, logical-charge publication, host polling and wire service. The cache
is real and follows the exact standalone stream, but that stream is not a search's
cache-hit/replacement distribution. There is no PGO, and read-only prepared data
has unusually stable locality. Three short samples cannot establish broad hardware
or workload robustness; some cheap synthetic samples are under 1ms.

One-thread direct mode has no worker. The parallel mode uses two total threads,
including the coordinator, and busy-spins while waiting. A production worker
spinning between FULL calls could consume an extra core for most of the search;
do not extrapolate the probe's CPU ratio to that lifecycle. OS parking on every
sub-microsecond call could remove the gain. Persistent lifetime and idle policy
belong in the integrated cost measurement.

## Dependency and cost sketch

After fixed Position, the exact supplied Influence, root material and weight pairs:

```text
worker: Activity → Shelter ──────────────────────────┐
owner: PawnCache.select → pawn terms/progress         │
       central/patterns/squares ─────────────────────join
owner: tempo → component composition → retained writes → finish
       relation ledger updated once at its existing owner
```

Source owners are `evaluator.rs:384–483`, `activity.rs:94–157`,
`shelter.rs:52–73`, and `pawn_structure.rs:95–135`. The worker returns complete
Activity/Shelter scratch values, including R counts. It does not mutate pawn cache,
TT, learning, clocks or host-poll state. Cache hits retain previous descriptors
and chronology; fresh recomputation is not equivalent. Tempo needs Activity pieces
even at zero mobility weight. Preserve existing rounding and relation-charge
boundaries; physical speculative work is not automatically prescribed work.

Current node inventories are Position-only. Initial priorities become independent
only after a fixed learning/TT snapshot. Future siblings cannot borrow that snapshot:
earlier consumers change learning/history and TT state. Mate/IIO ordering probes
perform prescribed recursive work and are not a parallel score-map batch. See
`movegen.rs:272,645`, `ordinary.rs:750,876,954,1138`,
`ordinary_policy.rs:406,497`, and `tactical.rs:269,338`.

Do not parallelize trivial per-move priority calculations or six sorting streams
first. Existing parked sorting variants gained only about 0.31–0.33% on their generic
screens. Checked bounded generation usually stops after two witnesses; making it
eager would add unused work. Simulated instruction shares (Activity 20.742%,
Shelter 4.898% in historical case35) are not native time fractions; that original
strict profile also failed a two-Ir reconciliation. The old 8.307µs functional
sequence includes 17 mixed full/fast observations and other work, not one FULL call.
These sources motivate investigation but cannot supply a whole-search budget.

## Recommended first integration

Add a private shared numerical seam for Activity→Shelter, with one-thread inline
execution and an optional one-worker path for confirmed FULL calls. Keep root
weights, actual material, Position and supplied Influence coherent in a reusable
owned packet. Keep cache selection, final retained writes, finish, R publication,
TT/history and all polling on the coordinator. Join before leaving the call or
reusing its scratch. Exercise default/nondefault and zero weights, supplied maps,
cache hits/collisions and lazy-full refresh boundaries in focused comparisons.
Measure complete owned calls and one small deterministic search sample, including
packet publication and idle CPU; do not select a production layout from this probe.

If that loses its margin, same-node legal inventory generation overlapping FULL
evaluation is the coarser reserve: join/discard before recursive null/mate/IIO,
retain the inventory for its original consumer, and publish generated counts only
there. It offers more independent work but wastes work on early returns and must
prove early geometry execution safe for admitted native inputs. This reserve was
source-inspected only; no second timing matrix or integration was started.

Raw artifact, histories, plans, full samples and receipts:
`/home/legolas/rook2-experiments/multicore-feasibility-20261024-01/`.
The compiled probe is an ordinary generic x86-64 O3/ThinLTO build, no new dependency
or PGO. [results.json](results.json) binds its concise outcomes and raw hashes.

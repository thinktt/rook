# After epoch3: conditional ordinary inventory on a fourth thread

2026-10-26. Source/existing-evidence assessment only, following PGO closure
`fb243a4c7b8f1e97f5c5c700d1675d6191127722`. No engine edit, prototype, build,
measurement, qualification or adoption. One disjoint Sol reader challenged the
conditional-reader protocol; Imp2 assessed the caller, scratch and costs.

**Recommend one post-Influence colors+inventory4 discriminator.** Preserve the
positive two side producers; add exact ordinary legal generation as a conditional
third reader of their existing immutable packet. This adds independent work rather
than replacing the successful FULL overlap. There is no source-level blocker;
profitability remains unmeasured. Retain exact epoch3 `67d01108` and generic
`7ac72fc6`, all previous images/profiles, and existing modes1/2/3.

## Admission and original consumption

Use a private ordinary-only wrapper at the confirmed FULL call in the frozen
source (`ordinary.rs:813–814`). Pass the Search-owned coherent-geometry permission;
root/public FULL, Q, FAST, FRESH and diagnostics that merely call public FULL do
not request inventory. Keep `ensure_influence_for_search` at its original demand:
scratch Some remains authoritative, scratch None builds once and charges once
(`evaluator.rs:522–548`). Post-Influence publication is the initial design.

The conditional helper rechecks the old early-generation domain: coherent caller,
exactly one king per side, and the opposite king not attacked by the current side
(old `579fc36b` evaluator974–976). Only then invoke unchanged
`movegen::generate_legal`. Domain rejection returns an explicit unavailable result; original
serial generation remains the fallback. Guard arithmetic is paid, even if moved
off the coordinator. Worker failure is terminal, never silently treated as a domain
skip or a successful empty inventory. Ordinary checked positions remain eligible when these guards
hold. Root/Q placement coherence alone does not admit extra generation.

Generate directly into one initialized, helper-exclusive `MoveList` output cell;
never borrow the whole Cells container mutably. The coordinator acquires completion
before copying only its used slice and length into `self.candidates[p]`. No per-call
Arc/key/Position allocation, owned-list return/Box or full512-slot copy is required.
Native output writes, the one used-list transfer, cache ownership and capacity
checks remain real work. An unavailable result never marks the row prepared.

Carry an activation-local prepared flag; at `ordinary.rs:867–876` skip only the
producer when true. Count/generated charges, empty/mate checks, current TT/learning
ordering and extension initialization stay at original demand. Unconsumed physical
work makes no semantic N/R/generated charge. No helper reads or mutates pawn cache,
learning, TT, retained evaluation, work clocks, host polling or diagnostic ledgers.

## Conditional participation: separate sparse request, not an empty job

Keep the existing colors request epoch and two matching color done epochs. Add a
private inventory request/done pair and a private Flight participant flag. Inventory
reads **only its own request**. A colors-only FULL leaves that request unchanged:
it needs neither an inventory store nor a fabricated inventory acknowledgment.
A later ordinary request can jump over arbitrarily many colors-only generations.
Epochs remain checked/nonwrapping and all readers start before publication.

For an admitted ordinary request e:

1. Under Control and Flight None, prepare the complete immutable Packet, including
   Position/Influence/timing. Record Published(e, inventory=true). Publish the
   existing colors request Release and inventory request Release. All validation,
   allocation and other fallible preparation must precede these stores; no partial
   publication may be rolled back to None.
2. Each color reader acquires its own existing request, finishes every Packet
   access and publishes its separate output/done as today. Inventory acquires its
   sparse request e, checks Packet generation, performs guard/generation, ends all
   Packet references and output writes, then publishes inventory done(e) Release.
   Inventory does not chase the latest colors epoch or borrow unrequested input.
3. Split current `complete`: acquire/copy both color outputs under Control and
   retain a Joined(e, inventory=true) flight instead of setting None. Run the
   unchanged weighted merge, tempo, retained updates and FULL finish on the
   coordinator. The inventory producer overlaps this remaining composition.
4. Settle inventory after numerical FULL, before the wrapper returns and before
   any recursive null call. Acquire matching inventory done, recheck flight/token
   and terminal status under Control, then copy its used list (or unavailable
   status). Finish all output reads before setting Flight None. Colors-only calls
   retain their two-reader completion/retirement path.

Current `colors_worker.rs:404–461` retires the packet in complete, before final
FULL composition; it cannot be reused unchanged for a participating third reader.
Likewise `both_done` at633–635 must remain a **two-color predicate**. Extending
its array iteration to three would require an empty acknowledgment on every
root/Q FULL. Lifecycle all-state/quiescent/start/join loops, in contrast, must
cover every actual configured helper.

The input edge is Packet writes → request Release/Acquire → each actual borrow
→ matching done Release/Acquire → next input write. For sparse inventory epochs,
its previous output is fully consumed before a later inventory request Release;
that Acquire supplies the reverse edge before its next output overwrite. Skipped
colors epochs introduce no inventory borrow or output write. Flight None therefore
requires both colors plus inventory **only for the recorded participant set**.
A slow last inventory reader blocks reuse even if both colors already finished.
Discard/retirement must handle Joined as well as Published; sampled color completion
must not be charged twice if a Joined flight is later discarded.

Keep exactly one coordinator completion waiter. Both completion stages use the
reviewed Sleep mutex/predicate/SC registration chain sequentially; each actual
inventory done/terminal publication performs the same unconditional SC latch
exchange as color publishers. No empty publication for skipped epochs. A missing
optional notification is not an adequate protocol.

Final scope close claims Discarding under Control and waits for all actual helpers
to be parked/exited, not merely one terminal flag or two color completions. The
inventory park predicate compares its **private** request with its last seen epoch:
no pending inventory job may be acknowledged as parked; skipped colors epochs do
not keep it artificially busy. Stop/failure retires only the exited reader's own
references. Shutdown joins all started readers before input reuse/destruction;
startup partial failure joins those actually started. Completion holds neither
Control nor Sleep while waiting on the other lock. Preserve the terminal/no-reset
path at epoch exhaustion. Production panic-abort remains terminal, not unwind
recovery.

The private ordinary wrapper must hold its one-call scope, if any, through inventory
settlement: current `evaluator.rs:695` closes that scope before final composition.
An outer Search scope normally exists, but correctness must not silently depend
on it. Cold/close/terminal controls are needed for the new participant, despite
reusing the existing two-reader proof.

## Why early installation needs no parent-list allocation

Settle and install after FULL, before bounds/threat/null handling. Between
`ordinary.rs:814` and original generation867, no native consumer reads row[p].
Recursive null enters p+1 at841–856; its descendants use higher rows. Q bounded
replies use ply+1 (`quiescence.rs:447–450`); ordinary IIO occurs after original
generation and also descends. The reused-Q-list authority is produced by its own
parent, not inferred from an old row length. Early bound/null/stop returns expose
no candidate scratch (`engine.rs:92–105` describes this private boundary).

Thus the parent's prepared row survives null continue without a Box/restore, while
null cutoff simply discards its flag. Next ordinary generation clears length when
not prepared. Do not retain packet ownership across null recursion, install an old
length, or move sorting/generated charges earlier. This reuses the concrete
[prior scratch proof](after-colors-dataflow-choice.md); it does not admit arbitrary
eager children or strengthen public/custom-position geometry permissions.

## Costs and actual available window

Let I be required Influence construction; P publication; E the post-publication
colors/owner critical path through color acquisition; F remaining FULL composition;
G native generation; D inventory guard; L its pickup/cache delay; J acquisition
and retirement bookkeeping; T used-list installation. A schematic consumed node:

- Epoch3: `I + P3 + E3 + F + G`.
- Combined4: `I + P4 + max(E4 + F, L + D + G) + J + T`.

The max already includes waiting. E4 is not assumed equal to E3: a third packet
reader/output writer and extra core can change locality, bandwidth and timing.
For an early-return node, original G was absent; extra guard/generation/retirement
and possible transfer are waste. Extra request/done stores, a completion SC RMW,
participant/stage metadata, conditional done checks, output cache traffic and
inherited lifecycle are all priced. Startup adds one thread; active search can
burn its core while no ordinary request is pending, even though root/Q pay no
empty acknowledgment. Outside owned scopes it must really park. No claim of
free fourth-core work or additive speedups.

| Existing observation |35|08|43|
|---|---:|---:|---:|
| Ordinary eligible census entries |971481|222480|1066340|
| Original inventory demand |76.33%|98.41%|76.99%|
| Native generation median, consumed no-null ns |370|191|250|
| New PGO all-FULL owner-ready mean ns |388.65|243.93|161.51|
| New PGO all-FULL latest-side minus owner positive mean ns |167.20|97.87|245.63|
| New PGO complete-entry→outputs acquired mean ns |264.56|189.19|347.03|

The first three rows are the old serial, instrumented
[inventory census](../../experiments/multicore-feasibility/inventory-overlap/report.md).
Its interval included Influence and serial FULL, which this post-Influence worker
cannot claim. The final three rows are sparse512 PGO observations across **all**
FULL calls, not matched ordinary inventory pairs; they omit publication and final
composition and have observer/layout effects. They suggest a short hundreds-of-ns
contest, not proof that guard+generation+transfer fits. Do not subtract medians from
means, multiply samples into predicted seconds, or run another census just to
rediscover the already established demand.

The [negative inventory2 trial](../../experiments/multicore-feasibility/same-node-inventory/report.md)
had99.86–100% delivery yet lost6.44% to current FULL. It replaced that FULL helper
and paid Arc/key/duplicate list/null Box costs. This proposal retains both positive
side consumers and removes those specific ownership costs; it still pays guards,
publication, discard, used-list transfer, third-reader cache traffic and idle CPU.
The negative remains evidence against assuming readiness implies profitability.

## Smallest informative next trial, if selected

Use one isolated generic integration and existing measurement/closure machinery:
preserved generic epoch3 plus same-image modes1/2/3/4 on original35/08/43, fixed
small rotated schedule and separate idle probes. Preserve positive PGO67d011;
no new PGO or broad qualification campaign. Verify cap/default/actual placement,
exact unsorted lists, generated/N/R/retained/cache equality, ordinary checked and
special moves, root/Q no-request, unavailable fallback, long skipped sequences,
last-reader delay, both close/dispatch orders, staged completion/unwind/failure,
output reverse edge and null continue/cutoff. This is focused validation of the
new seam, not a repeated suite for unchanged arithmetic.

Sparse observations should bind actual inventory-ready to the same node's FULL
numerical-complete and original demand/discard; report waits/installation and total
CPU, not merely ready percentage. Measure ordinary consumed/discarded jobs apart
from root/Q nonparticipation. No nested pool, readiness policy sweep, Q expansion,
color rebalance or staged-input variant is needed for the first discriminator.
No implementation or native lane is authorized by this recommendation itself.

Position-before-Influence publication is a separate reserve: it offers a larger
window but needs distinct field cells/readiness or a Position-only publication.
Never mutate Influence through a whole Packet while any reader borrows that Packet.
Likewise applying epoch ownership to the whole Activity/Shelter one-helper kernel
is credible but separate: it may improve mode2 without adding work, whereas this
trial tests genuine fourth-thread overlap. The memo's transport-generalization
reserve remains unselected; neither a general worker framework nor mode2 transport
replacement belongs in this experiment.

Source pins: the exact64 map is bound by
[PGO preparation](../../experiments/multicore-feasibility/epoch-own-pgo/preparation.json)
and [closure](../../experiments/multicore-feasibility/epoch-own-pgo/closure.json);
source root is `/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01`.
All line references above are to that frozen map, except the explicitly historical
guard. Current recommendation changes documentation only.

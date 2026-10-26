# Execution architectures after fusion

2026-10-26, imp2. Source/existing-evidence review under mission730d6fbe;
**no implementation or native work selected by this document**. Two independent
Sol readers reviewed (1) released arithmetic dependencies and (2) borrowed-input
lifetime feasibility. Imp2 compared their findings with the lead's completed
[replicated-control challenge](/home/legolas/agent-memos/imp2-lead-replicated-control-challenge-20261026.md).

**Recommend a one-epoch, type-disjoint Activity reduction as the next scaling
prototype.** It creates a third demanded arithmetic shard instead of making
another side consumer or predicting branches. Borrowed input is a credible,
smaller transport experiment, but creates no additional parallel work. Replicated
control tests a materially different locality/latency hypothesis at much greater
state and memory cost. None has an established speedup.

## Required order versus current boundaries

Source shorthand W: the exact64-file positive epoch workspace
`/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01`, bound by
[epoch preparation](../../experiments/multicore-feasibility/epoch-colors/preparation.json).
This is not canonical research source or the parked fusion derivative. S: released
`/home/legolas/king-spec/spec`, commit1c89c21a4645ec85adf28285616d822b3cd91f73.

| Prescribed dependency | Implementation freedom |
|---|---|
| Candidate windows/order/extensions consume earlier results; TT queries can mutate state and replacement/ties matter. | A different controller is allowed, but independent branch results cannot simply be installed. S ordinary-iterations:283–345; remembered-results:39–93. |
| Pawn selection consumes earlier ordered cache state, including zero identities/collisions/retained order. | One owner may hold the cache independently of pure arithmetic. S search-pawn-sequence:54–66. |
| Exact FULL score/retained effects and R must be available before their search/clock consumers. | Pure subexpressions need not run serially or on the thread that commits them. S activity:184–220; work-clock:11–27,83–93. |
| Activity pressure feeds shelter composition; per-piece and final rounds are prescribed. | All four piece kinds need not share one loop; shelter geometry need not wait for pressure. W activity:221–238,513–568; shelter:130–138,314–325. |

The prior [wide replay](../../experiments/multicore-feasibility/wide-internal/report.md)
negative prices one real effect-validation architecture. It does not turn these
state dependencies into a proof that every alternative controller fails. Equally,
a rewrite cannot make those dependencies disappear.

## 1. Type-disjoint raw reductions: new demanded width

Keep one immutable FULL publication and the owner's ordered pawn/local work.
Replace two whole-color helpers with three arithmetic helpers. Partition the
eight `(color,N/B/R/Q)` jobs into three fixed shards; **every whole color/kind
belongs to exactly one shard**, including all promoted same-kind pieces. Freeze
one assignment before data; balance remains a measured risk, not an assumed win.
Each shard returns raw piece sums[2], unclamped admitted pressure sums[2], R and
any uniquely assigned shelter-geometry Components. No queue or peer barrier is
needed; join once and compose on the owner.

This is stronger than arbitrary piece splitting. Marks are type/weak/strong
presence, ORed across pieces (W activity:300–303; S activity:154–180). Distinct
kind shards own disjoint bits, and the admitted pressure lookup is additive in
those bits. Each can scan the same king geometry using the original global piece
counts and return its raw pressure contribution. Their scalar sums exactly equal
the union's admitted mark sum; no128B mark-array reduction is required. Splitting
two pieces of the same kind across shards would invalidate that shortcut.

Preserve each piece's mobility/curve/penalty rounds. Sum raw scores before the
single `floor((276*S+128)/256)` per color; sum raw pressure before subtracting12
and clamping once. Preserve all weighted Activity rounds. Shelter Components are
pressure-independent; compose each complete side only after final pressure, then
keep its original cross-color round. Sum semantic R once, including repeated
charged queries; commit retained/stat/clock effects at the native owner boundary.
Public/supplied-map domains and serial arithmetic must remain authoritative.

Useful overlap comes from dividing the existing late Activity chain, including
FULL calls outside ordinary move-generation admission. The retained generic
report's sampled latest-side-minus-owner gaps are159/106/243ns for35/08/43
([boundaries](../../experiments/multicore-feasibility/epoch-colors/report.md)); these
support the hypothesis, not a recoverable-time budget. Extra pressure scans,
third-reader retirement, skew and the larger owner reduction can erase it.

Smallest decisive prototype: one shared extracted arithmetic body, inline and
new4-thread modes, preserved epoch3 and a matched new3 control; one small original
35/08/43 comparison after focused raw/rounded output, same-kind duplicate marks,
weak+strong coexistence, pressure12 threshold and R/retained checks. Price all
reader/reduction costs in actual search. Reuse the epoch ownership protocol and
existing collection, without a census or scheduler framework. No PGO initially.

The failed fusion added row production, three map copies and a peer barrier;
this keeps the already-available map and has no inter-helper dependency. Inventory4
left the late two-color kernels unchanged; this divides them. The negative
results warn about fine grain and layout, but do not test this arithmetic graph.

## 2. Lexically borrowed FULL inputs: simpler transport hypothesis

The owned Position/128B Influence copy is at W colors_worker:360–365. Kernels
need only shared immutable inputs, and the owner joins before retained changes
(W evaluator:602–695). Replace that copy with pointer-descriptor publication,
while retaining scalar metadata, exact supplied maps and the same two side chains.

Use an enclosing internal API such as `with_borrowed_epoch(inputs, owner_closure)`
returning owner results plus joined helper results. Its inaccessible armed guard
must drain before returning or unwinding; split evaluator fields so the closure
can mutate pawn/local state without borrowing the worker again. A publicly safe
returned Drop token alone is insufficient: `mem::forget` can end its compiler
borrow while helpers still run. Do not transmute references to static lifetime.

Every error path must retire both actual readers before the input borrow ends.
Current complete returns on terminal before draining its peer (W colors_worker:
409–426), and an outer active search makes start_call_scope return None (318–324).
That scope is activation ownership, not a per-input lifetime proof. Normal
abandonment can wait/discard this epoch; terminal paths wait for real exits.
Keep Control flight ownership, all input references ending before done Release,
matching done Acquires, reverse output reuse and the sole coordinator waiter.
Do not add a background drain waiter to the single-bit latch protocol. Test-build
unwind drains without a second panic; production abort is process termination.

This removes destination writes/copying, not request/done traffic, input cache-line
transfer or side arithmetic. Caller stack/Node placement may worsen sharing.
Existing sparse clocks start after the copy and cannot price its removal.
Smallest test: preserved3 / matched scoped-owned3 / scoped-borrowed3, same kernels
and small original cases; delayed reader during owner unwind, one-reader failure,
outer active scope, concurrent close and reuse are the decisive lifetime controls.
This is a reasonable precursor if transport simplicity is the priority; it is
not evidence of scaling beyond two arithmetic helpers.

## 3. Replicated controller with collective FULL: locality without packet input

The lead/Astra design is semantically plausible: each lane executes identical
search/TT/learning control, master alone owns PawnCache, and lanes compute their
assigned FULL arithmetic from local inputs. Allgather role scalars once, then
finish/update search-visible state identically on every lane. Do not add a second
master-final-score broadcast. Preserve full table geometry per lane, chronological
position state, logical N/R and each reset/stop boundary. Host acquisition/poll/
post/error effects eventually require one authority and ordered broadcasts.

It removes both owned and borrowed input publication and may give helpers local
inputs sooner. It adds two traversals of control, Influence construction, TT and
finishing, approximately three full-sized TT allocations, scalar collective
latency and arrival skew. Existing helpers spinning does not make that memory
traffic free. Private normal search state is a sufficient deterministic base;
unused follower pawn caches must never be read. Double-buffer scalar retirement
needs its own reviewed reverse-edge/cancellation proof, not forged ready counts.

The smallest decisive test is actual fixed-completion NoHost/timing-absent search
with three existing Search instances, unchanged full-sized TTs, role FULL and one
scalar collective. Audit collective sequence/inputs/output/N/R and final relevant
state against serial, then disable expensive audits for a small matched serial/
epoch3/replica measurement. Eval replay alone omits the duplicated work at issue.
Borrowing cannot answer whether eliminating publication plus local input readiness
beats replicated-control cost; replicas cannot identify the copy cost alone.

## Comparative decision

Type-disjoint reduction is the best next **scaling** question: it exposes actual
additional independent work without search speculation or TT replication. Borrowed
input has the smallest transport/state cost and should precede a replica trial
if the immediate question is packet-copy latency. Replicated control is a valid
bounded architectural discriminator, with modest/negative expectation rather
than a reason to start a greenfield rewrite. Do not combine these mechanisms in
a first experiment or reinterpret a loss in one as rejection of the others.

All baselines and parked dispositions remain unchanged. This review used source
and existing reports only: no engine edits, native measurements, build,
profile, census or benchmark. The next prototype remains the lead's selection.

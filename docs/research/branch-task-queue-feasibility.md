# Branch-task queue: bounded source recommendation

2026-10-24. Source only; no executor, engine change, build or run. Preserve the
[positive FULL-worker baseline](../../experiments/multicore-feasibility/integration/report.md).
Recommend **optimistic whole-branch transactions**, first on the restricted root
tail, with canonical ordered semantic validation. Queueing alone does not make
branches independent, but the source does not rule out useful validated reuse.

| Task class | What can run ahead? | What it demonstrates |
|---|---|---|
| Ready-only whole branch | The actual next call with settled inputs and authoritative shared-state view | Scheduling without changing computation; current DFS exposes no proven independent sibling calls |
| Speculative whole branch | Complete recursive execution on private state using proposed inputs | Real branch reuse if its demand, inputs and influential operations validate later |
| Pure prefix or salvaged result | Placement, check geometry, supplied-input Influence/Activity and similar pure calculations | Preparation despite changed branch decisions; **not** adoption of the searched branch |

“Window already known” is weaker than “execution ready.” The first two
unrestricted root attempts have settled windows; known seed adjustments remain
part of their exact Requests. They still share unresolved TT/learning/pawn effects.

## Concrete boundaries

- **Restricted root tail:** policy is frozen at iteration entry; tail order is
  fixed after child0. Initial nonfirst attempts use `aspiration(best, previous)`.
  A non-best completion leaves that proposed window unchanged. Enqueue the tail
  after the first completion, predicting unchanged best, then validate at each
  canonical turn. This is plausible window stability, not exact readiness.
  Source: [root_schedule.rs:82](../../src/root_schedule.rs:82),
  [:111](../../src/root_schedule.rs:111), [:143](../../src/root_schedule.rs:143).
- **Ordinary child:** settled parent Node/map/history, movement and full inventory
  do not settle the frontier skip, best/lower, full/scout window or retry.
  Tail IIO can reorder the unconsumed suffix after child0. Scout retry uses the
  same refreshed child; a transaction must retain it rather than reconstruct it.
  Source: [ordinary.rs:954](../../src/ordinary.rs:954),
  [:1006](../../src/ordinary.rs:1006), [:1041](../../src/ordinary.rs:1041),
  [:1092](../../src/ordinary.rs:1092).
- **Q child:** earlier siblings can change optimistic best, admission and lower;
  the next child upper is `-lower`. Q recursively stays Q, with no TT or history
  recording, but reads learned history, selects/mutates pawn cache and clears
  next-ply killers. Ordinary mate probes offer a simpler validation fixture:
  their Q window is fixed `[-9000,-8999]` until success ends the loop.
  Source: [quiescence.rs:317](../../src/quiescence.rs:317),
  [:359](../../src/quiescence.rs:359), [:449](../../src/quiescence.rs:449),
  [ordinary.rs:898](../../src/ordinary.rs:898).

Null and IIO calls are prescribed recursive work, not disposable preparation.
The timed root transaction must also preserve one ActualChild across aspiration
retry and keep per-pass boundaries; parent adaptation/publication remains ordered
([timed_sequence.rs:43](../../src/timed_sequence.rs:43),
[timed.rs:609](../../src/timed.rs:609)). Identify tasks by search epoch, parent
activation, immutable candidate ID, phase/pass and occurrence—not position hash
or current sorted index. Include full Position chronology, retained state, exact
Request/predecessor, history/arrivals, root parameters and geometry provenance.
`replies_available` additionally binds the produced reply inventory.

## Semantic validation and ordered state

Keep worker writes private. At actual consumption, require the branch still be
demanded and its exact entry tuple match. On a staged current-state overlay,
replay the task's influential shared operations in their original order and
compare the results consumed by search. Commit that staged state and validated
Node/PV/trace/work outputs only after complete validation; otherwise discard and
execute the canonical call. Never partially modify authoritative state during
validation, and never install speculative final table bytes.

Exact byte read-set equality is sufficient only with a complete external footprint,
including read-modify-write operations. It is unnecessarily strict when irrelevant
cells changed. Semantic replay can accept more:

- Replay native TT `probe(Query)` and compare the complete ProbeResult, not just
  score. Apply its actual mate-depth mutation to the staged current table.
  Replay `store(Store)` against that table's current replacement state. A store
  returning `()` does not permit omitting its effects. Later probe observations
  must agree. No matching snapshot of the entire group is inherently required
  ([remembered.rs:109](../../src/remembered.rs:109),
  [:192](../../src/remembered.rs:192), [:230](../../src/remembered.rs:230)).
- Preserve pawn selection's returned descriptors, order and reuse flag. “Miss
  remains miss” can tolerate a different overwritten payload; an identity hit
  can retain deliberately different descriptors. Validate the actual selection,
  not just pawn placement ([pawn_structure.rs:95](../../src/pawn_structure.rs:95)).
- Replay killer clears and native learning records, including global history
  rescaling. Validate the ordering observations actually used—initially full
  priority outputs conservatively, potentially the complete resulting ordered
  inventory if that is the only later consumer. Merely matching a selected move
  is insufficient ([ordinary_policy.rs:21](../../src/ordinary_policy.rs:21),
  [:403](../../src/ordinary_policy.rs:403), [:406](../../src/ordinary_policy.rs:406)).

Private scratch/PV and internal read-after-write dependencies belong to the
transaction; do not validate an internally produced value as an external read.
This is a conditional reuse argument: a complete operation boundary inventory
and measured cost remain to be established. See the
[lead's independent challenge](multicore-lead-review.md).

## Strongest first test, concurrency and limits

Use an **actual eligible restricted iteration**, preserving its serial prefix,
native policy/order and known seed adjustments. First experiment: a fixed-completion
NoHost adapter reusing the native scheduler and recursive kernel, with timing absent
and no internal node limit. Let speculative root candidates execute complete branches,
including any retry, with private state and staged semantic replay. Compare final
state, ordered per-pass outcomes/PV and rebased N/R against the same serial adapter.
This omits live clocks, polls and partial stops deliberately; it is not production
wire fidelity. Do not force fake work counts merely to select Restricted policy.

The broader queue can recursively admit descendants, but they must validate into
their owning transaction before that ancestor validates globally. Use one total
thread budget, bounded speculative frontier and private/snapshot state; disable
the separate per-evaluator worker inside branch workers. Workers must help execute
ready queue work or suspend continuations while waiting—blocking every worker on
queued descendants deadlocks. Root-tail width and descendants offer possible
concurrency beyond two; useful accepted concurrency is **unmeasured**. Count
accepted/discarded/reexecuted work, queue starvation, snapshot/log/replay cost,
memory and elapsed/CPU scaling before choosing a snapshot representation. Full
TT copies per recursive task are not a credible assumed cheap operation.

Main failure modes are best/window changes, retry/IIO phase mismatch, cache/learning
conflicts, cutoffs cancelling demand, stale epochs, validation approaching search
cost, speculative explosion and head-of-line waits. Pure-result salvage remains
an explicit alternative if whole-branch acceptance is poor, not a relabelled success.

Timed/live-host support needs more than scalar work deltas. Admission checks limits
before charging; polls follow each 4096th credited node. Changed canonical start N
shifts poll locations. Status uses the active history path; Time/Post/Easy alter
controls, and stop can retain only preceding effects. Later support needs an ordered
charge/poll/effect journal with interrupt-prefix state, or conservative rejection
of tasks crossing those boundaries—not just matching final counts
([work_clock.rs:5](../../src/work_clock.rs:5),
[timed.rs:400](../../src/timed.rs:400)). NoHost alone does not remove timed clock
checks: the proposed initial adapter must also have timing absent. A cheaper
subsequent Q-only rule can reject any span crossing a canonical poll or node limit;
that is a restricted adoption mechanism, not complete interruption support.

No further source question blocks this bounded test recommendation. Runtime
acceptance, genuinely available queue depth and whether validation amortizes remain
open. This checkpoint selects no implementation or native experiment by itself.

# Lead review: integrated baseline and branch-task research

2026-10-24. Under the [multicore mission](../deterministic-multicore-mission.md).
This is source review and architectural reasoning, not additional execution evidence.

## First integration closed

Reviewed `evaluator_worker.rs`, the `full_impl` seam and focused test assertions at
the first integration checkpoint `a27b7758`. Owned packets snapshot the actual
Position, supplied Influence, material and current weight pairs. Mutex-protected
packet/output slots and release/acquire state transitions separate submission,
completion and reuse. The coordinator owns PawnCache and publishes retained state,
relation counts and finishing results only after joining. Inline and worker paths
share the numerical chain and composition. No source repair is selected.

The [integrated report](../../experiments/multicore-feasibility/integration/report.md)
supports retaining a positive research baseline: finite replay and evaluator checks
passed, with selected generic search elapsed improvements. It does not establish
production adoption. Fixed CPU6 affinity, lifetime busy spinning and the wall-time
abort policy are prototype choices; arbitrary descheduling must not become a new
King stopping rule in a final implementation. Exceptional unwinding and failure
recovery are not broadly qualified. Do not extrapolate this three-case result to
all workloads, production PGO or a KingWCR comparison.

## Whole branches: validate operations, not merely returned scores

Toby's recursive branch queue is the next architectural priority. A task queue
solves scheduling; it does not establish independence. Earlier branches can change
windows, learned ordering, remembered results and selected pawn descriptors.

Exact raw read-set validation is a conservative starting model, but may reject
useful execution unnecessarily. A changed remembered-table group can still produce
the same complete `ProbeResult` for a particular query. Semantic operation replay
could therefore accept more work than byte equality. However, `RememberedTable::probe`
can also raise mate-record depth, and `store` chooses its destination and preserves
or displaces records from the current group. Replaying original operations against
current ordered state is different from installing speculative final table bytes.
Matching a probe's returned score alone proves neither its metadata nor its effects.

This is a candidate mechanism, not a correctness argument for a branch executor.
Validation must cover all influential dependencies and preserve the authoritative
operation sequence. Work limits and host polls can stop inside a branch: bulk
addition of its final counts is not enough. A design must explain partial progress,
state on interruption, and the cost of its validation or replay before claiming
faithful whole-branch reuse. Serializing every node through the coordinator can
also erase the scheduling benefit, even if mathematically correct.

Two concrete source observations sharpen the first experiment:

- `root_schedule::Iteration` freezes its Restricted policy and orders its tail
  after the first completed candidate. Remaining initial attempts use
  `aspiration(best, previous)`; a completion that does not improve best leaves
  that window unchanged. A queued restricted tail therefore has a plausible
  window prediction, though shared state can still invalidate it. In Unrestricted
  mode the first two windows are both `[-10000, 10000]`, with a likely smaller
  opportunity. Neither fact establishes branch independence.
- `timed::work_poll` reports Status from `history.search_path()`, and handles
  Time/Post/Easy controls as well as stopping. Polls occur every 4096 absolute
  charged nodes. A changed starting node count can shift the poll's location
  inside an otherwise identical branch. Replaying only the speculative task's
  original poll events or final N/R totals is insufficient. Initial fixed-work,
  no-live-host research may omit this support explicitly; adoption cannot.

## Salvage useful work when a branch cannot commit

A distinct alternative is a speculative branch that produces reusable pure
calculations rather than an authoritative subtree result. The coordinator still
executes the prescribed search, accepting prepared geometry or Activity/Shelter
only when its actual inputs match. Different speculative bounds or TT decisions
then need not invalidate every calculation that happened to be useful.

That could retain more value than all-or-nothing branch validation, but it has
substantial unanswered costs: shadow search, state snapshots, bounded result
storage, lookup/publication, cancellation and wasted paths. Native coherent input
provenance, chronological placement data, root weights and supplied-map authority
cannot be replaced by an unchecked hash match. Pawn-cache-dependent FULL results
are not interchangeable with placement-only calculations.

This alternative must be labeled honestly: it uses branch tasks to predict and
prepare work, not to commit independently searched branches. Examine whole-branch
execution directly before selecting a smaller mechanism. Neither approach is
selected for implementation by this review; Imp2's source investigation should
recommend the strongest concrete experiment and expose its limitations.

## Independent transaction soundness challenge

A single bounded Astra source review of the prototype over `adac8b03` found no
concrete false-accept counterexample within fixed-completion, NoHost, timing-absent,
zero-root-randomness execution. No builds, runs or edits were performed by that
reviewer. Reviewed SHA-256 prefixes include `branch_transactions.rs` `8311f8769984`,
`branch_journal.rs` `8c3bdffdca0dd`, `engine.rs` `895a533fa7b1`, `ordinary.rs`
`bc0af2a405fe` and `quiescence.rs` `15fb962a9910`. These identify an in-progress
source review, not certification of a later frozen image.

The important prerequisite is lifetime binding: root Position/retained state,
predecessor Influence, configuration, evaluator parameters and table geometry stay
immutable within the private run. The request/history comparison is not sufficient
as a general cross-root or cross-activation task certificate. A future executor
must bind those additional inputs explicitly.

The review found native replay covers the consumed mutable dependencies; private
scratch is initialized before use, including Q reply-list provenance; the same
child survives retry; current statistics are rebased; and canonical scheduling
does not install speculative ranking. Full ProbeResult/Selection equality remains
conservative. Focused tests still need to establish behavior; the source review
does not replace them or qualify live interruption support. Before removing the
independent canonical audit, evidence should exercise difficult interactions such
as learning rescaling, mate-depth probe mutation, retries and reply-list reuse.

The lead also identified and the evolving driver corrected two audit defects:
rollback must compare against a witness saved before validation, and a semantic
pass followed by canonical disagreement must terminate the experiment rather than
be classified as an ordinary transaction rejection.

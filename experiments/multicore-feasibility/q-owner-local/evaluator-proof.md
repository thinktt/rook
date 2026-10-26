# Q owner-local tactical preparation: evaluator/selector proof

Base is exact tested ordinary owner-local66 source copied to
`/home/legolas/rook2-experiments/workspaces/q-owner-local-20261026-01`.
The original ordinary option/entry remains active independently of the new
default-false Q option. No worker, packet, numerical owner-body factoring,
borrowed-input protocol, output copy, allocation, unsafe code or hot census is
introduced by this evaluator layer.

## One selector and at most one producer callback

Public `Selection` is unchanged. The private API is:

```rust
select_noncheck_q_inventory(
    &mut self, node: &mut Node, lower: i32, upper: i32,
    capture_exception: bool, scratch: &mut Option<Influence>,
    coherent: bool, allow_preparation: bool, list: &mut MoveList,
) -> (Selection, bool)
```

The Boolean starts false on every invocation and becomes true only after the
original tactical producer actually fills the supplied row. The private caller
owns the checked/non-observed/non-reused admission and supplies
`allow_preparation = !replies_available`; the evaluator does not add an opposite
king probe, position validation or a checked-state recomputation.

Original `select_noncheck_impl` remains a thin const-QHOOK=false wrapper. Its
single shared body, `select_noncheck_hook`, retains the original sparse formula,
immediate sparse return, FAST call, strict
`lower - 250 < fast.score && fast.score < upper + 250` condition and capture
exception override. Only the selected FULL call wrapper changes under const
QHOOK=true. The sparse branch returns immediately, so moving one FnOnce callback
there and into the later refresh branch is mutually exclusive: there is at most
one actual FULL and one tactical producer opportunity per Q selection.

FAST-only selection neither ensures Influence nor queries readiness nor generates
a row. Supplied Some Influence remains authoritative; the existing ensure path
builds a map only for an actual demanded FULL. FAST score, sparse/refresh flags,
stage order, cache selection, retained changes and exact R remain shared.

The Q callback captures only the disjoint mutable destination row and its local
prepared flag; it receives the actual immutable Position from the shared FULL
body. It calls unchanged `tactical::generate_for_search(position, list, coherent)`.
No full Evaluator/Node mutable alias is captured and no temporary inventory is
copied into the destination. No rows or search state are shared with helpers.

## Shared FULL gate and preserved ordinary behavior

The original ordinary `full_impl_hook` signature is preserved for existing callers
and focused controls. It forwards the ordinary option into `full_impl_prepare`,
the single original numerical FULL body. The new Q selector passes
`q_owner_local_inventory && allow_preparation` as that body's explicit per-call
`prepare_enabled`. This snapshot cannot change during the exclusive synchronous
call; ordinary behavior therefore retains its original option semantics.

The hook still occurs only in configured mode3 after original pawn/local work
and `owner_ready(token)`, with original `complete()` after it. Const HOOK,
prepare_enabled and private coherence all must be true before the readiness
query; only not-complete invokes the producer. Modes1/2 cannot enter the color
branch. False readiness is a racy hint, not remaining-time evidence or output
ownership. Terminal errors propagate normally; original complete still acquires
outputs and retires the epoch.

Public/observed/detailed/FRESH FULL and old selector entries keep const-disabled
hooks. Detailed/stage branches remain ahead of the private Q branch in the shared
selector. Checked Q, terminal ply, replies reuse and public/observed Search
geometry exclusions are enforced by parent-owned Q caller routing. They never
gain permission through this API's Boolean alone. Original full/fast numerical
bodies, rounds, pawn-cache behavior, original owned packet transport and final
retained/stat/R/observer/native finishing order are unchanged.

Owner-ready remains before preparation and the sampled residual join clock starts
inside complete after it. Residual join excludes generation. Integrated timing
must include queries, speculative/discarded generation, helper spinning and
code/layout effects; subtracting join observations cannot establish saved work.

At original Q demand the caller skips only the tactical producer when this
activation's flag is true. Count/empty handling, tactical order against current
learning, observer events, frontier/capture/legality checks and child creation
stay at their original sites. Static evaluation returns discard preparation with
no logical generation charge. Production tactical generation has no poll/ledger
effect, though speculative work can extend physical stop latency by one interval.
Actual consumer/discard/checked/reused/stop controls belong to the caller owner.

## Exact producer identity and accepted capacity argument

The producer sources are unchanged from ordinary owner-local66:

```text
src/tactical.rs
22fb473a0c3288a1ce392833e1dd09749bc77d795d3b697ba1071f21b58d3d4d
src/tactical/check_masks.rs
8468db1a066e1e6983271e3b54d6023c20d3b55386a775098f0db48472cec626
```

The accepted private-coherence bound is 15 nonkings times queen geometry27,
plus king captures8 and two EP/two quiet-pawn prefix emissions: 417 <512.
It does not require orthodox reachability or opposite-king safety. This change
adds no runtime validation, capacity probe, bounded-generator variant or new
proof framework. Existing maintained planes/mailbox/lists and exact producer
bytes supply the admitted domain.

## Added focused source controls

Six tests under `evaluator::q_inventory_tests` cover:

- Actual sparse FULL, no preliminary FAST, ordered native empty/promotion/joined
  nonpawn EP/ending lists, root ownership, contrary Some maps, R and retention,
  including both diagnostic settings.
- Actual FAST then one FULL refresh, exact strict policy, asymmetric root weights,
  produced FAST score, Some-map authority, R and original stage ordering.
- Both strict-equality FAST-only boundaries with no map/query/row/retained change,
  plus the original capture-exception refresh at an otherwise excluded boundary.
- Real-ready skip and mode1/2/Q-off/coherence-denied/allow-denied fallbacks, with
  untouched destination and exact native selection/statistics.
- Public/search old selectors, stage/detailed observers and public/FRESH FULL
  with zero test-only readiness queries and exact serial observations.
- Sparse static returns discarding prepared empty/special rows, plus a clearly
  labeled direct conditional FULL/producer check of joined EP under double check.
  That checked fixture is not admitted through unchecked-Q selection; actual
  caller controls establish checked exclusion.

Existing TLS readiness controls wait for real done on forced-ready and only
conservatively return pending; no acknowledgment is manufactured. No new
production observer or count is added. The Session proxy and private
`--q-owner-local-inventory` flag preserve the ordinary option and the two-field
thread-inspection JSON.

No compilation, tests, engine execution, builds, binutils, Git actions or subagents
were performed by this source owner. These source controls await native admission
and do not imply full conformance or gameplay qualification.

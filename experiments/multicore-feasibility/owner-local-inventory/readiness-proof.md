# Owner-local inventory: readiness hint proof

2026-10-26. Source-only worker handoff under
`/home/legolas/agent-memos/imp2-lead-to-imp2-owner-local-inventory-discriminator-20261026.md`.
The current RESET policy requires stopping on the external manager's explicit
RESET alert; it requests no present stop or local quota monitoring.

Base is exact positive64:
`/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01`.
The only engine file owned here is `src/colors_worker.rs` in isolated
`/home/legolas/rook2-experiments/workspaces/owner-local-inventory-20261026-01`.
No borrowed-input or inventory4 transport changes are imported.

## Concrete query and unchanged ownership

```rust
pub(crate) fn is_complete_now(
    &self, token: DispatchToken,
) -> Result<bool, String>;
```

First reject generation zero or a token whose scalar generation differs from
this coordinator's current generation. The shared reference excludes a
concurrent mutable coordinator dispatch; a separate scope guard may still close.
Then Acquire-load terminal stop and, if observed, return the original failure
through the existing failure() path. Otherwise use existing both_done(g), whose
true result requires both separate Acquire loads to equal this exact generation.
A false result can stop at the first pending reader and remains conservative.
No successful production query acquires Control, reads Packet/output cells,
changes Flight, acknowledges a reader, notifies or registers a waiter.

The original helpers still end every input reference before their output write
and done Release. Therefore true observes real completion, but grants no right
to read outputs or retire/reuse input. It may be called after completion with
the still-current scalar token; this intentionally conveys no Flight authority.
False provides no estimate of useful remaining time. Failure/final close after
the query remains subject to ordinary complete's terminal check, Control-owned
Published(g) validation, matching done Acquires and scalar output consumption.
No scheduling hint can replace that authority. Invalid tokens return the token
error; valid tokens observing terminal stop preserve the original worker error.

Production Packet, Cells, Control, Shared, Reader and DispatchToken storage is
unchanged. Dispatch/publication, kernels, 4096-spin/512-sampling policy,
single-waiter SC-latch handshake, reverse output edge and final close/shutdown
are unchanged. The query adds no synchronization publication or hot census.
The ordinary/evaluator owners alone implement legal-inventory admission, local
row lifetime and original demand/charge/ordering semantics.

## Test-only forced readiness

```rust
#[cfg(test)]
pub(crate) fn with_forced_readiness<R>(
    ready: bool, f: impl FnOnce() -> R,
) -> R;
```

A private coordinator-thread-local Cell<Option<bool>> records the override.
An inaccessible private Drop restores the prior value on normal return and
unwind, including nested calls. Other coordinator threads start with None.
The helper and TLS have no production definition, storage or access. A separate
test-only thread-local entry counter and `pub(crate) readiness_probe_count() ->
usize` accessor let integration tests snapshot whether an excluded route calls
the query at all. It counts query entry, including invalid and terminal tokens,
and introduces no production counter or publication.

The query still validates the token and checks terminal before either override.
Forced false returns a conservative pending hint, even after actual done.
Forced true actively waits for both real matching done Acquires and checks
terminal on every pass. It never writes done, consumes output or registers a
second condition-variable waiter. Test true may intentionally block until a
delayed helper is released; this is solely a deterministic test aid.

## Focused source controls and handoff

Three new worker tests use the `colors_readiness_` filter:

1. A helper delayed inside compute_input yields pending; forced true returns
   only with actual matching done; forced false, nesting, unwind restoration and
   independent-thread TLS are checked. Flight remains Published until ordinary
   complete reads the original correct output.
2. Zero, pre-dispatch future, later future and stale tokens reject; the current
   token remains pending then becomes ready after actual done.
3. A helper fails while its peer remains delayed inside input. The ordinary,
   forced-false and forced-true queries return the identical original failure;
   neither done epoch is fabricated and Flight remains Published until existing
   final scope close/shutdown drains.

The existing in_input test gate remains in its original location, before the
last Packet publication-time reads; no production or existing test hook moves.
The twenty-one original worker tests remain unchanged. Source expectation:
`colors_readiness_` selects 3 tests and `colors_worker::lifecycle_tests` selects
24. No builds, tests, engine/native helpers, Git operations or subagents were
run by this worker owner. Parent owns compilation and execution admission.

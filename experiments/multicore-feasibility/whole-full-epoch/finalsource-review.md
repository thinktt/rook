# Whole-FULL epoch transport: final source challenge

Source-only review, 2026-10-26. Reviewed
`/home/legolas/rook2-experiments/workspaces/whole-full-epoch-20261026-01/src/evaluator_worker.rs`,
SHA256 `0e88434a1c83a0b27c915599971b2912e2ee6ef4d4ec28c9ec19d101e7c81792`.
Pins below refer to those exact bytes. No implementation file was edited and
no engine, build, test or native experiment was executed by this reviewer.

**Finding:** no blocking source defect found in the specialized one-helper
transport. The implementation satisfies the concrete
[ownership proof](ownership-proof.md); controls/build admission and measured
benefit remain the owner's work, not conclusions of this source review.

## Exact scope

Compared with the positive epoch64 snapshot at
`/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01/`:

- The 64-file source corpus is `Cargo.toml`, `Cargo.lock` and 62 files under
  `src/`. There are no added/removed source paths. Only
  `src/evaluator_worker.rs` differs; the other 63 files are byte-identical.
- The `ActivityShelter` declaration, intervening documentation and complete
  `compute` block are byte-identical (new lines 27-52), block SHA256
  `c1e83ee2b14590a228b9f8070e6ac72df223676bfb053729b91a010798ad6d57`.
  All ten crate-visible function signatures, including the test-only parking
  query, have the same signatures; moving their declaration order changes no
  API.
- `evaluator.rs` is byte-identical: it dispatches the supplied complete inputs,
  joins at 684-694, and closes the standalone call scope at 695 before numerical
  composition and observer invocation at 738. Inline mode1, color mode3, root,
  FRESH/public callback boundaries, logical charges and caller ownership retain
  their original source. Inventory65 integration is absent.

## Concrete lease and lifecycle

Initialized cells contain a parsed valid Position, built Influence and ordinary
default scalar outputs (170-198). The private `UnsafeCell` implementation is
limited to input/output, with no mutable whole-Shared/Cells reference (69-88).
Dispatch requires an active nonclosing scope and None under Control (299-306),
checks a nonwrapping epoch before writing (307-325), and keeps the controlled
unpublished failure before publication/epoch advance (327-338). Installing
Published and releasing request form an infallible tail; no published job can
roll back to None.

The helper acquires request before its lexical Packet borrow and reads the
existing whole numerical chain directly (444-456,478-493). Only Copy output
escapes. Its output write precedes done Release, with no remaining input
reference (457-467). Complete waits without Control, then revalidates matching
Published, nonclosing/nonterminal ownership and done Acquire under Control
(341-355). Its scalar output copy ends before None (358-368). A later request
Release/Acquire therefore carries the reverse edge before the helper's next
output overwrite, including a delay after prior done but before prior latch.
There is no reader packet copy or kernel mutex.

Final close claims Discarding under the same Control and waits for actual
PARKED/FAILED/STOPPED acknowledgment before None (570-599). The loop checks an
unseen request before inactive-scope parking (443-473); park rechecks that
request under Control before acknowledging PARKED (601-617). Thus even a
published job not yet borrowed cannot be retired by a stale parked state.
Startup only acknowledges genuinely unstarted spawn failures or actual loop
exit (205-250). Unwind drops concrete cell references before terminal publication
(217-229,552-568). Shutdown publishes stop, signals without Control, joins
without either mutex held, then retires the flight (377-407). Outliving guards
wait for real quiescence (578-582). Exhaustion leaves request/done unwrapped and
actually joins before returning the terminal error (307-317).

## Cold completion and focused controls

The fixed 4096-spin policy remains (25,522-527). There is one coordinator
waiter. Registration holds Sleep, performs the SC RMW, then checks Acquire
predicates before atomic unlock/sleep; early/spurious wakes re-register
(528-549). Every normal done and every terminal publisher unconditionally
participates in the same SC RMW chain (463-467,510-520,564-567), including owner
shutdown (385-390). Earlier exchanges carry publication to the waiter recheck;
a publisher consuming true must acquire Sleep before notifying. No production
path holds Control while taking Sleep. Delay before an owed exchange can delay
a cold waiter; neither scheduling delay nor stop intent grants retirement.

Successful calls add no clocks, readiness counters, observer objects,
allocations or thread creation. The remaining Control/request/done/SC-latch and
cache costs still require integrated measurement. The 16 focused lifecycle
controls cover scope reuse/discard, real exit, delayed input/output retirement,
close/dispatch and output-read races, unpublished failure, overflow, cold wake
orderings, delayed prior latch and unwind (761-1149). The old eleven-second
delay control is preserved separately and explicitly ignored (1153-1162).
These are source-inspected controls, not reported test results.

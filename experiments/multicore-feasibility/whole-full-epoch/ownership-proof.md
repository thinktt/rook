# Whole-FULL epoch transport: one-helper ownership proof

Source-only design challenge, 2026-10-26. This specializes the accepted epoch
ownership to one helper; the final landed-source check is recorded separately.
The reference is the positive epoch64 snapshot at
`/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01/src/`.
Only `evaluator_worker.rs` transport may change. Its existing `compute` body
(`37-53`) and crate-visible API, the other 63 files in the source corpus, and evaluator's
pre-composition call-scope close (`evaluator.rs:685-697`) must remain unchanged.
No new timing/counter observer or generic worker framework is needed.

**Lease invariant.** A single `&mut` coordinator controls reuse of initialized
input and separate initialized output cells; only the helper writes output.
Control serializes dispatch, output
consumption and final close. Input is written only with Flight::None. None
means either matching helper done Acquire followed by ended coordinator output
reads, or the helper's actual parked/exited acknowledgment after a discard.
Neither stop intent nor elapsed time retires a live reference. Initial Position,
Influence and output values must be valid values, not fabricated zero storage.

**Publication and retirement.** Dispatch requires an active nonclosing scope
and None while holding Control. It checks the nonwrapping epoch, initializes
every Packet field, and performs all fallible work before installing
Published(g) and request(g) Release. Nothing may fail between that installation
and publication. Prepublication failure leaves the epoch, request and None
unchanged; after publication, completion or actual drain is required.

The helper acquires the exact new request before forming its lexical Packet
reference and calls the unchanged whole numerical `compute` directly on that
input. Every input reference ends before its sole output write and done(g)
Release. Complete waits without Control, then holds Control and rechecks
Published(g), nonclosing/nonterminal state and matching done Acquire before
copying the scalar output. Its output access ends before None. The next request
Release/Acquire therefore carries the reverse edge from that read to the
helper's next output overwrite. Descheduling before done retains the lease;
descheduling after done cannot retain an input/output reference.

**Close and lifecycle.** Final guard close claims Published as Discarding under
Control and waits for this actual helper to park or exit before restoring None.
Park touches metadata only, checks request==seen under Control, and acknowledges
PARKED only with no unseen publication. The loop checks request before its
inactive-scope branch. Thus an unseen pending job is handled before normal
parking or retired by the helper's own actual exit. Startup failure must join
any started helper; only a genuinely unstarted helper can be declared retired
without an acknowledgment. Terminal handlers run after the concrete loop and
unwind have ended all cell references. Shutdown wakes, joins without locks held,
then retires the flight; outliving guards also wait for real retirement.
Epoch exhaustion is sticky terminal shutdown, never wrap, reset or fake done.

**One cold waiter.** Only the coordinator waits for completion. After 4096
unchanged spins it holds Sleep, performs waiting.swap(true, SeqCst), and rechecks
done/terminal with Acquire before condition-wait unlock/sleep. Every actual
normal or terminal publisher performs the same unconditional
waiting.swap(false, SeqCst) after its done/stop publication and after releasing
Control. A publisher ordered before registration carries its publication
through that SC RMW chain to the recheck. A later publisher that consumes true
owes a notification while holding Sleep, excluding a notification slipping into
the recheck/sleep gap. Every early or spurious wake registers again. No path
holds Control while waiting on Sleep. Delay after done but before the exchange
may delay a cold waiter; it is not an engine timeout or permission to reuse a
live cell.

The numerical/public caller boundary remains actual FULL only: coordinator
cache/local work, supplied Influence authority, retained/ledger/poll ownership,
inline mode1, color mode3 and public callback parking remain in unchanged source.
The final review must verify those unchanged bytes and the new concrete lease,
not infer safety merely from resemblance to the color implementation.

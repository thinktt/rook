# Scoped owned/borrowed FULL input: pre-publication ownership proof

Status: proof reviewed and released by the parent for bounded worker
implementation, 2026-10-26. This proof preceded unsafe borrowed publication.
The parent owns build/test/native admission; no execution result is asserted
here. Base is the exact positive64 source
at `/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01`;
implementation destination is the isolated `borrowed-full-input-20261026-01`
workspace under the same experiments/workspaces root. Preserve positive64.

Authority: `/home/legolas/agent-memos/imp2-lead-to-imp2-borrowed-full-discriminator-20261026.md`
and `/home/legolas/agent-memos/imp2-lead-current-reset-stop-policy-20261026.md`.
The latter requires stopping on the external manager's explicit RESET alert;
there is no local quota monitor or threshold stop in this work.

## Concrete safe interface

```rust
pub(crate) fn with_epoch<R>(
    &mut self,
    position: &Position,
    influence: &Influence,
    material: i32,
    mobility_weights: [i32; 2],
    shelter_weights: [i32; 2],
    owner_work: impl FnOnce() -> R,
) -> Result<(R, ActivityShelter), String>;
```

The worker has a cold configured `InputMode::{Owned, Borrowed}`. Change mode only
while fully idle: no active scopes, no closing/shutdown/terminal state, Flight
None, Input Empty and both readers really parked. No per-call mode store,
counter, allocation, Arc clone or thread is needed. Both modes use this same
enclosing API at the actual evaluator mode3 seam. Existing private `dispatch`
always makes an Owned snapshot, regardless of configured mode; the old tests
must never acquire a raw borrowed obligation through their escaping token API.

An inaccessible private `EpochGuard<'worker, 'position, 'influence>` contains
`&'worker mut ColorsWorker`, the two references, installation/publication state
and the matching generation. Its fields and construction are private. Neither
the guard, its mutable worker access, nor an owning cleanup token reaches
owner_work or R. The public operation creates it before installing borrowed
pointers and retains it across owner_work, owner-ready recording and completion.
`complete` success disarms only after input/output retirement and Empty/None.
Every `?`, return and unwind before that point executes guard cleanup. Cleanup
must be non-panicking, including while already unwinding; retain failure in
worker state for explicit errors/later reporting. A cleanup failure cannot be
resolved by releasing the guard's references while a reader remains live.

Safe `mem::forget` cannot bypass this enclosing operation: callers never receive
the guard. A returned Drop token by itself would fail this requirement. No
reference-to-static transmute, unsafe whole-Evaluator alias or integer pointer
round trip is used. A nonreturning owner closure retains the call and its borrows;
process abort terminates all execution. Test-profile unwind is a separate path
which must actually drain.

Parent-owned evaluator factoring must split safe borrows of colors_worker and
pawn/root/weight/local inputs. owner_work performs the original owner branch;
node retained mutation, callbacks, relation-ledger publication and final
arithmetic remain after with_epoch returns. Caller inputs stay immutable and
address-stable for the whole operation, including custom supplied maps and
public/FRESH routes. Parent must not introduce a duplicated numerical body.

## Initialized storage and concrete unsafe boundary

Keep one initialized Packet containing generation, sampled publication Instant
and an Input enum:

```rust
enum Input {
    Empty,
    Owned { position: Position, influence: Influence },
    Borrowed { position: *const Position, influence: *const Influence },
}
```

The Borrowed pointers are formed directly from the guard's references and retain
their provenance. Empty is the genuine startup/retired representation: no fake
Position, fabricated reference or dereferenceable null is constructed. The
Owned variant is an actual snapshot on every dispatch. Packet metadata is owned;
material, phase and root-bound weights remain owned coordinator Metadata on
every call. Borrowing preserves the exact supplied Influence, not a rebuilt map.

Because raw pointers are not automatically Send/Sync, give only the concrete
private cell container the required unsafe Send/Sync implementations, with this
protocol as their justification. Do not add a reusable unrestricted pointer
wrapper or expose Packet/Input outside this transport. Position and Influence
are immutable ordinary data in this source; neither carries interior mutation.

Only the coordinator writes Packet under Control, after old retirement. Each
helper acquires request(g), validates Packet generation, matches Input and forms
references only inside compute_input's lexical block. Owned references point to
Packet fields; Borrowed references point to the caller's guarded objects. Both
execute the same original activity::compute_side and opposite shelter kernel.
There is never a mutable whole-Shared/Cells reference, and never an input write
while any helper Packet/Input/referent reference remains live.

All Packet/Input/referent accesses, including the sampled Instant, end before
the helper writes its own scalar output and performs done(g) Release. The outer
catch_unwind handler publishes terminal state only after that helper's concrete
loop and lexical references have unwound. No late helper code after done touches
Packet, Input or referents. Existing signal_completion may run late after done;
it touches only synchronization metadata, so descriptor clearing/reuse may then
proceed without waiting for that late latch exchange.

## Installation and publication

Under Control require a usable active scope, Flight None and Input Empty. Check
the next nonwrapping generation, form owned Metadata and choose the guard-owned
input. Initialize Packet completely before request(g) Release. Helpers acquire
that exact generation before accessing Packet. Install Published and release
request without an intervening allocation, formatting, callback or other
fallible/panicking operation. The already present inaccessible guard records the
obligation; there is no publication-to-guard-construction gap.

An unpublished failure, including the old fail_before_publish hook, clears only
this newly installed Input under Control before returning. Request, accepted
generation, Flight and observation counts remain unadvanced. Since no request
was released, this installation has no reader; the prior Flight None proof
already retired old readers. Guard state distinguishes unpublished installation
from a published generation so cleanup cannot wait forever for an epoch that
was never released. Epoch exhaustion retains the existing terminal shutdown and
actual-reader drain; no fabricated completion or epoch reset is allowed.

## Normal completion and reverse ownership

The existing done(g) Acquire pair proves both helpers' complete input reference
lifetimes ended and publishes their separate scalar outputs. Under Control,
completion must still own Published(g), be nonterminal/nonclosing, acquire both
matching done epochs and finish its two scalar output reads. Then clear Input
to Empty and change Flight to None before releasing Control. Compose using
scalar locals and owned Metadata, as before. No borrowed result escapes.

Reverse ownership is unchanged: owner output reads end before the next request
Release; each helper acquires that next request before overwriting its own
output. A helper's delayed old latch exchange is harmless because its old input
references and output write ended before done. The guard's exclusive worker
borrow prevents another coordinator dispatch, mode change or worker shutdown
until this call has completed cleanup. Independently owned scope guards may
still initiate final close, handled below.

## Error, abandonment and unwind

Normal healthy abandonment of a published call waits for both exact done(g)
Acquires, without holding Control or Sleep across incompatible operations. Then
under Control, if still owner of Published(g), discard outputs without reading
them, clear Input, record existing sampled discard accounting and set None.
Other outer active scopes may remain nonzero: this particular input still
retires now. Releasing an activation guard is not an input-retirement proof.

Current complete's early terminal error is insufficient: one helper may still
be reading. On stop/helper failure, guard cleanup invokes the real terminal
shutdown/join path as necessary and does not return until all started helper
loops have actually exited (unstarted helpers retain their existing explicit
startup retirement). Do not force/fabricate peer done. Terminal handlers wake
the existing lifecycle condition variable. After real joins/quiescence, clear
Input and retire this flight under Control. Kernel failure is returned, not
silently retried inline; no rollback of already performed owner pawn work is
promised.

For owner panic, the same guard cleanup runs before the caller's Position or
Influence can unwind. Healthy cleanup waits done; terminal cleanup joins. Drop
does not call owner_work, format an error or panic on a failure result. Poisoned
mutexes are recovered as in the existing transport. No timeout can authorize
borrow release. A reader that never retires necessarily prevents return; this
is preferable to memory unsafety and is not an engine wall-time abort.

## Concurrent final scope close

The independently owned final scope guard can win Control and change
Published(g) to Discarding(g). It keeps that ownership until BOTH real
parked/exited acknowledgments; a stop observed on one reader retires neither
its peer nor the whole packet. Park still cannot acknowledge an unseen request.

The epoch guard must not steal/reset Discarding or clear its descriptor early.
After releasing any completion Sleep lock, it waits on the lifecycle Control/
wake condition until that closer completes actual retirement and establishes
Input Empty/Flight None, or uses terminal shutdown/join if terminal. If both done
arrive first, that alone does not authorize overwriting another closer's
ownership. The closer clears Input under Control at its existing real-quiescence
retirement seam before None. Shutdown likewise clears only after real joins.

No other dispatch can begin through this worker while the epoch guard holds its
exclusive mutable borrow. Therefore observing final close's actual retirement
cannot be confused with a new coordinator flight. Any impossible generation or
ownership mismatch must fail closed through real shutdown/drain, not erase an
unrelated descriptor. Existing reactivation begins only after closing clears.

## Single waiter and unchanged policy

Only the coordinator uses the completion Sleep/SC-latch wait protocol. Normal
completion and guard cleanup run sequentially in that same thread; cleanup
begins after the failed/completed wait has released Sleep. No background drain
thread or helper-side completion waiter is introduced. Lifecycle close waits
use Control/wake as before, not the one-bit completion registration. Preserve
unconditional SC publisher exchanges, re-registration after spurious wakes and
the rule that Control never spans completion spinning/Sleep. Keep 4096 spins,
512 sampling, kernel arithmetic and existing observation policy unchanged.

## Necessary cold witness and verification obligations

After joined shutdown, the parent-owned report envelope may include
`{mode:"owned"|"borrowed",request:g,done:[g,g],retired:true}` for healthy runs.
Derive fields from configured mode, existing request/done epochs, actual Input
Empty and Flight None; retired also requires actual shutdown/join completion.
Do not manufacture done=g on failure. Modes1/2 report disabled. No hot census
is added and mode is configured before activation, never changed during a call.

Focused implementation admission must force: actual supplied-map/root-weight
equivalence; both scoped modes; outer active scope with per-call abandonment;
owner unwind while a helper holds input; helper failure while its peer holds
input; both orders of concurrent final close; unpublished rollback; abandonment
then reuse; delayed done-to-latch work; terminal/startup/shutdown and MAX epoch.
Legacy tests retain Owned dispatch. Existing numerical/reverse-edge/SC tests are
reused where their source remains applicable. Production panic-abort is not
claimed as unwind recovery.

Source anchors in positive64: colors_worker.rs:327-388 installation/publication;
409-459 complete and composition; 472-528 joined shutdown/Drop; 531-615 helper
loop and lexical input references; 650-708 sole-waiter/terminal protocol;
710-765 Discarding/close/park. evaluator.rs:602-695 is the parent-owned safe
field-borrow/closure seam, and 725 onward performs retained publication.

## Scope and economics

This is a matched transport experiment, with no TT/control/pawn-cache replication
and no additional arithmetic width. Borrowing removes coordinator snapshot
copies/destination writes. Pointer publication, caller-source cache transfers,
request/done/output synchronization, observation and retirement still cost.
Pointer storage layout and caller stack/Node placement may worsen sharing. Both
new modes must use the same enclosing operation; compare scoped borrowed versus
scoped owned separately from both new modes versus preserved positive3. No
source-only reasoning predicts the net time benefit or isolates a cache cause.

No material lifetime obstacle remains if every contract above is implemented.
The central obligations are unexposed guard ownership, per-call cleanup despite
outer activation, complete's terminal early-error drain, and descriptor clearing
at every real retirement/rollback seam. The parent released this proof before
implementation began.

## Worker implementation handoff

The isolated `src/colors_worker.rs` now implements the exact with_epoch API,
`set_borrowed(&mut self, bool) -> Result<(), String>` and
`scoped_report(&self) -> Result<String, String>`. The latter requires shutdown,
no remaining JoinHandles and both actual terminal states. Default mode is
Owned. The installation marker is armed before the packet write; cleanup treats
None/nonempty as unpublished only when its generation matches and request has
not published that generation. Unexpected ownership falls back to actual joins.
Final-close Discarding waits retain the closer's ownership. All normal retirement,
joined shutdown, final-close and controlled unpublished-error seams clear Input.

Added eleven `colors_scoped_` worker tests, each exercising both configured modes:
mode/configuration plus forced-Owned legacy dispatch; healthy abandonment under
outer activation and reuse; owner unwind while a real input reference is delayed;
helper failure while its peer holds input; combined owner unwind/helper failure
with poisoned-Control recovery; both close/completion ownership orders;
unpublished rollback/reuse; late done-to-latch reuse; early normal helper exit;
MAX epoch/exhaustion. Existing twenty-one worker tests remain, and their common
no_flight assertion now also requires Input Empty. Expected worker filter
`colors_worker::lifecycle_tests` contains thirty-two tests; `colors_scoped_`
selects the eleven new tests. These counts describe source, not executed results.

The existing cfg(test) in_input gate moved just before the activity/shelter calls,
after concrete Position/Influence references form. Both referents are used after
the pause, so the new delayed-reader controls establish an actual live borrow,
rather than merely pending request admission. Production timer and kernel
operations retain their existing order. The old shutdown debug assertion after
actual joins was removed to avoid an unnecessary assertion in unwind cleanup;
actual joins, rather than a bookkeeping assertion, authorize descriptor clearing.

Only isolated src/colors_worker.rs and this proof were edited by the worker
owner. No build, test, native helper, Git operation or subagent was run. The
parent owns safe evaluator/CLI integration and all subsequent execution.

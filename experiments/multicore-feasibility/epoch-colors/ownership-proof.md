# Epoch-slot ownership and cold wakeup design

From: imp2
To: imp2-lead
Scope: fixed colors transport; design only, before unsafe implementation.

**Proposed fixed design:** one initialized input UnsafeCell, two initialized,
separate output UnsafeCells, one release-published request epoch and one done
epoch per reader. Retain a lifecycle Control mutex at dispatch and at output
consumption. Replace reader Slots locks/copies with direct immutable access.
Pay two unconditional SeqCst wake-latch exchanges per completion pair. No tuning
or claim that the remaining coordination is free.

## Ownership and final close

Only ColorsWorker's single coordinator (&mut self) can write input or dispatch.
Control serializes scope counts/closing and flight=None|Published(g)|Discarding(g).
Dispatch holds Control, rejects closing/zero scopes/terminal/occupied flight,
checks g+1 before mutation, installs the owned packet, sets Published(g), and
release-publishes request(g) before unlocking. Thus scope-count load alone is
never a lease: final close either wins and dispatch rejects, or sees the actual
published flight and drains it.

Readers acquire request(g) before forming a Packet reference. A lexical block
per reader performs unchanged side arithmetic; outputs contain only Copy scalar
results/timing values, no borrowed references/pointers. After its last input
access/reference ends, reader i writes only output_i, then release-stores done_i=g.
It does not touch that output again until acquiring a later request. Matching
acquire loads by the coordinator establish both input retirement and output
visibility. Merely seeing stop/failure is never retirement of the other reader.

Complete first spins/waits on matching done epochs or terminal state, **without
holding Control**. Once both done(g) acquire checks pass, it locks Control,
requires Published(g), copies both outputs to locals, records observation/retirement
and sets flight=None before unlocking. No input reference/full Packet copy is
needed: composition metadata is retained coordinator-side at dispatch. All output
reads end inside this short critical section; cross-color numerical merge runs on
local values afterward. The coordinator's later request(g+1) release carries this
output-consumption edge to each reader's acquire before it may overwrite output_i.
No whole-Shared/whole-output-array mutable reference is constructed.

Final scope close holds Control, decrements to zero, sets closing, and claims a
Published flight as Discarding. It then waits on the Control condvar until both
readers acknowledge PARKED or terminal retirement. If complete won the Control
mutex first, output reads already ended; if close won, complete sees Discarding/
None and returns an error without reading cells. Close retires the flight only
after both readers are quiescent. It never clears input/output cells. Activation
cannot pass closing until drain/retirement finishes. Dispatch cannot race this
step; after complete returns, &mut coordinator ownership also prevents simultaneous
new publication by another safe caller.

On zero scopes, readers process an already published unseen epoch before parking;
parking holds Control, rechecks request/scope/stop, then acknowledges quiescence
and waits on its Control condvar. It never resets input. Next activation changes
the scope predicate under the same mutex, notifies both, and waits for both active
acknowledgments. This keeps the existing lexical scope/spin policy.

## Completion wakeup handshake

Use a separate Sleep mutex/condvar and one AtomicBool latch W, initially false.
**Every** successful done publication and terminal publication executes
`W.swap(false, SeqCst)` after its release publication. If it reads true, it must
lock Sleep and notify (no conditional early return). Hot publishers never merely
load W. The one coordinator waiter holds Sleep and repeats:

1. `W.swap(true, SeqCst)`;
2. recheck both done epochs with Acquire, or stop with Acquire;
3. if still incomplete, condvar.wait(Sleep), then repeat registration/recheck.

On leaving this cold loop it clears with `W.swap(false, SeqCst)`, then releases
Sleep before acquiring Control. No plain W stores after initialization.

Proof: latch RMWs form one modification-order acquire/release chain. If a
publisher's exchange precedes the waiter's registration exchange, that chain
carries its preceding done/terminal publication to the predicate recheck. If it
follows registration while W is true, it consumes the registration and must take
Sleep before notifying; Sleep prevents notification slipping between recheck and
atomic unlock/sleep. If another publisher consumed the true bit first, that
publisher is already obligated to deliver the wake. Every spurious/early wake
re-registers before checking/sleeping again. Delayed prior-epoch exchanges can
cause only extra wakes; every current completion still executes its exchange.
Thus this is not independent release/acquire flags or notification without the
wait mutex. The unconditional hot RMW traffic is explicitly measured.

Completion waiting holds Sleep and reads atomics only; consumption uses Control
after Sleep is released. Terminal handlers update Control, release it, then run
the same latch/notify operation. No code holds both mutexes; scope parking uses
only Control. There is no reversed nested lock order or engine elapsed deadline.

## Error, initialization and exhaustion

Initialize input from a real parsed valid starting Position, real Influence and
valid scalar defaults; initialize each output to a valid scalar sentinel.
request/done start at0 and0 is never published. No zeroed Position/MaybeUninit.
Each output cell has one reader writer; only the coordinator reads after done.
The private Sync justification covers these concrete cells/operations only.

Reader catch_unwind uses AssertUnwindSafe only around this fixed concrete loop:
on unwind, its input references drop before the outer terminal handler marks that
reader retired. Partial output writes are never read without a matching successful
done. The handler sets stop/failure, wakes both predicate families and cannot
fabricate peer retirement. Coordinator terminal handling drains/joins both before
reuse or destruction. Production panic-abort supplies no unwind recovery promise.
Coordinator unwind with a published call is drained by lexical scope close or
Worker Drop; cells are not mutated by the guard.

Startup waits for two parked acknowledgments. Spawn/entry failure marks only the
unstarted/actually exited reader retired, stops and joins every started thread,
and returns no usable worker. Shutdown requests stop, releases locks, joins both,
then retires metadata; it never mutates input while a peer remains alive. Epoch
advance is checked nonwrapping. Exhaustion publishes nothing, makes the worker
terminal and drains/joins; reset requires a fresh worker with old threads gone.

Focused controls will force both close/dispatch orders, output consumption/reuse,
last-reader delays, waiter registration/publication interleavings, terminal and
spurious wake paths, discard/reactivation, startup failure and near-MAX overflow.
They supplement this ownership proof rather than establish it by testing.

Rust contracts consulted: [UnsafeCell](https://doc.rust-lang.org/std/cell/struct.UnsafeCell.html),
[Condvar](https://doc.rust-lang.org/std/sync/struct.Condvar.html),
[Ordering](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html).
The synchronization argument above is our proposed design, not a quoted library
guarantee. No unsafe implementation has started; fixture/tool work is independent.

# Selected single-owner contract: source obligations

This is an implementation proof map for the frozen source in preparation.json,
not a claim of executed tests, exhaustive correctness or performance. The baseline
is exact writer68. Owned Packet/numerical producers, writer-region types, original
SC-RMW completion notification and observation definitions are retained.

## Receiver and activation identity

Private ActiveSearch/ActiveEvaluator facades contain a hidden exclusive borrow of
the original receiver. Their only public-to-the-enclosing-operation methods are
named fixed body forwarders. No Deref, receiver/evaluator reference, configuration,
shutdown, map_host, ownership conversion or receiver-reference return is provided.
The enclosing HRTB operation's result is independent of its facade lifetime.
Forgetting the facade cannot suppress cleanup; scoped transfer cannot outlive the
enclosing call. Fixed forwarded bodies remain trusted code, audited not to replace
or reconfigure the active worker; this invariant is not type-proved by the facade.

Opening and body run inside catch_unwind; restoration operates on that same
receiver before returning/resuming. Cleanup failure cannot replace an already
propagating panic. Production panic=abort is unchanged and runs no lexical cleanup.
Nested entries restore only their entry depth while live; final outer exit parks.
Terminal/drained shutdown dominates saved depths. Inner exhaustion can join at
depth two; both subsequent cleanups must be idempotent, retain zero depth and
avoid a second retirement charge/panic.

All production entry sites are covered: ordinary fixed/seeded, timed, public
root/Q/subtree/observed/continue and first_iteration with its nested root/continue
calls. Standalone FULL/FRESH/observed numerical prefix returns only owned
intermediates, closes its one-call activation, then runs the original shared
retained/stat/observer/finish suffix. An outer active search calls the common
prefix directly, adding no per-FULL catch/refcount. Public callbacks receive
values/snapshots or their Host, never mutable Search/Evaluator. Public conditional
Send/Sync and completed-call migration remain; default mode1 and existing mode2
are distinct, with mode2 retaining its previous private guard contract.

## Cells and owner state

Box OwnerState owns generation, depth, Flight/Metadata, Readiness and monotone
drained state. Ordinary fields require exclusive worker access. Shared contains
only immutable publication/input, independent output/done cells, lifecycle/wake
and cold synchronized failure/parking state. Helpers cannot read or retire Flight
or update histograms. Narrow Cells Sync remains the only such unsafe impl.

Dispatch requires active original owner, nonterminal observation and local None.
Initialize the same Packet, install local Published and release exact request(g).
None proves old input reads and output consumption ended. A helper failure racing
publication cannot reclaim cells or fabricate a peer acknowledgment.

Each reader acquires request(g), ends all Packet references including timing,
then writes only its own scalar output and releases done(g). Normal complete
acquires both matching done, verifies the local Published generation and scalar
generations, checks terminal before committing, records the same observations and
sets None. No independent final closer can race consumption. Ended owner output
reads precede the next request Release/reader Acquire before output overwrite.
is_complete_now remains a scheduling hint and never supplies retirement.

Final close owns local Discarding, publishes inactive under the cold mutex and
waits for both real parked/exited acknowledgments. The reader's request/seen
recheck under that mutex forbids acknowledging PARKED with unseen published work;
request publication precedes closing's release. Reopening waits for actual IDLE.
Terminal handlers publish only their own error/exit plus stop. On error, cleanup
stops/wakes and joins both actual started readers before clearing/freeing state.
Only genuinely unstarted readers may receive startup-retired state. No timeout or
terminal flag retires a live peer. Repeated already-drained cleanup is a no-op.

## Notification and costs

The original unconditional publisher SC exchange, sole waiter registration,
predicate recheck, Sleep-coordinated notification and spurious-wake re-registration
remain. No cold lock spans spinning/Sleep or real join, and Sleep is not nested
with cold control. Late prior-generation latch work does not access Packet or
outputs and cannot authorize reuse.

Normal dispatch/complete Control acquisitions and sampled owner_ready acquisition
are removed, with no replacement per-call CAS/Arc lease. Cold activation/failure/
park/join still synchronize. Box startup allocation, indirection, shared-tail
relocation, entry catches, common prefix return storage and generated-code changes
are part of the candidate cost. The cold production query must report actual
Shared/OwnerState and preserve the selected request/packet/output offsets and
alignment. No cache cause or isolated mutex saving follows from a wall difference.

Existing independent Send-final-close race tests no longer describe an available
operation. Replace those capabilities with enclosing discard/unwind and whole-owner
migration controls while retaining delayed input/output/done, real peer drain,
startup/exhaustion and SC registration controls. Actual focused filters/counts,
source checks and limits are frozen in preparation.json before native work.

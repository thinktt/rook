# Per-reader completion registration: source design

Recommendation: one fixed generic discriminator is justified if selected.
Separate the two hot notification writers while retaining the original
unconditional SC RMW and every completion/retirement predicate. No concrete
lost-wake blocker was found by this source review or one independent Sol proof
reader. Profitability is unmeasured; no implementation or native run was made.

Proposed base is exact single-owner69, source checkpoint19a1c1b8 and provisional
PGO imagec242f0e4/profile1a81bdac. Its frozen
`/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01/src/colors_worker.rs`
has SHA256 `28403ecd416b7c4db04ab04100540be444ecf6b7e356372435cfb7b00bd88e2c`.
[PGO closure](../../experiments/multicore-feasibility/single-owner-own-pgo/report.md)
remains unchanged. This is independent of the
[parked two-fence experiment](../../experiments/multicore-feasibility/completion-fence/report.md).

## Concrete contract

Replace Shared.latch with `latches: [LatchRegion; 2]`; each existing
`repr(C, align(64)) LatchRegion` holds one AtomicBool. Initial values are false.
Reader i publishes output/done exactly as now, then always performs
`latches[i].waiting.swap(false, SeqCst)`. If true, it acquires Sleep and notifies
the existing completed Condvar, without a second flag/terminal check. A false
result skips only Sleep/notification, never the exchange.

The sole coordinator preserves4096 spins. On the cold path it holds Sleep,
exchanges flag0 true and flag1 true, BOTH SeqCst, then checks the original stop
and matching-done predicates. On a resolved predicate it exchanges BOTH false
before dropping Sleep. Otherwise Condvar::wait atomically unlocks/sleeps. On
every spurious or early wake it registers BOTH again before either predicate;
there is no clear between a failed predicate check and sleep.

Cold owner/all-reader signaling performs BOTH unconditional SC false exchanges,
saves their results, then locks Sleep/notifies once if either was true. Boolean
short-circuiting must not skip the second exchange. All signal calls occur after
releasing Control. No new waiter, mutex, generation reset or notification-as-
completion rule is introduced.

## No-lost-wake argument

For one cold loop let R_i be its true exchange for reader i and P_i a false
exchange after that reader's done publication. Each flag's updates after
initialization are acquire/release SC RMWs; each reads its immediate predecessor
in modification order. Intervening RMWs therefore carry publication transitively,
including via release sequences. No synchronization through the other flag is
assumed.

If P_i precedes R_i in that order, its done store happens before the subsequent
predicate load through the acquired chain. That load cannot observe a preceding
done value. Under the sole-owner contract no later request can overwrite done
while this call waits. If P_i follows R_i, the first intervening false exchange
consumes true and owes a notification. It may be P_i, a delayed older publisher,
or a cold terminal signal. All such true consumers notify without rechecking.
The waiter holds Sleep from registration through its check and atomic
unlock/wait; the notifier cannot complete its Sleep-protected notification in
the check/wait gap. If the predicate remains false, a wake is owed.

This applies separately to every incomplete reader. Both registrations precede
the combined predicate checks, including an event between the two exchanges.
An already-complete reader may cause an unnecessary wake; any still-incomplete
reader keeps the same argument. Short-circuiting both_done's loads does not
matter: a false aggregate has at least one incomplete demand requiring progress.

A prior-generation P_i may clear a new generation's registration after its old
done allowed the owner to advance. It still owes the wake, then that reader
processes the new request and exchanges again. If the current completion finds
false, the earlier true consumer already owes a wake. Two pending true consumers
may notify redundantly, including after another wake or a later generation;
every new cold loop registers both again and uses only actual predicates.
Neither notification nor flag value can authorize output consumption. Exit
clears are safe because this waiter has resolved its predicate and will not
sleep; any previously owed notification remains harmless and unconditional.

For terminal publication substitute stop.store(Release) for done.store(Release).
A reader terminal uses its own flag; owner terminal exchanges both. If that
publication precedes registration, the acquired chain carries stop. Otherwise
some true consumer owes the Sleep-protected wake. This includes a stop after
the false terminal check. A successful completion racing stop retains the
existing complete() terminal rechecks, not a stronger new linearization claim.
Spurious wakes are safe only with both re-registrations on EVERY cold loop.

This proof requires eventual scheduling and functioning primitives. A reader
descheduled after done but before its exchange/notification can still delay a
sleeping coordinator. There is no bounded wall-time guarantee. Stop is never
peer retirement: the owner must still acquire matching done or obtain both real
parked/exited acknowledgments/joins before input reuse or destruction.

## Complete signal inventory

Line references below name the frozen colors_worker.rs, not mutable main.

| Event / source | Proposed signal |
|---|---|
| Normal output/done,765–771 | Reader i only, after original done Release |
| Reader normal exit/error/caught unwind,314–327 and889–905 | publish_terminal(i): original state/stop publication, then reader i signal |
| Spawn failure/unstarted slots,303–357 | Existing failed_spawn→publish_terminal for each explicit genuinely unstarted slot; no invented peer done |
| Uncaught join failure,659–664 | Existing publish_terminal(i), same side-specific signal |
| Owner shutdown/Drop,640–658 and711–721 | Stop under Control, release Control, then both-flag cold signal |
| Epoch exhaustion,441–452 | Same both-flag cold signal after stop/owner failure, before original shutdown/drain |

These cover every production stop.store and existing signal_completion call.
Activation, startup/parking, final-scope close and quiescence waits use the
separate Control/wake protocol (340–422,928–945); retain it unchanged. Actual
single ownership excludes concurrent owner shutdown during complete, but does
not justify deleting those cold signal sites. Native panic=abort cannot promise
unwind recovery; existing test-unwind and ordinary returned-error evidence remain
distinct.

## One prospective geometry and complete cost

Preserve request, packet, both output+done slots and lifecycle prefix exactly.
Output56+done8 already fills its64-byte slot; do not repack it. The proposed
non-test production layout is:

| Region | Offset | Bytes |
|---|---:|---:|
| request | 0 | 64 |
| packet | 64 | 320 |
| white output+done | 384 | 64 |
| black output+done | 448 | 64 |
| lifecycle | 512 | 64 |
| reader0 registration | 576 | 64 |
| reader1 registration | 640 | 64 |
| Sleep/Condvars | 704 | 64 |
| cold Control | 768 | 128 |

Expected Shared896B/align64 replaces832B; OwnerState6368B/align16 and Cells448B
stay unchanged. This is a source-derived expectation, not a compiled observation.
An actual production-type cold projection must confirm it before any selected
timing; no allocator/header investigation is needed.64-byte separation is a
fixed hypothesis, not discovered host cache geometry.

Two normal completions still perform two unconditional SC exchanges. Their
different words/regions remove the explicit shared writer word; reduced
helper-to-helper coherence cost is only a hypothesis. Each helper still writes
a registration region separate from output/done. Cold coordinator registration
and exit clearing each double; owner terminal doubles exchanges; the polling/
transfer footprint grows one region and moves Wait/Control. Two true publishers
may each lock Sleep/notify. Preserve output/math, input copying, both winning
owner hooks, observations/clocks, spin policy, close/drain and cell access rules.
Future results would price the whole code/layout/protocol variant, not isolate
coherence nanoseconds or imply scaling beyond three threads.

## Smallest decisive next scope, if selected

Change only this worker protocol/storage and its cold projection. Rerun the
27 existing worker lifecycle controls with new layout/flag assertions; reuse
the43 unaffected single-owner controls and numerical evidence. Extend the
existing forced interleavings proportionately: publication before/between/after
both registrations for each side; delayed prior-generation true consumer;
both true consumers pending on Sleep; spurious re-registration; side terminal
and owner/all-reader terminal during registration; assert the second cold
exchange occurs even when the first reads true. Keep real delayed-peer drain,
partial startup, output retirement and nested epoch-exhaustion controls. No
general model checker or new observation framework is proposed.

One generic original35/08/43 old1/old3 versus matching new1/new3 fixed48+4 would
price inline drift and the complete transport effect using existing machinery.
One cold actual-layout/CLI/affinity admission precedes it, query off during
timings; same spins, hooks, owned inputs and native bounds. No new census,
padding sweep, fence weakening or automatic PGO/qualification/adoption. This
note selects none of those executions; implementation remains a lead decision.

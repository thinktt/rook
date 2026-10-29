# Completion epoch as strong publication: source recommendation

Recommend ONE later generic discriminator if selected. No source-level
lost-wake blocker was found by this review or one independent Sol challenge,
provided the cold done predicate is SC and all old terminal signaling remains.
This does not establish profitability. No implementation, lowering inspection,
build, native test, model checker or measurement was performed.

Base is exact single-owner69 at
`/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01`:
colors_worker.rs SHA256 `28403ecd416b7c4db04ab04100540be444ecf6b7e356372435cfb7b00bd88e2c`.
Preserve provisional c242/profile1a81, genericd71 and every predecessor. The
[slower two-flag result](../../experiments/multicore-feasibility/per-reader-completion/report.md)
remains parked; this proposal restores the original single flag/layout and moves
strong publication onto each existing output/done region.

## Exact changed seams

At the sole normal done store (frozen line765), change Release to SeqCst, keeping
all input borrows ended and scalar output written first. After the unchanged
seen assignment and test scheduling seam, replace the normal signal call at771
with an SC load of waiting. True unconditionally owes Sleep-lock/notify; there
is no normal flag clear/exchange, explicit fence or second predicate check.

Keep both_done's Acquire loads for hot4096-spin polling, is_complete_now and
the actual output-consumption recheck. Add a distinct cold-only predicate whose
done loads are SC; use it only after the existing SC true registration at871
inside wait_completion's cold loop (original predicate878). Every loop registers
before checking stop/done, including spurious wakes. Keep the resolved-exit SC
false exchange at880 and Sleep/Condvar gap unchanged.

Keep the original signal_completion helper851–855 as the COLD terminal helper,
with unconditional SC false exchange and true-consumer notification. Leave all
its terminal callers unchanged: reader return/error/unwind314–327/889–905,
failed spawn/genuinely unstarted slots303–357, join error659–664, owner shutdown/
Drop640–658/711–721 and epoch exhaustion441–452. Release Control before Sleep.
Activation/park/quiescence still use the separate Control/wake protocol.

No field/type, request, Packet, output, retained state, math, hook, observation,
spin or activation-boundary change is needed. Expected actual layout stays the
base Shared832/align64, OwnerState6368/align16, single latch576, Wait640,
Control704 and original request/packet/output/lifecycle prefixes.

## Normal no-lost-wake argument

The [Rust Ordering reference](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html)
identifies its C++20 correspondence. The
[atomic-order rules](https://eel.is/c++draft/atomics.order#4) preserve order for
sequenced SC operations and constrain SC order by per-object coherence. SC stores
are also Release operations. These are local premises, not whole-program SC:
the [mixed-order warning](https://eel.is/c++draft/atomics.order#6) remains relevant.

Applying those rules to this protocol: let R be this cold loop's SC true
registration. If the combined cold done predicate is false, choose a reader
whose actually executed SC done load Q is below the current generation g.
Its current SC publication D follows all payload accesses; its subsequent SC
flag load is L. Sequencing gives R<Q and D<L in SC order. Done writes have one
writer per side, strictly increasing nonwrapping epochs, and every normal store
is now SC. Coherence therefore puts Q<D. Together **R<Q<D<L**.

No g+1 store can exist while this sole owner waits for g: a new request requires
completion/output-read retirement of the current Flight. Thus Q cannot fail
equality by reading a future epoch. Short-circuiting the pair is harmless: one
executed mismatching Q supplies the argument. Initialization precedes thread
publication and cannot provide a later non-SC modification bypassing R or D.

Waiting's modifications after initialization remain SC RMWs: coordinator true
registrations/resolved-exit clears and cold terminal clears. Normal publishers
only load it. If none intervenes after R, L sees true and owes a notification.
If a cold terminal clear intervenes, its first true consumer owes the wake
instead; later false consumers cannot cancel it. A coordinator exit clear means
this sole waiter resolved its predicate and will not sleep. An older exit clear
is sequenced before the current R, so cannot clear the new registration.

The waiter holds Sleep across R, the predicate checks and atomic unlock/wait.
An owed notifier cannot complete its Sleep-protected notification in the
check/wait gap. It must notify without a later flag/terminal recheck. Every
spurious or early wake repeats registration before predicates. This proves a
wake obligation when the cold predicate remains false, under eventual scheduling;
it gives no scheduling-time bound.

The SC cold Q is essential to this argument. An Acquire-only load supplies no
Q<D relation in SC order; keeping the old cold predicate would not implement
the proved protocol. No claim is made that ordinary interleaving tests alone
can detect that abstract-memory-model mistake.

## Terminal, delayed publication and retirement

For terminal event T, stop.store(Release) precedes its old SC false exchange C.
If C precedes R in flag modification order, R acquires its publication directly
or through intervening acquire/release RMW modifications. The added normal loads
do not modify the flag or break that chain. Consequently the subsequent Acquire
stop check observes terminal. If C follows R, C or an earlier terminal clear
consumes true and owes the Sleep-protected wake. A terminal event after a false
stop check is covered by the same two cases. This proof does not require stop
or every hot load to become SC.

An old-generation L that already read true keeps its notification obligation
across exit clears/new registrations. A delayed old false L is harmless: that
reader must return to the loop, acquire the next request and perform its new
D/L. Two readers can both read true because neither clears the flag; redundant
notifications are safe and may cost more. They can arrive after re-registration
or in a later generation but grant no output-access authority.

A successful completion racing stop retains all existing complete() terminal
rechecks and original error/drain handling. Terminal observation never retires
the peer. Hot polling/output consumption may remain Acquire because matching
reads still acquire D's Release component. Lexical input-borrow end before D,
both actual done/real park-or-exit retirement, and next-request reverse output
reuse edges remain indispensable. Monotone terminal/drained state still dominates
nested saved-depth restoration. Native abort and test unwind remain distinct.

## Economics and smallest decisive continuation

Old normal completion has a Release done store plus SC flag exchange. Proposed
completion has an SC done store plus SC flag read, no normal shared-flag write.
It moves strong publication to a region the helper already writes, without the
two-flag trial's64B growth/cold-region relocation. On x86 this could avoid an
exclusive write to the shared flag; exact lowering/cost remains unobserved.
Strong done publication can contend with owner polling, delay publication or
perturb code layout. A registration left true can cause both helpers to lock
Sleep/notify instead of one true-consuming publisher. Extra cold SC done loads
also count. It removes neither all strong operations nor any search arithmetic.

The two-flag negative prices a different code/layout variant; it neither proves
shared-flag traffic was cheap nor predicts this mechanism's gain. The parked
two-fence protocol likewise is not being rescued: there is no explicit fence,
and the critical SC relation now includes actual done publication/observation.
No new parallel width or exact performance forecast follows.

If selected, reuse43 unaffected single-owner controls and rerun the27 affected
worker controls on a one-file derivative of base69. Target the new normal-load
path with completion before/around registration, a true L paused across resolved
exit/new generation, two simultaneous true loaders, spurious registration and
mixed terminal exchange while a true loader remains owed. Keep delayed-peer,
partial startup, nested exhaustion and actual output/borrow retirement controls.
Source admission must check the cold SC predicate and unchanged hot Acquire
scope; native controls support interleavings, not exhaustive weak-memory proof.

One unchanged-layout generic old/new inline1/3 original35/08/43 fixed48+4 would
price complete transport drift, reusing existing tools and one cold actual
layout/CLI/affinity admission. No new collector, census, model-checker, padding
sweep, profile or automatic qualification/adoption. This note recommends that
finite discriminator but selects no implementation or native work.

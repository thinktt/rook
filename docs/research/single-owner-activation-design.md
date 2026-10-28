# Single-owner activation with owner-local Flight

2026-10-28, imp2. Source-only design and one Sol API/lifetime challenge against
retained writer68; no implementation, unsafe change, build, test or timing.
Preserve `a4ecf096` / profile `6cb9dcaa` and all earlier artifacts.

**Feasible: recommend one isolated generic discriminator if separately selected.**
Remove the independent closing capability, not its locks under today's contract.
An inaccessible enclosing operation can retain the exclusive original receiver
through actual closure, with owner-local Flight/readiness and cold shared failure/
parking. A restricted facade is essential: an unrestricted `FnOnce(&mut Self)`
could replace Search.evaluator or move the active receiver into its return value,
then cause cleanup to close a replacement. Private visibility alone is insufficient.

## Supported use and the boundary to preserve

Anchors refer to
`/home/legolas/rook2-experiments/workspaces/writer-regions-20261026-01/src`,
whose reviewed files match the [retained source map](../../experiments/multicore-feasibility/writer-regions-own-pgo/preparation.json).

| Actual use | Required treatment |
|---|---|
| ordinary555; timed497; Q138/179/194/232 | Enclose each existing public search/preparation entry, preserving normal/error/unwind cleanup. Recursive visit methods do not open per-node activations. |
| first_iteration50 calls prepare_root64 and continue_subtree87 | Preserve real nesting; inner entry closure must not park an active outer search. |
| evaluator680–774: standalone FULL/FRESH/observed and selection wrappers | End one-call activation immediately after chain completion, **before** retained/stat/observer/finishing suffix. Outer-search calls retain the enclosing activation. FAST-only starts no helper. |
| public callbacks | Evaluator passes values, Q observer gets snapshots, seeded callback gets i32, Host gets only its own mutable receiver/records/commands. None receives the active Search/Evaluator. |
| Search.map_host153; Session.go_live593/615 | Preserve ownership transfers before/after run_work_timed, and ordinary Send/migration between completed calls. Host cancellation remains prescribed cooperative polling, not an independent worker-close API. |

ColorsActiveScope and ColorsWorker are crate-private. Concurrent final guard
drop is a real current internal capability, extensively tested, but no public
callback or production entry requires that capability. Safe external code cannot
replace the active receiver through a second mutable borrow while the enclosing
call exclusively borrows it. Public `Search.evaluator`, configuration, reporting
shutdown and map_host remain available between calls; they are not exposed by
the active facade. Branch-transactions already has an Rc-based non-Send sink:
preserve existing conditional traits, not a stronger all-feature Send claim.

## Enforceable enclosing API

Use a private lifetime-bound facade with a hidden `&mut` borrow of the original
Search, and a separate equivalent for standalone Evaluator preparation. No Deref,
receiver/evaluator reference, configuration, shutdown, ownership conversion or
reference-returning forwarder. Expose only named operations forwarding to the
existing fixed entry bodies. Keep construction/forwarders in the owning module;
make only the necessary body functions crate-visible. They never replace the
receiver or reconfigure its worker. This is a small closed API, not an extensible
user callback framework.

Type sketch, **uncompiled**: the enclosing operation accepts
`impl for<'a> FnOnce(ActiveSearch<'a, D, H>) -> R`, with `R` independent of `'a`.
It keeps the original receiver borrowed, invokes that facade under
`catch_unwind(AssertUnwindSafe(...))`, closes the same owner, then returns or
`resume_unwind`s. The closure never gets `&mut Search`. Forgetting the facade
cannot suppress wrapper-owned cleanup or retain a usable receiver reference.
Scoped transfer may move its exclusive borrow to another thread when the
existing types are Send; safe scoped threads finish before wrapper cleanup.
Single ownership does not require a permanently fixed coordinator thread.

Record the owner-local entry nesting depth before opening. Protect opening as
well as the body: partial activation failure must restore that entry depth and
drain any actually awakened readers. Nested entry increments/decrements ordinary
depth; only zero-to-one wakes and one-to-zero parks. Cleanup errors on a normal
return follow the existing error/panic policy. During existing unwind, drain
without a second panic and resume the original panic; do not promise search-state
rollback. Production panic=abort remains abort and runs no lexical cleanup.

For standalone public FULL, extract one shared numerical **prefix** through the
joined ActivityShelter result, returning only owned intermediates needed by the
existing common suffix. The enclosing Evaluator operation closes before that
suffix publishes retained/stats or calls observers. An observer panic therefore
sees already parked standalone helpers; inside an outer search it unwinds to the
outer cleanup. Inventory-hook/prefix panic is inside the protected interval.
Outer-search FULL takes the direct shared prefix under its existing activation:
no new per-FULL catch, closure lease, Arc clone or refcount. Prefix/suffix factoring
is shared by inline and parallel modes; no numerical duplication or borrowed
input change. Its returned storage, spills and code layout are genuine costs.

## Concrete owned/shared split and execution proof

Choose one cold-start `Box<OwnerState>` owned exclusively by ColorsWorker:
generation, nesting depth, Flight/Metadata and the unchanged Readiness/Metric
types. This avoids embedding the large histograms directly into Evaluator/Search
while preserving ordinary-field Send/Sync properties. It adds a startup allocation
and pointer access; no per-call allocation. Do not use Cell/RefCell or broaden
UnsafeCell/Sync to mutate owner state through shared references.

Keep Arc Shared for the existing owned Packet, two output/done regions, request,
stop/reader states, original SC-RMW/Sleep completion protocol and cold mutex/
condition-variable parking/failure records. Cold active state plus the existing
active_scopes atomic communicate only outer activation transitions; nested depth
is owner-local. Helpers never read or retire owner Flight and never update its
histograms. Startup, helper terminal handlers and joining retain cold locking.

1. **Dispatch:** exclusive owner requires active depth, Flight::None and a
   nonterminal observation. Initialize the same owned packet; install local
   Published metadata/counters and release request(g), with no fallible gap.
   None follows ended output reads plus both matching done Acquires, or actual
   retirement of both readers. A helper failure racing the terminal check can
   make this job fail, but cannot reclaim or overwrite cells; terminal handlers
   have no owner-state access.
2. **Completion:** retain the original spin/cold predicate wait. Check matching
   local Published/generation and both real done, copy scalar outputs, verify
   generations and recheck terminal before committing local readiness/None.
   No owner close can race these operations: the facade cannot close, and closure
   requires the exclusive receiver after its operation returns. A terminal event
   ordered after the final success check may affect the next operation; this is
   not fake output or a promise that no later failure can occur.
3. **Ownership edges:** both concrete helpers end every Packet access, including
   sampled timing, before output write/done Release. Owner done Acquires publish
   outputs; Copy reads end before None. The next request Release/reader Acquire
   carries the reverse edge before output overwrite. Composition/rounding and R
   remain unchanged. is_complete_now stays a hint, not retirement.
4. **Final close/discard:** owner marks local Discarding, then under the cold
   mutex publishes inactive and waits for **both** real parked/exited states.
   A reader must process an unseen request before parking; the existing cold
   request/seen recheck remains. Request publication precedes closing's mutex
   release, so a parking reader acquiring that mutex sees the published work.
   Reopening waits for actual IDLE acknowledgments before dispatch.
5. **Failure/shutdown:** helpers publish only their own terminal state/error and
   stop, never peer done or Flight::None. Error cleanup stops/wakes and actually
   joins both started readers before freeing/reusing cells/OwnerState. Only
   genuinely unstarted readers may receive startup-retired state. A terminal bit
   or deadline is not peer retirement. Drop owns the same worker and drains it;
   no independent close handle survives the enclosing borrow.
6. **Wake:** leave every publisher's unconditional SC exchange and every cold
   registration/recheck unchanged. Sleep still orders notification against atomic
   unlock/wait; re-register after each spurious wake. Keep cold and Sleep locks
   unnested, and hold neither during join. Moving Flight does not replace this
   lost-wake proof or turn terminal into completion.

## What disappears, what remains, and the smallest later test

Normal dispatch's Control lock/unlock and normal completion's Control lock/unlock
disappear; sampled owner_ready also writes its metadata locally. Local exclusivity,
depth/Flight checks and the existing atomic predicates replace arbitration, not
per-call CAS/refcount/another shared lease. Owned input copies, done/request edges,
SC notification, conditional Sleep locking, all sparse observations and numerical
work remain. Cold activation, parking, failure and shutdown still synchronize.

Moving the large control/readiness tail out of Shared changes allocation/storage
and owner locality. Preserve existing concrete request/packet/output region types
and observation definitions; require actual geometry admission later, rather than
assuming identical layout or a cache benefit. Inline has no worker allocation,
but common entry/prefix factoring can still alter its generated code. Mode2 can
keep its existing one-helper guard privately inside its enclosing wrapper; do not
silently change that worker contract or claim its hot locks removed.

Old tests map to the new supported contract:

| Existing obligation | New representation/control |
|---|---|
| Concurrent independent final guard wins dispatch/consumption; outliving guard | Capability removed. Verify facade cannot expose/extract/configure/close receiver or return a borrowed lease; replace the race witnesses with supported whole-owner migration and enclosing unwind/discard. Do not delete helper-drain obligations. |
| Delayed input, output-before-done, sampled last read, reverse reuse | Retain actual gates: final enclosing close must wait for both readers and next publication must not reuse early. |
| Helper failure/normal stop, partial startup, unpublished failure, exhaustion | Retain real terminal/join and no-output controls against local Flight. |
| Completion before/during registration, prior delayed latch, spurious wake | Reuse original SC-RMW controls; no memory-order weakening. |
| Standalone/nested/use after error | Add actual first-iteration nesting; FULL/FRESH observer parking; prefix/Host/observer unwind; configuration afterward; conditional public Send/Sync assertions and migration. |

This targets two normal acquisitions on **every** FULL rather than an unpriced
rare shape, with a concrete way to remove their cross-thread closing cause.
That breadth justifies one later integrated discriminator, not a saving forecast.
If selected, reuse the original three-case generic machinery for preserved writer
generic1/3 (`8c217f96`) versus same-source new inline1/new3, with both winning
inventory hooks on, full CPU/lifetime/idle and replay checks. Keeping old1 prices
the common wrapper/refactor cost directly. The lead's preliminary fixed48+4
comparison remains unselected pending its safety challenge. Preserve a4ec PGO;
no collector, padding/observation sweep, PGO or adoption is proposed. Reuse
unchanged numerical evidence and focus the controls above on the changed contract.

The [borrowed-input trial](../../experiments/multicore-feasibility/borrowed-full-input/README.md)
shows enclosing/refactor costs can erase a conceptual saving. It did not remove
the independent activation-close capability or test owner-local Flight. This
design preserves owned input, original arithmetic and SC-RMW; its first result
would price the complete contract/storage/refactor change, not isolated mutex ns.
No implementation is authorized by this source-only checkpoint.

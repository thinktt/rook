# Concrete pre-map ownership and caller argument

Source base and design are bound by preparation.json. This argument covers the
fixed private call graph, not a reusable asynchronous borrowed-input API.

The coordinator owns Flight/activation and requires None before publication.
It writes immutable Supplied or FreshPosition Packet once, then releases request g.
Request Acquire orders its earlier active_scopes=1 store. Each helper borrows that
Packet while preparing private128B geometry. Fresh readers poll exact mapReady g;
only the coordinator writes the separate initialized Influence cell and releases g.
An acquired exact epoch authorizes immutable direct map reads until that reader
has ended all input/map borrows. Supplied jobs use their supplied map and never
infer readiness from the separate cell. Old epochs across supplied gaps cannot
satisfy equality. No whole-Packet mutation or helper-local full-map copy occurs.

Successful output/done publication follows all Packet/map reads, including sampled
accesses. Both matching Acquire done acknowledgments end input ownership before
copying outputs and retiring Flight. Next request carries the reverse output edge.
Original completion SC RMW chain/Sleep single-waiter proof and terminal exchanges
are unchanged. A terminal failure never fabricates a peer done; actual joins
retire both readers. Retained state/cache stats/semantic R and observers occur
only in the original coordinator composition after actual completion.

A fresh missing-map wait also observes last-scope inactive. It returns an OWNED
Abandoned value after every input/map reference ends; only then reader seen=g
advances and the existing Control-serialized park runs. The owner remains
Discarding until both real PARKED/exited acknowledgments. No successful done or
mapReady is invented. Request Acquire excludes seeing stale pre-activation zero.
Activation reopen/next publication cannot precede actual retirement. Stop/failure
ends waits and joins rather than treating one reader as both.

Positive-depth restore leaves the outer activation live and is not cancellation.
The combined private FULL entry may not return normally/Result with map missing,
or catch and retry internally. Its straight segment has no Host, observer, poll,
recoverable error or descendant call: dispatch -> original ensure/map charge ->
map publication -> common pawn/local/join prefix. Panics propagate through every
nested finish_activation, which resumes the original panic after restoration,
until saved-zero owner close drains the request before receiver reuse. Standalone
private entry encloses that entire prefix and parks before full_suffix/observers;
outer searches retain their existing activation ownership. This relies on the
fixed callers; adding internal recovery would require an explicit cancel seam.
Native panic=abort does not promise cleanup; test unwind covers unwind behavior.
Terminal/joined state continues to dominate saved-depth restoration.

Private coherence permission comes from validated joined ancestry, never public
planes/hash inference. <=16 pieces/color including one king gives <=15 Activity
sources; eight bytes/source plus friendly occupied-mask8 =128B. Rays <=7 targets.
Direct prefix includes first occupied; friendly targets remain filtered. Visited
prefix preserves transparent extensions. Knights retain original target order.
Shared consume_destination retains numerical/category/capture/marks/R; original
per-piece penalties/pressure/rounding and coordinator finishing remain owners.
Some/custom/public/FRESH/observed/noncoherent/modes1/2 do not use fresh staging.

Focused numerical, actual-owner, stale-epoch, cancellation, delayed-borrow,
nested-unwind, real-reuse/failure/terminal controls support this source argument;
interleaving tests do not establish weak-memory correctness exhaustively.
No API escape, per-FULL Arc allocation, peer phase barrier, alternate map producer
or hot activation census is introduced. Storage/second-pass/cache transfer and
changed inventory readiness are complete timed costs, not free semantic facts.

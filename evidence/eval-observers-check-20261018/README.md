# Shared evaluation observer regression

Isolated generic native `2c741929` passes all54 unchanged strict profiling
replays and eight interruption fixtures/24 searches, after134 native unit tests.
The linked adapter `1f5a0ceb` separately passes64 operations/3470 unique cases
and58 adapter units. Exact binary/source/build/report identities are retained
in [identity.json](identity.json) and the linked receipts.

The only native43 changes are `evaluation.rs` and `shelter.rs`. Existing
root material interpolation and oriented square interpolation become shared
native functions; production uses those same functions. An explicit-current-phase
square-balance entry shares the old body, while the production entry derives
the same phase as before. Existing raw shelter components become public.
RootContext/Position/Node layout, cache ownership, formulas, rounding, charge
order and search entry points are unchanged. No new arithmetic lives in JSON
transport. Unsupported/invalid inputs still fail explicitly.

The five added diagnostic routes cover root material values/current counts,
square values/current balance and raw king shelter. They preserve independent
root/current phase, color ownership, broad admitted promotion-heavy setups,
adjacent kings, duplicates, empty square-query arrays, single king rounding and
pawn-only doubling. The extra native king square query uses the existing basis;
production root storage still contains its original five non-king kinds.

The first external attempt failed the released loader's version-header check
before any external diagnostic case executed. Its58 units had passed. The
fresh corrected selection preserves the three original identity case objects
and metadata; both failed and successful attempts remain. Two later offline
wire reconciler path mistakes were corrected against the retained `.raw` files;
neither reran an engine. The final identity checks original exits, complete
streams, all24 search results and raw wire hashes.

These are isolated source proposals, not integrated source or a new canonical
PGO/performance checkpoint. Existing8d timing/gameplay observations retain their
own exact artifact. The runtime build has no fixture or expected-answer access.

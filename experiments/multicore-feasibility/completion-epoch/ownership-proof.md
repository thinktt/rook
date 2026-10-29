# Strong completion-epoch proof and unchanged ownership

Base exact single-owner69: only colors_worker.rs protocol/tests. The
[source design](../../../docs/research/completion-epoch-publication.md) contains
the full local SC/coherence plus Sleep argument, mixed terminal acquire/release
RMW chain, delayed true loads/spurious wake and actual retirement premises. One
independent Sol source challenge and lead review found no concrete blocker.

For one cold mismatching reader, R<Q<D<L: SC registration precedes cold SC done
load, coherence puts the old-epoch load before current SC store, which precedes
its SC flag load. Without terminal/exit clear L reads true and owes a Sleep wake;
a cold true-clearing terminal publisher instead owes it. Exit clears occur only
after this sole waiter resolves. Hot/output Acquire matching loads still acquire
the Release component of SC done. No future epoch exists while the sole owner
waits, epochs never wrap/reset, and a notification never grants cell access.

Cold terminal helper and every caller remain identical; normal loads do not break
the flag modification RMW acquire/release chain. A delayed true loader must notify
without any flag/terminal recheck. Parent must verify the distinct cold SC predicate
is not accidentally replaced by hot Acquire. Native tests support forced schedules,
not exhaustive weak-memory proof. Eventual scheduling is assumed, no time bound.

ALL production types, layout/projection, numerical bodies, input ownership,
activation/terminal depth, original observation/spin policy and Cells Sync remain
unchanged. Actual done / both real park-or-exit acknowledgments and the next-
request reverse output edge retain the existing unsafe-cell contract. Native
panicabort is distinct from test unwind. Lowering and geometry are pre-data gates;
there is no new unsafe ownership or lock-order relaxation.

# Per-reader registration ownership and wake proof

The implementation base is exact single-owner69. Only colors_worker.rs changes;
packet/output cell access, Flight/nesting, math/observations and both inventory
hooks remain fixed. The private Cells Sync contract is unchanged.

The [source design](../../../docs/research/per-reader-completion-registration.md)
contains the full per-flag SC modification-order/acquire-release-chain argument,
sole Sleep waiter gap proof, stale-epoch/two-notifier/spurious-wake cases,
terminal routing inventory and expected geometry. Normal reader i always swaps
its own flag false after actual done. A true consumer owes a Sleep-protected
notification without a second check. Sole owner registers BOTH flags before
EVERY cold predicate and clears BOTH on resolved exit. Cold all-reader signal
executes BOTH swaps separately before OR; Control is released before Sleep.

Neither flag nor notification acknowledges input retirement or permits output
consumption. Matching done acquire / actual both-reader park or join and original
reverse output edge remain authoritative. A delayed true notifier still owes its
wake; no scheduling-time bound is added. Native panic=abort is distinct from
focused test-unwind evidence. Expected non-test Shared896/align64 and owner6368/
align16 require actual cold production admission before timings.

No unsafe payload ownership or active-scope boundary is broadened. The one change
separates existing completion-registration writes; it does not weaken their SC
ordering, remove sparse observations, retune spins or alter demanded work.

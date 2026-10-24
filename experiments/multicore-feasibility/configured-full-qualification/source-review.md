# Configured FULL source review

Reviewed frozen engine source `66f35e440b2180d4d22c2bcd0e5a8c99c0f1185d`
for the selected ordinary PGO image `8f26d39f…`. No material source blocker
found in the supported one-coordinator, at-most-two-thread mode. This review
read source and existing evidence only; it ran no build, test, engine, audit
helper or Git command. Exact-image qualification results remain a separate
obligation, not a result supplied by this review.

Each confirmed FULL copies Position, the exact supplied Influence, current
root-material scalar and color-bound mobility/shelter coefficients into owned
transport storage. Both placements invoke the same Activity→Shelter numerical
body. Binding follows the original root side; it is not redone for the moving
child. The helper receives neither Node/retained state nor pawn cache, TT,
learning, Host or a work ledger. Pawn selection, FRESH bypass, composition,
retained writes, finishing and the single combined relation-count publication
remain ordered on the coordinator after completion and checked standalone-scope
closure. FAST neither dispatches nor selects the pawn cache.
Sources: [binding](../../../src/evaluator.rs#L192),
[FULL](../../../src/evaluator.rs#L553),
[FAST](../../../src/evaluator.rs#L724),
[owned packet/dispatch](../../../src/evaluator_worker.rs#L56).

Ordinary iterations, timed entry, first iteration and public Q preparation/
subtree/continuation paths own lexical scopes; normal Result exits explicitly
finish them, including stopped/error results, while unwinding uses Drop.
Nested guards preserve the outer lifetime. Root rebinding/cache clear occurs
on the coordinator between synchronous calls; fresh packet inputs prevent old
root weights crossing that boundary. Host transfer moves the same evaluator
and worker rather than cloning them. Node charging/polls remain at the original
coordinator boundary; waits add no polling, N/R credit or recomputation.
Sources: [ordinary](../../../src/ordinary.rs#L550),
[timed](../../../src/timed.rs#L490),
[first iteration](../../../src/first_iteration.rs#L44),
[public Q](../../../src/quiescence.rs#L130),
[reset](../../../src/evaluator.rs#L459),
[host transfer](../../../src/engine.rs#L152),
[charge/poll](../../../src/engine.rs#L223).

The wait protocol is coherent for its single submitting coordinator. Completion
registration and output/COMPLETE publication use Slots, so completion before
registration is observed by the predicate and registration before completion
requests notification. Lifecycle predicates use Control. Terminal publication
locks Control→Slots and notifies both conditions; no inspected Slots-held path
acquires Control. Parking clears transport before acknowledgment. Shutdown
requests stop, releases locks and unconditionally joins. A FAILED worker remains
an explicit error after join/retry; setters cannot silently replace it with
inline execution. Newly encountered normal destructor-close errors fail rather
than print and return success; already returned shutdown errors are not reported
twice. Sources: [completion/terminal](../../../src/evaluator_worker.rs#L339),
[parking](../../../src/evaluator_worker.rs#L422),
[shutdown/error ownership](../../../src/evaluator_worker.rs#L269).

Configuration rejects zero and queries above-one requests before mutation.
Exactly one permitted CPU configures one thread while retaining the request;
larger masks permit at most two. Query/start/shutdown failures do not commit a
new requested budget. The Linux query reads the configuring thread's mask,
grows an aligned buffer on EINVAL and reports unsupported/query failures. It
does not widen affinity or estimate physical capacity. Existing helpers are not
reactively reconfigured after external placement. Session configuration rejects
an active search. Sources: [setter](../../../src/evaluator.rs#L343),
[query](../../../src/thread_budget.rs#L1),
[session](../../../src/session.rs#L138).

Existing worker-aware comparisons cover nonneutral/zero weights, root changes,
contrary supplied maps, FAST refresh, FRESH, zero/group/full-identity cache
collisions, repeated searches, node stops and budget transitions. Owner tests
cover live finish/abort/Host error, capacity error, first iteration and public
Q exits. Protocol evidence covers both terminal wakes, completion-before-wait,
abandoned output, nested ownership, joined shutdown and the explicit 11-second
test barrier. The configured-source receipts record eight evaluator comparisons,
three owner tests and the parser check; the unchanged protocol's earlier receipts
and their limits are separately retained in the
[configured report](../configured-full/report.md).

One concrete coverage gap is worth filling without changing frozen production
code: the threaded public-Q owner test uses `Observer::ENABLED=false`
([test](../../../src/evaluator/lifecycle_tests.rs#L54)). Diagnostic Q-tree uses
enabled stage/leave callbacks, but constructs default-one-thread Search
([adapter](../../../diagnostic/src/quiescence_tree.rs#L79)). A focused enabled-
observer Q comparison of mode1/mode2 stage order, retained outputs, PV and N/R
would cover that distinct observation route. Direct FULL detailed-observer
comparisons already cover its numerical producer; this is a test gap, not an
identified race or a reason to label a default1 mandatory pass as mode2.
The parent selected that standalone public-API control outside frozen `src`.
Treat this obligation as addressed only if the qualification record binds its
passing receipt to the same engine source and actual configured mode2; this
source review does not assert a future pass.

Remaining limits: production panic=abort does not execute unwind cleanup;
synthetic failure/query seams and a held test barrier are not native OS fault
or suspension tests. Waiting/joining requires eventual helper progress and is
bounded externally during qualification. Active searches may burn helper CPU
while Host callbacks block. The configuration-time affinity snapshot is neither
continuous placement monitoring nor evidence of scaling beyond two. No additional
production mechanism or general qualification framework is needed to address
these stated limits.

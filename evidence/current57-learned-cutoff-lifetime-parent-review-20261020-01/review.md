# Learned cutoff update and normal fresh-search lifetime

Read-only source crosswalk for actual57 Learning::record/clear and named normal ordinary entry owners. All bound native/adapter files match accepted57 source117; the native bytes also match62. It is not a new runtime test or complete ordinary-search proof. Shared placement/component admission is imported where stated. The active62 measurement's source, flags, samples and inputs were not changed.

## Cutoff numerical owner under admitted component inputs

Assume the supplied placement/piece tags and event descriptor satisfy SEARCH-CANDIDATE-ORDER's component checks, ply1..62, depth0..62, source occupied by the specified side, destination empty or opposing non-king, initial nonnegative history entries with sum<=10000, and valid supplied killer pairs. The direct adapter actually calls moves::candidate before every non-null event update; it does not merely assume remembered descriptors fit a board. Its shared placement parser is a separate admission owner, not re-proved here.

record first filters absent/NONE selections, then returns for any occupied destination. This includes promotion captures and does not depend on MoveKind. For an admitted empty-destination event, source is nonempty, so the implementation's additional empty-source return is unreachable in this direct domain. That defensive branch supplies NO normative rule for an uncertified empty-source native hint; the composed-call question remains unresolved.

For eligible M and old[A,B], testing M==B swaps the pair, and otherwise M!=A selects either empty A or second-slot replacement. If M equals both A and B, the early swap is observably identical to no change. With M==A only, nothing changes. With M==B only, [B,A] results. With no match and A null, [M,B] results; otherwise [A,M] results. Null movement cannot alias a non-null killer because admitted different endpoints have nonzero Move payload. Exact tagged Move equality retains promotion/kind identity for killer comparisons.

Regardless of whether killers changed, the same event adds8*(depth+1) to one history cell keyed by the ORIGINAL source piece's color/type and the destination. A promotion therefore uses the pre-move pawn. EnPassant/castle eligibility follows empty destination; no quiet-only restriction is substituted. Source square and ply do not enter the history key. The board is borrowed immutably; repeating an event uses the same supplied pre-move placement.

If pre-total<=10000, increment lies[8,504], updated total/cell<=10504. Thus all u32 additions, including value+1 during reduction, are exact. Reduction triggers only when total>10000, not on equality. Every one of768 cells is replaced by(value+1)/2=ceil(value/2), and total is recomputed from those values. The resulting sum<=floor((10504+768)/2)=5636<=10000. This proves the history-sum invariant inductively for any allowed repeated events, including4096 repetitions, without a second reduction pass. Killers are untouched by reduction. These are direct-domain bounds; native depth producer admission remains separately scoped.

## Direct reset and snapshot boundary

The adapter starts Learning::default. Initial history keys are duplicate-checked across both colors/all6types/all64squares, with each0..10000 and running total<=10000. Initial killer plies1..62 are unique, and both descriptors are syntax-parsed without requiring them to fit a later board. Cutoff events parse depth0..62/times1..4096 and component-check non-null events before invoking record that many times; no move is applied. Changing event placement/side/ply/depth does not clear learning.

An explicit reset event must have exactly reset:true. It invokes clear, which zeros all768 history cells, total and all65 physical killer pairs. Repeated resets are idempotent; the extra unexposed ply slots introduce no observation. The initial snapshot precedes events, and exactly one further snapshot follows each event's repetitions/reset.

learning_snapshot iterates White then Black, PieceKind::ALL pawn/knight/bishop/rook/queen/king, squares0..63 (rank1..8,filea..h); it omits zero history entries. Killers serialize increasing1..62 and omit only [NONE,NONE], preserving partially null pairs and full tagged descriptors. The descriptor helper emits ordinary+promotion suffix or explicit EP/castle kind as appropriate. No source key or private array order replaces the contract's canonical output.

## Normal ordinary fresh-search versus iteration

Session::go and go_live invoke run_work_timed on the session's reusable Search; go_live's map_host transfers the learning field by ownership without cloning/resetting it. run_work_timed_inner validates entry/ensures the table, then calls prepare_root_with_influence before legal-root generation and first root attempt. That shared preparation calls learning.clear. Therefore every named evaluating ordinary lifetime begins with empty learned state, even when the same Session/Search is reused and without requiring new/undo/setboard/personality to clear it while idle.

Root preparation occurs once before constructing ActualEffects. That owner borrows the same Search throughout timed_sequence::drive. Its begin_iteration_records resets only iteration/PV reporting; begin_candidate constructs a child Node; execute directly calls visit_ordinary_impl on that same Search. Neither creates a new Search nor invokes prepare_root/learning.clear at iteration boundaries or retry callbacks. The non-timed run_iterations_body likewise prepares once before its depth loop. Learned updates therefore persist across depth iterations/root retries within the search.

This retention does not freeze particular killer slots: ordinary entry's early_draw can clear only next-ply preferences after the repetition guard, as separately specified. This memo does not prove that guard's complete caller domain or all ordinary-entry ordering. The standalone first_iteration::run is a separate explicitly fresh-root helper; the native timed iteration Effects do not call it to restart learning.

## Limits

No general guarantee is claimed for arbitrary public Learning/Position/Query mutation, negative/huge supplied depths, malformed placement decoding, all native cutoff eligibility, root/window/TT/IIO/stop composition, analysis/hint/solve/ponder transitions or panic recovery. Validation/setup failures before an evaluating entry are not reclassified as completed searches. Normal early clearing may discard unused state before a failure, which the lifetime contract permits; no full reset-policy extension follows.

The explicit source bounds10504/5636 apply to the direct depth0..62 component and its imported coherent board/state premises. Existing native capacity proofs retain their own producer scope. This review complements finite fixture evidence and the separate remembered-result owner/admission reviews; it does not close final performance or external3288 qualification. No build, engine, test, profiler, archive or Git work was launched for this source review.

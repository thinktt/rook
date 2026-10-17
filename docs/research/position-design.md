# Position, move production and history investigation

This is an independent design investigation, not an architecture decision or an implementation. Sources are the released [KingRE specification](../../../king-spec/README.md) and [Imp2 mission](../../../imp-perf-mission.md). No Imp1/Rook source, architecture or private material was inspected. Byte counts below are proposed payload estimates, not measured Rust layouts or performance results.

## Binding behavior

**Setup and continuation are different entrances.** [POSITION-SETUP](../../../king-spec/spec/position-setup.md) derives initial order: king first in the whole-color sequence, then all other pieces by increasing rank/file, in White board coordinates for both colors. Type order is the restriction of that sequence. Requested castling rights survive only with the matching king/rook on their home squares; setup does not inspect transit attacks or path occupancy. A requested empty EP target survives when a geometrically eligible moving-side pawn exists, even if pinned or the opposing pawn is absent. Setup is idempotent. In contrast, [POSITION-MOVE-SEQUENCE](../../../king-spec/spec/move-sequence.md) accepts an established state and explicit type order without rerunning setup normalization. Protocol `setboard` additionally resets counters/history under [session lifecycle](../../../king-spec/spec/ordinary-session-lifecycle.md#idle-command-transitions).

**Type chronology is observable state.** A mover retains its slot; capture removes the victim while preserving survivor order; promotion removes the pawn and appends to the promoted type; castling moves the rook without reordering rooks. Identical placements and fingerprints can have different chronology. Swap-removal, square sorting after a move, and rebuilding lists from a final FEN violate this contract. Global whole-color chronology after moves is not specified by the move-sequence diagnostic; do not invent it as another invariant. [Transition rules](../../../king-spec/spec/move-sequence.md#placement-and-ordering-transitions).

**Rule fields have exact arithmetic.** Every move processes both source and destination through the home-square castling-right removal table, regardless of the piece moved. Rights never return. EP expires on every move; a double push retains its intervening square only if an opposing pawn is adjacent on the destination rank, including a pinned pawn. Pawn moves/captures reset the reversible count; other moves, including castling, increment modulo 256. FEN fullmove context is not placement identity. [Rules](../../../king-spec/spec/move-sequence.md#turn-rights-en-passant-and-reversible-count).

**Fingerprints are compatibility values, not complete keys.** [POSITION-IDENTITY](../../../king-spec/spec/position-identity.md) defines primary/secondary/pawn 32-bit XOR fingerprints and a seven-bit pawn group. They exclude side, rights, EP, counter and chronology. The coefficient generator's signed division is floor division; Rust signed `/ 65536` alone would mishandle negative nonmultiples. An arithmetic signed shift by 16 expresses that particular floor. Coefficients are fixed and consume no gameplay randomness. A valid-square remapping of the two coefficient sets needs 6,144 bytes; the published mathematical indices do not prescribe a mailbox layout.

**Actual phase and fixed root context differ.** Every transition's public phase describes its resulting placement, including unusual promotion-heavy count normalization. Root material values remain tied to the root phase/ownership while descendants change. Maintain or recompute current phase without accidentally rebuilding root values. [Phase/root material](../../../king-spec/spec/root-material-context.md), [move-produced evaluation](../../../king-spec/spec/evaluation-moves.md).

**Null is an explicit search transition.** It keeps placement, chronology, rights, phase, fingerprints, square contribution and inherited evaluation pair; flips side, clears EP, and increments reversible count/evaluation age modulo 256. It is not a legal played move. It participates in search-path history but null endpoints never satisfy short reversal. [Null transition](../../../king-spec/spec/evaluation-moves.md#null-transition), [reversal](../../../king-spec/spec/move-reversal.md).

## Natural candidate order and legality

The [ordinary non-root producer](../../../king-spec/spec/search-candidate-production.md) requires the complete legal list, with no opposing-king destination. Ordinary candidates leaving the moving king geometrically attacked are absent. Pinned enemy pieces still attack geometrically; legal attacks are not obtained by generating the opponent's legal moves. Castling needs retained rights, home pieces, empty path, and safe king start/transit/destination. EP safety must use the board after removal of the behind-target victim. Check reporting distinguishes none/single/double; an empty list alone cannot distinguish mate from stalemate.

The base traversal is long castle, short castle, then retained pawn/knight/bishop/rook/queen chronology, then king. Sliders visit near squares before far squares within each direction. Directions are board-relative:

| Piece | Ordered `(file, rank)` changes |
| --- | --- |
| White pawn | captures `(1,1)`, `(-1,1)`, then one push, then two push |
| Black pawn | captures `(-1,-1)`, `(1,-1)`, then one push, then two push |
| Knight | `(1,2)`, `(-1,-2)`, `(-1,2)`, `(1,-2)`, `(2,1)`, `(-2,-1)`, `(-2,1)`, `(2,-1)` |
| Bishop | `(1,1)`, `(-1,-1)`, `(-1,1)`, `(1,-1)` |
| Rook | `(0,1)`, `(0,-1)`, `(1,0)`, `(-1,0)` |
| Queen/king | bishop directions, then rook directions |

Every promotion destination expands queen, rook, bishop, knight. Legal EP moves then become a prefix, lower-file source before higher-file for **both** colors, independent of chronology. In single check, keep that EP prefix, then pawn blocks from king toward checker, pawn captures of the checker (White lower-file first; Black higher-file first), other pawn evasions, and remaining non-pawn evasions. Double check does not receive this single-check prefix. A representation's bit-scan order cannot silently replace these sequences.

The list is passed unchanged into [ordinary ranking](../../../king-spec/spec/search-candidate-order.md): selected unsigned priorities wrap modulo 2^32; priorities zero/one retain their input order at the tail; the preferred subsequence is first reversed and then receives the specified [modulo-six priority permutation](../../../king-spec/spec/tactical-capture-order.md#order-priority-sequence). A stable sort of the original list is insufficient. Hash matching compares endpoints only; killers compare the complete descriptor. Keep those operations explicit in the move API.

Do not reuse this producer indiscriminately. [Non-check quiescence](../../../king-spec/spec/quiescence-candidates.md) deliberately produces a narrower **pseudo-legal** tactical set, only queen promotions, different prefixes, and no own-king safety filtering at that boundary. Its Black EP prefix is higher-file first. Root scheduling is another contract; the ordinary candidate-production diagnostic is expressly non-root.

### Domain traps

The standalone candidate diagnostic rejects an initially attacked nonmoving king and requires normal EP rank/pawn geometry. [Joined ordinary ingress](../../../king-spec/spec/ordinary-play-ingress.md#joined-request-ingress) admits broader setups: retained-target EP has no further target-rank test, can remove an opposing non-king piece of any type behind the target, and still requires resulting moving-king safety. One narrowly specified king-victim EP command transition is accepted and a subsequent `go` fatally exits. A validated ordinary-position core may keep strong invariants, but the enclosing command path must implement that exception without converting it into generic empty-candidate mate/stalemate handling.

Likewise, setup permits sixteen pieces/color without the move-sequence diagnostic's tighter per-type limits. A universal list cannot assume queens never exceed nine. The candidate diagnostic's 230-descriptor bound is not evidence for silently truncating production lists. Capacities and validation belong to the admitted consumer domain.

## Representation candidates and costs

All choices need chronology in addition to occupancy.

| Board candidate | Approximate board payload | Expected tradeoff; unmeasured |
| --- | ---: | --- |
| 64-square byte mailbox | 64 B | Direct piece/victim access; simple ordered ray traversal; more geometry/attack work may be repeated. |
| 0x88 byte mailbox | 128 B | Cheap off-board tests and ray increments; larger copy footprint and square conversion. |
| Twelve bitboards + two color occupancies | 112 B | Cheap masks/checker sets; piece-at-square needs another structure or type probing; chronology and exact emission order still required. |
| 64-square mailbox + the above bitboards | 176 B | Direct lookup and masks together; redundant state increases move stores and restoration work. |

For chronology, a compact proposed form is sixteen square bytes per color, grouped by type, plus six type counts/color: **44 B** before optional offsets. Ordinary moves overwrite one square; capture and promotion shift at most fifteen entries, preserving order. Type boundaries can be derived from counts or stored explicitly. A simpler comparison is fixed sixteen-slot arrays for every color/type plus counts: **204 B**, with short per-type searches and shifts but a larger state copy. Stable piece IDs alone do not encode promotion append order; adding age/order metadata must be counted. Neither list scheme needs allocation per move.

A proposed `u16` move can hold six-bit source, six-bit destination, and a four-bit tag for ordinary/promotion/EP/castle. Reserve an invalid endpoint encoding for null or use an explicit nullable wrapper. This preserves complete descriptor equality while permitting an endpoint-only hash hint. A `u32` alternative can carry source-list index or moving/captured type to avoid tiny searches; measure the saved work against candidate bandwidth and stale-index risks after list mutation. Candidate indices are not persistent piece identities.

Mailbox + bitboards + compact chronology starts at **220 B**, before rules, counts, fingerprints, alignment and optional derived state. Measure `size_of`, generated assembly and actual copies rather than assuming a round size. A 256-entry `u16` move array is 512 B per active ply; priorities/permutations add separate scratch. Keep scratch per ply and allocate it once, with visible overflow handling for broader domains. Do not clone it with the position.

## Copy versus make/unmake

**Proposal:** start with a small allocation-free position value and copy it into a child. Use the same transition function for history replay and search moves, with entrance validation kept separate. Copying provides a cheap correctness baseline and straightforward sibling isolation, but a roughly 250-byte state moves several cache lines per explored child before attack tests and evaluation. Compiler copy elimination is a measurement question.

The competing delta design stores prior rights/EP/counter, victim square/type and original chronology index, mover index, promotion insertion/removal information, and optional old derived values. A quiet move can require few writes; capture/promotion undo must insert at the original list index, not append. Castling restores two pieces; EP restores its actual behind-target victim, including the broader ingress type. Null needs a separate record. No exact undo byte count is justified before layout selection.

Incremental fingerprints are simple XOR removal/addition operations, with pawn identity changed only by pawn contributions. Store old fingerprints in undo for cheap restoration or XOR the inverse; debug recomputation can verify either. Phase counts and starting-square occupancy can also update locally, but retain a recomputation reference until promotion carry boundaries are qualified.

Keep root context and shared search caches outside both copied positions and reversible deltas. Position restoration does not imply rolling back learned ordering or retained pawn/table effects from a searched sibling. Conversely inherited evaluation pair/age and square balance require their own correct child/parent ownership when evaluation joins the prototype. The state-only [sibling restoration workload](../../../king-spec/performance/functional-workloads.md#semantic-observations) does not qualify retained-score restoration.

## History ownership and equality

[History admission](../../../king-spec/spec/history-admission.md) requires the **primary** placement fingerprint plus side, rights and retained EP for recursive historical equality. Secondary identity or complete-board verification must not silently strengthen that rule: specified collisions matter. Repetition scans available distances 4,6,8,... through the reversible count, not distance two. Counts above 100 return 50; exactly 100 does so only outside check, otherwise it scans. Count/`ana`/root-relative-ply admission and next-ply killer clearing remain separate consumers. [Exact query/admission](../../../king-spec/spec/repetition-admission.md).

A proposed search repetition entry is eight bytes: primary `u32`, side, rights, EP sentinel and reversible count. Eight hundred such boundaries cost about 6.25 KiB, excluding richer state needed for protocol rewind. Retain the initial boundary and all active pre-root states for up to 799 prior plies; append search-path states separately, restoring only that tail on return. A 256-query diagnostic limit is not a game-history limit. `undo`/`remove` discard the replaced branch from active history. Null appends only to the search tail. [History ownership](../../../king-spec/spec/history-admission.md#ordinary-play-history-ownership), [session persistence](../../../king-spec/spec/ordinary-session-lifecycle.md#state-that-persists).

Short reversal needs root-relative ply at least three, reversible count at least three, non-null moves into P and P−2 with reversed endpoints, and current rights/EP equal to the state at P−3. Side equality, piece placement, promotion and kind do not participate. Keep a move per search ply and a rights/EP boundary per state. Its draw consumer checks an upper-bound guard after historical admission/clearing; it is not a replacement repetition hash. [Predicate](../../../king-spec/spec/move-reversal.md), [composition](../../../king-spec/spec/draw-boundary.md).

Protocol terminal/history acceptance is a separate ordered list: legal-move exhaustion, counter >99, more than two occurrences, the specified material-unit test, then movelist capacity. A terminal state may be the final root but cannot precede another retained move. Do not substitute a chess library's broader game-over predicate. The 800th retained move produces the movelist-full boundary rather than another search root. [Ingress history limits](../../../king-spec/spec/ordinary-play-ingress.md#history-and-qualification-limits).

## Cheap baseline experiment and unresolved decisions

The smallest representation comparison is A: 64-square mailbox, versus B: mailbox plus twelve bitboards/two occupancies. Hold the compact type-grouped chronology, packed moves, copy-child restoration, exact directional traversal and geometric attack semantics fixed. Execute the four released generation units and sibling restoration, consuming every generated descriptor and required state field. Compare full generation plus legal-child construction/restoration, including B's bitboard maintenance. Require identical ordered inventories and full restored parent state, with recomputed fingerprints as a correctness check. This isolates whether cached occupancy masks repay their maintenance without simultaneously changing restoration strategy. It remains a local diagnostic until the same two variants can execute an identical integrated branching search. Do not add a second representation change before this comparison is interpretable.

After the architect selects a first layout, compare **one** copy-child route with **one** delta route using identical generation, state and evaluation work. Begin with ordered mailbox rays/leaper tables and move-then-geometric-check legality; specialized pin/evasion shortcuts can follow measured need. Preserve the same legal inventory and emission order. Start with the released opening-history, capture-promotion, Black EP, counter-wrap, four generation and sibling-restoration functional units; add null state restoration and a short branching search once integrated. No fixture answer enters engine code or the timed runtime adapter.

Measure complete semantic sequences, including reset/copy/restoration and live result consumption; also retain a complete-lifetime measure including setup. Record binary/build/input identity, one excluded warmup and at least three samples, instructions/cycles with compatible scopes when available, CPU time and output equivalence. Show totals and dispersion; do not subtract synthetic consumption controls or infer a whole-engine win from isolated generation. Return to the three controlled searches and then the production corpus as soon as the integrated route exists. These are diagnostic experiments, not new local ceilings. [Functional guide](../../../king-spec/performance/functional-benchmark-guide.md), [operation boundaries](../../../king-spec/performance/operation-definitions.md), [mission](../../../imp-perf-mission.md).

Open decisions for the architect:

1. Does the hybrid's faster attack/evaluation access repay its redundant move stores versus mailbox-first? This needs integrated search, not only a generator loop.
2. Does compact-list shifting plus child copy beat per-type lists plus delta undo, especially across promotions and captures? Benchmark whole branching sequences.
3. Which derived fields should be eagerly maintained, and which can reuse evaluation's work? Geometric attack/check data and evaluation influence have different semantics and cannot be merged by assumption.
4. What production candidate overflow policy follows the broader setup population? The local 230 limit alone does not answer it.
5. How should protocol rewind retain/rebuild full chronology without bloating every search child? Persistent game checkpoints and compact replay/undo are alternatives, outside the hot search position.
6. The placement-identity contract does not define full production TT identity/group composition. Resolve that dependency from the complete search contracts before treating these placement hashes as universal cache keys.

No implementation, benchmark run or performance claim is included in this investigation.

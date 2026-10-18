# SEARCH-ORDINARY-CANDIDATE-PRODUCTION — legal production into candidate ranking

This contract produces the complete legal candidate sequence at
one ordinary non-root search position and passes that sequence directly into
[SEARCH-CANDIDATE-ORDER](search-candidate-order.md) by default. It composes normalized
setup and chronological legal moves with ordinary ranking; it does not define
root, solve-mode or recursive search behavior. The explicit local quiescence
ordering option below composes the same legal producer with the shared
quiescence preference rule; it does not execute quiescence search.

## Input and admitted position domain

Diagnostic `search.produceAndOrderCandidates` accepts exactly:

- `fen`: the six-field FEN accepted by `position.setupMoveSequence`;
- `moves`: zero through 256 legal coordinate moves following that setup;
- `ply`: an integer from 1 through 62 selecting the supplied non-root ranking
  context. It is independent of `moves.length`;
- `values`, `squareAdjustments`, `history`, `hashMove`, and `killers`: exactly
  the fields and bounds defined for `search.orderCandidates`.

### Explicit quiescence evasion ordering

The input may additionally contain `orderingMode: "quiescence"`. No other value
is admitted. When absent, every existing ordinary admission and output remains
unchanged. This option requires `moves: []`, an in-check moving side after setup
normalization, `hashMove: null`, and both killer pairs `[null,null]`. All other
input bounds and safety conditions remain in force. It is a setup-only local
component boundary, not full-search entry or a history-reset assertion.

Derive the complete legal evasion sequence from `fen`; do not accept a supplied
candidate list, calculated preferences, check state or permutation. Rank that
list by the shared [quiescence preference rule](quiescence-candidates.md#quiescence-preference-value)
instead of SEARCH-CANDIDATE-ORDER. For that rule, supplied `values` are contextual
material values and `squareAdjustments` provide the victim-square adjustment;
omitted adjustments are zero. Supplied `history` uses the same side/piece/square
keys as `orderingHistory` in SEARCH-QUIESCENCE-CANDIDATES. Promotion and capture
preferences are calculated, not supplied. Hash and killer promotion do not apply.

Return the same position/check/terminal/generated/ordered result schema defined
below, with zero charged relation queries. Terminal classification here describes
the legal inventory, not a recursive quiescence return or public game outcome.
An empty in-check list remains valid and reports `checkmate`; no moves or scores
are invented. The narrower non-check `search.quiescenceCandidates` interface is
unchanged. See the [composed local example](quiescence-evasion-priority-example.md).

The request does not accept placement, turn, piece order, check state or a
candidate list separately. These are derived from setup and move history.
Zero moves means setup only. The initial setup must additionally satisfy this
consumer's local king-safety condition: the side **not** to move is not in
check. This narrows this consumer, not POSITION-SETUP. It prevents an already
attacked opposing king without claiming that every admitted setup has a real
game history. The moving side may be in no check, single check or double check.

These are standalone diagnostic preconditions. Complete ordinary search instead uses
the explicitly broader admission and exceptional en-passant transition in
[ordinary-play ingress](ordinary-play-ingress.md#joined-request-ingress); the diagnostic
request domain and existing fixtures are unchanged.

After setup normalization and before applying history, this consumer also
checks local en-passant geometry. A retained target must be on rank six with
White to move or rank three with Black to move, and the square immediately
behind the target in the moving pawn's direction must contain the opposing pawn
that would be removed. POSITION-SETUP intentionally retains some geometrically
usable targets without these facts; such results remain valid there but are
outside this candidate-production domain. These local checks do not prove that
the position or preceding move has a legal history.

Move history follows POSITION-SETUP-MOVE-SEQUENCE. In particular, a mover keeps
its piece-type chronology slot, a captured piece is removed without reordering
survivors, a promotion is appended to the promoted type, and castling retains
rook chronology. Reconstructing chronology from the final placement is not
equivalent.

All ranking context remains supplied at this boundary. This contract does not
claim how material values, positional adjustments, history scores, hash moves
or killers are produced, learned, reset or retained by a complete session.

## Candidate descriptors and legal set

Candidates use the `{move, kind}` descriptors from SEARCH-CANDIDATE-ORDER.
The generated set is the complete standard legal move set for the final
position, including captures, four promotion choices, en passant and castling.
A pseudo-legal move is absent if the resulting position leaves the moving king
attacked. Sliding moves stop at the first occupied square. An own piece and the
opposing king are not available destinations.

Castling requires a retained right, the king and rook on their home squares,
an empty path, and an unattacked king start, transit and destination. Long and
short castling are separate candidates. En passant must satisfy both its
ordinary geometric conditions, the local retained-state geometry above and
king safety after removing the captured pawn.

The full generated sequence must contain at most 230 descriptors in this
diagnostic domain. Exceeding that limit is an error; neither generation nor
ranking may silently truncate the sequence.

## Base generation order

Let a displacement be `(file change, rank change)` from the moving side's
source square in White's board coordinates. Within one sliding direction,
nearer destinations precede farther destinations. Skip unavailable moves while
retaining the relative order of all available moves.

The base order is:

1. legal long castling, then legal short castling;
2. pawns in retained chronology;
3. knights in retained chronology;
4. bishops in retained chronology;
5. rooks in retained chronology;
6. queens in retained chronology;
7. the king.

For each White pawn, consider capture displacements `(1,1)`, then `(-1,1)`,
then the one-square forward move, then its initial two-square move. For each
Black pawn, use `(-1,-1)`, then `(1,-1)`, then one square forward, then its
initial two-square move. Whenever a pawn move promotes, its choices for that
one destination are queen, rook, bishop, then knight.

The direction order for every non-pawn piece is:

| Piece | Ordered displacements or directions |
| --- | --- |
| Knight | `(1,2)`, `(-1,-2)`, `(-1,2)`, `(1,-2)`, `(2,1)`, `(-2,-1)`, `(-2,1)`, `(2,-1)` |
| Bishop | `(1,1)`, `(-1,-1)`, `(-1,1)`, `(1,-1)` |
| Rook | `(0,1)`, `(0,-1)`, `(1,0)`, `(-1,0)` |
| Queen | the four Bishop directions, then the four Rook directions |
| King | the four Bishop displacements, then the four Rook displacements |

These are board-coordinate relations, not a required board representation or
iteration structure.

## Search-specific prefixes

Before ordinary ranking, adjust the legal base sequence as follows. Each move
appears exactly once.

First, if en passant is available, legal en-passant moves form a prefix. From
the target square, consider the pawn on the lower-file source first and the
higher-file source second. The source rank is one below the target for White
and one above it for Black. This fixed geometric order is independent of pawn
chronology. Remaining moves retain their relative base order.

If the side to move is in single check, retain the en-passant prefix and then
place these legal pawn evasions before the remaining base sequence:

1. blocks on squares strictly between king and checker, from the king outward;
2. pawn captures of the checker, using lower-file then higher-file source for
   White, but higher-file then lower-file source for Black;
3. any other pawn evasions in their applicable base order.

Non-pawn evasions retain their base relative order after the pawn prefix.
Double check is distinct: do not apply the single-check pawn-evasion prefix.
Ordinary legal filtering consequently leaves only legal king evasions. When a
particular double-check position has no pawn evasion, a mistaken empty pawn
prefix is observationally indistinguishable; semantic double-check reporting
still remains required.

## Composition and output

Pass `generatedCandidates`, unchanged and without an intermediate sort, as the
candidate sequence to SEARCH-CANDIDATE-ORDER with the supplied ranking context.
With the explicit quiescence option, instead pass that same sequence to the
shared quiescence preference/partition/permutation rule. The selected rule
determines `orderedCandidates`. It may reverse or permute tied
subsets, so generation order remains observable after composition.

Return exactly:

- `position`: final `placement`, `sideToMove`, normalized `castling`, normalized
  `enPassant`, and `halfmoveClock`;
- `check`: `none`, `single` or `double` from the final position;
- `terminal`: `none` when at least one legal candidate exists, otherwise
  `checkmate` when `check` is non-none and `stalemate` when it is none;
- `generatedCandidates`: every legal descriptor in the order above;
- `orderedCandidates`: a permutation of exactly that list after the selected
  ordinary or explicit quiescence ranking;
- `chargedRelationQueries`: the value returned by the selected ordering rule,
  zero in both modes.

An empty candidate list is therefore not sufficient by itself to distinguish
checkmate from stalemate. No packed move, private state field, address, buffer,
piece-array representation or source decomposition is part of this contract.

## Exclusions

This contract does not define root scheduling or randomization; non-check
tactical production or solve candidates; recursion, child scoring, extensions, reductions, windows or
retries; evaluation; work, time or stopping; learned-state production and
lifetime; undo/remove, null moves or repetition consumers; alternate protocol
modes; or behavior for a setup where the side not to move is already in check
or retained en-passant state fails this consumer's local geometry checks.

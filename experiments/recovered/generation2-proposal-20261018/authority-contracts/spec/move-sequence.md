# POSITION-MOVE-SEQUENCE — move history, ordering and position identity

This contract describes position transitions along a supplied legal move
sequence. It includes ordering information that can affect later evaluation
and move selection. It does not require incremental hashing, a particular
board representation or any physical piece-list layout.

## Diagnostic input and scope

`position.moveSequence` accepts `{initial, moves}`. `initial` contains exactly:

- `fen`: a six-field FEN, with one ASCII space between fields;
- `pieceOrder`: `white` and `black` objects, each with arrays named `pawn`,
  `knight`, `bishop`, `rook`, `queen`, `king`.

Every current piece must appear exactly once in its matching color/type array,
as an algebraic square. Order within each array is explicit semantic input;
it need not be sorted by square. Both colors have one king, at most eight
pawns, no pawn on a promotion rank, and at most sixteen pieces including the
king. This diagnostic additionally bounds knights, bishops and rooks to ten
each and queens to nine, throughout the sequence.

The FEN uses `w`/`b`, canonical `KQkq` subsequence ordering or `-`, and an
en-passant square on rank three or six or `-`. Its initial halfmove count is
an integer from 0 through 255; its fullmove number is 1..1000000. The fullmove
number supplies FEN notation context but is not a position identity component
or an output of this diagnostic.

`moves` contains 1..256 legal coordinate moves, each four lowercase square
characters plus an optional lowercase `n`, `b`, `r` or `q` promotion suffix.
A promotion suffix is required for promotion and forbidden on an ordinary
move. The starting state and sequence must have ordinary legal chess meaning;
this diagnostic is not the complete engine command parser or legal-move
generator specification. Extra fields, missing/duplicate ordered pieces,
malformed move spellings, illegal moves and out-of-domain values are rejected.
Moves can continue after a draw threshold for the purpose of observing state;
this operation does not itself adjudicate or stop a game.

The 256-move maximum belongs only to the portable `position.moveSequence`
diagnostic. [Ordinary-play ingress](ordinary-play-ingress.md) reuses the transition rules
below one move at a time for zero through 799 prior plies. That reuse does not
make an oversized `position.moveSequence` request valid and does not introduce
a different transition rule after move 256.

## Placement and ordering transitions

Apply ordinary chess placement changes for each move, including captures,
en passant, both castling directions and all four promotions. Preserve the
following semantic order:

- An ordinary moving piece keeps its place among pieces of the same color
  and type; its square changes to the destination.
- A captured piece disappears from its color/type ordering. All surviving
  pieces keep their relative order. For en passant, remove the pawn on its
  actual occupied square, not the empty destination.
- A promoted pawn disappears from the pawn ordering. The promoted piece
  follows all already existing pieces of its new color/type. Do not insert
  it according to destination square or reuse a captured piece's position.
- Castling changes the king's square and the participating rook's square
  without reordering that rook relative to other rooks.

Consequently, two identical final placements can have different ordering
after different histories. Rebuilding order from the final board is not an
equivalent transition rule. Fingerprint equality also does not imply equality
of this ordering or the other state below.

## Turn, rights, en passant and reversible count

Switch the side to move after every move. For each of its source and destination
squares, remove these rights if present:

| Square | Rights removed |
| --- | --- |
| a1 | White queenside |
| e1 | Both White rights |
| h1 | White kingside |
| a8 | Black queenside |
| e8 | Both Black rights |
| h8 | Black kingside |

Rights never return merely because a king or rook returns to its original
square. Destination processing matters when a corner rook is captured.

Clear the previous en-passant target on every move. After a pawn advances two
ranks, retain the intervening square as the new target only when an opposing
pawn occupies an adjacent file on the destination rank. This is an adjacent-pawn
condition, not proof that an en-passant capture would be legal: a pinned enemy
pawn still meets it. Without such a neighbor, report `-`, even though a generic
FEN producer might report every double-push target. Initial supplied FEN state
is reported as supplied; the first transition applies the rule above.

Reset the halfmove count to zero on a pawn move or capture, including promotion
and en passant. Otherwise increase it by one modulo 256: 255 is followed by 0.
Castling is a non-pawn, non-capture move for this count. This diagnostic exposes
that transition arithmetic; it does not redefine draw adjudication.

## Identity, phase and output

Report an initial state followed by one state after each move, in order:
`{results: [...]}` with exactly `moves.length + 1` results. Each has:

- `placement`, the FEN placement only;
- `sideToMove`, `white` or `black`;
- `castling`, the canonical `KQkq` subsequence or `-`;
- `enPassant`, an algebraic square or `-`;
- `halfmoveClock` and complete `pieceOrder` as defined above;
- `identity`, the [placement fingerprint](position-identity.md), including
  primary, secondary, pawn identity and pawn group;
- `phase: {opening, middlegame, endgame}`, as in
  [position phase](root-material-context.md).

Identity and phase describe the resulting placement after every transition,
including rook displacement during castling, removal during en passant and
the changed piece type on promotion. An implementation may compute them anew
or update them incrementally, provided results are identical. Turn, rights,
en-passant state, reversible count and ordering are not added to the placement
fingerprints; repetition/search identity contracts must handle their own
additional state requirements.

## Composition and evidence limits

Splitting a sequence at an observed state, then continuing with that state's
placement, rights, turn, target, count and ordering, yields the same later
outputs. Every request starts independently; there is no implicit state from
the preceding request. Resulting pawn order can supply later retained-pawn
evaluation diagnostics without guessing it from the final board.

Original-backed fixtures cover opening development, both-color promotions
with and without capture, castling, corner-rook capture, rook return, en-passant
creation/expiry/capture, pinned capture eligibility, reordered pieces, a
middle-pawn removal and reversible-count wraparound. Separate fingerprint
production and split-replay comparisons check composition.

Initial order is still supplied by this operation. [Position setup](position-setup.md)
separately derives it and normalizes requested flags before history. Full textual
protocol setup/editing,
complete legal generation and its ordering, undo command behavior, repetition
history production, evaluation-readiness state and complete search integration
remain separate requirements. This contract does not infer them from final
placement parity.

For the fresh ordinary-play path, every produced boundary state remains in chronological
order for the enclosing history/repetition owner. A state producing one of the
exact protocol-terminal reasons enumerated by ordinary-play ingress is permitted only as
the final reached root; if another retained move follows it, the supplied history is
invalid. Do not replace that enumerated list with a broader library `game over`
predicate. At 799 prior moves that final root may enter ordinary outcome
handling. An attempted 800th retained protocol move instead reaches the
separately specified `1/2-1/2 {Movelist full}` boundary and does not create an
additional ordinary-search root. These enclosing rules do not alter this
diagnostic's 1..256 request capacity.

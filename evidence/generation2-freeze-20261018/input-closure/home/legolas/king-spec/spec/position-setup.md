# POSITION-SETUP — initial ordering and requested-state normalization

This contract establishes a position from a placement and requested turn,
castling rights and en-passant target. It creates initial semantic piece order
and removes unsupported requested flags. It is distinct from advancing an
already established position through moves.

## Diagnostic input

`position.setup` accepts `{queries: [...]}`, with 1..4096 independent queries.
Each query contains exactly:

- `placement`: FEN placement, with one king per color, at most eight pawns per
  color, no pawns on the first/eighth rank, and at most sixteen pieces per color;
- `sideToMove`: `white` or `black`;
- `castling`: a canonical subsequence of `KQkq`, or `-`;
- `enPassant`: `-` or an empty square on rank three or six.

Rights and target are requests, not assertions that they must survive setup.
The diagnostic permits unsupported requested rights and geometrically
unusable targets so their normalization can be tested. It does not require a
legal game history to the supplied placement. Missing/extra fields, invalid
placements, occupied targets and malformed values are errors.

## Initial piece order

For each color, the king comes first in the initial piece sequence. Other
pieces follow by increasing rank, and within a rank by increasing file:
a1 through h1, then a2 through h2, and so on toward rank eight. This is the
same orientation for both colors, not a viewpoint-relative order.

For each color and piece type, its initial ordered squares are that sequence
restricted to the matching type. This order is newly derived from setup,
not inherited from an earlier position or sorted by piece value.

These are semantic ordering requirements for later consumers, not a required
memory layout. [Move history](move-sequence.md) subsequently preserves and
changes ordering according to moves; re-running setup on a resulting placement
is not equivalent to retaining its history-derived order.

## Castling normalization

A requested right survives only with the following pieces present:

| Right | Required king | Required rook |
| --- | --- | --- |
| K | White king e1 | White rook h1 |
| Q | White king e1 | White rook a1 |
| k | Black king e8 | Black rook h8 |
| q | Black king e8 | Black rook a8 |

Remove unsupported requested rights. Do not add a right that was not requested,
even when the appropriate pieces are present. Setup does not test empty paths,
attacked transit squares, current check or past king/rook movement. Those are
separate legality/history conditions; this rule only normalizes requested state.

## En-passant normalization

No requested target means no target. Otherwise keep the target only when at
least one pawn of the side to move occupies a diagonal source square from which
that color's pawn could advance onto it: one rank below the target for White,
one rank above for Black, on an adjacent file within the board.

This is geometric pawn presence, not legal-capture verification. It does not
require an opposing pawn behind the target, and a pinned pawn still qualifies.
It does not infer an unrequested target. When neither diagonal source contains
the required pawn, clear the target.

## Result and state

Output is `{results: [...]}` in query order. Each result contains exactly
`placement`, `sideToMove`, normalized `castling`, normalized `enPassant`,
`pieceSequence: {white, black}`, and `pieceOrder: {white, black}`.

Each piece sequence is an array of algebraic squares. Each piece-order object
has arrays `pawn`, `knight`, `bishop`, `rook`, `queen`, `king`, matching the
move-sequence contract. Placement and requested turn are unchanged. Canonical
rights spelling and `-` for absent rights/target are preserved in output.
Queries share no state. Applying setup to an already normalized result yields
the same result.

## POSITION-SETUP-MOVE-SEQUENCE — setup followed by history

`position.setupMoveSequence` accepts `{fen, moves}`. Its six-field FEN and
1..256 move sequence follow the domains of [POSITION-MOVE-SEQUENCE](move-sequence.md),
except there is no supplied piece order. First apply POSITION-SETUP to the
placement, side, requested rights and target. Use its resulting order and
normalized flags as the initial move state, retaining the supplied halfmove
count and fullmove-number notation context. Then apply POSITION-MOVE-SEQUENCE.

Return exactly its `{results: [...]}` shape: initial state plus each post-move
state, including fingerprints, phase, counter and ordered pieces. Every move
must be legal from this normalized initial state. No caller-provided ordering
or raw-state override is accepted by this operation.

The lower `position.moveSequence` diagnostic deliberately remains different:
it supplies an already established initial state and order, without implicitly
running setup normalization. This distinction permits independent transition
testing and continuation from an observed state.

## Evidence limits

Tests cover both-color setup order, all sixteen requested-right combinations,
missing/wrong/moved king or rook, edge files, both eligible-pawn directions,
absent opposing pawns, pinned pawns, unavailable targets and broad placements.
Composed tests include openings, castling, promotion, captures, counter wrap
and normalization before subsequent moves.

This is not the complete original textual setup-command grammar, editing
completion, undo/repetition history production, or full root/search lifetime.
Original code execution establishes setup and move composition through semantic
intermediate state; it does not establish every enclosing protocol caller.

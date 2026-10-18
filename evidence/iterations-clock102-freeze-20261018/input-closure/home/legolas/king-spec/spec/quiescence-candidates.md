# SEARCH-QUIESCENCE-CANDIDATES — non-check tactical production and ordering

This contract continues the exact state and evaluation results of
[EVAL-QUIESCENCE-DISPOSITION](quiescence-disposition.md). When that contract
selects tactical continuation, it produces the pseudo-legal tactical candidate
sequence for the current position and applies the quiescence preference order.
It does not recurse into any candidate or classify an empty list as mate or
stalemate.

## Input and local domain

Diagnostic `search.quiescenceCandidates` accepts every input of
`evaluation.quiescenceDisposition` plus `orderingHistory`. The position is
supplied as the same six-field `fen`, chronological `history`, and final
coordinate `move`; the current placement, side, piece chronology, retained
state, evaluation choice, bounds, and disposition are derived rather than
supplied again.

`orderingHistory` contains zero through 768 unique entries with exactly:

- `side`: `white` or `black`;
- `piece`: `pawn`, `knight`, `bishop`, `rook`, `queen`, or `king`;
- `square`: a coordinate from `a1` through `h8`;
- `value`: an unsigned 32-bit integer.

There are exactly 768 possible semantic keys: two sides times six piece types
times 64 squares. An omitted key has value zero. This boundary supplies the
values; it does not define how a complete search learns, ages, clears, or
retains them.

After POSITION-SETUP normalization and before applying history, this consumer
requires that the side not to move is not already in check. A retained
en-passant target must be on rank six with White to move or rank three with
Black to move, and the square immediately behind it in the moving pawn's
direction must hold the opposing pawn that an en-passant move would remove.
These are local safety and geometry conditions, not proof of historical
reachability, and they do not narrow POSITION-SETUP itself.

The final position must be a non-check position as required by
EVAL-QUIESCENCE-ENTRY. The generated list may contain at most 230 candidates.
As a provisional diagnostic restriction, if the moving side has a pawn on its
penultimate rank, that side may have no more than eight queens before
generation. This prevents a promoted child from exceeding the validated
piece-population boundary; it is not a general chess or engine limit.

## Candidate descriptors and pseudo-legal boundary

Each candidate is `{move, kind}`. `move` is source, destination, and an
optional lower-case promotion letter. `kind` is `ordinary` or `enPassant` in
this contract. Only queen promotions are produced.

The tactical set contains:

1. ordinary captures by every piece, including king captures;
2. en-passant captures;
3. quiet queen promotions; and
4. quiet moves that give check directly by the moved piece. For pawns, only
   the one-square forward move is admitted; knights and sliding pieces use
   their full ordinary move geometry.

It excludes castling, underpromotions, quiet king moves, quiet two-square pawn
moves, and quiet moves that check only by uncovering another piece. Sliding
geometry stops at the first occupied square. The source piece must belong to
the moving side, and an own piece is unavailable as a destination.

This is deliberately pseudo-legal production. A candidate is not removed here
merely because moving it exposes the moving king. King safety of candidate
children belongs to a later, excluded consumer. Consequently this set is not
the standard legal move set, and an empty set says nothing by itself about
mate or stalemate.

## Base sequence and tactical prefixes

Before tactical prefixes, consider pieces in this order: pawns, knights,
bishops, rooks, queens, king. Within a type, use retained piece chronology.
Within one sliding direction, nearer destinations precede farther ones.

White pawn capture directions are `(1,1)` then `(-1,1)`; Black uses
`(-1,-1)` then `(1,-1)`. A one-square forward move follows captures. At a
promotion destination, produce the queen descriptor only.

The non-pawn direction sequence, in White board coordinates, is:

| Piece | Direction or displacement order |
| --- | --- |
| Knight | `(1,2)`, `(-1,-2)`, `(-1,2)`, `(1,-2)`, `(2,1)`, `(-2,-1)`, `(-2,1)`, `(2,-1)` |
| Bishop | `(1,1)`, `(-1,-1)`, `(-1,1)`, `(1,-1)` |
| Rook | `(0,1)`, `(0,-1)`, `(1,0)`, `(-1,0)` |
| Queen and king | the four Bishop directions, then the four Rook directions |

Move the following candidates to the front, without duplication:

1. en-passant captures from fixed target geometry: lower-file source then
   higher-file source for White, higher-file then lower-file for Black;
2. quiet pawn checks selected from the two pawn-attack squares below the enemy
   king for White or above it for Black, lower file then higher for White and
   higher then lower for Black.

Remaining candidates keep their base relative order. Within the promotions of
one pawn, its quiet queen promotion precedes its capture promotions in the
generated sequence; this does not change their preference calculation.

## Quiescence preference value

Compute an unsigned 32-bit preference for each generated candidate. Contextual
piece values and the root phase are the values derived by the composed
evaluation contracts. A captured piece's effective value `V` is its contextual
material value plus its root-phase positional value on the destination square,
using [POSITIONAL-VALUES](positional-values.md).

For an ordinary capture, let `A` be 1500 when the attacker is a king;
otherwise use the attacker's contextual material value and add 300 when that
value is below 200. Its preference, with unsigned 32-bit wraparound, is:

```text
band + 65536*V - A
```

where `band` is `0xe0000000` when `V > 150`, and `0xd0000000` otherwise.
The comparison is strict: 150 remains in the lower band and 151 enters the
higher band.

A quiet promotion has the following preference, whether or not it directly
checks: knight `0xe0000100`, bishop `0xe0000200`, rook `0xe0000300`,
queen `0xe0000400`. This diagnostic's non-check producer emits only the queen
choice; the shared ordering rule also applies to all four choices in ordinary
legal evasions imported by [QUIESCENCE-TREE](quiescence-tree.md).
An occupied destination is a capture even when the move promotes: use the
ordinary capture formula, without adding or substituting the quiet-promotion
preference. An en-passant capture has preference `0xe0000800`.
Every remaining quiet move uses the `orderingHistory` value keyed by moving
side, the piece on the source square **before** the move, and destination.
This includes quiet non-checking evasions and quiet king evasions in the
in-check consumer. A quiet promotion never takes this history fallback.
The broader shared ordering rule does not widen this diagnostic's production
or admission domain.

Preferences zero and one are deferred. They retain their generated relative
order after every preferred candidate. Values two and above are preferred.
Collect that preferred subsequence by traversing the generated candidates in
reverse order, then apply
[ORDER-PRIORITY-SEQUENCE](tactical-capture-order.md#order-priority-sequence) to
its unsigned preferences. The resulting candidate permutation precedes the
deferred subsequence. In particular, equal preferred values are not generally
summarized by a later-generated-first shortcut when a mixed preferred list has
more than six entries; ORDER-PRIORITY-SEQUENCE defines the exact tie behavior.

The [quiet-promotion evasion example](quiescence-evasion-priority-example.md)
composes these values, ordinary evasion production and the existing ordering
permutation without introducing a new wire or trace interface.

## Result and effects

Return all `results` from EVAL-QUIESCENCE-DISPOSITION unchanged, followed by
`tacticalGeneration`.

For lower-bound, upper-bound, or stand-pat return:

```json
{"reached":false}
```

No candidate lists or charge fields are present, and production and ordering
are not executed.

For tactical continuation return:

```json
{
  "reached": true,
  "generatedCandidates": [],
  "orderedCandidates": [],
  "additionalChargedRelationQueries": 0,
  "additionalChargedSearchUnits": 0
}
```

`orderedCandidates` is a semantic permutation of exactly
`generatedCandidates`. The two zero charges are measured across this producer
and ordering region; they do not describe later candidate eligibility,
optimistic estimates, child construction, king-safety rejection, recursive
search, time control, or output reporting.

## Evidence boundary and exclusions

Portable cases include all three static returns, immediate-full, fast-only and
refresh selection, both nonempty and empty reached lists, en passant, quiet
pawn checks, promotions, history priorities, value thresholds, king and low
attacker adjustments, root-phase victim-square adjustment, fixed chronology,
and an original-backed king-exposing candidate.

The cases qualify candidate production and ordering after composed evaluation,
not complete search behavior or natural-game reachability of constructed
setups. Search admission, repetition, candidate eligibility,
optimistic pruning, child legality, recursive scoring, learned-state lifetime,
root behavior, randomized behavior, timing, mate classification, protocol
commands, and alternate startup modes remain outside this contract.

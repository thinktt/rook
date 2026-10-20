# SEARCH-CANDIDATE-ORDER — ordinary recursive search

This contract composes ordering categories for a supplied
candidate list at a non-root search position. It does not generate or validate
legal moves, and it is not root, quiescence or solve-mode ordering.

## Inputs and state

Diagnostic `search.orderCandidates` receives:

- `placement`: the EVAL-INFLUENCE board-placement syntax and bounds;
- `side`: white or black, selecting the moving side;
- `ply`: an integer from 1 through 62, with root numbered zero;
- `values`: white/black material values for pawn, knight, bishop, rook and
  queen, each an integer in 0..10000;
- `squareAdjustments`: entries `{side, piece, square, value}` specifying
  positional adjustments for captured-piece valuation; omitted entries are
  zero. Values are integers in -128..127, and material plus adjustment
  must also lie in -10000..10000. Kings are not entries here;
- `history`: entries with the same four fields, representing history preference
  by piece color, type and destination square. Values are integers in
  0..4294967295. Omitted entries are zero;
- `hashMove`: a move descriptor or null;
- `killers`: `current` and `twoPliesEarlier`, each a two-element list of move
  descriptors or nulls. At ply 1 or 2, twoPliesEarlier must contain two nulls;
- `candidates`: an ordered list of 0..230 distinct move descriptors.

A move descriptor is `{move, kind}`. `move` is coordinate notation such as
`e2e4` or `c7d8q`; `kind` is `ordinary`, `enPassant` or `castle`. Only ordinary
descriptors may have a promotion suffix. Source and destination differ.
Candidate sources contain a piece of side; destinations are empty or contain
an opposing non-king piece. Promotion candidates have a pawn source;
enPassant candidates have a pawn source and empty destination; castle
candidates have a king source and empty destination.

These are component-domain checks, not complete chess legality. Descriptors
remembered as hash/killer moves need not occur in the candidate list or fit the
current placement. Candidate uniqueness includes kind and promotion. History
and square-adjustment entries have no duplicate color/type/square keys, and
each list has at most 768 entries.

Influence is derived from placement using EVAL-INFLUENCE. Material values are
already oriented by color; the current moving side must not cause them to be
swapped again. This is one fresh ordering operation with supplied context.
It does not learn or modify history or killers. SEARCH-CUTOFF-MEMORY defines
cutoff updates; their lifetimes remain separate state contracts. The diagnostic permits synthetic history values
without claiming they are reachable through normal history updates.

## First-applicable priority calculation

For each candidate, choose the first applicable rule below. All comparison
priorities are normalized modulo 4294967296 and compared as nonnegative
numbers. These magnitudes define behavior; their representation is not a
required implementation structure.

Let promotion bonus be none 0, knight 256, bishop 512, rook 768 and queen 1024.

1. If source and destination match hashMove, use `4294901760 + promotionBonus`.
   Hash matching ignores promotion and kind. Consequently every promotion
   sharing the preferred source/destination receives this category, with
   queen above rook above bishop above knight within that group.
2. If the special queen preference described below is nonzero, use
   `4026531840 + queenPreference`.
3. If the destination is occupied, calculate TACTICS-CAPTURE-PREFERENCE using
   the destination influence, moving piece's material value, and captured
   piece's material plus square adjustment. If its normalized comparison
   magnitude is nonzero, use `3758096384 + captureMagnitude`.
4. For a promotion or enPassant descriptor, use
   `3758096384 + promotionBonus + enPassantBonus`, where enPassantBonus is
   2048 for enPassant and zero otherwise. Castle is not included in this rule.
5. Match killers by the complete descriptor, including promotion and kind.
   The first matching entry in current-first, current-second,
   two-plies-earlier-first, two-plies-earlier-second order yields respectively
   `3489660933`, `3489660932`, `3489660931`, `3489660930`.
6. For an occupied destination, use the captured type's fallback priority:
   pawn 2, knight 3, bishop 4, rook 5, queen 6.
7. Otherwise use history for the moving piece's color/type and destination.
   The source square is not part of that history key.

Rule precedence selects the calculation; it is not an unconditional promise
that every earlier category outranks every later category for synthetic
extreme inputs. Normalize the selected result before comparing priorities.
For example, addition to a category base can wrap to zero. Do not then retry
later rules: the selected result remains zero and enters the low-priority
partition described below.

In particular, an ordinary capture receiving zero from its capture-preference
stage remains eligible for promotion and killer preference. Only after those
fail does occupied-destination fallback apply. A castling descriptor may
receive hash, killer or history preference, but not an automatic promotion
preference merely because it is a special move.

## Special queen preference

This applies only to a queen candidate whose destination neighbors the
opposing king (one square orthogonally or diagonally). At that destination,
normalize own influence. Its queen-category count must be one, and its
mixed-radix influence magnitude must exceed two. Thus a lone queen's influence
is insufficient, and carry normalization can remove eligibility even when
multiple physical queens influence the square.

Exclude one queen contribution using EVAL-ADJUSTED-RELATIONS. The resulting
queen relation must be favorable. If these conditions hold, queenPreference
is 65536 for an empty destination, or 65536 times the captured piece's material
value for an occupied destination. The captured piece's square adjustment is
not included in this special calculation. Zero material value therefore
produces zero queenPreference and allows ordinary capture preference to run.

## Partition, order and output

Partition candidates by their selected normalized priority:

- Priorities zero and one form a low-priority list in their original candidate
  order. Do not sort this list, even to place one before zero.
- Priorities greater than one form a preferred list in **reverse** candidate
  order. Apply ORDER-PRIORITY-SEQUENCE to this reversed list.

The final order is the ordered preferred list followed by the unchanged low
list. This reversal is separate from the priority permutation's own tie rule.
Neither stage should be summarized as a universal later-first tie policy.

Output is `{orderedIndices, chargedRelationQueries}`. orderedIndices is the
permutation of zero-based input indices, containing every candidate exactly
once. chargedRelationQueries is zero: influence construction, the adjusted
queen/capture queries and this ordering operation add no relation units.

EVAL-SQUARE-VALUES defines the supplied positional square adjustments. Complete
move generation order, root
context lifetime, history/killer learning and their reset behavior, and the
other search modes' ordering remain separate required contracts.

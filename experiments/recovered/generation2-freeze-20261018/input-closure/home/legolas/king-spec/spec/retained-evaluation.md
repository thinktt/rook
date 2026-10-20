# EVAL-RETAINED-SEQUENCE — full-produced evaluation state and fast reuse

Working composition contract for a fixed-root sequence of full and fast
evaluations. Each full evaluation produces information that subsequent fast
evaluations reuse. Full evaluations also share retained pawn classifications.
This diagnostic chooses the evaluation kind explicitly; it does not define
when a search chooses that kind.

## Diagnostic input

`evaluation.retainedSequence` accepts exactly:

- `rootSide`: `white` or `black`;
- `averageDepth`: integer −100..100;
- `percentages`: complete `own` and `opponent` objects with the eleven names
  and integer 0..1000 bounds of [evaluation weights](personality-evaluation-weights.md);
- `cfd`: integer −10000..10000;
- `sop`: integer 0..100;
- `positions`: 1..512 ordered evaluations.

Each position contains exactly `kind`, `placement`, `sideToMove`, `pawnOrder`
and `reversiblePlies`. The last four retain the domains of
[fresh scoring](fresh-score.md). `kind` is `full` or `fast`. The first kind
must be `full`, and its side must equal `rootSide`. Its placement establishes
the root for the entire request. Missing, unknown or invalid fields are errors.

These are controlled evaluation positions, not necessarily successive legal
moves. Pawn order and reversible count are explicit semantic inputs. No
retained score, phase, identity, material balance, cache entry, clear command
or per-position personality override is accepted.

## Fixed context and retained information

Root phase, root material values, root-owned evaluation coefficients,
non-king square values, draw preference and variation range are produced
from the first placement and fixed request settings, using the contracts
referenced by [fresh evaluation](fresh-score.md).

Start with cleared retained pawn information, including the zero-identity
behavior in [retained pawn structure](retained-pawn-structure.md). A full
evaluation selects or replaces this information using the actual current
pawn identity. A fast evaluation neither looks it up nor changes it.

Consequently, the full evaluations alone form an
[EVAL-SEARCH-PAWN-SEQUENCE](search-pawn-sequence.md) with this same root.
Intervening fast positions must not populate or evict retained pawn entries.
An identity match may retain earlier classification order even when the
new supplied pawn order differs. Clearing initially is not forced recomputation.

There is also one retained pair for this diagnostic sequence:
`positionalSubtotal` and `pawnProgress`. A full evaluation replaces both with
its newly computed values. A fast evaluation preserves both. Later final-score
adjustments never replace this pair with the finished score.

## Full evaluation

Compose [EVAL-FRESH-SUBTOTAL](evaluation-subtotal.md), except that its pawn
contributions come from the retained pawn selection above rather than forced
fresh classification. Current activity, influence, shelter, patterns, phase,
check, material and square balance are still evaluated for this position.

The ordinary full-evaluation tempo remains activity- and phase-dependent.
Produce and retain the positional subtotal and pawn-progress contribution;
finish the result using the identity and final-scoring composition of
[EVAL-FRESH-SCORE](fresh-score.md).

## Fast evaluation

Let `M` be current material balance under the fixed root material context,
and `Q` the square balance defined by EVAL-FRESH-SUBTOTAL. Non-king square
values use root phase; king square balance uses current phase. The pawn-only
square-balance rule still applies.

Let `P` and `G` be the retained positional subtotal and pawn progress produced
by the most recent full evaluation. The current tempo is zero in check,
otherwise +6 for White to move and −6 for Black to move. Then:

`baseScore = M + Q + P + G + tempo`.

Use current placement identity, current check/phase, the supplied reversible
count, fixed root draw preference/variation range and retained `G` in the
same final/endgame scoring rules as EVAL-FRESH-SCORE. Produce new score and
bounds; do not simply return the earlier full evaluation's finished score.

The fast path adds no charged relation queries and preserves the retained
pair. This does not mean it consumes no search work or machine instructions.
Complete search-work charging and clock observations are separate contracts.

## Result and sequence lifetime

Return one result per position, in order, with exactly:

`kind`, `rootPhase`, `currentPhase`, `inCheck`, `baseScore`, `identity`,
`variationIdentity`, `drawPreference`, `variationRange`, `adjustedBase`,
`lateEndgame`, `scaledScore`, `score`, `lowerBound`, `upperBound`, `retained`,
`relationQueries`, `pawnEntryReused`.

Phase, identity and final-stage result shapes and orientations are unchanged
from EVAL-FRESH-SCORE. `retained` is
`{positionalSubtotal, pawnProgress, evaluationAge}`. `evaluationAge` is zero
throughout this diagnostic: full evaluation resets it and this sequence
contains no moves that advance it. It is not a count of fast evaluations.

For a full result, `pawnEntryReused` is the boolean identity-match outcome and
`relationQueries` is the sum of its actually evaluated activity and pawn
relation charges. For a fast result, these are respectively `null` and zero.
Null means no selection occurred, not a cache miss.

Each request starts independently. Repeating an entire request gives the same
result. Arbitrary reordering of positions inside a request need not do so.

## Remaining boundaries

This joins real full-produced scores with their fast consumer and ordinary
pawn retention. It does not establish legal move/undo/null state inheritance,
evaluation-age advancement, full/fast admission, history-derived pawn order
or reversible counts, or session/reset scheduling. In particular, unrelated
diagnostic positions are not evidence that search naturally carries the
retained pair between those positions. Those production connections still
require their own original-backed tests.

[EVAL-MOVE-SEQUENCE](evaluation-moves.md) now provides the forward ordinary/null
transition composition from normalized setup, without supplied per-position
pawn order or reversible counts. Search selection and backtracking remain
separate obligations.

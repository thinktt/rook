# EVAL-RELATIONS — evaluation attack relations

These classifications belong to evaluation and tactical scoring.
They are not legal-move attack maps, full static-exchange analysis or a promise
that a move is safe. The names `unfavorable`, `contested` and `favorable` label
three distinct outcomes consumed by other rules.

## Contributions and classification

An attack profile consists of nonnegative counts named `weak`, `queen`, `rook`,
`minor` and `pawn`. `minor` includes knight and bishop contributions. `weak`
includes king-neighbor influence and slider influence weakened by a friendly
queen. These are evaluation contributions, not a census of legal attackers.

Normalize the profile with these carry rules, in order:

1. Keep weak count modulo 2; add its quotient to queens.
2. Keep queen count modulo 2; add its quotient to rooks.
3. Keep rook count modulo 4; add its quotient to minors.
4. Keep minor count modulo 4; add its quotient to pawns.
5. Keep pawn count modulo 4 and discard the remaining quotient.

This normalization can change the apparent type of influence in crowded
positions. Preserve it; do not replace it with unlimited attacker counts.

The effective multiplicity is the sum of the normalized counts, capped at 4.
The least-value tier is the first present category in this order: pawn = 1,
minor = 3, rook = 5, queen = 9, weak = 99. A profile with no remaining
contributions has multiplicity zero and no tier.

For a relation queried from one side's perspective, let `a` be the opponent's
multiplicity and `d` its own multiplicity. Let `v` and `u` be their respective
least-value tiers. Evaluate the following definition for tested-piece values
`t = 1, 3, 5, 9`, producing the `pawn`, `minor`, `rook`, `queen` outcomes:

- If `a = 0`, the outcome is favorable.
- Otherwise, if `d = 0` or `v < t`, it is unfavorable.
- Otherwise, if `v = t`, it is contested when `a <= d`, and unfavorable when
  `a > d`.
- Otherwise (`v > t`), it is favorable when `a <= d` or `v > t + u`, and
  unfavorable otherwise.

The tier values here are fixed relation categories, not the personality's
material values. The two kinds of values must not be conflated.

## EVAL-INFLUENCE — contributions from a placement

For each side, derive contributions at queried squares from current placement.
Pins, turn, castling and en-passant rights do not suppress contributions.
Occupied friendly and enemy squares receive influence too.

- A king contributes one weak influence to each neighboring board square.
- A knight contributes one minor influence to each knight destination.
- A pawn contributes one pawn influence to each forward-diagonal destination.
- A rook traces orthogonal rays, initially contributing one rook influence
  per visited square. A bishop traces diagonal rays with one minor influence.
  A queen traces both with one queen influence.

On each slider ray, include the first occupied square before deciding whether
to continue. Empty squares do not block. For this evaluation calculation only,
the opposing king is transparent: include its square and continue beyond it.

A friendly rook is transparent on an orthogonal ray; a friendly bishop is
transparent on a diagonal ray. This applies to rays originating from queens
as well as rooks/bishops. A friendly queen is transparent on either ray type,
but all influence *beyond* that queen on the ray is weak. The queen's own square
receives the contribution in effect before it was passed. Passing another
transparent slider does not restore the earlier contribution type.

Other pieces block after receiving influence. One special case extends one
square farther: if a diagonal ray traveling in the side's pawn-forward
direction stops at a friendly pawn, add the ray's current contribution to
the next square, if on the board, and stop. The extra square may be occupied.
There is no corresponding extension on backward diagonals or orthogonal rays.
The side's own king is an ordinary blocker for its slider rays.

Sum all contributions at the target, then apply the normalization and relation
definition above. No chronological piece-list ordering is required by this
contract: these contribution sums are commutative. Position/history dependence
of other evaluation behaviors is not removed by that statement.

## Diagnostic operations and work charges

`evaluation.relations` receives `pairs`, a list of `{own, opponent}` profiles.
Each named count is an integer from 0 through 31. The diagnostic permits
synthetic profiles that need not arise in legal play.

`evaluation.squareRelations` and `evaluation.influence` receive `placement`
and ordered `queries`.
Each query has a square such as `e4` and `side` (`white` or `black`). Placement
uses the EVAL-PHASE syntax and bounds, additionally limiting each side to ten
knights, ten bishops, ten rooks and nine queens. This is a bounded component
diagnostic, not a complete definition of production FEN acceptance.

The relation operations accept 1..1024 queries per fresh request and return
`{relations, chargedRelationQueries}`. Each relation has the four named outcome
fields. Results retain query order. Repeated identical queries remain separate
operations and separate results.

`evaluation.influence` accepts the same 1..1024 square/side queries and returns
`{profiles, chargedRelationQueries}`. Each profile contains the five named
normalized contribution counts for the requested side at that square, before
multiplicity capping and relation classification. Weak/queen counts are in
0..1 and rook/minor/pawn counts in 0..3. These are the result of the functional
normalization above, not uncapped counts of physical attackers. This diagnostic
distinguishes influence differences that may share the same final relation.
Its charge count is zero: observing influence is not a relation query.

Each explicit, unadjusted relation query charges one KingRE relation unit,
regardless of its outcome. Thus the reported charge count equals the number
of queries. Constructing the influence used by this diagnostic adds no such
charge. This does **not** mean an entire evaluation is uncharged; other
evaluation rules decide which queries to perform. Adjusted relations have the
separate exclusion and charging rule below; selection of queries by their
capture/activity consumers remains separate work.

## EVAL-ADJUSTED-RELATIONS — removing a contribution

Some tactical decisions classify support after excluding one contribution of
the moving piece. This exclusion occurs **after** influence normalization,
not before it. It is not the same as removing a physical attacker and then
recounting all remaining pieces.

For normalized own counts `w, q, r, m, p`, define the mixed-radix magnitude
`S = w + 2q + 4r + 16m + 64p`. Excluding one weak, queen, rook, minor or pawn
contribution subtracts respectively 1, 2, 4, 16 or 64 from S. If the result is
negative, own support is empty. Otherwise decompose the result with the same
radices as normalization and use that profile in EVAL-RELATIONS. Opposing
support is unchanged. Borrowing between categories is intentional.

For example, eight minor and two pawn contributions normalize to no support.
Excluding a pawn still leaves no support; it does not restore the discarded
influence. In contrast, a normalized pawn contribution with one minor excluded
becomes three minors, not a pawn with a negative minor count.

`evaluation.adjustedRelations` receives 1..1024 `pairs`, each containing `own`,
`opponent`, `remove` and `side`. Profiles have the same diagnostic bounds as
`evaluation.relations`. `remove` is one of the five contribution names;
`side` is `white` or `black`, selecting whose contribution is excluded. The
`own` profile always belongs to that selected side. Color does not change the
mathematical result. Synthetic tests may request removal from an empty profile.

Output is `{relations, chargedRelationQueries}` with the same four outcomes
per query and preserved order. These adjusted queries charge zero relation
units, even for repeated queries. This exception does not remove charges
from other operations performed in the same tactical decision.

Full evaluation composition, automatic query
selection, cached-state lifetime and complete engine work accounting are not
closed by this slice. The diagnostics do not mandate a production API or
an implementation's representation of attack information.

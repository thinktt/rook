# POSITION-IDENTITY — deterministic placement fingerprints

Working behavioral contract. These numerical identities support compatibility
of later reuse, ordering and score rules. They are not proof that two complete
game states are equal: side, rights and history have additional semantics.

`position.identity` takes `input: {queries: [...]}`, with 1..4096 independent
queries, each exactly `{placement}` in the
[bounded pawn-candidate domain](pawn-candidates.md). The result for each query is
`{primary, secondary, pawn, pawnGroup}`. The first three are integers in
0..4294967295; `pawnGroup` is in 0..127. No state carries between queries.
Malformed or extra fields are diagnostic errors.

## Numerical definition

Let `M = 4294967296`, `a = 0xbb40e62d`, and `s(0) = 0x01234567`.
For positive integer `n`, define

`s(n) = (a*s(n-1) + 1) modulo M`, using the least nonnegative residue.

Let `signed(x) = x` for `x < M/2`, otherwise `x-M`. Define
`h(x)` as the least nonnegative residue modulo M of
`floor(signed(x)/65536)`.

For `j = 0..1919`, define the 32-bit coefficient

`K(j) = h(s(2*j+1)) XOR s(2*j+2)`.

The signed interpretation before the division is significant. It is not an
unsigned high-part extraction. The sequence is fixed; it does not consume the
engine's gameplay random stream or depend on wall-clock seeding.

Assign type/color numbers in this order:
White pawn 0, Black pawn 1, White knight 2, Black knight 3, White bishop 4,
Black bishop 5, White rook 6, Black rook 7, White queen 8, Black queen 9,
White king 10, Black king 11.

For a piece with number `t`, file number `f` (a=1 through h=8) and rank `r`,
its primary contribution is `K(80*t + 10*(r-1) + f)` and its secondary
contribution is `K(960 + 80*t + 10*(r-1) + f)`.
These are mathematical coefficient selections, not required storage indices,
board representation or initialization-loop structure.

`primary` is the XOR of all primary piece contributions; `secondary` is the
XOR of all secondary piece contributions. `pawn` is the XOR of primary
contributions from White and Black pawns only. An empty set contributes zero.
Finally, `pawnGroup = pawn modulo 128`.

Only placement participates. Piece enumeration order has no effect. Moving a
non-pawn can change primary/secondary but cannot change the pawn identity.
Different placements can collide; no uniqueness promise is made.

## Boundaries

This defines fingerprints from a complete placement. It does not yet specify
incremental update scheduling, repetition comparisons, transposition identity
composition, or history-dependent piece ordering. The pawn identity's retained
structural use is specified separately in
[retained pawn structure](retained-pawn-structure.md).
Its primary/secondary XOR is consumed by position-dependent score variation
in [fresh evaluation](fresh-score.md); it is not a gameplay PRNG seed.

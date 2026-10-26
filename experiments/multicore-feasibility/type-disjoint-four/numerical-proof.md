# Type-disjoint Activity reduction: numerical source proof

Source owner: bounded numerical extraction. Source workspace:
`/home/legolas/rook2-experiments/workspaces/type-disjoint-four-20261026-01`,
derived from positive epoch64. Behavioral authority is the released
`/home/legolas/king-spec/spec/activity.md` and `king-shelter.md`.
This records source reasoning and added controls, not executed test results.

## Ownership and reduction

Mask bits 0/1/2/3 own whole knight/bishop/rook/queen jobs, respectively.
The selected fixed roles are `[3,8]`, `[8,3]`, `[4,4]`, indexed by color.
For each color their masks are disjoint and their union is 15. All pieces of
one color/kind, including promoted inventory, stay in one call to the existing
`accumulate_kind` body and share one fresh private mark row. Thus identical
type/strength marks retain presence OR; weak and strong marks may coexist.

`compute_partition` calls the existing destination and piece-score bodies.
It returns raw side score sums, unclamped admitted pressure sums indexed by
defender, and the exact sum of charged relation queries. No per-piece formula,
capture shortcut, additional-ray charge or low-mobility query is rewritten.

The pressure body is shared with original serial/side evaluation. Those callers
use owned-kind mask 15. Partial callers use the opposite attacker's selected
mask for each defender. A family without an owned contributing kind has zero
bits in the private marks: no R/Q skips orthogonal traversal, no B/Q skips
diagonal traversal, and no N skips knight steps. This is fixed pre-data zero
elimination. Every contributing family still uses the original global piece
counts, original type masks and original own/opposing occupancy/termination;
no owned-piece count substitutes for global inventory.

At an admitted square distinct kind bits contribute independently. Consequently
the scalar pressure sums from disjoint whole-kind owners add exactly to the
original OR-combined marks' pressure sum. `combine_partitions` sums raw scores,
then applies the original `(276*S+128).div_euclid(256)` once per color. It sums
raw pressure, then subtracts 12 and clamps once per defender. Original weighted
Activity rounding follows unchanged. It never sums rounded scores or clamped
partial pressures. R is integer addition, including repeated charged queries.

Shelter geometry uses unchanged `components`, with white assigned to role 0,
black to role 1, and no geometry assigned to role 2. `compose_components` calls
the existing `compose` once per complete defender pressure, then existing
`combine` once. Geometry does not depend on Activity pressure. No raw geometry
fragment or already rounded shelter term is independently recombined.

## Bounds for regrouping

Native `Position` admits at most 16 pieces per color and exactly one king
(`position.rs` setup/validation), hence at most 15 Activity pieces per color.
Normalized influence-byte digit sums are at most 11, including arbitrary
authoritative supplied bytes (`influence.rs::profile_sum`). Destination category
is in 0..3 and destination value is at most 47. A conservative traversal bound
is eight rays times seven squares, with rook value doubling conservatively
applied to every square: T <= 56*3*47*2 = 15,792. Per-piece mobility/phase rounds
retain their existing nonnegative intermediates and curve index cap 119.

The curve is in 0..36. Source attack subtraction is at most 5*11+2 = 57.
Low-mobility subtraction is at most 3*12+6+15 = 57. Therefore a piece score is
in [-114,36], a raw side sum in [-1710,540], and its rounded magnitude is at
most 1844. Existing i64 score arithmetic and final i32 conversion are safe.
At most 56 additional-ray charges and one source charge per piece give at most
1710 Activity R units across both sides; integer u64 regrouping is exact.

The pressure traversal performs at most 8*7+8 = 64 square observations, each
at most the full u8 mark value 112. Its raw sum is at most 7168. Disjoint-bit
scalar addition has this same conservative bound, and i32 subtraction/clamping
is safe. Effective weights are in 0..10240, material clamps to +/-256, so each
adjusted Activity weight is at most 12800. The already retained i64 weighted
products/phase rounds are far below i64 limits and produce i32-range results.
Shelter's original composition receives exactly its original produced values;
this extraction introduces no new arithmetic regrouping inside it.

## Added source controls

Five Activity controls cover raw and final equivalence against unchanged serial
composition over six placements, four native/supplied maps, material clamps,
asymmetric/zero/max weights, completion-order permutations and empty jobs;
15-piece inventories of each promotable kind, reversed same-kind chronology and
fresh-call isolation; duplicate weak/strong presence, type-additive raw pressure,
zero-family skips and global occupancy/inventory admission; signed rounding and
pressure around 12; and an independently specified six-charge rook case.
One Shelter control compares extracted geometry composition with unchanged
serial composition, including actually reduced Activity pressure.

No build, test, engine run or Git action was performed by this source owner.

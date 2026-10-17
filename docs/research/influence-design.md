# Influence representation investigation

This investigation uses only the released KingRE contracts. The original study
proposed an influence layer for the architect's mailbox/ordered-list position;
the Rust baseline described below now implements it. No performance benchmark
is claimed. The accompanying [arithmetic control](influence-arithmetic-control.c)
is an independent, board-free research check with no fixtures or oracle data.
[Recorded results](influence-arithmetic-results.json) passed.

## What one byte preserves

[EVAL-RELATIONS](../../../king-spec/spec/evaluation-relations.md) normalizes five counts with radices `2,2,4,4,4`. Their product is 256. The corresponding place weights are `1,2,4,16,64` for weak, queen, rook, minor, pawn.

For arbitrary nonnegative raw counts define

`T = weak + 2*queen + 4*rook + 16*minor + 64*pawn`.

Each carry below the final category preserves T; discarding the final pawn quotient changes T by a multiple of 256. Therefore normalized influence is exactly `S = T mod 256`. Conversely, every S in 0..255 uniquely decodes as:

```text
weak  = S & 1
queen = (S >> 1) & 1
rook  = (S >> 2) & 3
minor = (S >> 4) & 3
pawn  = S >> 6
```

**Proposed baseline:** freshly zero `[[u8;64];2]`, then wrapping-add the current contribution weight at every visited target. This is 128 bytes for the complete two-color map. It is mathematically equivalent to summing explicit counts and normalizing afterward, including crowded carries and complete discard. A nonzero set of physical contributions can intentionally encode zero. Saturating addition would be wrong.

Explicit five-byte count profiles need 640 bytes for the same map, plus normalization work. They remain useful as a simple independent builder/checking representation. No measured speed advantage is claimed for either representation. The byte is lossless for the normalized profile, not for the original physical contribution counts.

The byte also directly implements the lexicographic `(pawn,minor,rook,queen,weak)` comparisons used by [pawn progress](../../../king-spec/spec/pawn-candidates.md#coordinates-and-influence) and the ordinal used by [central influence](../../../king-spec/spec/central-influence-balance.md#profile-normalization-and-comparison). Neither comparison uses attacker count. Consumers that need uncapped count sum must decode or look it up; that sum ranges from zero to eleven, rather than the relation multiplicity cap of four.

## Adjusted exclusion and physical removal differ

The contract's [adjusted relation](../../../king-spec/spec/evaluation-relations.md#eval-adjusted-relations--removing-a-contribution) first normalizes, then subtracts the tested piece's category weight, clamping below zero. Thus the exact byte operation is `S.saturating_sub(weight)`, followed by ordinary classification. It must produce a temporary adjusted code without changing the base influence map.

Borrowing is intentional: code 64 with a minor excluded becomes code 48, representing three minors. For raw eight-minor/two-pawn support, normalization yields zero; adjusted pawn exclusion leaves zero. Removing a physical pawn contribution before normalization instead yields code 192. Wrapping subtraction of 64 from the normalized zero also gives 192, which is wrong for **adjusted** exclusion.

There is a useful qualification: exact physical contribution deltas *can* update a base modular sum with wrapping addition/subtraction. Modulo arithmetic remains a group even though the raw quotient was discarded. This is valid only when every changed physical contribution and its category is known. The byte cannot reveal which raw contributions existed, and slider blocker/transparency changes can alter many remote targets and weaken categories beyond a queen. The specified adjusted subtraction is not that physical update. Saturation also loses information: adding the weight back cannot undo an exclusion that clamped below zero. Do not apply adjusted subtraction to maintain or restore a base map.

Fresh map construction avoids these incremental dependencies and fits the proposed first architecture. Later incremental influence needs its own complete delta algorithm and restoration evidence, rather than assuming a moved piece's local destinations are the only changes.

## Classifier choices

Relations depend only on each normalized profile's capped multiplicity and least-value tier, not its whole byte. The realizable summaries are:

| Least-value tier | Possible capped multiplicities |
| --- | --- |
| none | 0 |
| weak, 99 | 1 |
| queen, 9 | 1,2 |
| rook, 5 | 1,2,3,4 |
| minor, 3 | 1,2,3,4 |
| pawn, 1 | 1,2,3,4 |

There are exactly **16 summaries**. This supports three competing pure implementations:

| Choice | Proposed static payload | Tradeoff to measure |
| --- | ---: | --- |
| Branch formula | No pair table; optional 256-byte profile metadata | Select only the requested tested-piece class; branch behavior depends on real queries. |
| Compressed pair table | 256-byte code→summary map + 16×16-byte relation table = **512 B** | Two independent summary loads, then one dependent pair lookup. Pack the four outcomes into one byte, two bits each. |
| Full byte-pair table | 256×256 bytes = **64 KiB** | One pair lookup and extraction; greater cache footprint and pressure on board/search data. |

The compressed relation table can be generated from the published formula, not fixture answers. Adjusted classification merely maps the saturated own code before the same lookup. Side selects which map is own; color does not otherwise alter the function. Material/personality values do not enter this classifier.

For an independent branch/predicate comparison, with opponent multiplicity/tier a,v and own d,u, the normative ordered branches are equivalent to:

```text
favorable = (a == 0) || (d != 0 && v > t && (a <= d || v > t+u))
contested = (a != 0 && d != 0 && v == t && a <= d)
unfavorable = neither
```

This may permit branchless machine code, but C/Rust Boolean syntax does not itself establish that result or make it faster. Compare compiler output and integrated cost. A compressed-table pair result can be reused for several tested-piece classes without another classification computation; every semantically selected charged relation query still incurs its charge.

**Keep the original byte.** The 16-state summary discards uncapped count sum, exact pawn/rook/queen category presence, and ordinal. Activity, pawn pressure, pawn-piece bonuses, pawn progress, central balance, king-pressure guards and special queen ordering need those distinctions. An optional `sum[256]` adds 256 bytes and serves several consumers; category presence is a mask/shift of S. The summary is a classifier index, not an alternative complete influence representation.

## Building the right geometry

The map is evaluation influence, not legal attack or mobility. [Influence geometry](../../../king-spec/spec/evaluation-relations.md#eval-influence--contributions-from-a-placement) includes friendly/enemy occupied squares, pinned pieces, an opposing king transparent to sliders, friendly rook transparency on orthogonals and bishop transparency on diagonals, and friendly queens transparent on either ray type. A queen's square receives the old contribution; only squares beyond it become weak, and later transparent sliders do not restore the old category. A friendly pawn stopping a forward diagonal adds the current category once on the next square, then ends the ray, even if that extra square is occupied. The own king blocks normally.

A direct mailbox builder can carry one current weight per ray. Add before examining the occupant; continue through the specified transparent pieces; switch to weight one after an own queen; implement the one-square forward-pawn extension before stopping. Ray direction and color determine transparency/extension, not side to move. Piece traversal can use any convenient order because final sums are commutative.

Do not reuse that same transparency policy for [activity rays](../../../king-spec/spec/activity.md#direct-destinations-and-additional-rays). Activity has ordinary direct destinations, a different bishop/rook continuation rule after selected blockers, no queen additional rays, and additional-ray relation charges. Legal attack/check detection has another policy with ordinary blockers and no such transparency. Sharing direction tables is safe; sharing these meanings is not automatic.

Activity also builds fresh pressure marks: eight presence bits per side/square suffice for weak/strong knight, bishop, rook and queen marks, another 128 bytes. Repeated identical marks OR together; weak and strong marks of the same type may coexist. Only direct destinations mark. Numeric category zero still makes a weak mark; category three is strong. These marks are separate from weak *influence*. [Pressure marks](../../../king-spec/spec/activity.md#potential-king-pressure-marks).

## Commutativity does not erase lifetimes or work

The influence sum and mark OR are commutative only for a fixed placement and the same selected destination calculations. They do not authorize rebuilding history-derived pawn order or changing evaluation selection.

* A full evaluation uses current influence, but [retained pawn structure](../../../king-spec/spec/retained-pawn-structure.md) may preserve earlier weakness categories and order under equal pawn identity, even though non-pawn geometry changed. Current penalties/progress and current piece influence still consume the new map. [Retained pawn subtotal](../../../king-spec/spec/retained-pawn-subtotals.md) also mixes retained pawn-file conditions with current occupants/material/influence. Refreshing descriptors merely because the new map differs changes behavior.
* [Fast evaluation](../../../king-spec/spec/retained-evaluation.md#fast-evaluation) preserves the inherited positional/pawn pair and does not select a pawn entry. It must not become a full evaluation merely because fresh influence is available. Pressure marks reset for every full activity evaluation; they never accumulate across positions.
* Influence is needed **outside full evaluation**. [FAST-THREAT](../../../king-spec/spec/fast-threat.md) compares previous/current influence near the current king before a potential fast cutoff, and [material threat](../../../king-spec/spec/material-threat.md) queries current piece relations. Ordinary candidate ranking also uses current influence. A strict “build only on full evaluation” owner is too narrow; propose a lazy map available to any actual influence consumer, reused if full evaluation subsequently occurs.
* Fast pressure compares uncapped sums for the opponent of the **current** side at neighbors of the **current** king, in both positions. It cannot substitute relation summaries or previous-side/previous-king observations. [King-pressure guard](../../../king-spec/spec/king-pressure.md).

An initial implementation can use per-node lazy scratch outside the copied position. Retaining 128 bytes across 64 search plies would cost 8 KiB and make parent maps available; a shared workspace with saved previous-neighborhood observations can use less memory if consumer liveness permits. Both require explicit validity tied to placement. Do not assume a child may overwrite the only parent data before a later sibling or previous/current guard reads it. Null changes no placement, so a pure placement map can be shared, while side, history and evaluation-age semantics still advance separately.

Pure classification tables or memoized results may persist because their mapping never changes. Keep semantic charge selection at consumers:

* Unadjusted explicit relations charge one per selected query, including repeated identical queries and cache hits; adjusted relations and influence construction charge zero. [Relation accounting](../../../king-spec/spec/evaluation-relations.md#diagnostic-operations-and-work-charges).
* Activity charges every included additional-ray query and admitted low-mobility source query. Direct adjusted queries and no-query shortcuts are zero. Capture-category overrides do not undo a prior selected query, and doubling vertical rook value does not double query charges. [Activity work](../../../king-spec/spec/activity.md#work-accounting).
* Pawn exposed-level/empty-forward gates and eligible pawn-piece rooks select their own unadjusted queries. Phase gates can omit piece work; retained structural reuse does not waive current penalties or their selected charges. [Structural scoring](../../../king-spec/spec/pawn-structure-score.md), [pawn-piece work](../../../king-spec/spec/pawn-piece.md#local-work-and-limits), [retained subtotal](../../../king-spec/spec/retained-pawn-subtotals.md).
* Material threat charges every eligible own non-king with nonzero opposing normalized influence, even favorable or losing-maximum candidates. Earlier cutoff gates can suppress the estimator entirely. Computing every potential charge eagerly would alter work-clock behavior. [Material threat](../../../king-spec/spec/material-threat.md#result-and-work), [fast cutoff](../../../king-spec/spec/fast-cutoff.md).

The safe interface distinction is a pure classifier plus caller-owned semantic charging. Computing a cached classification must not automatically mean either “charge a query” or “omit a charge.”

## Evidence and first experiment

### Initial Rust baseline

`src/influence.rs` implements the 128-byte two-color profile map with a fresh
mailbox scan. `Influence::build(&Position)` reads only current placement and
returns an owned map. It uses `Square::offset` for every destination/ray step;
no rights, side-to-move, pins, chronology or legal-move filters affect it.
The private board-only builder permits independent synthetic geometry tests
without requiring history or legal positions.

Every visited square receives the current ray contribution before occupancy
is considered. Opposing kings continue the ray. Friendly rook/bishop
transparency depends on orthogonal/diagonal direction, including queen sources.
A friendly queen changes the contribution to weak for subsequent squares
only; later transparent sliders retain that weakness. A friendly pawn on a
forward diagonal receives its contribution, contributes the same category
once on the next board square even if occupied, then stops the ray. The
implementation does not share this transparency policy with legal attacks.

The wrapping addition proof above applies to each individual contribution:
all place weights divide 256, and every intermediate byte is the partial
weighted sum modulo 256. Associativity makes piece traversal order irrelevant.
The resulting byte uniquely preserves all five normalized digits. Their sum
is computed by masks/shifts without the classification cap; relation queries
cap it at four and select the highest nonzero digit's tier. The ordered branch
classifier is the released formula with no pair lookup table. Knight and
bishop select the same minor tier; a king has no tested-piece tier and is
outside this helper's query domain.

Adjusted exclusion uses saturated subtraction from the already normalized
byte, then the same branch classifier. It never mutates the stored profile
or charges semantic work. All query selection, including charging repeated
unadjusted queries and charging zero for adjusted queries, stays with consumers.

Module-local controls cover opposing/own king and ordinary blocker behavior,
rook/bishop transparency with queen sources, nonrestoration after weakening,
both pawn-forward directions, occupied extra squares, forbidden backward and
orthogonal extensions, and crowded carry/discard. An independent target-centric
reference considers each source/target pair, accumulates full five-category
counts and performs ordered carries; whole 128-byte maps are compared for 32
deterministically varied bounded placements and their color/rank reflections.
These tests do not call the production ray builder as their reference.

The relation reference decodes by division/remainders, excludes by explicit
digit borrowing, and evaluates the equivalent Boolean relation predicates.
It compares every 65,536 own/opponent byte pair for all four query tiers and
the bishop alias, plus all 327,680 pair/removal combinations for all four tiers.
This checks 1,310,720 adjusted classifications independently of the production
saturated subtraction. No expected fixture answer is embedded in engine code.

Compilation and these controls use housekeeping CPUs `0-5,8-13`. They validate
this pure component; no integrated-search speed, complete evaluation, charged
work schedule or final conformance claim follows from their result.

Validation on 2026-10-17: after the coordinator wired `pub mod influence`, the
coordinator ran the focused module suite and reported **7 tests passed in
1.53 seconds**, including exhaustive byte-pair/exclusion classification and
the target-centric whole-map comparisons. This implementation agent did not
repeat that successful run. An earlier focused command before module wiring
found zero tests and is not counted as validation. Released external diagnostic
fixtures and consumer-owned work selection remain separate integration checks.

The standalone arithmetic control exhaustively checked:

| Control | Cases |
| --- | ---: |
| Ordered carry normalization versus weighted sum modulo 256; every raw count 0..31 | 33,554,432 profiles |
| Byte encode/decode and realizable summary discovery | 256 codes; 16 summaries; maximum uncapped sum 11 |
| Ordered relation branches versus predicate and compressed table, all four tested classes | 65,536 pairs |
| Independent digit borrowing versus saturated subtraction and adjusted classification | 327,680 pairs/removal choices |
| Lexicographic profile ordering versus byte ordering | 65,536 pairs |
| Deterministic shuffled wrapping accumulation and exact modular physical removal | 1,024 contribution sequences |

Deliberate counterexamples also distinguish saturated adjusted exclusion from physical removal and wrapping subtraction. Reproduce with assertions enabled:

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror docs/research/influence-arithmetic-control.c -o /tmp/rook2-influence-arithmetic-control
/tmp/rook2-influence-arithmetic-control
```

Observed toolchain: Debian GCC 14.2.0. Control-source SHA256: `906fed7b0dc9d0f363a3dbbb3354e6712e18ea87ef0e72c7db4d27028cb01dff`. These are arithmetic correctness checks, not board-geometry validation, performance data or conformance qualification.

**Concrete proposed experiment:** first hold mailbox traversal and all consumers fixed and compare explicit-count accumulation plus normalization against wrapping-byte accumulation. Consume/compare all 128 normalized map bytes, selected component scores, pressure marks and exact relation charges. Use synthetic transparency/weakening/forward-pawn cases plus the released bare-king, queen-ray and crowded-carry functional units; include a sequence that reuses pawn identity after non-pawn geometry changes. Time reset/build/consume together, retaining setup-inclusive evidence. The selected public influence queries alone do not validate a whole map, and the reference's extra observation work need not be imitated.

Then hold the winning builder fixed and compare branch classification against the 512-byte compressed table. Use both the exhaustive synthetic pair stream and actual varied consumer traffic; uniform synthetic pairs alone do not represent branch/cache behavior in search. Keep optional 64-KiB-table results separate rather than expanding the first comparison. Measure retired instructions, compatible cycles, CPU time and dispersion with live outputs consumed, then repeat through integrated full/fast search once available. No synthetic consumption-cost subtraction. [Functional measurement guide](../../../king-spec/performance/functional-benchmark-guide.md).

The main risks are geometry confusion, a saturated temporary leaking into the base map, relation-summary information loss, stale parent scratch, refreshing retained pawn state, and charge deduplication. Arithmetic controls settle the proposed encoding/classifier identities; they do not settle those lifecycle and integration risks or which implementation is faster.

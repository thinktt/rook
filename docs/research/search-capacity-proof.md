# Search representation bounds and scratch-lifetime addendum

Status: independent proof/critique of the proposals in [architecture],
2026-10-17. This note uses released KingRE 2.5.0 contracts only. It adds no
engine implementation or replacement architecture. **Fact** denotes a contract
rule; **derived** denotes a conservative consequence; **proposal** denotes a
representation choice. Loose upper bounds below are not claims that one
naturally reached search attains them.

## 1. A 512-entry candidate row covers the specified ordinary domains

### Domain invariant

**Fact.** [Setup] admits exactly one king and at most sixteen pieces per color,
including at most eight pawns, with no pawn initially on ranks one/eight.
[Production wire] uses those setup semantics for both FEN4 and FEN6. [Joined
ingress] uses the same placement capacity while explicitly broadening the
standalone candidate diagnostic's check and en-passant preconditions.

**Derived.** Sixteen pieces per color remains an invariant of every ordinary
search position:

- Ordinary movement and castling preserve piece count.
- A promotion replaces one pawn with one promoted piece, not two pieces.
- Captures remove an opposing piece; joined en passant can remove an opposing
  non-pawn but still cannot increase either color's piece count.
- A null transition changes no placement.
- Copying/restoring a branch, retrying, or executing more IIO passes does not
  place the positions of separate branches on one board.

Sources: [move sequence], [ordinary iterations], [joined ingress]. The
specified exceptional king-victim command continuation terminates on the
following ordinary `go`; it does not create a normal search position requiring
an additional moving king. Arbitrary unspecified kingless continuations are
not silently included in this proof.

### Per-piece inventory bound

For one piece in one reached position, blockers, own occupied destinations,
king-safety filtering and a forbidden opposing-king destination can only reduce
the following geometric maxima. These maxima count distinct move descriptors,
so promotion expansion is included explicitly.

| Moving piece | Maximum non-castling descriptors | Derivation |
| --- | ---: | --- |
| Queen | 27 | Rook rays total 14; bishop rays total at most 13 on an 8x8 board. |
| Rook | 14 | Seven remaining squares in its rank plus seven in its file. |
| Bishop | 13 | Sum of four edge distances, maximal on a central square. |
| Knight | 8 | Eight distinct displacement directions. |
| King | 8 | Eight adjacent squares; handle castling separately. |
| Pawn, nonpromotion rank | 4 | Two forward-diagonal destinations, one forward step and possibly one two-step. |
| Pawn, promotion rank | 12 | At most three destinations, four promotion choices at each. |

The complete legal set and four promotion choices are facts from [candidate
production]. The geometry arithmetic is derived; there is no need to assume
the maximum-legal-moves result for reachable standard-chess positions.

**Joined en passant does not break the bound.** Setup retains only an empty
rank-three/rank-six target with an adjacent moving pawn. Joined generation
allows that pawn's forward diagonal onto the target without an additional
moving-side target-rank test, and accepts an opposing non-pawn behind the
target. This changes the removed piece and admits unusual states, but adds no
third diagonal direction. Because the target is empty, that same destination
cannot simultaneously be an ordinary occupied-destination capture. Rank three
or six is never a promotion destination for either color. Thus it fits within
the nonpromotion pawn's two diagonal destinations. Sources: [setup], [joined
ingress], [candidate production].

### Total bound

**Derived.** A coarse bound, independent of piece mixture, is

`16 moving pieces * 27 descriptors each + 2 castling descriptors = 434`.

Accounting for the required king gives the slightly stronger bound

`15 non-kings * 27 + 8 king steps + 2 castles = 415`.

Neither bound needs to be attainable. For example, all fifteen non-kings being
queens would prevent the required castling rooks; counting both is harmless
overestimation. **Proposal:** the architecture's capacity 512 exceeds both
proved bounds. The standalone diagnostic's 230 limit and root scheduling
diagnostics' smaller abstract-list limits are not used in the proof.

**Quiescence also fits.** In-check quiescence imports the complete ordinary
legal evasion set, already covered. Non-check quiescence produces a pseudo-
legal subset of the same piece movement geometry: all captures, en passant,
quiet queen promotions and specified quiet direct checks. It omits quiet king
moves, castling, underpromotions and pawn double pushes. A tactical queen still
has at most 27 destinations, and a tactical pawn at most three destinations
with only the queen promotion descriptor. Omitting early king-safety filtering
does not increase any piece above its unfiltered geometric bound. Sources:
[quiescence candidates], [quiescence tree].

**Implementation condition.** This proves capacity for the required unique
candidate sequence. The producer must apply special prefixes without
duplicating entries, as the contracts require. An internal algorithm that first
materializes several duplicate inventories needs its own temporary-capacity
analysis; it cannot call that larger temporary sequence the proved inventory.
Track populated length separately, use checked appends in validation builds,
and never truncate a purportedly full sequence. At most 434 produced entries
also makes u16 candidate indices/cursors sufficient; a sentinel still needs a
separate value or flag. A parent piece-list index is 0..15 and fits four bits.

**Lightweight corroboration.** Exhaustive arithmetic over all 64 source squares
confirmed empty-board ray maxima queen=27, bishop=13, rook=14. This is only a
check of the bound arithmetic, not engine move-generation testing.

## 2. Signed 16-bit remaining depth is safely sufficient

This proof distinguishes root iteration depth I, ordinary remaining depth d,
absolute target T=P+d, fresh extension e, and accumulated extension flags a.
Conflating these is the source of the signed-byte hazard.

### Root, ply and fresh-extension bounds

**Fact.** A completed iteration with I>61 stops before the next iteration,
independently of personality `md`, average allowance or terminal mate scores.
Thus ordinary iterative search can enter I=62, but not I=63. Each root child
starts at P=1 and d=I-1. Ordinary dispatch delegates to quiescence at P=63,
d<=0, or the personality depth boundary, before ordinary TT lookup/store.
Sources: [iteration stop], [ordinary iterations].

**Derived.** Fresh extensions satisfy 0<=e<=6:

- Previous extension input a is in 0..7, so R=max(0,2-a) lies in 0..2.
- Sparse capture extension is victim contribution (2,3 or 4), plus zero,
  one or two pawn additions, plus R-2. Its minimum is 2+0+0-2=0 and maximum
  4+2+2-2=6.
- Other branches return only zero, one or two.

Source: [move extensions]. Values 0..7 in [ordinary iterations] describe the
three-bit extension representation and accumulated OR. For example, accumulated
flags can be 7 even though the local fresh producer returns at most 6. The
accumulated value is the child's previous-extension context, **not** the value
added to current child depth.

### Bound every ordinary edge

| Edge or repeated invocation | Child remaining depth/target | Maximum target growth |
| --- | --- | ---: |
| Main candidate | d'=d-1+e at P'=P+1, so T'=T+e | +6 |
| IIO child | d'=S+e-P-1; last shallow target S<=T-2, so T'=S+e | +4 |
| Null trial, d<6 | d'=d-3 at P'=P+1, so T'=T-2 | -2 |
| Null trial, d>=6 | d'=d-4 at P'=P+1, so T'=T-3 | -3 |
| Scout/full retry | Same produced child, same remaining depth | 0 from retry |

These are the actual depth rules in [ordinary iterations]. A null child does
not receive a further implicit decrement. Every admitted IIO shallow target
is at least P+2, so its child remaining depth is at least one. Later ordering
passes and main visits are fresh child searches from the unchanged parent
depth; one pass does not cumulatively add its extension to the next pass's
depth. Accumulated OR flags only change later extension context.

**Derived by induction.** At any produced ordinary position at ply P>=1,

`T(P) <= I + 6*(P-1)`

and therefore

`d(P) <= I-1 + 5*(P-1)`.

The base P=1 has T=I. Every child edge increases P by one and target by at most
six, proving the induction. IIO and null edges only tighten it; retries create
no deeper edge. With I<=62 and ordinary TT access confined to P<=62:

`maximum ordinary TT required/stored remaining depth <= 61+5*61 = 366`;

`maximum ordinary TT target <= 62+6*61 = 428`.

Ordinary TT access has d>0. Null children can have d=-2 or -1, and main children
can have d=0, but those dispatch to quiescence before ordinary TT access. Even
the P=63 handoff position has d<=371 and T<=434. Quiescence check-target
increments are at most one per further ply, so later quiescence target also
cannot exceed 434. A checking-mate probe begins at child target P+1, giving a
smaller bound. Quiescence does not add ordinary remembered-result queries.

**Robustness check.** If a caller conservatively uses the looser 0..7 bound for
fresh extensions, the same induction gives TT remaining depth <=427, TT target
<=489 and P=63 target <=496. These also fit i16 easily. No correctness decision
depends on squeezing the fresh-extension upper bound to six.

### Component table domain and mate mutation

**Fact.** [Remembered results] allows component store/query P in 0..63 and T
in 0..64, including negative remaining depth. Its component range T-P is
[-63,64]. Mate cutoffs can increase stored depth to the current required depth;
they do not create a depth larger than the queries already bounded above.

**Derived.** One signed-i16 field covers both production and these component
events, including negative diagnostic depths: a safe union of the tighter
derived ranges is [-63,366]. Compare signed depths; do not encode emptiness as
a depth that can collide with a valid negative component result.

**Conclusion about i8.** A signed byte covers the component range but the
simple production proof reaches above 127. This does not establish a naturally
reached i8-overflow witness: the loose bound ignores material/extension
correlations and pruning. It establishes that “root iterations stop by 62” is
not a proof that i8 is safe. An i8 proposal would need an additional materially
tighter proof. The proposed i16 needs no such assumption and fits the proposed
12-byte record.

## 3. The concrete 12-byte TT record proposal is feasible

This validates field capacity and the ordinary Rust C layout, not the complete
remembered-result algorithm, replacement correctness, cache performance or
engine behavior.

| Proposed field, in order | Type | Offset | Capacity justification |
| --- | --- | ---: | --- |
| Secondary identity | u32 | 0 | [Position identity] defines secondary in 0..2^32-1. |
| Normalized score | i16 | 4 | Stored S in [-10000,10000], mate normalization adds/subtracts P<=63; [-10063,10063] fits. |
| Remaining depth | i16 | 6 | Covers the production/component bound above. |
| Endpoint hint | u16 | 8 | Six source plus six destination bits; a same-square code can denote no hint. Promotion/kind are deliberately not retained. |
| Permissions/markers | u8 | 10 | Two bound permissions, quiet-check marker and marked-depth marker require four independent bits; an optional validity flag also fits. |
| Logical generation | u8 | 11 | A proposal for fresh-search clearing; not a specified semantic field. |

With `repr(C)`, this has alignment four and size twelve; four consecutive
records have size 48/alignment four. Default Rust struct reordering must not be
assumed to reproduce these offsets. No packed/unaligned layout is necessary.

**Independent layout experiment.** An isolated `/tmp/imp2-search-layout-proof.rs`
containing only the proposed struct, four-record wrapper and `size_of`,
`align_of`, `offset_of` assertions was compiled with local
`rustc 1.85.1 (4eb161250 2025-03-15)`. It ran successfully and printed:

```text
record=12 align=4 offsets=[0, 4, 6, 8, 10, 11]; group=48 align=4
```

This is a representation probe outside the engine repository. Actual engine
fields/layout must still be asserted when implemented.

**Generation caveats.** Generation zero can represent logically empty after a
physical clear; use nonzero live generations and perform a real clear before
reusing a generation after wrap. Old-generation identity zero must not become
a valid TT hit. Clearing must make all three retained priorities and recent
empty, preserving first-empty/least-depth tie rules after initialization.
Records copied/displaced into recent must retain validity in the live search;
displacing an empty retained priority must empty recent. Byte-generation wrap
cost belongs to whole-lifetime measurements. Generation does not weaken exact
identity equality or change the specified group count G=floor(`tts`/48)'s
largest-prime selection. Source: [remembered results], [ordinary iterations],
[session lifecycle].

The component diagnostic's opaque group/identity labels are supplied equality
relations, not real position hashes. A cold adapter can assign request-local
injective numeric IDs to its bounded labels. Hashing arbitrary strings into
this u32 field without collision handling would add unspecified collisions.

## 4. Shared priority scratch is live only until order materialization

**Derived safety condition.** One global priority/permutation workspace is
sufficient if every node completely materializes its ordered candidate row
before any recursive child visit. Its lifetime ends at that materialization.
The persistent row, extension flags, scan cursor, entry TT observation,
pass-best, running windows and PV have longer, separate per-ply lifetimes.

Ordinary ordering is completed before checking-mate probes/IIO/main search.
Quiescence ordering is completed before its candidate-decision loop. Neither
subsequently needs the original numeric priorities. IIO transforms the
persistent row using returned child scores and per-candidate flags; tail IIO
uses an explicit suffix range. Sources: [ordinary iterations], [quiescence
tree], [candidate order], [quiescence candidates].

There is no specification-driven counterexample to that carefully scoped
scratch lifetime. The following implementation choices would invalidate it:

| Counterexample | Failure | Required ownership condition |
| --- | --- | --- |
| Lazy preferred-move picker keeps its pending indices/priorities in global scratch, then searches its first child | Child ordering overwrites the parent's pending visitation order. | Materialize the full ordered row before recursion, or give such a picker its own persistent storage. |
| Parent or checking-mate probe scans a global permutation without applying it to its row | First recursive probe destroys the scan order and next cursor interpretation. | Scan the persistent ordered row; scratch indices are already dead. |
| Accumulated IIO extensions live beside global priorities | A descendant destroys flags needed by later ordering passes/main search. | Keep flags attached to the parent candidate identity in its retained row. |
| IIO fills global candidate scores, calls another child, then sorts all scores at pass end | Descendants overwrite earlier scores. This can also misimplement immediate promotion semantics. | Process the returned score into pass-best/promotion immediately; keep persistent pass control per ply. |
| Root exploration/ranked-prefix indices are borrowed from the global workspace | Root prefix/order changes after a child uses scratch. | Root visitation/ranking/work ownership persists independently of temporary sort workspace. |
| Tactical reply-count helper writes its generated replies into the current node's candidate row | It destroys candidates not yet visited. | Use an explicitly separate helper buffer or bounded count-only generator. |
| A helper or trace observer retains a borrowed scratch slice after its immediate computation | Later helper/child overwrites the observed result. | Finish consumption before reuse, or copy requested diagnostic output on the cold path. |
| Priority scratch aliases a parent influence map, retained evaluation, current PV or selected output capture | These have consumers after descendant return. | This proof covers priorities/permutation only; it does not justify aliasing longer-lived data. |

In particular, “one shared workspace” is not “one candidate list for every
ply.” Sibling/scout/IIO visitation can reuse descendant rows after the prior
invocation returns, but all active ancestors' rows must remain intact. A scout
retry may reset its invocation candidate/PV state while retaining its produced
child evaluation state; global sorting scratch is free to overwrite because
the previous invocation's priorities are no longer needed.

## 5. Result for the pending architecture critique

The proposed 512 candidate capacity and signed-i16 TT depth have conservative
released-spec proofs. The twelve-byte concrete field layout is independently
verified as a layout proposal. Shared priority scratch is compatible with the
specified search if the materialization and helper-lifetime conditions above
are enforced. These results justify proceeding to integrated measurement; they
are not performance evidence or full conformance claims.

[architecture]: ../architecture.md
[setup]: ../../../king-spec/spec/position-setup.md
[production wire]: ../../../king-spec/spec/ordinary-xboard-wire.md
[joined ingress]: ../../../king-spec/spec/ordinary-play-ingress.md
[move sequence]: ../../../king-spec/spec/move-sequence.md
[ordinary iterations]: ../../../king-spec/spec/ordinary-iterations.md
[candidate production]: ../../../king-spec/spec/search-candidate-production.md
[quiescence candidates]: ../../../king-spec/spec/quiescence-candidates.md
[quiescence tree]: ../../../king-spec/spec/quiescence-tree.md
[iteration stop]: ../../../king-spec/spec/iteration-terminal-stop.md
[move extensions]: ../../../king-spec/spec/move-extensions.md
[remembered results]: ../../../king-spec/spec/remembered-results.md
[position identity]: ../../../king-spec/spec/position-identity.md
[session lifecycle]: ../../../king-spec/spec/ordinary-session-lifecycle.md
[candidate order]: ../../../king-spec/spec/search-candidate-order.md

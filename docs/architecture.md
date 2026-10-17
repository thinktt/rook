# Initial architecture — proposed baseline

Status: initial design critically reviewed, 2026-10-17; implement provisional
baseline per [decision0001](decisions/0001-initial-architecture.md). This is a proposal,
not measured evidence, a claim of conformance, or an adoption of another engine's
architecture. Imp2 owns the final decisions. The governing
[mission](../../imp-perf-mission.md) prioritizes an efficient integrated engine,
followed by progressively exact behavioral fidelity.

## Objective and invariant boundaries

Build a single-threaded Rust production engine with a cold text/JSON boundary and
one concrete native search kernel. The first implementation should already have
the position, evaluation, search, state and measurement ownership needed by the
complete engine. Early reduced-fidelity searches are experiments with explicitly
listed omissions, not approximations presented as KingRE performance.

The [ordinary composition](../../king-spec/spec/README.md#ordinary-play-composition)
binds these constraints:

- Placement, chronological type order, rights, EP and active history are distinct
  state. Captures preserve survivor order; promotions append to the new type.
- Root material/square/weight context is fixed through a search; current phase,
  material counts and geometric checks change with placement.
- Legal geometric attacks, evaluation influence and tactical support are
  different predicates. Non-check quiescence deliberately produces pseudo-legal
  candidates and can consume an estimate before a later king-safety rejection.
- Branch-local retained evaluation belongs to the produced child. A scout and
  full-window retry reuse that child after its evaluation mutations; siblings
  inherit the unchanged parent. TT, pawn retention and learned ordering effects
  survive child returns and iterations, but clear logically at a new search.
- Work charges and ordering/reuse policies are observable behavior. Machine-work
  savings cannot remove semantic relation charges or strengthen hash equality.
- Production ingress is broader than some component diagnostics. Their capacity
  and legality preconditions must not become undocumented production limits.

Detailed sourced investigations: [position](research/position-design.md),
[search](research/search-design.md), [measurement](research/measurement-design.md).

## Position and transition kernel

Start with a dense 64-square byte mailbox and compact chronology. A square is a
`u8` in a1=0 through h8=63 order. A piece code identifies color/type, with zero
empty. Keep each color's sixteen ordered square slots grouped by type and six
type counts. A type's chronological slice follows from count prefixes. Ordinary
moves change one entry; captures and promotions shift at most fifteen entries.
Do not use swap removal. The setup whole-color sequence can be rendered cold
without imposing an extra mutable global-order invariant.

Approximate payload before Rust layout measurement:

| State | Bytes |
| --- | ---: |
| Mailbox | 64 |
| Two color square sequences | 32 |
| Twelve type counts | 12 |
| Three placement fingerprints | 12 |
| Side, rights, EP sentinel, reversible count | 4 |
| Starting-square measure and alignment allowance | about 4 |

This suggests a roughly 128-byte position. Do not contort the code merely to
hit that size. Keep root-dependent retained evaluation outside the position.
There is no square-to-list map or twelve-bitboard duplicate in the baseline.
Candidate production already knows the mover's list index; store ephemeral
source-index metadata with a generated candidate to avoid repeated searches.
Victim-index lookup is at most fifteen entries on captures. Metadata is valid
only against that unchanged parent and never survives as a TT/killer identity.

Maintain placement fingerprints by XOR deltas, counts through chronology, and
the starting-square occupancy measure by local deltas. Recompute the cheap phase
formula from these produced facts, preserving promotion carries. Maintain the
root-valued non-king square subtotal separately in branch evaluation state.
Debug checks compare derived fields with slow recomputation outside timed runs.
Store the raw starting-square measure even while materialM<=32 makes its
effective phase contribution zero. A promotion can cross that gate; updating a
previously zeroed measure with only local move deltas would lose remote pieces.

Use one `u16` move: six source bits, six destination bits and a tag distinguishing
ordinary, four promotions, EP and castle. Reserve an invalid same-square value
for absence; public null transitions have an explicit separate representation.
Provide explicit full-descriptor versus endpoints-only comparisons. Do not let
the encoding choose generation order.

Start with copy-child transitions for the compact position and retained branch
state. This offers a controlled sibling-restoration baseline and makes scout
retry ownership explicit. It is a provisional cost decision. The first competing
experiment adds a reversible delta route without changing generation, evaluator,
ordering or searched work. Captured chronology must be restored at its original
index. No copy includes a candidate buffer, root tables, shared TT or pawn cache.

Start geometric attacks with precomputed leaper destinations and ordered ray
steps, direct occupancy lookup and early exit. Emit exact directional chronology
and special prefixes. Candidate safety uses a temporary occupancy/mailbox
projection with the actual changed squares, without updating chronology/hash/
phase for every examined candidate. Verify its geometry against a fully
produced child; avoid two independent transition rule engines. An alternative
adds selective occupancy masks or piece/occupancy bitboards to the same
mailbox and chronology. Measure all maintenance, legality and child/restoration
costs before selecting it; isolated bitboard attack speed is insufficient.

Strict diagnostic legality and broader ordinary EP ingress are explicit policies
at the boundary, not duplicated engines. Keep the exceptional specified
king-victim command continuation narrowly represented as an ingress outcome;
do not spread arbitrary missing-king handling into normal search.

## Root context and evaluation

Build one immutable `RootContext` per search: root side/phase/counts, color-owned
material and evaluation coefficients, non-king square adjustments, contempt,
variation and personality search controls. Use ordinary references, no reference
counting or virtual evaluator dispatch in the production recursion.

Each ply has a small `EvalState`: retained positional subtotal, pawn progress,
evaluation age and root-valued non-king square sum. A child inherits the retained
pair and increments age modulo 256. Full evaluation replaces that child's pair
and resets age; fast evaluation preserves it. Null changes only its specified
state fields. Root context is never rebuilt from descendant phase.

Construct evaluation influence on demand per ply, with a validity flag for the
current board. Each side/square uses one byte: weak=1, queen=2, rook=4, minor=16,
pawn=64 contributions summed modulo256 exactly encode the specified carry rules.
Adjusted support uses non-wrapping saturation at zero, leaving the base map
unchanged. Legal attack detection never uses this map. A small classifier table
or simple formulas can derive relations; choose from measured integrated costs.
This algebra requires exhaustive verification before use.

Demand includes fast-cutoff pressure/threat and move-ordering consumers, not
only full evaluation. Pressure can need both parent/previous and current maps
at the current king's neighbors. Keep previous-position access until those
gates finish; lazily build its map if not already available.

Fresh construction is the baseline. Incremental slider-influence updates are an
alternative only if profiles show construction dominates and the extra changing
ray bookkeeping repays its stores. Transparency and pawn-forward extra squares
make ordinary legal-attack incremental updates inapplicable by assumption.

Reuse the same produced influence within activity, pawn, shelter, central and
tactical consumers. Keep it per ply when a parent may need it after a child.
Cache pure relation classifications if useful, but add each required semantic
relation charge at the consuming operation even for identical cached queries.
Activity pressure marks are fresh evaluation scratch and may use compact masks.
Do not retain current penalties with a structural pawn entry.

Use exact integer formulas with explicit mathematical-floor helpers, wrapping
where specified and checked wider intermediates at unbounded diagnostic seams.
Do not use floating-point scoring or reassociate intermediate rounding. Native
hot values may be narrowed only after deriving their admitted ranges.

The 128 pawn-retention groups keep full identity, ordered structural descriptors
and base terms, initialized to identity zero/empty. This is deliberately not a
valid-bit cache: initial zero matches and real identity collisions are behavior.
Preserve retained order and apply current membership/geometry at consumption.

## Search and memory ownership

Use direct recursive functions with an explicitly allocated search arena indexed
by ply. Sixty-four ply slots own their candidate storage/extensions, PV and
lazy influence. Separate the produced `NodeState` (position and retained
evaluation) from invocation controls/PV: retry resets the latter and preserves
the former. Reset invocation lengths/scalars on entry;
never clear or clone the entire arena per node. The initial search uses only a
fraction of the allocated depth. Compute actual `size_of` and inspect allocation
and copy assembly rather than relying on the estimates here.

Candidate storage must cover the production domain. A 512-entry scratch buffer
is a conservative proposed bound: at most sixteen moving pieces times at most
27 queen destinations, plus two castles is 434; a pawn's promotion expansion is
below27. Confirm this derivation against every ingress domain before using it.
The standalone diagnostic's230 limit is not the bound justification. If an
admitted domain exceeds the proved bound, use a cold overflow path rather than
truncation. Separate populated length from capacity; move-only, priority and
extension arrays can avoid copying a large combined struct when reordering.
Pack move, optional parent-list index and three accumulated extension bits in
one32-bit candidate. Materialize ordering before recursion, then reuse one
global priority/permutation workspace: parent priorities are no longer needed
while children search. Helpers that nest candidate generation require a separate
explicit workspace so they cannot overwrite the retained parent list.

Returning nodes produce a score/status and a per-ply PV length, with moves
copied to the parent only on the specified improvement. An interruption is a
distinct status propagated without fabricating a score, PV or completed child.
Retain completed-root publication separately from terminal stopping work.

Ordinary and quiescence entry have explicit owners for the one search charge,
natural4096 poll, draw admission, next-ply killers and TT query. Implement their
ordered decisions directly. IIO, null probes and checking-mate probes invoke the
same child kernel and preserve the enclosing iteration context; ordering-pass
results do not become the parent's main score/PV.

Root scheduling is separate from ordinary candidate ranking. It retains stable
completed rankings, uses the second-ranked score for following windows and
freezes late-work scheduling at iteration entry. Preserve all specified
aspiration/randomization/retry rules when those slices enter the fidelity set.

### Shared state

The remembered-result table implements the exact three-depth-priority plus
recent policy and its recent-first metadata/score query rules. It is not a
generic strongest-depth TT. Use the specified prime group count and key
composition. A proposed record packs identity, score, endpoint hint, depth,
permissions/markers and generation into twelve bytes; four records make48bytes.
Use at least a16-bit depth: the iteration ceiling does not bound extended
remaining depth to a signed byte. A byte generation tag fits this proposal;
check actual field ranges/layout and the amortized wrap-clear cost. Generation
tags can implement new-search
logical clearing while retaining allocated storage; generation wrap performs a
real clear. Invalid entries are never observed. The initial allocation and every
page touched remain whole-lifetime engine costs. Compare a48-byte group with a
cacheline-aligned alternative before claiming either is faster; requested `tts`
selects semantic capacity, not arbitrary replacement behavior.

History preferences are fixed arrays by side/type/destination; killers are by
ply. Both use the specified wrapping/update/reset arithmetic. Shared pawn and
TT state survive ordinary child return. Keep these mutable stores in a single
search owner, outside any `Position` copy. No mutexes, atomics or hash maps are
needed in the single-threaded hot path.

History equality uses its prescribed fingerprint/side/rights/EP, not stronger
whole-board verification. Preserve up to799 active protocol plies plus search
tail. Keep persistent game rewind/replay storage separate from compact search
positions. Rewound branches are absent from repetition history.

## Interfaces, observability and build

The native kernel owns production computation. A cold ordinary XBoard parser
owns persistent session/game/personality/clock state. A separate diagnostic
binary translates strict JSON domains to the same native routines. Optional
trace collection is compiled or monomorphized away from the production search;
no per-node JSON values, strings, maps, heap vectors or dynamic callbacks.

Start with a small Cargo package using std-only engine core. Add serde only to
the diagnostic boundary when needed; table data comes only from normative spec
constants, never expected answer fixtures. Build release with explicit recorded
optimization/LTO/codegen settings. Compare generic x86-64, target-native and PGO
as distinct artifacts; do not silently substitute native for the generic-PGO
reference. Measure setup and destruction as well as inner search.

Use deterministic private development commands first: position/perft checks,
fixed-depth search, consumed output and full environment/artifact receipts.
These do not masquerade as a complete XBoard implementation or a mandatory
production interface. Keep test/reference slow recomputation out of measured
production builds. Debug assertions and allocation observation are separate
artifacts with their own identities and overhead.

## First integrated implementation and experiments

1. Implement the compact position, exact chronology and identities, generated
   legal moves and child restoration. Validate known legal-tree inventories,
   castles, promotions, EP, counter wrap and state recomputation. Build one
   branching traversal so child production/restoration cost is measured together.
2. Integrate actual root context, square/material scoring, normalized influence,
   activity and relation accounting with deterministic recursive search. Keep a
   machine-readable list of omitted pawn/endgame/search policies. This is a
   representation/evaluation cost baseline, not a KingRE timing comparison.
3. Compare copy vs delta and mailbox vs hybrid one change at a time with identical
   workloads, generated inventories, scores, work and output witnesses. Retain
   failed variants' evidence and select on integrated cost and maintainability.
4. Add the specified pawn/endgame evaluation and ordinary/quiescence policies in
   vertical slices, updating the fidelity declaration and expanding exact checks.
   Recheck the chosen architecture against whole searches, not only local wins.
5. Move to the released54 searches/12game units only as their full behavior is
   supported. Complete adapter, production mapping, gameplay and measurement
   qualification; never declare full performance from a cheaper partial search.

The initial advisor critique tightens this sequence: the first slice is smoke
and cost evidence only. Before selecting a production representation, include
actual full/fast tactical selection, pawn reuse/replacement and remembered
results in varied contexts. Revisit representation/restoration jointly when
one-factor results interact. Record occurrence counts in a separate diagnostic
artifact, with overhead excluded from the measured production build.

Measure process CPU/wall and semantic work immediately. Current unprivileged
PMU probes on Vic are denied, including outside the tool sandbox. Record
instructions/cycles as unavailable until a scoped authorized observer exists;
do not infer PMU counts from disassembly or virtual work. Development results
remain reported-only; final comparison needs the released frozen measurement
and uncertainty procedure. Hardware calibration is a per-case estimating aid.

## Questions for initial independent critique

1. Is the compact mailbox/chronology plus copy-child baseline a sufficiently
   credible foundation, or does an overlooked ownership/generation interaction
   make delta restoration or bitboards necessary from the outset? Preliminary
   judgment: retain this small baseline and test alternatives before committing.
2. Are per-ply scratch and retained evaluation ownership sufficient for scout
   retries, IIO, quiescence and natural interruptions? Preliminary judgment:
   yes, provided retries preserve their produced child and only next siblings
   reinitialize it; generic function-entry reset would be a serious defect.
3. Does the first integrated fidelity slice exercise enough evaluator/search
   cost to detect an unsuitable architecture promptly? Preliminary judgment:
   material-only search does not; influence/activity and allocation/restoration
   must join before interpreting architecture measurements. Pawn/endgame and
   exact search policies remain necessary before target-performance claims.

Alternatives and evidence should be challenged, not solved afresh by the
advisor. No approval gate is created by this consultation.

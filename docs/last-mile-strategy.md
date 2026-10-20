# Rook2 last-mile strategy

2026-10-20. Active under the
[working agreement](leadership-working-agreement-last-mile.md).
Candidate62 remains the production control. This document records current
decisions and hypotheses; frozen historical evidence keeps its original scope.

## First decision: locate comparative weakness

Rook2's largest cost is not necessarily its largest disadvantage against KingRE.
Use the released functional reference to distinguish comparatively expensive
operations from ordinary costs of doing the required work. Imp2 selected three
units: opening evaluation, opening position history and light-start composed
search. Evaluation has separate scalar and production-coherent Influence rows,
giving four measured routes. The
[closed study](../experiments/functional-cost-three-unit/report.md) is committed
at b25c1424. Its isolated derivative preserves retained62 and the canonical
engine source. All four projections match; one calibration per row and one
warmup plus three measured batches closed without a measurement retry.
Candidate25's fresh diagnostic-process observations could not supply these
local-loop observations.

| Complete sequence / route | Rook2 median CPU, µs | Reference median CPU, µs |
|---|---:|---:|
| Opening evaluation, scalar Influence | 8.955 | 15.753 |
| Opening evaluation, coherent Influence | 8.307 | 15.753 |
| Opening position history | 1.888 | 11.562 |
| Light-start search, enclosing local scope | 44.451 | 38.986 |

The study supplies no positive case for a broad Position/Node or evaluation
rewrite. It does not establish that their pure engine operations are
proportionally cheaper: the reference position consume-only control alone is
about 4.001µs, exceeding Rook2's whole local position sequence. Different
observation/normalization and allocation work can matter substantially.
That control cannot be subtracted. The already-retained coherent producer's
7.24% lower evaluation median than scalar is not a new production gain.

The search difference remains unlocalized. Rook2's scope includes root
preparation and logical resets, reuses physical storage and contains 35 TT
generation-wrap scans per batch. Its narrower reference-inner-call ratio is
unavailable. Do not subtract the position/evaluation rows from search or turn
this opening sample into a claim about dense middlegames.

The reference has important limits. It uses separate observation artifacts;
some units include substantial output consumption. Synthetic consume-only
controls cannot be subtracted. The three composed searches have different
inner/outer boundaries and some large whole-lifetime system-CPU shares.
Hardware and build differences remain explicit. A useful comparison must
change an architectural choice, not merely fill a table.

Meanwhile, investigate whole-path opportunities directly. Do not make a
complete 23-unit study a prerequisite for useful source work.

A [contemporary same-host comparison](../experiments/retained62-reference-pair/README.md)
is now prepared locally for owner review: exact retained62 and approved
generic-PGO KingRE, all54 original cases, one warmup plus three measured
lifetimes per artifact/case, fixed paired order. The432-lifetime proposal is a
descriptive baseline, not the unadopted final uncertainty policy. Payload
copies and source/workload identities are verified. External transfer,
operator contact and execution await explicit owner authority; no external
job or new local engine run was launched for the preparation.

## Current architectural questions

| Question | Current assignment / decision | Evidence needed to advance |
|---|---|---|
| Which semantic sequences are comparatively expensive? | Four-row study closed. Preserve the current ownership baseline; no broader functional framework or production cost partition is selected. | Revisit only for a specific decision that these boundaries cannot answer. |
| Can checked generation avoid traversing irrelevant directions? | Source prototype reviewed. One isolated generic compiler/test discriminator is selected after pressure's failed screen; no timing or adoption yet. | Exact ordered inventories, bounded king-first exits and EP; actual skipped traversal versus setup, unchecked-path and code-size costs. |
| Can Activity pressure avoid materializing per-square mark bytes? | Parked. All200 library tests and70 live/offline replays pass, but the fixed generic screen is0.4281% slower, with3/7 cases lower. | No retune, second screen or PGO rescue. Preserve the failed result. |
| Does the TT access population justify a different layout? | Imp2/Sol owns a source-only plan for one small probe/store census on35/08. No census execution or layout variant is selected. | Recent returns, metadata continuation, retained matches, identity/generation misses, stores and reset costs together. |
| Can Phase reuse avoid both recomputation and extra call arguments? | Narrow dependency-owned field hypothesis reviewed, unselected. Keep behind current discriminators. | Actual producer/consumer costs and complete mutation ownership without narrowing supplied-count semantics. |

### Checked generation: narrow the work, preserve the semantics

`GenerationSafety::accepts` already rejects checked off-mask destinations
before projection. The existing04/35 census therefore supplies an enumeration
population, not removable safety-check work.

The first source candidate tests each checked B/R/Q source/direction against the
existing evasion mask before entering its mailbox ray walk. Empty intersection
means the entire direction can be skipped, including coordinate steps and
occupant loads. The intersecting direction can retain the old near-to-far
walker and final safety projection. This avoids committing immediately to a
new full bitboard move generator or a target-order reconstruction.

Preserve source chronology, direction order, pawn-prefix ordering, promotion
choices, and king processing. LIMIT2 checked calls must keep their early king
witness path; below two, the returned complete inventory remains reusable.
EP runs through its independent prefix and projection, including joined setups
where the removed victim is a non-pawn. After that prefix, a double-check
ordinary/promotion evasion mask is empty; skipping those nonking classes must
not suppress EP. An independent old enumeration path is required for
differential tests; sharing the new pruning with the oracle would hide errors.

The first variant leaves pawn/knight enumeration and all king handling unchanged.
Unchecked calls must not acquire a new per-direction mask test. The current
single-check census averages only about 0.9–2.1 visited squares per attempted
slider direction across the B/R/Q groups on04/35; the proposed table load and
mask branch have competing cost.
This is a hypothesis of modest integrated benefit, not a forecast of parity.
Do not attribute all generation cost or all off-mask counts to removable time.

### Pressure: change the producer/consumer boundary

The current scalar Activity walk already computes each destination's category.
It writes a weak/strong bit into a 128-byte marks array; king pressure then
walks selected squares and sums those individual bits. The selected source
prototype retains presence as destination sets and reduces it directly against
admitted king regions. Mobility, rounding, source penalties and relation
charges remain.

Use one weak/strong pair across all pieces of the current kind, reduce it once,
then discard it. Duplicate marks remain set membership; weak and strong labels
can coexist, including category zero. Knight, diagonal and orthogonal visibility
remain separate; queens consume the disjoint slider union. The single subtraction
and clamp follow all four kinds. Scalar mailbox visibility preserves the public
placement/supplied-map boundary without a new coherence permission.

The isolated prototype uses baseline SSE2 byte-SWAR and PSADBW to count the two
masked words together. An independent old byte producer/consumer and seven
focused differential controls passed in the [compiler discriminator](../experiments/pressure-presence-compiler/report.md).
The lead's source review found no semantic objection. This differs from
rebuilding the whole Activity frontend or only accelerating king-ray traversal, but does not remove
most king geometry. Indexed word updates, shifts, two accumulator dependency
chains, SIMD transfers, live visibility masks and outlining can erase any gain.
A smaller source scratch array is not evidence of fewer spills or faster code.

The compiler exposed that tradeoff: the intended SSE2 reduction replaced the old byte
consumer, but destination updates remained stack read/modify/write operations.
The active Activity stack chain shrank632→456 bytes while its combined code
grew9119→10322 bytes. One unchanged [fixed70 generic screen](../experiments/pressure-presence-compiler/screen-results.md) then measured summed
medians13.392375s control versus13.4497075s candidate, ratio1.00428098.
Only3/7 cases improved; worst ratio1.00773765. All70 original live and independent
offline replays passed. The screen does not isolate the cause of the loss.
The miss parks the source; correctness and smaller
frames do not authorize a retune or PGO rescue. Retained62 remains unchanged.

### TT: filter identity before fetching payload

Existing access reviews already show conditional scalar identity-first loads.
There is no eager48-byte group read to remove. A compact identity header could
reduce distinct lines touched by misses; a live or stale identity match would
then need payload access, and stores can become more expensive. Recent usable
returns are especially important because today's recent record can already fit
within one conditional64-byte line.

The source-only census plan must price those populations together. Distinguish
recent metadata-only continuation from a usable recent return, and identity
misses from generation rejection. Include replacement/displacement and clears,
not just query counts. A conditional distinct-line ledger is useful but does
not measure cache misses, residency or CPU cost.

Two dense arrays—16 bytes of full identities and32 bytes of payload per semantic
group—are one possible alternative to per-group headers or64-byte padding.
They preserve48G payload and need no partial-identity filter. Dense-header
residency is a separate hypothesis from reducing lines per query. The specified
group count, collision and priority rules remain unchanged. Neither layout nor
a native experiment is selected until the workload mix supports a concrete
discriminator.

### Phase: own only the dependencies that justify reuse

An unselected alternative to E26's extra Phase arguments is a packed field in
Position's existing padding, reached through the already-passed Position pointer.
For phases produced by the current formula, opening/16 needs five bits and
endgame needs nine; middlegame is256 minus the other two. Source layout suggests
a u16 at126 without changing Position160/Node176. Actual sizes, copies and
lowering would still need verification.

The invariant would be exactly `cached = phase_formula(counts, starting_units)`.
It must not require those supplied counts to agree with the mailbox. Released
material diagnostics deliberately admit independent counts. Private mutation
of just those two dependencies, readonly access and literal supplied-count
setters could establish this narrower invariant. Explicit independent Phase
arguments remain authoritative and need not satisfy the cache's encoding.

Refresh once at a completed dependency-changing transition; preserve raw
starting occupancy below its material gate. Do not increment a simple weighted
material total: carry normalization means a capture can increase that measure.
Quiescence's material-only hypothetical must remain counts-only through one
material formula, without acquiring a Phase refresh.

This is different transport from E26, but its economic objection is substantial:
capture/promotion children can return from repetition/TT or enter checked
quiescence without ever demanding Phase. The cache shifts work into those
producers and adds loads/unpacking elsewhere. E26's old measured phase pool was
small, and source call counts overstate savings where the compiler already
shares work. Keep this as a reserve hypothesis, not a selected refactor.

### Dependency elimination: a narrower opportunity than whole shelter

Source review confirms that screen and pattern/exposure have exact zero phase
factors in some positions. Pressure does not: with phase weights summing to 256,
its scale `(E + 2O + 4M)/4` is at least 64. All 54 workload configurations also have
nonzero king-shelter weights (minimum 17 percent), so disabling shelter and its
Activity-pressure demand through zero personality weights would not help that
corpus. Pure screen/pattern guards remain untried; they do not justify removing
the entire pressure dependency or forecast a material whole-engine gain.

## Workload choice and evidence

The retained [whole54 report](../evidence/exttsp-profiled-standard54-results-20261020-01/report.json)
records historical raw differences of0.286968s on04,0.246692s on42,
0.237454s on52 and0.170148s on35. These are differences between separate
windows/hardware, not an observed same-hardware engineering budget.

The seven familiar screen cases account for0.808238s of the4.208581s raw
difference (19.2%), and17.5% of candidate62's whole54 time. This does not itself
prove a bad screen. It does mean04/35 cannot stand in for the whole gap, and a
mechanism affecting other cases should receive relevant coverage chosen
before its results. Use actual production PGO/ExtTSP settings for native
performance decisions; do not revive old failures by changing their gates.

One bounded experiment record should hold the mechanism, changed semantics,
artifact/build identity, correctness evidence, timing scope and decision.
Keep raw outputs outside Git per the [storage guide](evidence-layout.md).
Do not multiply approval documents or rerun unchanged proof layers.

## Completion remains broader than optimization

The [qualification gaps](qualification-gaps.md) and
[Vic scope](qualification-scope.md) remain obligations. Parity is the
optimization target; qualification uses the released acceptance policy and
requires compatible measurements, behavioral evidence and the external game
gate. No raw ratio, microbenchmark or partial profile closes those obligations.

The [uncertified-hint note](research/uncertified-hint-completion.md) now has a
smaller conditional completion certificate based on a zero-valued sparse
ending. It supplies no public collision witness or authority for new behavior;
that qualification question remains open.

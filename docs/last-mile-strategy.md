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

## Current architectural questions

| Question | Current assignment / decision | Evidence needed to advance |
|---|---|---|
| Which semantic sequences are comparatively expensive? | Four-row study closed. Preserve the current ownership baseline; no broader functional framework or production cost partition is selected. | Revisit only for a specific decision that these boundaries cannot answer. |
| Can checked generation avoid traversing irrelevant directions? | Imp2/Sol source prototype complete; lead reviewed the patch. No build or tests executed; parked behind the pressure compiler discriminator. | Exact ordered inventories, preservation of bounded king-first exits and EP, actual skipped traversal versus added mask/setup cost. |
| Can Activity pressure avoid materializing per-square mark bytes? | Astra source prototype complete and reviewed by the lead. Imp2 now owns one generic build, focused/library tests and actual caller/helper review. Timing and adoption are not selected. | Actual lowering, register and frame costs before deciding whether it deserves a native screen. |
| Does the TT access population justify a different layout? | Deferred behind the initial discriminators. Existing source/access reviews are sufficient; do not repeat them. | Recent-return versus retained/miss populations, complete probe/store and footprint costs. |

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
focused differential controls are present but unexecuted. The lead's source
review found no semantic objection. This differs from rebuilding the whole
Activity frontend or only accelerating king-ray traversal, but does not remove
most king geometry. Indexed word updates, shifts, two accumulator dependency
chains, SIMD transfers, live visibility masks and outlining can erase any gain.
A smaller source scratch array is not evidence of fewer spills or faster code.

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

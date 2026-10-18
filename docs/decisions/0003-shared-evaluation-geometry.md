# Shared immutable evaluation geometry

Date: 2026-10-18. Owner: Imp2. Decision: adopt shared valid board-step tables,
then verify compiler-PGO impact separately. This is an incremental algorithm
choice; no independent advisor approval was requested or required.

The optimized profile-01 Callgrind diagnostic identifies activity and influence
as prominent remaining simulated-cost rows. The full54 local CPU collection
also shows a broad cost gap to the raw uncalibrated reference. The experiment
shares the existing valid ray/knight steps across legal attacks, activity and
influence, adds fixed pawn/king destinations, and removes repeated coordinate
bounds calculations in evaluation. Position/Node layout and restoration stay
unchanged; no mutable derived cache or fingerprint reuse is introduced.

Along each ray, transparency/weakening and the forward-pawn extra square keep
their prior order. Between independent rays/pieces, influence accumulation is
wrapping addition and commutes. Activity keeps its original directional order,
pressure marks and semantic relation charges. Trusted table steps are generated
from Square.offset and remain inside0..63; debug checks and a prior-coordinate
oracle validate the generated domain.

The prototype passed130 native tests, all54 strict public replays, and a
10,000-placement differential check of complete influence bytes and activity
scores/pressure/weighted results/relation counts against our own prior coordinate
implementation. The latter covers broad promoted/check/king-adjacency domains.
The first compile-only attempt missed constants still used by king pressure;
its logs/source are retained and it contributes no runtime evidence.

The fixed six-case generic/non-PGO CPU pilot completed all60 lifetimes with
strict behavioral/accounting success. Sum of case medians changed from
17.1693775s to16.7837260s (ratio0.977538, about2.25% lower).
Every median improved; case02 alone is inconclusive because ranges overlap.
The remaining samples support a modest whole-pipeline benefit with low state
complexity. Exact samples and prospective selection are in
`evidence/eval-geometry-cpu-pilot-20261018/`.

Adopt the source, retaining the frozen prototype artifact
`e734494836337f86d84fe166ae4952d192f3dc07346d482d5ecbb3a22831260c`.
A new same-source compiler-PGO train/use build and comparison are required before
attributing that benefit to the production PGO profile. Older PGO artifact3660
and its54-case CPU collection remain separate baselines. Full gameplay,
mandatory conformance, calibration and final performance qualification remain
open; this decision does not select a permanent mutable position layout.

The independent matched-PGO procedure also completed60 strict-oracle lifetimes.
Its sum of six case medians changed from16.001395s to15.4905955s (ratio0.968078,
3.19% lower), with every median improving. New production PGO artifact1dc996b2
passes all54 strict replays and the eight wire interruption fixtures. Keep the
source decision; full54/12 cost collections under the final qualification
profile remain separate. The prior3660 full54 collection stays a baseline.

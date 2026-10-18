# Typed piece lists for influence construction

Status: adopted in canonical source;134 native tests and the49-operation/
2215-case adapter regression pass after integration. Fresh canonical PGO and
CPU evidence remain separate. Date:2026-10-18. Imp2 owns this decision.

Influence construction now enumerates existing coherent per-color/type piece
lists instead of scanning64 mailbox squares and classifying each occupied
source. Actual ray semantics still read the board. Targets, directions,
transparency, queen weakening, pawn extension and contribution wrapping are
unchanged. Each contribution is a placement-only addition modulo256, so
changing source or type-group enumeration order cannot change the final bytes.
Semantic R charges remain with consuming queries. No cache, mutable shared
state, additional Position/Node field or restoration mechanism is introduced.

This relies on the existing mailbox/list invariant. FEN construction and actual
transitions establish it; restored chronology preserves type membership, and
reflection tests restore both views. Raw count-only material and supplied
destination hypotheticals do not call this builder. Public writable fields do
not enforce coherence automatically; the production consumers were audited.
Ordinary joined special transitions retain their existing actual-tag/list
maintenance and terminal ownership. This change adds no admission restriction.

The previous mailbox builder remains test-only.10,000 constructed placements
match both it and the independent target-centric coordinate oracle, then match
again after per-type order reversal and independent Position validation.
Generic10634820 passes134 native tests,54 strict replays and eight interruption
fixtures/24 searches. Its60-lifetime matched generic pilot sums15.4118105s
versus16.181479s baselinef28279c3, ratio0.952435219(4.756478% lower). All six
observed candidate ranges are below baseline; these finite observations do not
establish a confidence band or universal improvement.

The compact relation kernel from decision0005 was then combined with this
enumeration in a fresh formatted clone and independently trained PGO build
b17776fb. It passes134 tests,54 strict replays and eight interruption fixtures.
The matched three-variant pilot retains90 independently reconciled lifetimes:
18 excluded warmups and72 measured, four samples/variant/case.

| Sum of six CPU medians | Seconds |
| --- | ---: |
| Canonical915f83e4 |14.7940530|
| Relation lookup1e5d075d |14.3190285|
| Combinedb17776fb |13.7237695|

Combined/base is0.927654477(7.234552% lower), and combined/lookup is0.958428814
(4.157119% lower). All six combined observed ranges lie below both controls.
This measures the complete separately trained variants, without assigning an
exclusive CPU share to either function or assuming generic gains add.

The combined source is integrated byte-for-byte, including the134-test code,
and the identical49-operation frontend passes against it with36 units/2215
external cases. Canonical instrumentation uses its own crate path/profile;
trial timing is not transferred to a new binary. Source/build/profile/raw
evidence is retained under `evidence/influence-groups-*`,
`evidence/pgo-eval-kernels-combined-*` and `evidence/eval-kernels-integration-*`.
Complete mandatory diagnostics, production audit, current-artifact gameplay/
full3288, final54/12 costs and PMU/resource/observer/uncertainty/calibration
remain open.

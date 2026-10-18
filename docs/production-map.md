# Production ownership and qualification map

Status: initial review map, 2026-10-18; not a completed requirement audit.
The released KingRE v2.5.0 contracts remain authoritative. Each row identifies
the production owner and existing evidence class, with the remaining obligation.
A native seam check is not mandatory external DIAG acceptance, and finite replay
agreement is not a proof over every admitted setup or a full gameplay pass.

| Contract responsibility | Native owner | Existing evidence and remaining review |
| --- | --- | --- |
| Placement/chronology, FEN admission, rights/EP, local transition, phase and identities | `position`, `types`, `identity` | Native special-move/ordering/derived-field tests and component projections. Audit every broader ordinary-ingress clause, including exceptional king-victim continuation in `session`. |
| Geometric attacks and ordered ordinary legal candidates | `movegen` | Native perft/order/EP tests; all54 ordinary replays. Generation-summary experiments add differential ordered-inventory checks on constructed setups. Preserve projection fallback and bounded reply semantics. [Capacity/source review](decisions/0002-geometric-legality.md#source-review-production-capacity-and-bounded-lists) proves a conservative417-slot ordinary bound within512; the shared-producer oracle does not independently prove pseudo-candidate completeness. |
| Influence radix, relations and semantic charging | `influence`, consuming evaluators | Exhaustive normalized-code relation checks and external native evaluation fixtures. Confirm every consumer owns its charge even when computation is reused; geometric legality must never use evaluation influence. |
| Frozen root context, material, square values, full/fast retained state and age | `evaluation`, `evaluator` | External native full/fast and composed-root checks, plus ordinary replay anchors. Complete mandatory adapter evaluation operations and review branch ownership through retries/null/IIO. |
| Pawn structure/retention/collisions, progress/race, subtotals and current penalties | `pawn_structure`, `pawn_terms`, `pawn_progress`, `evaluator` | External native evaluation/lifetime sequences and unit checks. Verify admitted collision/initial-zero behavior and all ordered reuse seams through mandatory DIAG. |
| Activity/pressure, shelter, positional patterns, endgame adjustments and bounds | `activity`, `shelter`, `positional_terms`, `endgame`, `evaluator` | Native and external component fixtures. Final formula/range/rounding audit and complete evaluation-stage traces remain. |
| Search history, repetition/draw admission, learned history/killers and TT policy | `history`, `remembered`, `ordinary_policy`, search owners | Native replacement/reset/collision and policy fixtures. Explicit review of uncertified/colliding endpoint hints remains; an empty-source guard is not a completed semantics audit. [Conditional composed-call gap](research/uncertified-hint-completion.md) remains unresolved; direct diagnostic candidates require occupied sources. |
| Quiescence entry, fast/full selection, tactical production, pruning and reply probes | `quiescence`, `quiescence_policy`, `tactical` | Native recursive tests and composed ordinary anchors. Complete required quiescence traces, broader admitted states and interruption boundaries. Optimistic estimates may precede later own-king rejection. |
| Ordinary entry, extension/depth policy, null, scout/full retry and IIO tail | `ordinary`, `ordinary_policy`, `engine` | Native policy fixtures, integrated search and all54 replay anchors. Check full IIO/extension/retention composition beyond finite examples and expose mandatory trace operations. |
| First root iteration, rankings/windows, aspiration/randomization and work scheduling | `first_iteration`, `engine`, `timed`, `timing` | Native root/timed sequences, all54 exact posts and focused games. Complete diagnostic root families and a naturally reached first-root fallback witness. |
| N/R charges, natural4096 polls, captures, terminal work and publication | `work_clock`, `engine`, `timed`, `host`, `session` | External native timing fixtures, active-time native tests, all54 work-post replays and eight literal interruption fixtures. Review every pre/post-capture interrupted ownership boundary. |
| Persistent game/clock/parameters/seed lifetime and ordinary command meaning | `session`, `clock`, `parameters`, `timing` | Persistent native sequences, literal seed controls, same-artifact focused12/632 plus continuity. Full3288-game gate and admitted command-domain audit remain. |
| Framing, nonblocking queue/polls, live records, result/fatal exits, PV/score spelling | `wire`, `host`, `output`, `bin/rook2` | Literal process controls, eight wire interruption fixtures, complete all54 and focused replay. Full ordinary protocol requirement review remains. |
| External mandatory JSON schemas and operation transport | Separate `diagnostic/` crate calling native owners | Frozen c4cd8566 passes27 operations/1130 cases across22 complete files plus25 selected cases from two partial files, with23 adapter units. All remaining mandatory operations are explicitly unsupported; admission/schema audit is incomplete. |
| Owned whole-engine cost, repeatability, cross-host calibration and final performance | External measurement tools and frozen build artifacts | Direct wait4 controls, balanced local pilots and a complete54-case local CPU collection; PMU unavailable through disabled self-opens. Final measurement profile, calibration and complete54/12 collections remain separate obligations. |

Production search uses static generic diagnostic/host specialization. Ordinary
`Session<false>` has no development counters/traces; `NoHost` is zero-sized when
not serving live input. Cold JSON is in a separate Cargo package, with a pinned
public parser dependency, and is not linked into the ordinary executable.

Current frozen baseline evidence is under
`evidence/live-wire-build-20261018-frozen/`,
`evidence/live-wire-check-20261018-frozen/`,
`evidence/live-interruption-wire-20261018-frozen/`,
`evidence/focused-games-20261018-first/` and
`evidence/diagnostic-20261018-first/`. Each experiment/build receipt identifies
its actual code/artifact; passing observations are not silently transferred to
a later binary. This map must be expanded to individual normative clauses and
closed with executed evidence and production review before mission completion.


A narrower [scalar source review](research/scalar-production-review.md) now
maps WC-LEDGER arithmetic/reset/snapshot and historical repetition/reversal
predicates to the exact latest production source, including admitted arithmetic
bounds. This closes that source-review subset only; mandatory scalar DIAG and
all charging, observation, lifecycle and interruption consumers remain open.

A separate [depth/history range review](research/depth-range-review.md) binds
ordinary recursive depth/target and learned-history capacity to this same native
source. It proves those arithmetic ranges without closing score storage or
uncertified-hint eligibility. Frozen adapter c4cd8566 now verifies twelve more
native-backed routes, including ledger, placement/pawn terms, learned/table
sequences and supplied candidate order:23 units and1130 external cases pass.
That closes the transport subset that was still pending at the scalar review's
original checkpoint; its immutable source-review receipt remains historical.
The first1022-case attempt and its12 unsupported ordering failures are retained.

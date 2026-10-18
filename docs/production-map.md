# Production ownership and qualification map

Status: initial review map, 2026-10-18; not a completed requirement audit.
The released KingRE v2.5.0 contracts remain authoritative. Each row identifies
the production owner and existing evidence class, with the remaining obligation.
A native seam check is not mandatory external DIAG acceptance, and finite replay
agreement is not a proof over every admitted setup or a full gameplay pass.

| Contract responsibility | Native owner | Existing evidence and remaining review |
| --- | --- | --- |
| Placement/chronology, FEN admission, rights/EP, local transition, phase and identities | `position`, `types`, `identity` | Native special-move/ordering/derived-field tests and component projections. Audit every broader ordinary-ingress clause, including exceptional king-victim continuation in `session`. |
| Geometric attacks and ordered ordinary legal candidates | `attacks`, `movegen`, placement setters/recompute | Integrated persistent planes pass133 native tests; independent tag/query/projection and broad-generation comparisons support the new Boolean kernel. Ordered checker identities and quiescence mailbox reuse remain separate. [Decision0004](decisions/0004-persistent-attack-planes.md) retains matched generic/PGO evidence and limits. [Capacity/source review](decisions/0002-geometric-legality.md#source-review-production-capacity-and-bounded-lists) proves a conservative417-slot ordinary bound within512; the shared-producer oracle does not independently prove pseudo-candidate completeness. |
| Influence radix, relations and semantic charging | `influence`, `relation_table`, consuming evaluators | Formula-derived compact relations pass exhaustive normalized-code checks; typed-list influence matches mailbox and independent coordinate oracles across10,000 broad placements, including per-type order reversal. Both are integrated with134 native tests and49-operation regression; decisions0005/0006 retain cost/domain evidence. Confirm every consumer owns its charge even when computation is reused; geometric legality must never use evaluation influence. |
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
| External mandatory JSON schemas and operation transport | Separate `diagnostic/` crate calling native owners | Frozenef406db7 passes59 operations/3236 cases across49 complete files plus25 selected cases from two partial files, with49 adapter units, linked to current integrated compact-relation/typed-list/static-kind activity native source. All remaining mandatory operations are explicitly unsupported; admission/schema audit is incomplete. |
| Owned whole-engine cost, repeatability, cross-host calibration and final performance | External measurement tools and frozen build artifacts | Direct wait4 controls, balanced local pilots and canonical8d9dddc5 complete54 CPU collection:216 strict lifetimes,81.131004s summed case medians. PMU unavailable through disabled self-opens. Final measurement profile, calibration, qualified54/12 costs and current-artifact gameplay remain separate obligations. |

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
predicates to the exact1dc996b2 source at that review checkpoint, including
admitted arithmetic bounds. This closes that source-review subset only; remaining scalar DIAG and
all charging, observation, lifecycle and interruption consumers remain open.

A separate [depth/history range review](research/depth-range-review.md) binds
ordinary recursive depth/target and learned-history capacity to this same native
source. It proves those arithmetic ranges without closing score storage or
uncertified-hint eligibility. Frozen adapterfab90bb7 now verifies fourteen more
native-backed routes, including ledger, placement/pawn terms, learned/table
sequences and supplied candidate/priority/capture ordering:25 units and1214 external cases pass.
The subsequent0f8c7226 expansion adds root randomization/aspiration, quiescence
capture policy and PV line boundaries:29 units/1262 cases across33 operations.
The supplied-context expansiona3c94922 adds material balance, capture exception/
defense/allowance, frontier estimate, king pressure and fast cutoff, producing
32 units/1475 cases across41 operations with the same native source closure.
The admission/history/extensions expansionbb872509 passes34 units/1968 cases
across44 operations. Native production source remains unchanged.
Five endgame components produce36 units/2215 cases across49 operations in
137a71e9. The identical frontend then passes against integrated pure kernels
in ab8b7c3c, with both source closures and all original reports retained.
That closes the transport subset that was still pending at the scalar review's
original checkpoint; its immutable source-review receipt remains historical.
The first1022-case attempt and its12 unsupported ordering failures are retained.

The subsequent four score/weight transports in9c8780c9 pass39 units and2496
cases across53 operations against unchanged canonical native source. Supplied
final-score context remains distinct from placement-derived fresh evaluation.
The full signed32 coefficient conversion and narrower composed central domain
retain separate admission. This extends finite component transport coverage;
production context lifecycle and global arithmetic review remain open.

Four selected/full endgame-bound transports bring frozenf8e0b7b0 to57
operations,2868 cases and42 units, including contradictory intervals and
strict material eligibility. Current ordinary8c4619a7 separately passes fresh
focused12/632, continuity4/8 and both public seed controls. Full gameplay and
qualified performance remain open.

A bounded [current-source score review](../evidence/score-range-review-20261018/score-range-cold-review-20261018-imp2-subagent.md)
proves selected FULL race/queen endpoint bounds and distinguishes the discarded
ply63 FAST endpoints. A subsequent [production TT-origin review](../evidence/store-origin-review-20261018/production-tt-origin-cold-proof-20261018-store-origin-review.md), independently reviewed against the current native source, closes normalized TT score capacity at +/-10062 through actual store sites, root windows and table lifetime. It imports the consumed endpoint bounds and valid completed upstream arithmetic; global retained/intermediate bounds remain open. These cold reviews identify no reachable runtime defect.

Current static-kind activity integration passes134 native tests. Canonical
8d9dddc5 has verified own54-case PGO training and passes54 strict replays/eight
interruption fixtures. Its fresh60-lifetime pilot independently reconciles
2.052997% lower summed CPU medians than8c, with profile29 slightly higher and
overlapping. The unchanged57-operation adapter freshly relinks as e31263ac
and passes2868 unique cases/42 units against this same native source. Complete
cost and current-artifact gameplay are separate from these observations.

The linked [production score-capacity review](research/production-score-capacity.md)
connects the bounded endpoint, retained producer, raw search-intermediate and
TT/window proofs. This closes the stated numeric premises under admitted
position/root invariants, without closing full lifecycle or source-global audit.

Fresh8d9dddc5 full54 cost now independently reconciles216 normal strict
lifetimes:81.131004s summed medians,0.852305% below the previous81.828432s.
There are41 lower and13 higher case medians. The raw uncalibrated reference
ratio1.279027725 and maximum finite spread2.398788% do not close qualification.

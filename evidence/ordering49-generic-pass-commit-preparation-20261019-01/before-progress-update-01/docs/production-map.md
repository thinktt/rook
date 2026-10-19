# Production ownership and qualification map

Current retained implementation: candidate43, 2026-10-19. This is an engineering
review map, not a completed clause-by-clause qualification audit. The released
KingRE v2.5.0 package remains behavioral authority. The [historical map and
chronological notes](production-map-history-20261019-01.md) preserve the
previous document exactly; its earlier unsupported-operation and timing counts
are historical.

## Current integrated evidence

The [source-promotion checkpoint](../evidence/influence-bitsliced-sum-qualification-20261019-01/final-state.json)
binds native/tools graph `e89dcb33`, combined native/tools/diagnostic graph
`8a49fa28`, ordinary own-PGO image `36251ecf` and diagnostic image `b024c045`.
The exact isolated tested images are retained; source promotion does not claim
a separate canonical rebuild. Candidate44 was built in isolation and
[parked at its compiler gate](../evidence/influence-direct-fill-parent-backend-review-20261019-01/decision.json):
the intended copy survived, and the three inspected complete function bodies
are byte-identical to43 generic. It ran no native tests or timing and is not
production.

Candidate45's private source-index masks removed the intended bounds branches,
with a55B larger producer and16B larger frame. Its11 focused tests and70 exact
replay checks passed, but its fixed generic screen improved only0.345564%
(6of7 lower), below the required0.5%. It is
[parked without retry or own-PGO](../evidence/influence-source-range-decision-20261019-01/README.md);
the accepted production artifact and whole54/12 timings remain43's.

Candidate46 bypassed unused relation reads for forced capture categories. Its10 focused tests and70 exact replay checks passed, but the fixed generic screen improved only0.048659%, with3of7 lower cases, failing both preset improvement gates. It is [parked without retry or own-PGO](../evidence/activity-capture-override-decision-20261019-01/README.md). Candidate43 remains accepted.

Candidate47 removes the ordinary parent Position snapshot using a split evaluation interface. Its13 focused controls and generic70 pass (1.117892%lower,7of7). Fresh own-source54 training/profile remerge/use-build and all70 own-PGO replay checks pass, but the fixed own-PGO screen improves only0.013752%,4of7 lower. It is [parked without retry or adoption](../evidence/ordinary-position-borrow-pgo-decision-20261019-01/README.md). Generic gains do not transfer; production and whole54/12 timings remain43.

Candidate48 removes the parent snapshot with two shared Position loans around the unchanged full call, keeping the evaluator source and ABI intact. Its13 focused controls and70 exact replay checks pass. Generic70 improves0.306387%,7of7 lower, below the fixed0.5% aggregate gate. It is [parked without own-PGO or retry](../evidence/ordinary-position-reborrow-decision-20261019-01/README.md). Candidate49 preserves the public sorting helper and512-entry workspace while giving internal consumers equal-length knowledge. Its generic backend reduces bound-check sites11→6 per inlined caller with unchanged frames and+182B selected code. Six existing controls and all70 live/offline original replay checks pass. The fixed generic screen improves0.6650503%,7of7 lower,worst0.997841443, so it [advances only to fresh own-source PGO](../evidence/ordering-equal-length-decision-20261019-01/README.md). Instrumented PGO build is closed and training/provenance/backend/own-PGO screen remain pending; retained43 already inlines sorting under PGO, so no generic gain transfers. Candidate43 remains accepted; no49 adoption or broader qualification follows.

Fresh [mandatory validation](../evidence/influence-bitsliced-sum-conformance-preparation-20261019-01/validation-summary.json)
passes189 native tests,209 diagnostic tests and7,673 cases across117 operations
and115 whole fixture files. The ordinary image separately passes all54 strict
replays, eight interruption fixtures/24 searches, the12-game/632-search pre-gate,
eight continuity searches,11 seed children and three persistence searches.
Original raw observations, exact inputs and actual exits were independently
reconciled. These finite results do not establish every admitted production
state or complete the external3,288-game gate.

The [complete standard54 report](../evidence/influence-bitsliced-sum-standard54-20261019-01/README.md)
records216 fresh lifetimes,54 excluded warmups and162 measurements. Summed case
medians are69.809672s whole-native user+system CPU and69.380000s search CPU.
The historical Rust-PGO whole-native reference is63.431779s; the raw1.100547
ratio spans different hardware/windows and is reported only. The [complete current43 whole12 report](../evidence/influence-bitsliced-sum-games12-results-20261019-01/README.md)
records701.276947s whole-native CPU across48 lifetimes/2,528 searches. Its raw
historical reference ratio is1.088562; it is reported only. The earlier source-promotion
JSON intentionally retains its earlier cost-incomplete flags; the later
[timing state](../evidence/influence-bitsliced-sum-qualification-20261019-01/timing-state-after-standard54.json)
records standard54 closure, and the [later whole12 state](../evidence/influence-bitsliced-sum-qualification-20261019-01/timing-state-after-games12.json)
records whole12 closure. Final performance qualification remains open.

## Production responsibilities and remaining work

| Responsibility | Native owner | Evidence and remaining obligation |
| --- | --- | --- |
| Placement, chronological lists, tags/planes and transitions | `position`, `types`, `identity`, `session` | Current structural coherence review covers admitted roots and enumerated owned descendants. Broader legality, history and every ordinary-ingress clause remain separate. |
| Attack geometry, ordinary candidates and quiescence routes | `attacks`, `movegen`, `tactical`, `quiescence` | Persistent planes and finite generation checks are integrated. Candidate capacity, ordered checker identities and pseudo-candidate completeness retain their individual proof scopes. |
| Influence profiles, relations and semantic charges | `influence`, `relation_table`, evaluators |43 uses local bit-sliced wrapping accumulation with fixed transpose when sliders exist; the scalar no-slider branch remains. Arithmetic review covers the changed producer. Consumer charge/demand and complete geometric-domain obligations remain distinct. |
| Root context, full/fast retained evaluation, pawn reuse and endgame bounds | `evaluation`, `evaluator`, pawn/activity/shelter/positional/endgame modules | Complete finite component transport now passes. Source review of all formula ranges, cache collisions, ages and lifecycle composition is not inferred from those fixtures. |
| History, repetition, learned ordering and remembered results | `history`, `remembered`, `ordinary_policy` | Finite policy and collision checks pass. The conditional uncertified-hint completion gap remains unresolved; no source type, skip or fallback is invented. |
| Ordinary recursion, extensions, null/scout retries and IIO | `ordinary`, `ordinary_policy`, `engine` | Bounded IIO lifecycle and numeric reviews exist alongside current fixtures. Full admission, extension/TT/age/stop composition and natural reachability beyond controlled witnesses remain open. |
| Quiescence evaluation, pruning, reply probes and interruption | `quiescence`, `quiescence_policy`, `tactical` | Current mandatory traces pass. Full admitted-state and interrupted ownership review remains separate from finite traces. |
| Root iterations, aspiration/randomization and work scheduling | `first_iteration`, `engine`, `timed`, `timing`, `work_clock` | Current replay, root and timing fixtures pass. All production poll/capture/publication boundaries require source review at their actual owners. |
| Persistent game, seed, clock and ordinary command meaning | `session`, `clock`, `parameters`, `timing` | Current pre-gate, continuity and seed evidence pass. Admitted command-domain review and external full-game qualification remain open. |
| Input framing, queues, live records and process outcomes | `wire`, `host`, `output`, `bin/rook2` | Current strict/interruption controls pass. The bounded current framing/polling source review is accepted; directed boundary/fragment/multi-poll/late-idle runtime witnesses and the full ordinary protocol remain separate. |
| Mandatory JSON operation admission and transport | Separate `diagnostic/` crate calling native owners |117-operation finite fixture closure is current. It does not close every schema/admission combination or substitute diagnostic results for ordinary production paths. |
| Owned whole-engine work and final performance | Native synchronous process and external measurement tools | Bounded source audit supports direct wait4 accounting under the declared native profile. Same-hardware qualification, uncertainty/resource validation and external gameplay remain open; PMU is unavailable on Vic. |

The [current arithmetic review](../evidence/influence-bitsliced-sum-production-review-20261019-01/review.md)
proves the changed modulo256 accumulation and transpose, including overlap,
multiplicity and color separation; it imports existing geometric and admission
premises. The [coherent permission/descendant review](../evidence/coherent-permission-descendant-review-20261019-01/review.md)
and [owned-work review](../evidence/native-owned-work-review-20261019-01/review.md)
have a bounded [parent disposition](../evidence/production-source-audit-parent-review-20261019-01/decision.json).
Structural coherence means mailbox/list/canonical-tag/plane agreement, not a
proof of all chess legality or history. Normal Result cleanup is not an RAII
unwind guard for arbitrary user callbacks. The exact release native profile
aborts on panic and has no identified engine-owned thread/service route; its
stdlib/libc/loader/environment and finite observation limits remain explicit.

The [current framing review](../evidence/production-wire-framing-review-20261019-01/review.md)
and its [parent disposition](../evidence/production-wire-framing-parent-review-20261019-01/decision.json)
confirm current-source continuity and single-line poll ownership. Four subsequent
[directed CLI witnesses](../evidence/production-wire-directed-independent-review-20261019-01/review.md)
pass on exact43, with [parent acceptance](../evidence/production-wire-directed-parent-review-20261019-01/acceptance.json):
maximum LF/CRLF records, fragmented input, observable FIFO polls and graceful
completion followed by idle commands. Raw bytes, four normal exits and input
identities reconcile independently. These finite schedules do not establish
all protocol clauses, arbitrary interleavings or the unobservable last-poll to
move-publication arrival interval.

Earlier scalar, score-capacity, depth, IIO and ingress reviews remain linked in
the historical map, with their original source/artifact identities and limits.
The [uncertified-hint composition issue](research/uncertified-hint-completion.md)
remains a specification question without an established public reachable
witness. The new uncertainty proposal is an unadopted mathematical draft and
changes no historical result or execution authority.

Before completion, expand this map to individual normative clauses and close
each with evidence of matching scope. Final performance qualification and the
external3,288-game functional gate are still required. Intermediate fixture
passes and speedups are progress rather than mission completion.

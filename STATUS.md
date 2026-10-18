# Implementation status

## Current stage — 2026-10-18

The independent native engine serves the live King XBoard stream, including
work-timed recursive search, actual publication and one-command-per-poll input,
persistent sessions/clocks/seed controls, full/fast retained evaluation, pawn/TT/
learned state and specified root scheduling. Ordinary `Session<false>` excludes
development tracing; cold JSON is a separate adapter package. Position160/Node176
now owns exact placement attack planes while retaining copied-child ownership.
Current source implements88 mandatory diagnostic operations and passes6161
unique cases/133 adapter units plus145 native tests. Source promotion exactly
matches both tested proposal closures; frozenfed8a40a passes54 strict replays
and eight interruption fixtures, and adapter75097e2a owns the component result.
These new source/artifact observations have no own-PGO/cost/gameplay result.
The earlier85-operation Q observer restored default evaluation call scope and stack size;
its disposition extraction retains a small code difference. The original
metadata-instability failure and stable replay retry remain preserved. See
[85-operation integration](evidence/move-q-evaluation-integration-20261018/README.md).
The subsequent87-operation retained/fixed-root pawn routes change only two cold files, with
native142/strict54/eight-wire reused by exact source equality. See
[87-operation integration](evidence/retained-search-pawn-integration-20261018/README.md).
The88-operation source adds an outside observer to the actual shared Q recursion
and native evaluation stages. Its default NoTrace body retains the reviewed
call scope and recursive ABI, with32 additional local stack bytes and116 fewer
text bytes. This bounded risk is accepted without a CPU-neutrality claim. See
[88-operation integration](evidence/quiescence-tree-integration-20261018/README.md).
The matched storage experiments and independent PGO trial support this source
integration. Canonical915f83e4 passes54 strict replays, eight interruption
fixtures and its own six-case timing pilot; final qualification remains.
Compact relation tables and typed-list influence are now also integrated,
passing134 canonical native tests and the49-operation adapter regression.
The subsequent cold score/weight and endgame-bound expansions pass57
operations/2868 cases and42 adapter units against unchanged canonical native
source. Canonical8c4619a7 also passes all12 focused games/632 searches, the
eight-search continuity check and both released seed controls.
Private static-kind activity is now integrated after a separate own-PGO pilot
finds2.205812% lower summed medians(all six lower; profile29 ranges overlap).
Fresh canonical8d9dddc5 passes134 native tests, independently verified own54-case
training and54 strict production replays/eight interruption fixtures. Its
balanced60-lifetime CPU pilot independently reconciles2.052997% lower summed
medians against8c; five medians improve and profile29 is slightly higher with
overlapping samples. The unchanged57-operation adapter freshly relinks as e31263ac and passes
2868 cases/42 units. Its complete54 CPU evidence is now recorded below; current-artifact gameplay and
final cost qualification remain separate. Complete CPU/gameplay evidence below still belongs to frozen8c4619a7.
Fresh canonical8c4619a7 passes all54 strict replays and eight interruption
fixtures/24 searches. Its own complete54 CPU collection is recorded below.

A generation-local pin summary and necessary check-evasion screen now avoid
redundant full projection under explicit geometric conditions; king/EP/uncertain
cases retain projection. The independent advisor's bounded critique was
incorporated; Imp2 owns the decision. See
[decision0002](docs/decisions/0002-geometric-legality.md).
Shared immutable geometry is now also used by influence and activity. Its
10,000-position coordinate-oracle check and all54 replays pass; a separate
six-case generic CPU pilot gives a2.25% sum-of-medians reduction. See
[decision0003](docs/decisions/0003-shared-evaluation-geometry.md). A separately trained PGO comparison also improves the six-case sum by3.19%.
The previous production PGO artifact8c4619a7 owns the complete54 CPU collection
recorded below; its timing is not transferred to fresh8d9dddc5.
A reproducible generic x86-64 compiler-PGO build is available
through the staged [build procedure](tools/README.md#staged-compiler-pgo).

Current artifact-specific evidence:

- The checked-only capped king-first trial passes144 native tests,54 strict
  replays/eight-wire and a matched generic60-lifetime pilot. Its summed medians
  are1.247418% lower, with five lower case medians and four separated ranges.
  Matched exact-source own-PGO artifacts each pass54 strict replays/eight-wire;
  their60-lifetime pilot independently reconciles1.512609% lower summed medians,
  all six lower, with five separated ranges and profile29 overlapping. This
  supports adoption pending fresh composition validation against current88;
  no complete cost result follows. See
  [reply-order pilot](evidence/bounded-reply-king-first-cpu-pilot-20261018/README.md).
  The [matched PGO pilot](evidence/pgo-bounded-reply-cpu-pilot-20261018/README.md)
  keeps each artifact's profile, source and validation evidence separate.

- The Q-local material endpoint cache trial is parked. Its balanced generic
  60-lifetime pilot independently reconciles0.008663% lower summed medians,
  with three cases lower, three higher and all six sample ranges overlapping.
  The source-demand census does not establish a useful CPU gain. No cache
  variant is integrated or advanced to PGO. See
  [cache pilot](evidence/q-material-reuse-cpu-pilot-20261018/README.md).

- Canonical8d9dddc5 now independently reconciles216 full54 CPU lifetimes,
  summing81.131004s in case medians versus81.828432s previous8c:0.852305%
  lower, with41 case medians lower and13 higher. Raw uncalibrated reference
  ratio is1.279027725; maximum observed three-sample range/median is2.398788%.
  Its separate balanced six-case pilot is2.052997% lower. These finite local
  costs do not close qualification or transfer previous focused gameplay.
  See [current full54](evidence/production54-cpu-activity-specialization-20261018/README.md).

- The integrated pure kernels pass132 library+2 CLI tests. Adapterab8b7c3c
  passes36 units and2215 cases/49 operations against the exact new source.
  The own-PGO combined trialb17776fb passes54 replays/eight interruption fixtures;
  its independently reconciled90-lifetime comparison gives7.234552% lower
  summed CPU medians than915f83e4 and4.157119% lower than lookup-only1e5d075d.
  Every combined observed range is below both controls, a finite observation
  without confidence/acceptance allowance. Canonical8c4619a7 uses its own54-case
  profile7858420d, passes54 strict replays/eight interruption fixtures and
  independently reconciles216 full54 CPU lifetimes. See
  [decision0006](docs/decisions/0006-typed-influence-enumeration.md).

- The historical persistent-bitplane checkpoint passes131 native library tests and two
  development-CLI tests. Adapterbb872509 passes34 units and1968 cases/44 operations
  against that source. The isolated PGO trialf4a2f8bf passes54 strict replays and
  eight interruption fixtures/24 searches; its independently reconciled60-lifetime
  pilot sums14.805304s versus15.296771s baseline1dc996b2(ratio0.967871193).
  Canonical repository artifact915f83e4 has its own54-case training profile,
  passes54 strict replays/eight interruption fixtures and independently
  reconciles60 CPU pilot lifetimes. Its sum of six case medians is14.907624s
  versus15.388885s baseline1dc996b2(ratio0.968726714,3.127329% lower), with
  profile04 sample ranges overlapping. Its complete54 CPU collection independently
  reconciles216 lifetimes and sums88.486549s in case medians. Trial timings do
  not transfer to a different binary. See
  [decision0004](docs/decisions/0004-persistent-attack-planes.md).

- Previous PGO ordinary artifact `1dc996b2a78854f7138142eff62cbc16cbbbb051ab9f0b8d74ea0b82d6584a89`
  passes all54 strict profiling replays and all eight wire interruption fixtures
  (24 searches). Its compiler profile was trained on54 unchanged ordinary
  replays; raw process identities, source, merge and profile inputs are verified,
  archived and bound to the build. No missing-function warnings were emitted.
  See [PGO build](evidence/pgo-eval-geometry-use-build-20261018/README.md).
- The earlier generic baseline artifact
  `e734494836337f86d84fe166ae4952d192f3dc07346d482d5ecbb3a22831260c`
  passes all54 strict replays and130 native unit tests. Tests compare ordered
  inventories with full-projection admission over10,000 constructed setups;
  a separate10,000-placement check compares influence/activity fields and R
  counts with prior coordinate loops. The newer PGO binary owns its interruption
  evidence separately.
- Earlier frozen artifact
  `da82041f29091ed8db54f2cd2ffd0c338da5ae5216cae3caea6130974573e648`
  passes all12 focused games/632 searches, combined with its same-artifact
  continuity control. The released collector reports complete focused replay,
  with full gameplay qualification false. See
  [focused replay](evidence/focused-games-20261018-first/README.md).
  This older observation is not transferred. Canonical8c4619a7 now owns a
  fresh complete12/632 focused replay, eight-search continuity check and both
  released seed controls. All13 focused/continuous native lifetimes exit
  normally; the released collector reports completeFocusedReplay=true and
  completeGameplayQualification=false. See [current focused replay](evidence/focused-eval-kernels-20261018/README.md).
- The separate external DIAG adapterf8e0b7b0 implements57 operations and passes2868
  cases across47 complete fixture files plus25 unchanged selected cases
  from two partially supported files. All42 adapter unit tests pass. The first
  expanded attempt and its12 unsupported ordering failures remain retained;
  prior attempts and their source links remain preserved. Other mandatory operations
  remain explicitly unsupported. See [diagnostic scope](diagnostic/README.md).
- A balanced four-anchor pilot selected the generation-summary/evasion
  algorithm: all80 lifetimes passed the strict oracle, and the sum of four
  case medians was12.3% lower than its baseline. A separate40-lifetime
  generic/PGO pilot on identical native source found an additional6.5% lower
  sum of medians. All samples, placement and accounting boundaries are retained
  in [generation pilot](evidence/generation-cpu-pilot-20261018/README.md) and
  [PGO pilot](evidence/pgo-cpu-pilot-20261018/README.md). These are local pilots,
  not complete performance collections or qualified cross-host ratios.
- Current8d9dddc5 passes the strict profile-01 oracle under Callgrind and
  independently reconciles11,603,840,314 simulated instructions,3.520946% fewer
  than previous8c. Source-row attribution includes inlining and supplies no
  PMU instructions/cycles or native CPU claim.
  [Current profile evidence](evidence/callgrind-activity-specialization-20261018/README.md).

A complete canonical8c4619a7 local54 CPU collection retains216 normal,
strict-oracle lifetimes(one excluded warmup and three measured per case).
All raw receipts reconcile independently; the sum of case medians is81.828432s.
The published reference sum is63.431779s(raw uncalibrated ratio1.290023).
The previous915f83e4 collection summed88.486549s; all54 new case medians are
lower, with a7.524440% lower aggregate. The earlier3660 collection summed
97.685122s. These sequential historical observations are separate from matched
attribution pilots. The maximum observed three-sample range/median is1.751798%;
it is not a confidence or acceptance interval. No qualified performance
pass/fail follows. See [canonical whole-native54 collection](evidence/production54-cpu-eval-kernels-20261018/README.md).

A complete12 whole-native CPU collection on artifact1dc996b2 has completed
48 fresh lifetimes/2528 searches with independent original-byte, normal-exit and
input/artifact reconciliation. Its sum of12 game CPU medians is941.928787s;
the raw uncalibrated reference planning ratio is1.462116. Four
recorder controls, fixed5s forced-cleanup reconciliation and a balanced complete-
game observer pilot passed first; observed CPU median overhead was0.15% within
overlapping ranges. The collection remains reported-only: guest helper/lead
affinity was not uniformly constrained, and interference cost is unquantified.
After actual termination, all57 verified own lead/client threads were restricted
to housekeeping CPUs; this does not retroactively qualify existing samples. See
[game collection](evidence/production12-cpu-20261018-pgo/README.md).

Mandatory diagnostics, production review, the full3288-game gate, current-artifact
full12 CPU costs and final performance qualification remain open. The [production map](docs/production-map.md) is an initial ownership map,
not a completed normative audit. The last retained disabled PMU self-open returned EACCES with
UID1000/zero effective capabilities/paranoid3/seccomp0; no security setting was
changed. Clock sampling was unreliable and its percentages are unused.
Calibration and final measurement/uncertainty conditions remain open, alongside
substantial independent engine work. See
[qualification gaps](docs/qualification-gaps.md).

Next: use measured remaining pipeline costs to select further computational
reuse/representation experiments, expand mandatory external diagnostics and
production review, and complete artifact-specific gameplay/performance evidence.
The isolated private activity-width trial passes134 native tests, a10,000-
position coordinate-oracle comparison and both generic artifacts'54 replays.
Its independently reconciled60-lifetime pilot is0.261914% lower in summed
medians, with all six ranges overlapping and three increased medians. It is
parked; no source adoption or PGO benefit is inferred.
The isolated static-kind activity trial passes134 native tests,10,000 coordinate
oracle placements and54 strict replays on genericc946104a. Its independently
reconciled60-lifetime pilot is2.707839% lower in summed medians, with all six
medians lower and four disjoint observed ranges(profile02/29 overlap). Its own
PGO and canonical results are complete above; see decision0007.
Earlier partial timings below are historical development checkpoints.

The isolated compact relation kernel now passes133 native tests and all54
replays. Its own-PGO1e5d075d also passes54 replays/eight interruption fixtures
and independently reconciles60 CPU lifetimes:3.484682% lower summed medians
than canonical915f83e4, with profile02/29 ranges overlapping. The exact combined source is integrated
under
[decision0005](docs/decisions/0005-compact-relation-kernel.md).
A separate typed-list influence prototype passes134 tests and54 replays/eight
interruption fixtures; its60-lifetime generic pilot is4.756478% lower in summed
medians, with all six observed ranges disjoint. A combined source passes134
tests and its own PGO buildb17776fb passes54 replays/eight interruption fixtures.
The complete90-lifetime comparison finds7.234552% lower summed medians than915f
and4.157119% lower than lookup-only, with all six combined ranges below both.
Exact combined source is now integrated and passes134 canonical native tests
plus36 adapter units/2215 cases. Fresh canonical8c4619a7 uses its own54-case
profile7858420d, passes all54 strict replays/eight interruption fixtures and
independently reconciles its own216-lifetime54 CPU collection. No trial timing
transfers to this artifact or completes qualification.

## Runtime policy

Lead and implementation subagents use Normal speed under the owner's latest
`/fast off`. The gate verified the lead's Normal footer. The three original native
implementation subagents are completed and remain stopped; their runtime tiers
have no exposed read/set control, so no conversion is claimed and no child is
resumed without a route that can verify Normal. One new Sol6.1 High subagent
completed a bounded cold score-range review; its Normal request had no exposed
speed readback, so actual runtime speed was reported as unknown. No native
subagent remains running. The operational gate target is absent in the current
Herdr instance, and the current pane has no centrally assigned name; no new
live-agent prompt is sent under an inferred identity. A quota reset does not change
the engine objective. The guiding mission remains `/home/legolas/imp-perf-mission.md`.

## Earlier native/development checkpoints

These observations retain their original source/artifact scopes; they are not
newer-artifact DIAG, gameplay or performance qualification.

Current evidence:

- 122 library tests and two CLI tests pass, including start depth4 legal trees,
  influence exhaustiveness, chronology, retained identities/TT, full/fast
  restoration, bounded reply probes, quiescence stopping and terminal returns.
- 884 external native policy cases pass, including11,136 selective-depth
  queries, full candidate-order observations, material threats, move extensions
  and learned-memory sequences. Expected data lives only in an external test
  crate. This does not qualify DIAG validation or complete search. See
  [policy check scope](evidence/ordinary-policy-check-20261017-final/README.md).
- 1,352 external native evaluation/root cases pass, with201,374 evaluator
  queries. Every observed root field matches for ten first iterations, six
  neutral ordinary searches and three selected-personality searches, including
  windows, move kinds, score-ranked carryover, PV and cumulative N/R work.
  These are native computation checks, not full diagnostic transport or
  completed gameplay qualification. See
  [evaluation check scope](evidence/evaluation-check-20261017-roots/README.md).
- 70 external native clock/timing/search cases pass: ledger/reset boundaries,
  adaptive limits, terminal iteration decisions, 22,530 root random/aspiration
  queries and six actual timed-search traces. The latter compare every native
  root step, time check, interruption and retained capture; public events are
  outside that check. All 1,352 evaluator/root regression cases pass on the
  same frozen timed source. See
  [timing scope](evidence/timing-check-20261017-frozen/README.md).
- The newer 193-case native session/output check passes with release optimization
  settings. It adds parameter/clock commands, exact schedule allocation, King
  notation, full timed-search event trails, four fresh joined projections,
  persistent clock-seeded sessions and every snapshot/root step of the
  three-search inherited-settings sequence. All 1,352 evaluator/root cases also
  pass with the same release test settings. Test harnesses unwind panics;
  production abort remains separately recorded. See
  [session/output scope](evidence/session-output-check-20261017-frozen/README.md).
- 12,621 external inspections passed selected released expected projections
  across two separate schedules. The first schedule's 285 unsupported source
  cases and all omitted fields remain explicit. The added 8,727 inspections
  cover fresh pawn, shelter and activity terms, not retained search parity.
- Three frozen partial-search cases have CPU/wall baselines on CPU14 with
  one excluded warmup and three measured fresh processes each. Each process
  performs eight identical completed searches; all repeated outputs agree.
  See [baseline results](evidence/development-baseline-v1/results.json).
- A second frozen baseline exercises the composed evaluator/quiescence mix,
  including pawn hits/replacements and reused replies. Diagnostics on/off
  preserve score, PV and charged work. Three cases, 20,000 fresh preparations
  per process, one excluded warmup and three measured processes each: CPU
  medians with diagnostics on are 0.097003/0.117309/0.353494 seconds. Guest
  CPU15 recorded only idle time during this collection. See
  [quiescence evidence](evidence/quiescence-v1/README.md). Missing evaluation
  terms still affect scores and one of ten explored fixture trees.
- The first root iteration reproduces all ten explored fixture candidate
  sequences. Independent consumption checks and diagnostics on/off agree;
  all ten earlier quiescence outputs remain unchanged after the sequence API
  refactor. Missing evaluation changes several root choices, so these are
  explicit development observations. A separate measured first-root corpus
  records 5,000 complete preparations/iterations per process, with diagnostics
  off CPU medians0.128500/0.349432/0.413148 seconds. See
  [first-root evidence](evidence/first-iteration-v1/README.md).
- The frozen ordinary pipeline now measures full/fast/pawn/TT traffic together.
  Four workloads exercise4189/5588/1484/50766 charged visits; the last uses a
  deliberately tiny TT to stress collisions and internal ordering. All repeated
  results agree, and diagnostics on/off preserve every iteration's score, PV,
  order and work. CPU15 recorded three non-idle ticks during collection, retained
  as interference evidence. See [ordinary evidence](evidence/ordinary-v1/README.md).
- The newer composed-evaluation baseline matches four released fixed-root
  expectations, including all emitted windows/ranking/PVs/work with diagnostics
  on and iteration/final parity with diagnostics off. Eight schedules each use
  one excluded warmup and three measured fresh processes. CPU medians off are
  0.418455/0.837676/0.416842/0.287501 seconds for512/256/256/128 searches.
  CPU15 recorded one user tick during collection. See
  [current baseline](evidence/neutral-evaluation-v2/README.md).
- The work-timed native path has separate CPU14 measurements for seed 0 poll
  interruption and seed 2147483648 completed-root stopping. With 128 searches
  per fresh process, diagnostics-off CPU medians are 0.890844/0.908052 seconds.
  Repetitions and diagnostic modes preserve selected captures and total work.
  CLI md99 differs from the fixture's md20; measured output projections agree,
  while the native checker binds the complete vectors. CPU15 recorded two user
  ticks. See [timed baseline](evidence/work-timed-v1/README.md).
- Instructions/cycles remain unavailable to the unprivileged account; a request
  for a scoped observer has been sent to the owner through the conversation.

## Milestones

1. Record normative architectural constraints, candidate representations and
   measurement limitations. Produce a coherent initial design and obtain the
   requested independent critique.
2. Implement a compact position/move kernel and integrated deterministic search
   with a declared fidelity subset. Establish reproducible instruction/CPU cost
   observations and legal/state sanity checks before broad conformance work.
3. Integrate the actual evaluator, candidate/search policies and work clock in
   progressively larger vertical slices. Track semantic differences explicitly;
   compare performance only within compatible work/fidelity boundaries.
4. Expand the thin external diagnostic adapter and exact conformance, persistent
   ordinary wire behavior, focused gameplay/continuous switching and profiling.
5. Complete production mapping/review, full gameplay gate and performance
   qualification under a fixed validated measurement/uncertainty procedure.

Competitive prototype performance does not establish final performance. Passing
component diagnostics does not establish production or gameplay conformance.

## Fixed starting references

- Mission SHA256: `74b8793052d559de9258f522f62afe2e89b271ac599dd5f48fe136ccd861067b`.
- Spec checkout HEAD: `1c89c21a4645ec85adf28285616d822b3cd91f73`.
- Spec source version: `v2.5.0`; upstream package commit
  `80550dd37d09293f179abd0e0c7ec06390dcfbbb`.
- Spec manifest SHA256:
  `b8ce317fa5577c28bc35f0cbadad61cd984bdd4824c59f2c37d4ebef55335e0d`.

These identify the starting inputs, not a claim of a completed package audit.
Updates must preserve which version supported each experiment or decision.

The diagnostics-only full-evaluation opportunity probe matches all54 replays:
18,569 of37,094,821 full calls enter at retained age0 (0.050058%, including
first-root calls). The proposed same-produced-node component cache was rejected
as the next target; no cache was implemented. Pure material/phase input reuse
passes all54 replays; its six-case generic CPU pilot gives0.75% lower summed
medians with overlapping samples, so it remains experimental. Direct
king-coordinate metadata also passes132 native tests and all54 replays, but
its six-case pilot is effectively flat (0.12% lower summed medians); production
adoption is rejected. Both frozen experiments and all attempted samples are
retained; production native source remains unchanged by them.


The fourteen added native-backed diagnostic routes (placement terms, ordered pawn
progress/endings, work ledger, cutoff learning, retained results and supplied
candidate/priority/capture ordering) now pass25 units/1214 cases in frozenfab90bb7.
The first1022-case attempt passed1010 and exposed12 missing candidate-order
transport calls; it remains preserved with its original source/build/report.
The identical frontend also passes against the integrated persistent source.
The subsequent native-backed policy expansion0f8c7226 passes29 units/1262 cases
across33 operations, adding root randomization/aspiration, quiescence capture
policy and PV line boundaries. See
[deferred verification](evidence/diagnostic-placement-preparation-20261018/README.md).

Both matched bitplane variants pass133 native tests and54 strict replays. Their
complete90-lifetime generic pilot favors persistent Position160/Node176 by2.13%
in summed case medians, while this local Position128/Node144 strategy is0.48%
higher. The independent raw reconciliation and all samples are retained in
[matched trial](evidence/bitplanes-20261018/README.md). Persistent advances to a
separate PGO training/build/regression and pilot, which finds3.21% lower summed
medians across60 lifetimes. Persistent source is integrated; its canonical root
PGO artifact915f83e4 also passes54 replays/eight interruption fixtures and its
own60-lifetime pilot(3.13% lower summed medians; one case's ranges overlap).
No trial result is transferred to final
54/12 performance qualification.

The next cold diagnostic expansion adds material-threat production and composed
fast-threat work without changing native production source. Frozenef406db7
passes49 adapter units and3236 unique cases across59 operations, including
49 complete fixture files plus the unchanged25 selected cases. Full mandatory
transport remains incomplete. No prototype performance result transfers here.

An isolated destination-table generation prototype125d7446 preserves runtime
piece-kind dispatch and changes only non-pawn pseudo-destination traversal.
It passes134 native tests, including independent prior coordinate/full-projection
full and capped ordered comparisons, and54 strict replays. Generic control
c946104a is the identical already-validated activity-specialized artifact; its
prior54 replay is explicitly reused. The prototype is not adopted and has no
performance claim before its balanced pilot.

The destination-table pilot now reconciles60 native lifetimes and gives only
0.231190% lower summed medians, with all six observed ranges overlapping and
profile05 higher. It is parked without PGO/adoption. Canonical8d9dddc5 remains
the current production cost checkpoint.

The isolated shared evaluation observers now pass134 native tests,64 diagnostic
operations/3470 cases/58 units,54 strict generic replays and eight interruption
fixtures. Its only native changes extract existing material/square interpolation
and expose existing raw shelter components. Generic2c741929 and adapter1f5a0ceb
retain separate source/build identities. The first external attempt failed a
missing fixture version header before external execution; the corrected fresh
attempt and original failure are both retained. The subsequent79-route source integration is recorded below; these isolated
observations carry no new performance result.

The earlier79-operation observer integration passed with fresh canonical adapter
a9f6e9f6 passes4521 unique cases/86 units across73 whole released files after
135 canonical native tests. Isolated1bce8aea passes54 strict replays/eight wire
fixtures; fresh canonical generic9709f8e9 also passes54 strict replays/eight wire fixtures.
Score-context, fresh/retained pawn and phase/subtotal routes share native owners.
Retained cache construction uses a static miss-only builder, preserving cache-hit
suppression; no state/layout was added. Remaining mandatory inventory is38
operations/3152 cases at that checkpoint; final own-PGO/cost/gameplay evidence stays separate.

The separate profile_sum lookup prototype passes134 native tests, the exhaustive
normalized-byte digit model, a strengthened10000-coordinate oracle,54 strict
replays and eight interruption fixtures. Its generic balanced60-lifetime pilot
independently reconciles1.109747% lower summed CPU medians (five lower, one
higher; all six ranges overlap). Own54-case training and strict54/eight-wire regression pass on
f3562ff6. Its matched60-lifetime PGO pilot independently reconciles13.424908s
baseline8d9dddc5 versus13.4303025s lookup,0.040183% higher; four medians
decrease, two increase, and all six ranges overlap. It is parked without
adoption or broader cost runs. The independent pressure-value table passes135 native tests,10000
coordinate placements and54/eight-wire regression, but its60-lifetime generic
pilot is0.311677% higher with all six ranges overlapping; it is parked without
PGO or integration.

The detailed forced-fresh and retained full/fast source is now integrated as82
operations/4721 unique cases across76 whole files, with139 native and99 adapter
tests passed. Frozen ordinary c6839096 passes54 strict replays/eight interruption
fixtures. Both native/frontend source closures exactly match those tested
artifacts; no canonical-path rebuild is implied. Default full_impl and
visit_ordinary are byte-identical to frozen79 generic; visit_q differs only in
three table-base operands whose decoded target windows match. Other artifacts,
data layout and PGO are outside that static result. Current mandatory remainder
is35 operations/2952 cases. The new routes share actual native finishing,
fresh/nonfresh selection, retained state and per-call relation work.

The frozen79 diagnostic census passes54 unchanged strict replays and independent
counter reconciliation. It finds32,274,602 repeated material endpoint source
demands (19.7298% of search-segment demand), primarily in Q. A Q-only local
lazy endpoint trial is selected for investigation; no persistent state or CPU
benefit is selected from the counts. See its separate RESULTS.md.

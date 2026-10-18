# Implementation status

## Current stage — 2026-10-18

The independent native engine serves the live King XBoard stream, including
work-timed recursive search, actual publication and one-command-per-poll input,
persistent sessions/clocks/seed controls, full/fast retained evaluation, pawn/TT/
learned state and specified root scheduling. Ordinary `Session<false>` excludes
development tracing; cold JSON is a separate adapter package. Position/Node
layout and copied-child ownership remain the provisional architecture.

A generation-local pin summary and necessary check-evasion screen now avoid
redundant full projection under explicit geometric conditions; king/EP/uncertain
cases retain projection. The independent advisor's bounded critique was
incorporated; Imp2 owns the decision. See
[decision0002](docs/decisions/0002-geometric-legality.md).
Shared immutable geometry is now also used by influence and activity. Its
10,000-position coordinate-oracle check and all54 replays pass; a separate
six-case generic CPU pilot gives a2.25% sum-of-medians reduction. See
[decision0003](docs/decisions/0003-shared-evaluation-geometry.md). A separately trained PGO comparison also improves the six-case sum by3.19%.
The latest production PGO artifact1dc996b2 passes all54 strict replays and eight
interruption fixtures; the complete54 CPU collection below remains attached to
the prior3660 artifact. A reproducible generic x86-64 compiler-PGO build is available
through the staged [build procedure](tools/README.md#staged-compiler-pgo).

Current artifact-specific evidence:

- Latest PGO ordinary artifact `1dc996b2a78854f7138142eff62cbc16cbbbb051ab9f0b8d74ea0b82d6584a89`
  passes all54 strict profiling replays and all eight wire interruption fixtures
  (24 searches). Its compiler profile was trained on54 unchanged ordinary
  replays; raw process identities, source, merge and profile inputs are verified,
  archived and bound to the build. No missing-function warnings were emitted.
  See [PGO build](evidence/pgo-eval-geometry-use-build-20261018/README.md).
- The same native source's generic artifact
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
  This observation is not transferred to the newer artifacts.
- The separate external DIAG adapter c4cd8566 implements27 operations and passes1130
  cases across22 complete fixture files plus25 unchanged selected cases
  from two partially supported files. All23 adapter unit tests pass. The first
  expanded attempt and its12 unsupported ordering failures remain retained;
  native production source is unchanged. Other mandatory operations
  remain explicitly unsupported. See [diagnostic scope](diagnostic/README.md).
- A balanced four-anchor pilot selected the generation-summary/evasion
  algorithm: all80 lifetimes passed the strict oracle, and the sum of four
  case medians was12.3% lower than its baseline. A separate40-lifetime
  generic/PGO pilot on identical native source found an additional6.5% lower
  sum of medians. All samples, placement and accounting boundaries are retained
  in [generation pilot](evidence/generation-cpu-pilot-20261018/README.md) and
  [PGO pilot](evidence/pgo-cpu-pilot-20261018/README.md). These are local pilots,
  not complete performance collections or qualified cross-host ratios.
- The optimized profile-01 Callgrind run passed the strict oracle and reports
  13,607,144,696 simulated instructions. PGO changes inlining/attribution, so
  source-line evidence is retained. Activity/influence remain prominent rows.
  This is a simulated diagnostic, with no PMU instructions/cycles claim.
  [Profile evidence](evidence/callgrind-pgo-20261018/README.md).

A complete local54 CPU collection now retains216 normal, strict-oracle lifetimes
(one excluded warmup and three measured per case). Its sum of case medians is
97.685122s, with all raw receipts independently revalidated. The raw published
reference sum is63.431779s (uncalibrated planning ratio1.5400); this is not a
qualified performance pass/fail. See
[whole-native54 collection](evidence/production54-cpu-20261018-pgo/README.md).

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

Mandatory diagnostics, production review, the full3288-game gate, the newer
artifact's full focused replay and final performance qualification remain open. The [production map](docs/production-map.md) is an initial ownership map,
not a completed normative audit. The last retained disabled PMU self-open returned EACCES with
UID1000/zero effective capabilities/paranoid3/seccomp0; no security setting was
changed. Clock sampling was unreliable and its percentages are unused.
Calibration and final measurement/uncertainty conditions remain open, alongside
substantial independent engine work. See
[qualification gaps](docs/qualification-gaps.md).

Next: use measured remaining pipeline costs to select further computational
reuse/representation experiments, expand mandatory external diagnostics and
production review, and complete artifact-specific gameplay/performance evidence.
Earlier partial timings below are historical development checkpoints.

## Runtime policy

Lead and implementation subagents use Normal speed under the owner's latest
`/fast off`. The gate verified the lead's Normal footer. All three native
implementation subagents are completed and remain stopped; their runtime tiers
have no exposed read/set control, so no conversion is claimed and no child is
resumed without a route that can verify Normal. A quota reset does not change
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


The twelve added native-backed diagnostic routes (placement terms, ordered pawn
progress/endings, work ledger, cutoff learning, retained results and supplied
candidate order) now pass the23-unit/1130-case regression in frozen c4cd8566.
The first1022-case attempt passed1010 and exposed12 missing candidate-order
transport calls; it remains preserved with its original source/build/report.
Native production source is unchanged. See
[deferred verification](evidence/diagnostic-placement-preparation-20261018/README.md).

Both matched bitplane variants pass133 native tests and54 strict replays. Their
complete90-lifetime generic pilot favors persistent Position160/Node176 by2.13%
in summed case medians, while this local Position128/Node144 strategy is0.48%
higher. The independent raw reconciliation and all samples are retained in
[matched trial](evidence/bitplanes-20261018/README.md). Persistent advances to a
separate PGO training/build/regression and pilot; production keeps its current
layout pending that evidence. No generic result is transferred to PGO or final
54/12 performance qualification.

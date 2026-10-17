# Implementation status

## Current stage

Initial architecture critically reviewed by `imp2-lead`; Imp2 selected the
provisional baseline and recorded [decision0001](docs/decisions/0001-initial-architecture.md).
The compact position/move kernel, material/square terms, influence, activity,
shelter, remembered-result table and pawn structural/piece terms are implemented.
Concrete quiescence now composes full/fast retained evaluation, shared pawn
retention, history admission, tactical ranking, capture estimates, geometric
safety and recursive PV consumption. The composed evaluator remains partial;
ordinary search, TT integration and timing are not connected to this slice.
The earlier generic alpha-beta development baseline stays separately frozen.
No conformance or performance qualification is claimed.

Current evidence:

- 98 library tests and two CLI tests pass, including start depth4 legal trees,
  influence exhaustiveness, chronology, retained identities/TT, full/fast
  restoration, bounded reply probes, quiescence stopping and terminal returns.
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
- Instructions/cycles remain unavailable to the unprivileged account; a request
  for a scoped observer has been sent to the owner through the conversation.

Next: connect ordinary recursive search and remembered results, then extend
the evaluator and work-clock consumers. Do not choose a production position
representation until full/fast/pawn/TT traffic is measured together. The present
quiescence measurements add evidence but do not complete that experiment.

Latest owner update: `/fast off`; normal speed for lead and subagents. This
supersedes the temporary fast-subagent request and restores the goal's original
speed policy. The collaboration tool cannot select or verify service speed.
All three implementation subagents are completed and remain stopped. The gate
verified this lead's Normal footer. Child runtime tiers have no exposed read/set
control and their saved metadata does not establish a tier; no conversion is
claimed. Continue on the verified Normal lead until a delegation route can
verify Normal. The operational-only status was relayed to Vic's system agent;
cleanroom-gate is not registered locally and Bee SSH host-key verification
failed without bypass. A usage quota reset does not alter the engine objective.

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

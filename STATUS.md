# Implementation status

## Current stage

Initial architecture critically reviewed by `imp2-lead`; Imp2 selected the
provisional baseline and recorded [decision0001](docs/decisions/0001-initial-architecture.md).
The compact position/move kernel, material/square terms, influence, activity,
shelter, remembered-result table and pawn structural cache are implemented.
The development executable runs a declared partial search with material/square,
influence/activity and tempo. Shelter/pawn/TT are tested components awaiting
search composition. No conformance or performance qualification is claimed.

Current evidence:

- 59 native tests pass, including legal-tree counts through start depth4,
  normalized-influence exhaustiveness, chronology, retained identities and TT.
- 3,894 external inspections passed selected released expected projections;
  285 unsupported source cases and all omitted fields are explicit.
- Three frozen partial-search cases have CPU/wall baselines on CPU14 with
  one excluded warmup and three measured fresh processes each. Each process
  performs eight identical completed searches; all repeated outputs agree.
  See [baseline results](evidence/development-baseline-v1/results.json).
- Instructions/cycles remain unavailable to the unprivileged account; a request
  for a scoped observer has been sent to the owner through the conversation.

Next: finish current pawn terms and tactical generation/ordering; compose real
full/fast retained evaluation and quiescence with explicit omissions, then
revisit architecture costs. Do not choose a production representation from the
first partial-search baseline. Extend focused checks for newly integrated terms.

Owner update: implementation subagents should use fast speed (lead remains
normal). This supersedes the original goal's normal-subagent-speed clause.
The current collaboration tool cannot select or verify subagent service speed.
A mentioned impending reset is a usage quota reset; work continues normally.

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

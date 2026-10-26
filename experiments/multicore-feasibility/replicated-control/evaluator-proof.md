# Replicated actual-search evaluator: source proof and audit boundary

This extraction uses the positive epoch64 source copied to
`/home/legolas/rook2-experiments/workspaces/replicated-control-20261026-01`.
It does not derive from the parked type-disjoint-four variant. New lane and
audit storage/APIs/branches/tests are gated by `replicated-control`. Shared
native numerical bodies are extracted for use by both the unchanged inline /
packet execution routes and the new collective route. Matched native controls
must price any resulting layout/code-generation cost.

## Per-FULL simulation

Every replica independently reaches its actual FULL call with its own Position,
Influence, node retention, root context, N/R and private search state. No future
position, Influence, continuation or finished score is dispatched by the owner.
Root preparation calls the same FULL entry and therefore participates.

`full_pawn_inputs` is the one original FRESH/ordinary pawn selection and current
pawn-term body. `full_owner_components` is the one original structure/progress,
central influence, fixed patterns and square-balance body. The owner contribution
contains those components with Activity, Shelter and tempo zero, plus exact pawn
relation charges and the actual cache-reuse outcome.

Only role 0 invokes these producers in collective execution. Roles 1 and 2 call
the original `activity::compute_side` with White/Black attackers, respectively,
then the original opposite-defender `shelter::compute_side` using the produced
pressure. Follower PawnCaches remain allocated and may be cleared by the shared
search-start path, but collective FULL never consults or populates them. The
owner preserves the original cleared zero identity, replacement, collision,
retained chronology and FRESH-bypass rules. Cache equality is a cold direct
comparison delegated to `PawnCache::replica_eq`, not an additional cache lookup.

One `ReplicaLane::exchange` returns scalar copies of the complete three-part
gather. Each lane locally calls original `activity::combine_sides` and
`shelter::combine_sides`, mapping the black attacker's shelter term to White and
the white attacker's term to Black. Thus all original cross-color weight rounds
remain in the original kernels. There is no final-score broadcast.

`finish_full_components` is shared by native inline/packet and collective FULL.
It contains the original tempo round/sign, component insertion, retained
positional/progress reset and age zero, diagnostic FULL/cache statistics, exact
`pawn R + Activity R`, component observation and the single native final-score /
bound calculation. No N or R is summed across replicas. Each lane publishes the
same serial-equivalent logical contribution into its own ledger and follows its
own deterministic continuation. FAST remains the original local path.

Native FULL keeps its order: phase/material; packet dispatch if selected; pawn
selection/current terms; original inline chain if selected; local scalar terms;
actual packet join; shared finishing. Attached replica lanes reject configuring
existing FULL workers, second attachment or child preparation. Detached public
evaluator calls and normal 1/2/3 worker routes retain their numerical semantics.

## Exact bounded audit, separate from performance

`replica_audit_record` enables an independent serial recorder with a fixed 32768
FULL-event cap. `replica_audit_take` removes and returns its `Vec<FullAudit>`.
Each replica's `replica_audit_compare` receives the same immutable
`Arc<Vec<FullAudit>>`; its cursor belongs only to that lane. Inputs are compared
before producing/publishing a contribution, and complete output records are
compared after the shared native finishing call. Every comparison uses structured
equality, not a fingerprint. Root signatures are Arc-interned exact values;
Arc equality compares the underlying signature, not merely pointer identity.

Each input contains the complete actual Position, authoritative supplied
Influence, retained state before FULL, checked/FRESH flags, current logical N and
EvalStats (including current R). Its exact root signature contains root side,
phase, counts, material values, all square arrays, root average depth, all five
effective weight pairs, the current own/opponent parameter arrays, parameter
average depth/draw/selectivity, active draw preference and variation range.
Each output contains actual Evaluation, FullDetails (components/base/native
finished result/cache-reuse), retained state after FULL, EvalStats and logical N.

`engine::charge_node` updates audit N from the already charged `stats.nodes`
only while the audit is enabled. `begin_search` establishes root N zero; the
parent-owned `quiescence::begin_owned_sequence` hook resets audit N with the
existing work-segment stats reset. Root preparation work and post-reset work are
therefore distinguished without per-node journals, snapshots or extra charges.

The audit option is None in performance lives. That route allocates no trace,
constructs no audit signatures/events, reads no expected future FULLs and performs
no trace comparisons. The parent runner separately selects the bounded depth2
35/08/43 audit lives, then independent depth8 performance lives. This source
does not claim ordinary timed/protocol or complete gameplay qualification.

Unexpected/missing inputs, output mismatches or cap exhaustion cancel an attached
collective and panic; no dummy evaluation is returned. Incomplete comparison
finish returns an error and cancels. The infallible FULL collective-error branch
also cancels and panics. Both study libraries/drivers require panic=unwind and
actual runner boundaries must catch, cancel and join every started thread; the
collective constructor and evaluator attachment assert/reject other panic modes.
The collective ownership/retirement proof and outer startup/supervision/final
TT/learning/PV/work comparisons are separate parent/collective-owner work.

`replica_finish` calls the collective finish exactly once; the runner then drops
the evaluator. `replica_detach` is an alternative that finishes then removes the
lane, not an operation to call after `replica_finish`.

## Added focused source controls

Five tests in `evaluator/replica_tests.rs` cover:

- Exact serial-vs-three-lane FULL audit across two differently colored root
  bindings, asymmetric parameters, supplied contrary Influence, check, retained
  inputs, zero identity/group replacement, real full-identity collisions, FRESH
  bypass and resets; owner cache equals serial and follower caches stay empty.
- Actual seeded Search at depth1 and depth2 on the fixed initial/ending test
  positions, root FULL participation, work reset/N context, every root raw return,
  candidates/steps/PV, final work/statistics and owner cache versus independent
  serial execution. TT geometry remains equal and unsplit.
- Input mismatch cancellation before any collective publication.
- Output mismatch, incomplete trace and over-cap trace rejection.
- Nested FULL-worker/second-lane rejection.

Test thread bodies catch unwind, cancel failures and join every actual thread.
No builds, tests or engine runs were performed by this source owner. These are
source controls awaiting native admission, not reported passing evidence.

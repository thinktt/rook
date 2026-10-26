# Deterministic multicore research outcome

2026-10-24. Assessment by imp2-lead under the
[research mission](../deterministic-multicore-mission.md).

This is the historical two-thread checkpoint. The later
[three-thread own-PGO result](../../experiments/multicore-feasibility/epoch-own-pgo/report.md)
demonstrates further acceleration; its broader behavioral qualification remains
separate. The assessment and tables below retain their 2026-10-24 scope.

**Retain the practical, opt-in two-thread FULL evaluation split.** It reduced
search elapsed time by 6.79% against the accepted serial engine across the
54-case survey, consuming 1.863 times the total CPU. Its one-thread mode cost
1.12% in the same comparison. The selected local behavioral checks passed.
This is a useful implementation candidate, with evidence for two threads and
no demonstrated profitable scaling beyond two.

The research branch contains the implementation. This recommendation does not
merge it into main, replace the accepted Rook version 1 artifacts, update the
release manifest, or transfer their external qualification to the new binary.

## What works and why

The coordinator preserves King's search order and all authoritative state. At
an actual FULL evaluation demand, it sends an owned packet to one persistent
helper. The packet contains the exact position and supplied influence map,
root material and correctly bound evaluation weights. The helper computes the
pure Activity-to-Shelter chain; the coordinator performs the pawn/cache and
other local work. It joins before combining the score, updating retained state,
publishing relation counts or invoking the corresponding observation callbacks.
Both modes use the same numerical computation.

This gains concurrency inside a demanded calculation. It does not search later
branches early, change pruning, copy or merge the transposition table, reorder
pawn-cache accesses, or let the helper poll the host. Those distinctions explain
why this modest split succeeded where larger speculative work units struggled.

The practical version parks between owned search scopes, uses predicate-based
completion/lifecycle waits, joins on shutdown, and has no engine-imposed
ten-second wall-clock failure. It inherits affinity instead of pinning a helper
to a particular CPU. Errors remain explicit. Active-search spinning still has a
CPU cost, including when the coordinator is blocked in a host callback.

## Measured result

The [configured FULL report](../../experiments/multicore-feasibility/configured-full/report.md)
binds source, artifacts, profile, setup, raw audits and all 54 rows.

| Same-window configuration | Search elapsed | Whole-process CPU |
| --- | ---: | ---: |
| Accepted serial, `5cf01208` | 69.056196 s | 69.137609 s |
| Previous two-thread prototype, `a977bb00` | 64.270245 s | 128.593350 s |
| Practical candidate, one thread | 69.831350 s | 69.912544 s |
| Practical candidate, two threads | 64.369022 s | 128.778462 s |

The practical helper saves 7.82% relative to its own inline mode and 6.79%
relative to accepted serial. Practical cleanup costs a descriptive 0.15%
against the earlier two-thread image. Maximum observed RSS is 68,960 KiB versus
68,676 KiB for accepted serial. Short idle probes registered zero CPU ticks at
10 ms resolution; that is not literally zero idle cost.

There are gains in 46 of 54 cases. Eight losses total 0.233468 s; case 43 accounts
for 0.121712 s and also loses in the repeated small comparison. The worst
relative loss is 6.72% on case 15. Neither universal improvement nor a simple
short-search bypass follows from these results.

The full survey has one observation per case/configuration. The preceding
four-case repeated comparison supports a useful gain but does not supply
per-case uncertainty for the whole survey. Training and comparisons total
388 replay lives and 4,608 posts, with one own-profile merge and no engine retry.
These are Vic measurements under recorded guest placement, not exclusive-host
or final performance qualification. Historical KingWCR and KingRE totals belong
to other windows and endpoints: **we have not demonstrated beating KingWCR.**

## Fit to the vision

| Desired behavior | Demonstrated implementation and limit |
| --- | --- |
| One binary with optional parallelism | Default 1 and explicit `--threads=N`; no helper in mode 1. |
| Near-original serial performance | 1.12% additional elapsed time in this survey; not a universal bound. |
| Configurable total thread budget | Positive N includes the coordinator; current implementation uses at most 2. |
| Work with fewer available CPUs | Linux configuration with one permitted CPU caps execution to 1 while retaining the request. |
| Shared computation and fidelity | Shared numerical body; state and logical work remain coordinator-owned; selected checks pass. |
| Broad multicore scaling | Not established. Larger requests do not create additional workers. |

Affinity is sampled on the configuring thread when requesting more than one
thread. Multiple permitted CPUs do not establish physical-core capacity or
exclusive availability. Later external affinity changes do not reconfigure an
existing helper. Unsupported/query failures are explicit; default 1 does not
need the query. The earlier single-CPU two-thread experiment took 55.61 s on a
small workload; the configuration cap fixed that practical defect, with exact
PGO requested 1/2 controls both observing one task and passing original replay.

## Other approaches and the architectural lesson

| Investigation | Outcome |
| --- | --- |
| [Ordered whole-branch transactions](../../experiments/multicore-feasibility/branch-transactions/report.md) | Zero accepted ahead-of-head tasks among 36. Ordering, windows and state dependencies rejected work; large certificates were frequently capped. This is a bounded negative, not an impossibility proof. |
| [Pure child preparation queue](../../experiments/multicore-feasibility/child-preparation/report.md) | Real reuse, but summed elapsed rose 19.50% with 2 threads and 46.51% with 4 versus its inline mode. Useful work density and transport mattered more than available tasks. |
| [Reversed FULL ownership](../../experiments/multicore-feasibility/reversed-full/report.md) | Moving the pawn/cache branch to the helper lost 6.81% against the sibling successful split. Placement and ownership costs defeated the motivating kernel model. |
| [Same-node inventory](../../experiments/multicore-feasibility/same-node-inventory/report.md) | Almost every demanded inventory arrived ready, yet elapsed was essentially inline and 6.44% worse than the sibling FULL split, with nearly 2x inline CPU. Readiness was not a saving. |

The user's branch-as-task idea was investigated directly. Under exact King
semantics, a branch is a natural unit of computation but not automatically an
independent unit of execution: prior siblings affect windows, ordering and
stateful operations. Validation, discarded work and transport must be cheaper
than the reusable work. The tested policies did not satisfy that condition.

Additional cores do not solve these dependencies. Combining FULL and inventory
workers is not supported by additive measured savings, and the current FULL
chain alone cannot occupy arbitrary N productively. A future investigation
should bring a different dependency or useful-work argument, rather than start
with another queue-size or transport sweep.

## Behavioral evidence and its boundary

The [qualification record](../../experiments/multicore-feasibility/configured-full-qualification/README.md)
binds the exact ordinary image, same-source diagnostic companion, source review
and independent raw reconciliation.

- Default 1 diagnostics pass all 115 mandatory files / 7,673 cases / 117 operations.
  This is not a mode 2 diagnostic pass. Normal library, diagnostic and development
  tests pass, with exact-ELF reuse and the prior 11-second protocol test disclosed.
- Exact PGO configuration controls pass. Existing worker-aware tests cover
  supplied-map authority, FAST/FRESH, cache behavior, root changes and lifecycle.
  An external enabled-Q-observer control compares actual configured modes 1/2
  across 12 completed/stopped comparisons. Its initial compile-only harness error
  and repair are retained; production source is unchanged.
- Exact ordinary mode 2 passes the regular 12 games / 632 searches / 5,801 posts,
  continuity, seed, persistence and interruption/status/wire checks. The released
  literal combiner reports `completeFocusedReplay:true` and
  `completeGameplayQualification:false`.
- Mode 1 passes the selected short controls, with no claim of its own full 12-game
  focused completion. Actual task placement was gated before protocol input
  for all 32 search lifetimes across both modes. The 22 no-search seed lifetimes
  have a different, explicitly limited observation scope.

Two short-lived diagnostic post-exec observations were unavailable; supervised
execution, raw comparison and successful exits remain recorded. No failed
engine request was retried. Finite tests and source review support the local
candidate; they do not prove all admitted executions. Production panic=abort
does not promise unwind recovery. Waiting and shutdown require eventual helper
progress; qualification used external resource bounds.

## Recommendation and handoff

Keep the successful mode opt-in and default to one thread. Preserve this exact
candidate and its evidence for a separate adoption/release decision. Further
tuning is not selected: the practical gain survived integration and the selected
behavioral checks, while the other measured architectures provide no ready
profitable extension. This closes a useful research phase without claiming the
full N-thread vision is solved.

Before release, choose the intended supported artifact/platform scope, carry
the exact new artifact through the assigned external full-game gate, and update
release provenance deliberately. A contemporary KingWCR comparison is a separate
measurement task. The accepted serial release and its evidence remain unchanged.

Preserved candidate identities:

- Engine source: `66f35e440b2180d4d22c2bcd0e5a8c99c0f1185d`.
- Performance closure: `dce064807f14801a81901d3b27cc852021f51306`;
  local behavioral closure: `5f04a7a5b04c78ded01491100b53461af0e6538a`.
- Ordinary own-PGO image: `8f26d39fd1a69bc8a3aa6da2c364b6ddb4b065bc585a27c7420ae994566f8b1b`,
  7,536,152 bytes, at
  `/home/legolas/rook2-experiments/configured-full-20261024-01/production/rook2-pgo`.
- Own profile: `b7bd8ca21e8b9f64426af124be95bfc14feadd9b01bb94fb14bbefc7c550c6be`.
- Default 1 diagnostic: `3645eb0f80836e4adc2165ee2e2c94d2c92082ba6daea352fd859f44caf7a167`.

Raw qualification records remain outside Git under
`/home/legolas/rook2-experiments/configured-full-qualification-20261024-01/`.
The concise experiment records and research history are committed on
`research/deterministic-multicore`; main is preserved.

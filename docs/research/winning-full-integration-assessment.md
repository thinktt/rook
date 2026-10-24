# Integrate the demonstrated two-thread FULL split

2026-10-24. From imp2 to imp2-lead. **Source-only recommendation; unimplemented.**

Make the parked Activity/Shelter split usable before pursuing another parallel
architecture. Its [own-PGO survey](../../experiments/multicore-feasibility/full-split-production/report.md)
showed 63.946851s search wall versus 68.237305s accepted serial (6.29% lower),
with 1.873x total CPU. Candidate inline was 69.171315s (+1.37%). These are
single-observation54 totals, supported by a smaller repeated comparison;
neither adoption nor a guarantee that cleanup preserves the gain.

## Smallest integration

Start a new isolated derivative from winning source
`5612b55f395a31874ef9bc77611792155d5e920b`, preserving main, research history,
and frozen image `a977bb00…` / profile `f9eefbd0…`. This avoids importing HEAD's
failed reversal/cache extraction and inventory runtime branches. Existing
default-off research features can remain isolated; failed mechanisms need not
be shipped as ordinary runtime modes. Keep one shared Activity/Shelter numerical
producer and one FULL composition, with the pawn cache on the coordinator.

Use one positive total `--threads=N` budget, default1, and a small corresponding
library setter/getter. Configure `min(N,2)` threads: coordinator plus at most one
helper. Expose requested/configured counts through explicit configuration
inspection, without unsolicited wire output. Larger requests leave capacity
unused; they do not create additional workers or imply scaling. Budget1 creates
no helper; changes between1/2 drain and join the existing helper first.

Remove ordinary per-thread pinning. Inherit the creator's permitted affinity;
do not infer physical cores, exclusivity or spare capacity from its CPU count.
Controlled placement belongs to the benchmark supervisor. In particular,
launching the coordinator already pinned to14 would also restrict its unpinned
helper to14. Instead allow14/6 initially, identify and pin coordinator/helper
TIDs externally, verify both masks **before supplying protocol input**, then
release the unchanged replay. Recreated helpers need fresh verification.

## Waiting and ownership

Remove the ten-second elapsed abort everywhere, including startup, activation,
completion, parking and shutdown. Keep finite termination deadlines solely in
the supervisor. Preserve brief iteration-bounded completion spinning, then
block instead of monopolizing a permitted CPU.

The current [worker](../../src/evaluator_worker.rs) needs real publication
changes, not just deletion of clock checks:

- Keep the Control mutex/CV for lifecycle predicates; notify activation's IDLE
  acknowledgment as well as parking and terminal transitions.
- Add a completion CV paired with Slots. Publish output and COMPLETE under that
  mutex, then notify; recheck the predicate under the same mutex before waiting.
  COMPLETE is currently stored after unlocking, and normal completion does not
  notify a waiter.
- Publish terminal transitions with Control→Slots locking and notify both wait
  classes. Completion waiters never acquire Control or relock Slots through
  `failure()`. Release locks before unconditional shutdown `join()`.

Startup/transport/panic failures remain explicit terminal errors, never silent
inline recomputation. Check normal scope completion before returning search
success; Drop remains cleanup for abandoned paths, not a print-and-continue
error policy. Preserve direct-FULL scopes, nested root ownership, root reset,
retained terms, cache order and demand-owned R charges. Waiting neither polls
Host nor advances logical N/R: prescribed coordinator polls remain authoritative.
Production panic=abort still does not provide unwind cleanup. Active-search
idle spinning, including blocked Host callbacks, remains a disclosed cost.

## Proportionate sequence

1. Implement only this cleanup on the isolated derivative. Focus checks on
   numerical/retained/cache/R equivalence, repeated roots, direct FULL, nested
   owners, budget changes, stop/abort/Host-error exits and joined shutdown.
   Exercise completion-before-wait, failure notification and startup failure.
2. Verify default/1/2/larger budgets and inherited affinity, including one
   permitted CPU. Under an external deadline, deliberately deschedule the helper
   beyond the old ten seconds and verify resumption without an engine timeout
   or changed logical behavior. No numerical fallback or extra Host polling.
3. Run one small matched generic comparison on35/08/04/43: preserved winning
   generic control and cleaned1/2, repeated with complete CPU/wall accounting.
   Include inherited-mask liveness separately from externally pinned timing.
   New locking/notifications and default-path costs must be measured.
4. If promising, make one fresh own-source mixed1/2 PGO build and descriptive54
   comparison against accepted serial. The frozen profile does not certify this
   changed source. Report serial overhead, CPU cost and regressions as well as
   aggregate elapsed gain; no automatic numerical gain threshold is proposed.

Before **local adoption**, bind the exact new source/images to mandatory
conformance, focused evaluator/session checks in both modes, and the regular12
pre-gate plus seed, persistence, interruption/status and wire coverage. Reuse
unchanged fixtures/setup, not old-image pass claims. Existing finite research
checks justify implementation, not adoption. External full3288, delivery and
final performance/release qualification require separate selection.

## Beyond two

There is only one demonstrated independent helper chain. Branch transactions,
queued children, reversed FULL and inventory did not establish another
profitable work owner. Inventory's almost-inline wall with roughly2x CPU does
not justify additive three-thread savings. Further architecture research remains
possible, but is not the next useful step: first determine whether this measured
two-thread option survives practical integration. Scaling beyond2 remains open.

One Sol source reader challenged the waiting/affinity design and identified the
notification/lock details above. No engine edits, builds, helpers executing engine
code, new measurements or qualification were performed for this assessment.

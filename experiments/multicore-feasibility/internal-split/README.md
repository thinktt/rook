# Internal split with actual workers

Selected scope: `/home/legolas/agent-memos/imp2-lead-to-imp2-internal-split-workers-20261026.md`.
This is continuing beyond-two-thread research; main/release and canonical66/8f
remain unchanged. It is a different scheduling boundary from the closed
first-Restricted root-tail simulations, with the complete-order predicate.

Use the first ordinary internal parent in canonical order with proper finite
incoming bounds, requested depth>=3, at least8 remaining candidates, completed
child0>=2048N and best<=incoming lower. Initial IIO, quiet-mate work, child0 and
any tail IIO have settled. Coordinator executes the next demanded child; forecast
the following seven in order from one common snapshot. No future sibling size or
oracle chooses the split. A miss stays a coverage result, with no retune.

Budget1 runs natively; budgets2/4/8 use1/3/7 workers for the same seven tasks.
Requested-task waits, complete-order exact-entry replay/recovery, changed windows,
canonical fallback, cancellation and joined completion count as executor costs.
No recursive queue or FULL worker. Transfer owned inputs/results, create Rc-based
Search/journals only inside their owning thread, share one immutable native TT
base and use private native-group overlays. Native TT probe/store mutation,
pawn selection and learning effects retain their existing owners.

[Policy](policy.json) freezes one generic/noPGO image,35/08/43,48 lives (one
excluded warmup plus three interleaved observations per workload/budget). Before
collection, source, focused tests, image and all tools are pinned. Ordinary
source/setup repairs retain failed attempts; completed workload lives are not
silently retried. All actual selector/task identities must match across budgets.
The selected cap/selector may legitimately miss every workload.

Coordinator CPU14; workers in order6/4/2/0/8/10/12. Eight total threads occupy all
eight observed guest core pairs. At budgets1/2/4 the supervisor and selected agent/helper tasks use8–13, outside
active core pairs. At budget8 they use13, sibling of worker12. Other
housekeeping may still share worker cores. Affinity receipts
do not establish exclusive guest or host isolation. No global affinity settings
or host controls change.

Measure split setup-through-cancel/drain/join wall and all-thread process CPU,
alongside enclosing executor intervals and whole-process wait4 CPU/RSS. Oracle
computation stays outside executor intervals; whole wait4 includes oracle/startup
and is not executor CPU. Independent local-output/work and root-final shared-
state audits remain fatal. A transient erroneous write later overwritten can
escape the independent state audit. Fixed completion/NoHost/timing absent/rnd0;
no live stop/observer coverage, PGO, broad qualification, adoption or delivery.

Status: source preparation. No workload timing has begun. The prototype is
isolated at `/home/legolas/rook2-experiments/workspaces/internal-split-20261026-01`.

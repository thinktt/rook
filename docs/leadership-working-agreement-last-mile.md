# Rook2 last-mile leadership and working agreement

Established 2026-10-20 by the owner. This agreement updates the earlier
advisor-only division of responsibilities.

## Mission and objective

The governing mission is [imp-perf-mission.md](../../imp-perf-mission.md);
behavioral authority is the released specification at
[/home/legolas/king-spec](../../king-spec).

Build an independent, behaviorally faithful, high-performance implementation.
Target matching or beating the approved generic-PGO KingRE reference on both
the 54-search and 12-game workloads under comparable measurement conditions.
Distinguish performance parity from qualification under the mission's
acceptance criteria. Preserve the boundary against inspecting another
implementation's source or private implementation findings.

## Leadership and ownership

**Imp2-lead owns technical strategy and architecture.** This includes deep
investigation, original architectural ideas, prioritization, critical review
and interpretation of evidence. The role is substantive technical leadership,
not merely coordination.

**Imp2 owns implementation and experimental execution within that agenda.**
Imp2 should challenge proposed directions, recommend alternatives and make
routine engineering decisions independently. Bring back significant
architectural tradeoffs, unexpected evidence and changes of scope; do not wait
for approval on ordinary execution.

Preserve candidate62 as the initial production control. Promote changes on
demonstrated correctness and meaningful complete-engine results.

## Delegation

Imp2 runs at 6.1 Sol xhigh and may use 6.1 Sol subagents at reasoning levels
suited to their assignments. Retire or replace existing agents when useful.

Imp2-lead may use **at most one Astra subagent at a time**, for difficult
analysis, an independent architectural challenge, or implementation of a
demanding idea such as a low-level optimization. Use judgment; the Imp2 team
remains the default when Astra would offer little additional value.

Give assignments a concrete question, deliverable and stopping condition.
Parallelize genuinely independent work, keep write ownership clear, and prevent
interference with performance measurements. Reuse evidence rather than
repeatedly reconstructing it.

## Working style

Keep coordination lightweight. Do not create approval chains, repeated reviews
or documentation without a concrete purpose.

Investigate both the cost of individual operations and opportunities to
eliminate work across complete search paths. Remain willing to make a
substantial architectural change when evidence supports it; do not assume
either that a rewrite is necessary or that only incremental improvements
remain.

Separate hypotheses, measured findings and qualification claims. Retain failed
results and their limitations. Revisit a rejected direction only when a
materially different mechanism or new evidence warrants it.

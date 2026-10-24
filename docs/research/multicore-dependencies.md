# Initial multicore dependency findings

2026-10-24. Research under the [multicore mission](../deterministic-multicore-mission.md).
Source observations, not performance results or an adopted design. Initial
engine source is the accepted main snapshot at `a3de19d0`; workspace setup is
`009b4f8e`. Historical architecture.md describes the initial engine proposal,
so current source is authoritative for these findings.

## First opportunity: overlap two full-evaluation chains

In [Evaluator::full_impl](../../src/evaluator.rs), Position, Influence, root
context and color-owned weights are fixed for the call. Activity produces
pressure consumed by Shelter; both routines return values without mutating
search state. That chain can potentially run on a worker while the coordinator
selects the pawn-cache entry and calculates pawn terms, pawn progress, central
terms, patterns and square contributions.

The coordinator must join before constructing tempo and the final Components,
updating retained evaluation and relation counters, and performing the existing
finishing calculation. Preserve numerical formulas and their rounding. Worker
results include the original Activity relation-query count; scheduling must not
create or remove logical charges. Workers do not poll input, advance work clocks,
publish posts or update learning/TT state.

This is a small ownership change with a clear potential experiment. Its economics
are unknown: on a pawn-cache hit the coordinator's remaining work may be too
small to cover dispatch and join. A persistent worker does not eliminate
communication, cache-line transfer, waiting or added copying. The first probe
should compare the actual chains and their combined critical path, rather than
demonstrate merely that Activity can execute on another thread.

## Why independent search children are a different problem

[Ordinary search](../../src/ordinary.rs) selects later child windows from earlier
scores and can invoke an ordering phase after its first child. Children mutate
the shared remembered table, learning and pawn cache. Scout retries reuse a
child's modified retained state. Running whole siblings with private copies and
merging their scores would therefore change the prescribed computation.

[PawnCache::select](../../src/pawn_structure.rs) preserves previous descriptors
on an identity hit, including deliberate identity collisions. Substituting fresh
structure for worker convenience is not faithful. Cache selection must remain
ordered, or any speculative result must explicitly validate its actual selected
input before reuse. No whole-child speculative evaluation is selected initially.

## Reserve alternative: calculate pure child data ahead of demand

Child placement and some geometric/evaluation components can be determined from
the parent and move without knowing the future search window or learned state.
A later experiment could prepare Influence or Activity while the coordinator
searches another child, keeping every authoritative consumption ordered.

This would speculate on demand, not execute independent search branches. TT
returns, frontier skips and cutoffs can discard the prepared work. Ordering
passes can reorder siblings, so results must follow their actual inputs rather
than an array index. Only placement-dependent data should be reused across a
scout retry; retained evaluation and pawn selection are not interchangeable with
such data. Native coherent-plane construction also retains its existing input
provenance requirement.

Keep this option in reserve until the simple full-evaluation split is measured.
It may permit larger overlap, but adds wasted work, storage and lifetime issues.

## Current division of work

Imp2 owns the source cost/dependency readers and a bounded standalone worker
experiment in `experiments/multicore-feasibility/`. The lead reviews search
dependencies and interprets the results. Initial timing placement proposed by
Imp2 is coordinator14/worker6, with guest siblings15/7 idle and helpers0-5,8-13.
This is guest placement evidence, not a host-isolation claim. No full-suite or
PGO campaign is needed to answer this first mechanism question.

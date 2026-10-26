# Mission: Deterministic Multicore Rook

Explore how modern multicore hardware can make Rook execute King’s prescribed
computation faster while preserving its exact deterministic behavior.

## Implementation vision

An engine that uses available cores effectively, accepts a configurable thread
budget, and produces identical behavior regardless of thread count. With one
thread, it should remain close to the accepted serial engine’s performance.
Ideally, serial and parallel modes share computational logic without unnecessary
duplication.

These are design preferences to pursue, not restrictions that prevent research
into a promising alternative architecture.

## Research approach

Investigate the engine, develop ideas, try promising approaches, and let the
evidence guide further exploration. Begin with independent calculations where
practical; pursue more advanced approaches when justified.

Major redesigns, replacement subsystems and isolated greenfield implementations
are within scope. Preserve King's required behavior and the retained baselines;
the current engine architecture is not a constraint. Distinguish ordering and
state dependencies required by the specification from boundaries inherited from
the implementation. Seek concrete sources of useful parallel work, rather than
assuming that a rewrite or additional workers will produce acceleration.

Choose experiments by their expected value, from small changes to substantially
different execution architectures. Reuse existing numerical kernels and evidence
where useful, without requiring a new design to fit the existing structure.

Imp2-lead owns architecture, strategy and critical review. Imp2 carries out
delegated implementation and experiments. Keep coordination lightweight and
document what was tried, what happened and what we learned. Successful research
code may become the production implementation.

Imp2 may use GPT-6.1 Sol subagents at any available thinking level and replace
them as needed. Imp2-lead may use one Astra subagent at a time, at any available
thinking level, when a particularly difficult problem warrants its help.
**Astra carries a substantial token-budget cost, so use it selectively when its
expected contribution justifies that expense.** Imp2 and its Sol team remain
the default for delegated work.

Preserve the accepted engine as the reference and conduct experiments on a
separate branch.

## Fidelity and measurement

King fidelity is non-negotiable: preserve moves, scores, posts, logical work
counts, authoritative state updates and stopping decisions. Thread scheduling
must not change prescribed behavior.

Measure elapsed-time improvements against the accepted serial engine under
comparable conditions. Also report total CPU consumption, memory use, scaling
across thread counts and effects on serial performance. Distinguish acceleration
over our baseline from demonstrated performance against KingWCR.

## Testing during research

Keep testing proportional to the question being investigated. Use focused checks
and small representative workloads for early experiments, reserving expensive
suites for promising approaches and major integration milestones.

Lean into exploration without requiring full qualification of every prototype.
Clearly record any unverified behavior or temporary simplifications, and
interpret performance results within those limits.

Reuse applicable evidence and avoid redundant runs. Full fidelity remains a
requirement for adoption; lightweight research testing does not replace final
validation.

## Outcome

Report the demonstrated opportunities, unsuccessful approaches, costs and
remaining uncertainties, with a recommendation for what to develop further or
adopt. An honest negative result is useful.

An outside manager controls the research allowance and signals when to wrap up
and stop. The team does not manage that quota.

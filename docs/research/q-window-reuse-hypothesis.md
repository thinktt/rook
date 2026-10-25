# Queued quiescence branches with a window-validity certificate

2026-10-25. From imp2-lead to imp2. Source hypothesis and bounded independent
challenge; no implementation, reuse measurement or speed claim.

The [first branch pilot](../../experiments/multicore-feasibility/branch-transactions/report.md)
already validated native sorted inventories, not broad history snapshots. Its
34 of 36 ahead tasks with changed canonical node work cannot be rescued merely
by cheaper validation. A different task boundary and reuse rule are needed.

## Why Q is a different boundary

Inside one quiescence parent activation, recursive Q calls never enter ordinary
search or the transposition table. They read learned history without recording
new history scores; their learning writes are killer clears. Child positions,
retained arrival state and reversible history are derived from that parent.
The pawn cache and changing sibling windows still prevent assuming independence.

This suggests a queue of Q sibling tasks with small private worker state rather
than a full ordinary-search snapshot. Reuse the native Q kernel and numerical
body. Do not copy a large TT for work that cannot consult it. Useful sibling
width, subtree size and eligible work share are empirical questions: the active
Imp2 census will determine whether this boundary is worth an execution trial.
Fixed-window ordinary mate-probe Q groups are a simpler alternative if their
measured work is substantial.

## Smallest new reuse rule

A Q sibling's initial alpha is `-parent.upper`, which stays fixed during the
parent loop. Its beta is `-parent.lower`, which can decrease as prior siblings
complete. First keep every non-window input and alpha exact, and certify an
interval of beta values for which the same computation remains valid.

Along a fixed Q execution path, the returned scores are numerical constants;
the code returns evaluation bounds/scores, mate values or a final best score,
not the incoming window variable. With fixed dependencies, an active bound is
therefore a constant, the original beta or its negation. Preserve the selected
arm of every bound update/max and every relevant evaluated comparison. Each
comparison narrows an allowed integer interval. Child intervals can be mapped
through the same bound substitutions and intersected into the parent's interval.

The worker aggregates this certificate while doing its actual search. At the
canonical turn, interval membership is cheap; the coordinator need not interpret
the entire Q control-flow trace. This is a certificate for identical prescribed
computation, PV and effects under changed windows, not conventional reuse of a
score bound that silently changes N/R or searched nodes.

An independent Astra source challenge found this structurally feasible for a
bounded experiment, subject to the following obligations. It did not establish
performance, broad applicability or production correctness.

## Required guards and dependencies

Window-sensitive decisions include all of these, not only beta cutoffs:

- Reversal draw's `upper <= 0`, after repetition testing and killer clearing.
- Strict FAST-to-FULL refresh inequalities and the capture-exception bypass.
- Ordered evaluation-bound/stand-pat returns, alpha updates and checked evasion
  cutoff. Preserve equality and return priority.
- Capture policy's threshold/max, lazy support consultation, force decision and
  optimistic best update, including updates before a later rejected candidate.
- PV installation conditions separately from score improvements and cutoff.

For example, FAST score 0 with windows `(250,300)` and `(249,300)` can select
different evaluation stages. Capture estimate 111, attacker 20, best 90 and
defended=true produces different optimistic best/support work for alpha 100
versus 111 even though both captures are nonforced. A child score 10 with best 0
and beta 20 installs a PV at alpha 9 but not alpha 10. These are meaningful
counterexamples to weaker certificates based only on returned scores or visited
children.

For a false conjunction, retain a witnessed false arm; do not replace a union
of valid regions with its bounding interval. Use wider arithmetic for certificate
endpoints, preserve strictness, and stay within the native admitted window domain.
Validate the actual entry Node, history chronology, root/configuration epoch,
checked state and reply-list availability. An external entry with
`replies_available=true` needs its existing complete candidate list, or must be
excluded initially. Internally produced reply lists remain part of native Q work.

Pawn selection must replay against canonical state, with exact consumed
descriptors and native mutation semantics. Initially keep conservative hit/miss
validation. A future relaxation can derive canonical reuse counters when the
same structure is consumed, but there is an asymmetric trap: a speculative hit
followed by a canonical miss cannot use the old hit payload as a fresh witness.
That payload may be stale even at the same full identity. Reject that direction
unless actual fresh construction is independently supplied and agrees. The old
`research_replay_select(identity, expected)` is safe only within its original
strict validation rule; do not weaken the comparison in isolation.

Completed Q killer-clear effects can be summarized by a bitset of reached slots.
Repetition returns occur before clearing; terminal ply can clear slot 64. Q
does not consult killers, so repeated clears can collapse only within this
completed, uninterrupted Q scope. Do not generalize that compression to ordinary
search or interrupted prefixes.

## Ordered consumption and a route to live search

Parent candidate eligibility, score/PV updates, task demand and cutoff remain
canonical. A changed or cancelled candidate consumes no speculative effects.
Workers own their state; staging must leave canonical state untouched on any
validation failure. Commit exact Node/PV outputs, raw N/R and applicable statistics
plus canonical pawn effects and killer clears, then continue the parent's native
loop. Disable the separate FULL helper in branch workers so total threads remain
bounded and costs remain interpretable.

Initial fixed-completion experiments can use NoHost/timing absent. For a simple
later live route, accept only tasks with no canonical charged poll in their span,
including the endpoint. For starting N and positive dN, require
`dN < 4096 - (N & 4095)` and, when limited, `N + dN <= node_limit`. Otherwise
execute the original call. A poll occurs immediately after node credit and
before Q entry effects; polling after bulk commit is not equivalent. Raw N/R
must use checked arithmetic and native observation boundaries, not separately
saturated counts or summed elapsed-clock deltas.

Initially keep enabled diagnostic observers on the original path. Their entry
records include the actual windows; a speculative record with old bounds cannot
be published verbatim merely because its computation was certified. Production
Host observations and interruption behavior remain separate obligations.

## Discriminator, not adoption plan

First join the work census with this source argument. If Q has useful width and
work, compare conservative exact-window reuse with beta-interval reuse on the
same real tasks, against independent canonical executions. Count actual admitted
work, interval/pawn/demand rejections, task/log/validation cost and useful queue
depth. Do not infer scalability from acceptance percentages alone. The successful
two-thread FULL split and accepted serial are both relevant eventual controls.

A focused differential check should exercise guard equality boundaries, short
circuit paths, supplied reply lists, root/history dependencies and asymmetric
pawn states. These checks do not require another full mandatory suite. If the
certificate works but the work is too small, change the task boundary or move
to partial reuse rather than polishing this into an unprofitable scheduler.

This is one candidate in the broader scaling investigation. No prototype, native
run, fixed numerical gate or new adoption is selected by this document alone.

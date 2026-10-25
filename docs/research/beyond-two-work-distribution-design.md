# Beyond-two branch work: bounded distribution discriminator

2026-10-25. Source/existing-evidence assessment for the restarted multicore
mission. No new engine execution or performance claim. Preserve frozen66f35e44,
ordinary8f26, its profile/qualification and all earlier negative experiments.

**Existing records do not show where several substantial sibling tasks coexist.**
The smallest useful addition is an opt-in, coordinator-owned count census of
charged entries, direct recursive edges and sibling batches, on original35/08/43
once each. Counts describe potential work; they do not establish independent
execution or successful speculative reuse.

## What the evidence already answers

* The [transaction pilot](../../experiments/multicore-feasibility/branch-transactions/report.md)
  found no accepted work prepared ahead of another branch. Its selected depth6
  root tasks include substantial inclusive node counts, but certificate caps and
  changed requests/order dominate. Queue2/4 observations overlap; they are not
  additional independent work, and do not describe the complete tree or43.
* The [pure preparation trial](../../experiments/multicore-feasibility/child-preparation/report.md)
  establishes actual demand/waste for its particular depth2/first6 policy:
  79–87% of started tasks supplied nothing, and three workers were worse than one.
  It does not give full sibling subtree sizes, demand across depths, or an upper
  bound on a different branch policy.
* The [TT census](../../experiments/current62-tt-census/report.md) observes score
  returns on11.11%/47.82% of35/08 probes in its older source. That is strong reason
  to include no-evaluation entries, not current66 node percentages or task sizes.
* The [older source survey](../reviews/2026-10-20-architecture-performance-survey.md)
  attributes8.059% of one simulated35 instruction summary to full generation.
  Inclusive symbol attribution, whole-search times, cumulative posts and root
  work rows cannot reconstruct internal sibling overlap. No native-time budget
  should be inferred by adding those attribution shares or subtree counts.
* [Configured FULL results](../../experiments/multicore-feasibility/configured-full/report.md)
  show a useful two-thread checkpoint and a43 regression. They do not identify
  whether43 lacks demanded branch work or loses elsewhere.

## Exact source boundaries

| Boundary | Hook / treatment |
|---|---|
| Ordinary entry | `ordinary.rs:721–740`: handoff to Q precedes charging. Instrument the charged ordinary body only; the handoff is an edge annotation, not another node. |
| Ordinary exits | `ordinary.rs:749–876`: draw, TT score, fast cutoff, FULL-bound cutoff, shallow/null cutoff, empty inventory and mate-window return. Keep these mutually exclusive final reasons. |
| Ordinary main batch | Inventory/order at867/882; initial IIO completes at967; main loop986. Publish-point identity means the post-initial-IIO inventory, before first main consumption. |
| Ordinary main edge | Call1057 plus optional retry1070. Group scout and its retry as one candidate task, while recording each attempt separately. Frontier skip1021 has no recursive edge. |
| Other ordinary edges | Null841; checking-mate Q931; IIO1184. Each IIO pass (`1151–1168`) is its own batch, including tail-IIO after the first main candidate1114. Never treat probes/passes as additional main siblings. |
| Q entry/exits | `quiescence.rs:263–335`: draw, maximum-ply FAST, static evaluation return, empty inventory, checked mate-window return. Q has no TT probe at this entry. |
| Q candidate batch | Ordering341, loop361, recursive call489–495. Record each existing rejection at371/424/435/447/467 separately. Bounded legal-reply generation447 is a probe, not a charged child. |
| Root batch | `timed.rs:begin_candidate/execute` and `root_schedule.rs:next/returned`: identities are initial-root slots; windows, retries and tail order depend on prior returns. Group attempts for one candidate; preserve iteration/policy separately. |

Initial candidate identities can exist before their recursive demand is known.
Ordinary frontier thresholds, main windows/retries, IIO windows/promotions, Q
optimistic updates/eligibility and stopping depend on earlier consumers. Distinguish
**candidate-known potential** from **demand-known admitted calls**; neither alone
proves a worker can advance through unresolved TT/history/pawn/window reads.

## Minimal counters and accounting

Use a private compile-time feature in isolated trial source. No journal, per-node
timer, worker counter writes or full event trace. Snapshot monotonic coordinator
counters around entries and actual recursive calls:

`C = (charged N, charged R, actual FULL calls, FAST calls, Influence builds)`.

FULL/FAST/build counters must count actual existing native calls, including the
selector's refresh, without forcing demand or relying on disabled `DIAGNOSTICS`
statistics. The existing numerical owners are `evaluator.rs:full/evaluate`,
`ensure_influence_for_search` and `select_noncheck_impl` (854–919). Do not call an
extra evaluator/projection to classify a node. FULL0 is no FULL demand; R0 is not
zero CPU work. Count checked/maximum-ply Q entries separately.

For each entry, save `C_before`, direct-child totals and its exit reason. On exit:

* Inclusive work = `C_after − C_before`, including this entry and descendants.
* Exclusive work = inclusive minus **all immediate recursive call** deltas,
  including null, mate, IIO, scout/retry and Q edges. Own exclusive N is normally1.
* Aggregate an exclusive exit-reason × ordinary/Q × depth/check cohort matrix,
  plus independent inclusive-size histograms. Also cross-tab actual FULL0/positive
  and recursive-child0/positive; “no main child” can still contain null/IIO work.

Snapshot **before** `charge_node` and finalize every `Result`, including errors.
The4096th credit can be followed by a stopping poll returning `Err`; installing
a frame only after successful charging loses that credited node. Separate refused
admission N0, credited stops, normally completed subtrees and partial stopped
subtrees. Do not discard partial work or present its size as a complete subtree.
Observe each logical work epoch/reset explicitly; do not subtract across resets.

At every ordinary/Q/root batch, count inventoried, examined, skipped-by-reason,
entered, retried and untouched-after-cutoff candidates. Keep attempted-call
histograms by incoming edge kind and actual callee ordinary/Q. Record FULL/map/R
demand jointly with each completed edge's N-size bucket. This prevents a million
cheap TT returns or zero-demand candidates from becoming a million useful tasks.

## Sibling coexistence, without inclusive double counting

Keep a bounded temporary vector for one batch of **direct** candidate tasks:
actual sequence/rank, attempt count, inclusive N/R/FULL/build totals, completion
status. At most512 legal slots; IIO reuses a vector per pass, with a separate
scratch vector while a main batch is paused. No fixed first6/depth2 truncation.
Use fixed heap storage bounded by64 plies and existing move capacity; no retained
per-node vectors or publication of boards/TT contents.

For each threshold `T ∈ {32,128,512,2048,8192}` charged nodes, classify substantial
completed edges. At each canonical boundary before edge i, derive:

* substantial future siblings `j > i`, their total work and maximum size;
* whether current edge i is substantial, and future substantial siblings also
  have actual FULL demand;
* inventory-known but ultimately skipped/unvisited slots, to expose speculation
  waste rather than count them as demanded capacity.

Report width buckets0/1/2/3/4–6/7+, and parent counts with a substantial current
edge plus at least3 or7 substantial future siblings. Those are retrospective
4/8-thread **potential** cohorts, not measured runnable width: future requests,
cutoffs and effects are still unresolved. Include aggregate sibling work/max-child
ratios to expose one dominant branch. Keep main, each IIO pass, Q and root batches
separate. A retry of one move is not another simultaneously available sibling.

For additive work coverage, use separate invocation-tree cuts at parent ply0
(synthetic root),2 and4. Parents at one fixed ply form an antichain after collapsing
uncharged handoffs; their direct child subtrees are disjoint. For each cut verify:

`exclusive prefix work through the cut + inclusive direct-child work at the cut
 = whole epoch work`.

Use this partition for N/R and demand counters. Do not add cuts together. Global
subtree histograms and all-parent width counts describe populations, not additive
CPU coverage; parent and descendant opportunity cohorts overlap.

## Bounded output and discriminator

Collect all counts; do not sample only “interesting” large nodes. Use logarithmic
size bins0,1,2–7,8–31,32–127,128–511,512–2047,2048–8191,8192+;
depth bins0/1/2/3/4–5/6+, with mode/edge/check cohorts and iteration totals.
Avoid a full Cartesian product with every ply/window/return flag. Histograms and
fixed arrays suffice; optional illustrative parent records are limited to64 per
request, selected deterministically before size is known (e.g. fixed hash of
entry ordinal), with eligible/selected counts. No huge trace or per-node clocks.
Use checked u64 counters and an explicit overflow failure flag.

Focused controls should exercise handoff, TT/draw/bound returns, frontier skip,
Q rejection, IIO, scout retry and credited stop, and verify the partitions above.
Then one original35/08/43 request each with exact replay/accounting, coordinator14,
normal helper placement and finite supervision; no instrumented speed claim.

**Strongest scalable hypothesis:** substantial ordinary/root sibling continuations,
with narrower semantic validation and retention of expensive valid descendant or
pure computations after a conflict, offer a larger grain than per-move ordering
or eager single-child kernels. The census must first show meaningful disjoint work
in wide demanded sibling cohorts. If it finds only one heavy child or tiny/unused
siblings, cheaper validation alone cannot supply4/8 workers. Large Q evasion/forcing
subtrees remain a possible secondary cohort, not an assumed source of width.
Actual reusable progress before a dependency requires the separate conflict
assessment; this census cannot certify it. It selects no executor implementation.

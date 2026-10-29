# Frontier cap: local sample; no retained-policy case yet

The32-parent/128-lifetime-job cap in b5e3bfb0 was chosen to bound observation
work, not from a production break-even argument. I would NOT implement its full
two-pass timing/service observer as a profitability discriminator. It can show
local recurrence/newness; a thin result cannot reject the wider frontier cohort.
First32 parents are a biased early slice, not a representative sample.

Existing scale evidence is enough to deprioritize this FIXED policy, though not
to prove mathematical impossibility:

| Historical per-call scale |128 perfect first uses |
|---|---:|
| Initial composed FULL probe597.75ns |76.512us |
| Inventory census case35 serial FULL median1182ns |151.296us |
| Coarse first-new map207.383ns + inline chain696.857ns |115.743us |

The inventory census also reports08/43 medians521/617ns. These are different
workloads, builds and observed intervals; medians are NOT hard upper bounds or
costs of the selected frontier children. The coarse row divides1.471591ms/7096
map keys and4.123998ms/5918 chain keys, so even its sum combines populations.
Use the rows only as order-of-magnitude sensitivities, never add them together.
Perfect demand/readiness and no duplicates already favor the128-job policy.
Current3 overlaps chain work, so serial kernel CPU is not wall time removable.

The saved c242 original35 search takes3.314737s. Those illustrative totals are
only0.0023–0.0046% of it, before collection, exact lookups, copies, wasted work,
producer CPU or lost inventory overlap. As independent context, its512-stride
report has134.291ns mean side-ready minus owner-ready (clipped at zero), and
53.054ns measured residual join; neither is this cohort or a whole FULL budget.

Let L7 be all runtime consumer lookups in iteration7, h their average cost and
B the aggregate wall time actually removable by ready first-new results. A
necessary break-even condition is `B > L7*h + other owner critical-path costs`.
Producer service/readiness/CPU are additional constraints, not subtracted serial
CPU savings. With the FAVORABLE151.296us sensitivity above, the ENTIRE lookup
allowance would be:

| Hypothetical L7 | Maximum h before ANY other cost |
|---:|---:|
|10000|15.130ns |
|100000|1.513ns |
|1000000|0.151ns |

These are assumptions, not measured lookup times. For example,100000 lookups
at a hypothetical5ns already cost500us. Actual128-job coverage would need more
than3.906us removable wall per job merely to pay that bill, assuming every job
helps once. No source/evidence argument presently supports such unusually rich
selected work or such a tiny lookup domain. Exceptional slow calls are possible;
we cannot manufacture a hard upper bound from historical medians.

The128-job cap also does NOT bound a retained cache's total hits. Many repeated
uses of the same result could change its economics. Those are memoization value,
not additional first-new frontier work; this first-use sensitivity cannot reject
that distinct policy. No measured hot-key concentration supports it here.

The same saved search made1574502 FULL dispatches, but that is the WHOLE request,
NOT F7 or L7. Do not charge all of them to an iteration7-only consumer. We have
no saved S6 (qualifying skipped edges) or L7. Prefix novelty checks are audit-only
and must also stay out of an executor bill. These uncertainties prevent a formal loss proof. It could pay with a much narrower
lookup domain, unusually rich selected calls or concentrated repeats, but no
current evidence supplies those premises. Do not build the rich observer merely
to test the convenience cap.

Smallest proportionate correction, if a later observation is selected: ONE
original35 replay with only aggregate E6/S6/M7/F7 counters and6/7 completeness/
boundaries. E6 counts qualifying parent activations; S6 counts ALL admitted
ordinary depth0/fresh0 coherent non-king-victim skips, including duplicates; M7
counts actual scratch-None coherent map demands; F7 counts actual admitted FULLs.
Use the existing source seams/wrapper and both winning hooks; per-query integers,
two iteration-boundary timer pairs, one cold summary. No parent/child snapshots,
keys, payloads, prefix catalog, per-node timers or service batch. No implementation
or run is selected here.

That would establish supply/consumer-opportunity scale, not newness/readiness.
Actual L7 still depends on consumer gating/coalescing; M7+F7 is the simple
two-demand-query domain, not a lower bound on every possible lookup policy. It could motivate a later representative sample or a bounded
RESIDENT queue that recycles slots:128 resident entries is different from128
jobs over the whole iteration. Do not raise lifetime caps opportunistically or
scale the first32 yield to all parents. Even large S6 is only a supply count;
previous production, distinct keys, timely demand and actual savings remain open.

Disposition: analytically park the fixed128-lifetime-job POLICY as unsupported
at existing cost scales. Retain it only as an explicitly local yield sample if
that limited question is wanted. Do not execute the earlier rich plan merely to
rediscover its cap. Do NOT reject unbounded/coarser/different-admission frontier
policies or the source hypothesis from this assessment. c242/1a81 unchanged.

Evidence (existing, read only):
- [Initial probe](../../experiments/multicore-feasibility/report.md): prepared scalar-map standalone stream, generic/noPGO, FULL597.75ns.
- [Inventory census](../../experiments/multicore-feasibility/inventory-overlap/report.md): all-sample serial intervals1182/521/617ns; distinct observed population.
- [Coarse salvage](../../experiments/multicore-feasibility/coarse-pure-salvage/report.md): first-query disjoint component proxies, not a producer/consumer speedup.
- [Single-owner PGO](../../experiments/multicore-feasibility/single-owner-own-pgo/full54.csv): original35 owner3 search3314736512ns.
- Raw readiness: `/home/legolas/rook2-experiments/single-owner-own-pgo-20261028-01/full54/162-profile-35-owner3-r1/colors.json`.

Source/receipt reads and arithmetic only; no engine edits, build, native run,
census, new framework or artifact changes. This revises the economic interpretation
of [the earlier design](earlier-frontier-observation-design.md), not its semantic keys.

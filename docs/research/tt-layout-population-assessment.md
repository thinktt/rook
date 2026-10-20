# TT layout: conditional address model and parked production trial

2026-10-20. Lead assessment of the closed
[current62 census](../../experiments/current62-tt-census/report.md), committed
at e964dc83. This is a conditional address calculation and a prospective
experiment selection, not a measured layout improvement.

**Outcome:** the [one own-PGO trial](../../experiments/compact48-tt/report.md)
closed at5d6a33b3. Its0.292952% lower summed medians miss the unchanged0.5%
screen gate, despite6/7 cases lower and all correctness/backend gates passing.
The design is parked without repeat, retune or adoption. The calculation below
records why it earned that trial; it does not override the measured outcome.

The selected trial used one 48-byte group with four full 32-bit identities at offsets 0..15,
followed by four 8-byte payloads in retained0/1/2/recent order. Require 16-byte
alignment, unchanged semantic group count, one allocation and complete
initialization/wrap clearing. Retained62 remains the control.

## What the census distinguishes

Case35 is dominated by full identity misses; case08 is dominated by retained
matches. Usable recent returns are below 0.6% of probes in both. Concentrating
identity reads therefore has a plausible audience in both cases, while a
physically separate payload region would be visited much more often on case08.
Score returns alone undercount payload demand: metadata-only matches still
need generation and record fields.

Retained62 already uses conditional scalar identity-first loads. The proposed
change removes no eager whole-group copy. Its hypothesis is a better arrangement
of necessary accesses, with actual compiler and store costs still to resolve.

## Conservative conditional read-line bound

Assume 64-byte lines, the same semantic query sequence/group indices, and emitted
loads that consult payload only after the associated full identity matches.
The census observed no generation-rejected identity matches. Its old group
phases were 0/16/32/48. Changing the allocation base of an array with 16-byte
alignment and 48-byte stride rotates these phase classes.

| New group offset within a line | Condition for touching a second line |
| --- | --- |
|0 or16|Never; all 48 bytes fit.|
|32|An attempted recent or retained2 identity matches.|
|48|Any attempted identity matches.|

Let `N` be probes, `A` any-identity-match probes, `B` the union of recent and
retained2 identity-match probes, and `M` the largest observed phase population.
The number of second-line events is at most `min(A, M+B)`: the two relevant
phase classes are disjoint, their matching events are all within A, and the
phase48 contribution is at most M. This uses no independence assumption and
does not require the missing phase-by-outcome cross-tabulation.

The union B is recent matches plus retained2 matches minus the recent
metadata/retained2 overlap:
`14923+51583−65=66441` on case35;
`7891+2078−2=9967` on case08.

| Quantity |35|08|
| --- | ---: | ---: |
|N|1,661,201|426,339|
|A|318,149|291,572|
|B|66,441|9,967|
|M|416,406|107,041|
|Baseline ledger, total read-line union events|2,488,805|637,918|
|Compact upper bound, `N+min(A,M+B)`|1,979,350|543,347|
|Baseline events/probe|1.498196|1.496269|
|Compact upper bound/probe|1.191517|1.274448|

These are unions of modeled architectural read addresses within each probe,
at the diagnostic's observed baseline phases. They are **not** cache misses,
fills, traffic, retained62's actual allocation addresses, speculative accesses,
residency or cycles. The counterfactual preserves the query sequence and
requires actual conditional lowering. Stores and mate-depth writes are outside
this bound. No CPU gain follows from the table.

For comparison, separately aligned dense 16-byte headers and 32-byte payload
groups on distinct lines give `1+A/N`: 1.191517 on case35 and 1.683897 on case08 under the
same model. This does not prove dense storage slower: header residency is a
different possible benefit. Dense regions could share an allocation if their
alignment and sizing were explicitly handled. Neither their residency nor
their base-address and store costs have been measured.

## Costs that can reverse the result

Stores occur 88.87 and 51.35 times per 100 probes. About 60% of stores fill an
invalid retained slot and clear recent. On case35, 27.91% displace a full-group
record; on case08, 39.30% replace a matching retained record at equal/deeper depth.
Separated identity/payload writes may hurt a branch even while miss filtering
improves. Probe-only percentages cannot decide the layout.

Review every consumed store owner, including the previously uncaptured outlined
store, together with complete ordinary probing, allocation, initialization,
physical wrap clear and material frame/code/copy changes. Preserve identity0,
generation invalidation, signed-depth comparisons, duplicate recent semantics,
metadata-before-mate-mutation and all five replacement branches. The fresh
two-case census does not price stale generations, wrap frequency, 64MiB tables
or game sequences.

## Selected experiment

The lead's
[assignment](/home/legolas/agent-memos/rook2-lead-to-imp2-compact-tt-trial-20261020T183641Z.md)
delegates one isolated design, baseline and differential correctness checks,
one own-source original54 training and independently verified merge, one
own-PGO use build with current62 ExtTSP, complete backend review, and one
unchanged fixed70 screen against retained62. This production lane is selected
before results; there is no generic timing prerequisite or later lane switch.

Actual source, images, profile, helpers, schedule and finite resources must be
bound before their dependent stages. The native lane has a fresh 1,800-second
elapsed ceiling without resets. Incorrect behavior, a missing filtering
mechanism, an extra allocation/capacity change, invalid profile, unsupported
instructions or resource failure stops the lane. Routine stage activation is
delegated; a material departure returns to the lead.

The screen retains aggregate<=0.995, at least 5/7 lower, worst<=1.02, all 70
live/offline checks and no retry/retune. A miss parks the design; a pass returns
for a broad qualification decision. No dense/64-byte alternative, explicit
SIMD scheme, modulo change, sparse clearing, production promotion or external
execution is included.

Raw arithmetic inputs are in
`/home/legolas/rook2-experiments/tt-probe-store-census-20261020-01/execution/result.json`,
SHA256 `1a6f7e0f150ae96c7d945a6167500d67e1921a7b5bd64d81369b5d44b6753590`.
No additional engine observation was used.

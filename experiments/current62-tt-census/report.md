# TT census: miss filtering is substantial, writes remain consequential

Recommend one **compiler/correctness discriminator for compact48-byte groups**:
four full32-bit identities followed by four unchanged8-byte payloads, sameG
and one allocation. This is a proposed next step, not a selected layout, build,
speed claim or adoption. The two observations show enough filter-only demand
to investigate, while the frequent stores and08's retained payload demand
require complete producer/consumer code review. Dense16G/32G slabs remain an
alternative, with two-base/allocation and payload/store costs still unpriced.

Exactly original35 then08 ran once, fresh, with unchanged numerical owners and
ordinary protocol. Both original live and both independent offline replay
checks pass; every fixed counter partition, physical-slot prefix, selected
store/write association and lifecycle equation reconciles. No retries, warmups,
control process, timing comparison, PGO or layout prototype ran.

## Observed whole-process populations

Matches below mean the prescribed32-bit identity/generation association, not
proof of board equality. Retained counts include a preceding recent metadata
match where present; these rows are not a disjoint partition.

| Observation | Original35 | Original08 |
| --- | ---: | ---: |
| probes | 1,661,201 | 426,339 |
| all four identities differ | 1,343,052 (80.8483%) | 134,767 (31.6103%) |
| recent usable return | 6,405 (0.3856%) | 2,359 (0.5533%) |
| recent metadata-only continuation | 8,518 | 5,532 |
| retained match supplying score | 178,182 | 201,500 |
| retained match without score | 125,979 | 87,668 |
| all score returns | 184,587 (11.1117%) | 203,859 (47.8162%) |
| equal identity rejected by generation | 0 | 0 |
| stores / per100 probes | 1,476,322 /88.8708 | 218,907 /51.3458 |
| retained record writes | 1,447,745 | 217,242 |
| recent record writes/clears | 1,351,346 | 132,884 |

The32 joint bins preserve composition. Of35's8,518 recent metadata-only
continuations,118 later get a retained score,817 retained metadata and7,583 no
retained live match. For08 these are3,529/1,958/45 of5,532. A usable recent
return never examines retained slots. Actual retained0/1/2 attempts are
1,654,796/1,487,077/1,402,218 for35 and423,980/159,942/136,890 for08. Thus
returned-score counts alone miss substantial filtering and metadata demand.

| Exclusive store branch |35 count (%stores) |08 count (%stores) |
| --- | ---: | ---: |
| matched retained, shallower→recent | 1,002 (0.0679%) | 1,645 (0.7515%) |
| matched retained, equal/deeper→same slot | 124,976 (8.4654%) | 86,023 (39.2966%) |
| first invalid fill plus recent clear | 910,698 (61.6869%) | 130,935 (59.8131%) |
| full-group replacement/displacement→recent | 412,071 (27.9120%) | 284 (0.1297%) |
| full-group shallower→recent only | 27,575 (1.8678%) | 20 (0.0091%) |

All branch-slot and empty-scan distributions remain in the frozen counters.
Equal/deeper retained replacement leaves recent untouched; branch4's selected
least-depth slot is a comparison index, not a retained write. These aggregates
do not attribute a later recent hit to a particular earlier write cause.

Usable mates perform350 and17 modeled depth-WORD stores;94 and9 respectively
change the value. Unchanged-value stores remain included. Original pre-mutation
metadata and mate normalization/depth semantics were retained and tested.

## Conditional address coverage and lifecycle limits

Using the already established exact62 inline-probe pattern, the diagnostic's
unchanged48-byte group addresses yield one/two conditional64-byte read lines:
833,597/827,604 for35 and214,760/211,579 for08. Two-line shares are49.8196%
and49.6269%. Observed phases are0/16/32/48 in both cases. Identity DWORDs plus
conditional generation bytes already cover every line containing intervening
consider fields; diagnostic-only reads are excluded from this model.

This is address coverage at observed derivative phases, not the actual memory
accesses of the instrumented binary, unmodified retained62 allocation addresses,
cache misses/fills, traffic, residency or speed. It models no outlined-store
machine footprint. Phase and joint-outcome aggregates are separate, so exact
counterfactual hit/miss line savings cannot be reconstructed. New-layout
alignment/base phases must be explicit assumptions. A contiguous identity
header can concentrate miss filtering; payload reads, stale identities, mate
writes and stores still need their original data. No eager whole-group baseline
read, automatic64-byte padding or cache-residency conclusion follows.

Each fresh16MiB request allocates/initializes one table of349,519 groups, with
equal actual capacity, for16,776,912 logical bytes; each also performs one
generation increment and no physical wrap clear. Same-G dense slabs would be
5,592,304 identity bytes plus11,184,608 payload bytes before allocator overhead.
Compact headers preserve48G and one allocation. Preserve complete initialization
and wrap clearing; generation-only sparse clearing would be a separate change.
These workloads establish no multi-search stale-generation, physical-wrap,
64MiB, allocation-failure/deallocation or game-sequence costs. Unit wrap checks
are correctness coverage, not workload frequency or cost evidence.

## Exact closure

Diagnostic image `d0dd0ca609ffe1eac592d57298cca8e4396d63135de12b379c6f0f81e7f9014c`;
source52/tool24 graph `221276d440f8ecf1d2bb51652da7faa86eca8e1d8064e36c57ff67d09e4280d9`;
schema `87699fec469a98049fccb54327d4ba60b4146a11b3496fb8402f89de91dd7c8f`.
Only two existing files change; marker removal independently restores their
original bytes, all other73 baseline members remain exact, and one observer
module is added. No native-source repair was needed.

All197 library tests pass (`02e13a/0`), including four new observer controls.
One generic build (`d4d312/0`) and76-file verified source archive
`8c95c5513e30c610f4555f67ee037a35f248ad1584f69664ce68c53f82a88e8e`
close unchanged. Generic x86-64, Rust1.85.1/LLVM19.1.7, O3/thinLTO/one CGU,
panic abort/debug1; no PGO/ExtTSP. This is an observer derivative of retained62
source, not its performance artifact.

Collection `14f900/0`, independent verification `236d18/0`: two unique native
PIDs, both exit0;1,901 complete ASCII protocol bytes and2,740 census bytes total,
with no truncation/discard or unconfirmed cleanup. All146 immutable,76 live
source and7 helper pins plus the eight metadata bindings close. Guest CPU15
interval tick deltas are `[0,0,0,509,0,0,0,0,0,0]`; no owned15 job. These are
point observations, not continuous isolation or exclusive-host evidence.

No PMU, component timing, search-only attribution, original-game gate or final
performance/conformance qualification is established. Retained62 remains
unchanged at whole54 67.640360 CPU seconds and regular12 675.156653 CPU seconds.
See `closed-summary.json` and external raw root for exact named supports.

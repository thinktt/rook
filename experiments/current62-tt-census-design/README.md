# TT probe/store census design — historical preparation stage

Recommend one count-only census of original requests35 then08 before selecting
a layout prototype. The existing access reviews establish identity-first
conditional scalar probe loads. They do not establish the actual miss/hit/store
mix, and table_hits counts only usable returned scores. No engine, prototype,
build, test, model or timing ran for this design. Retained62 remains unchanged.

The Sol reader's complete source-only plan and source/spec/method hashes are
external: `/home/legolas/agent-memos/rook2-current62-tt-census-design-20261020T175438Z.md`,
SHA256 `96dd85f733baf4c749e8bbcc045cabcecc14d6e80832b13fc91b19438568ab53`.
Root reviewed it against remembered.rs and the existing access review. This is
the compact retained plan; source/image/build/schema/launch bindings remain
unset. The strategy lead selects any subsequent execution separately.

Observe existing decisions in a private derivative, without a shadow TT,
alternate lookup, policy replay or numerical ownership changes. Use fixed
main-thread aggregate counters; overflow or incomplete output invalidates the
diagnostic. No per-probe trace or per-group provenance ledger is needed.

| Observation | Required partition |
| --- | --- |
| Probe joint outcome |32 cells: recent {different identity, equal but stale, live metadata-only, usable score} × retained {not consulted, no live match, slot0/1/2 metadata-only or score}. Impossible cells must remain zero; usable recent implies retained not consulted. |
| Examined slots | Actual recent3→retained0→1→2 attempt prefix, each identity-different/equal-stale/live. Never inspect skipped slots to classify a hypothetical retained match. |
| Consider | Actual calls, usable normal/mate/no-score, mate depth changed/unchanged, metadata precedence. Some(0) is a score; at most two considers per probe. |
| Store | Five branches: matched retained shallower→recent; matched equal/deeper→retained; first invalid fill and recent clear; full least-depth replacement and displacement→recent; shallower full-group recent-only. Preserve selected slot and existing ties. |
| Writes/reset | Separate four recent-write causes, retained writes, mate-depth mutations, successful allocations/G/capacity, generation increments and physical wrap clears. Equal/deeper retained replacement leaves recent untouched. No CPU cost is inferred from these counts. |

Reconcile probes against joint outcomes, per-slot attempts against filter
partitions, live matches against considers, scores against usable recent/retained,
and stores against the five branches plus exact retained/recent writes. Preserve
recent metadata followed by retained metadata/score and final bound precedence.
Aggregate provenance cannot attribute a later recent hit to an earlier recent
write cause; leave that unknown. Allocation/drop costs remain unmeasured.

Optionally aggregate a conditional64-byte distinct-line ledger using the
already established inline-probe access crosswalk and observed baseline group
phases. Union actual conditional field spans within each operation; keep reads
and writes separate and exclude diagnostic-only reads. This models address
coverage, not cache misses, traffic, residency, CPI or speed. The outlined-store
machine footprint remains unknown; do not generalize the inlined store region.

Compare only same-G alternatives conceptually: a48-byte group with16 identity
bytes followed by32 payload bytes, versus two dense16G/32G slabs. Keep full32-bit
identities, all8-byte payloads, modulo, slot priorities, collisions, metadata,
mate-depth mutation and logical/physical reset semantics. Generation remains in
payload, so an equal stale identity still needs a payload read. Price payload-hit
lines, stores/displacement, two bases/allocations and full48G initialization/wrap
clearing alongside miss filtering. Counterfactual slab alignment/base phases
are assumptions; no64-byte padding or sparse-clear optimization is bundled.

For a future selected run, reuse the existing generation-safety count-only
collector/checker method under
`/home/legolas/rook2-experiments/original-worktree/evidence/current62-generation-safety-census-collector-preparation-20261020-01/`.
Freeze actual source/input/tool/schema/build/image maps and prove inverse
preservation of numerical/protocol bodies first. Exactly two fresh original
default requests,35 then08, no warmups/retries/control/CPU comparison. Original
runReplay/checkReplay live checks and two independent offline checks must pass;
rehash and reconcile raw exclusive counter JSON before/after.

HelpersH/native14/no owned15, one measurement stream; per-case setup15s,
search60s, cleanup5s, whole-study deadline180s. Preserve untruncated ASCII raw
protocol bytes (4MiB/case,8MiB total), counters≤64KiB/case, actual native exits,
work/posts/results/PIDs/affinity and confirmed detached-group cleanup. A failure
stops without replacing the case. CPU/wall receipts are ownership diagnostics.

This census is the single proposed next discriminator. If filter-only demand
is sparse, park; otherwise reassess complete hit/store/reset/footprint costs
before selecting one compiler/layout experiment. A favorable miss count alone
cannot authorize a layout or establish a gain.

The subsequently selected [two-case count-only study](../current62-tt-census/report.md)
is now closed. The unexecuted/bindings-unset statements above describe this
earlier source-only design stage; consult the study report for actuals and limits.

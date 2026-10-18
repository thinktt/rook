# Bounded next hot-path review

Date: 2026-10-18. Independent native child review for Imp2; parent owns the decision.
Snapshot: repository HEAD `c38ce616cd6b3cc2dcd97e2fb456d5e221f37141`, canonical activity-specialized artifact `8d9dddc58d3b5dd1128bc7cedb4ee83a0df6310d33fb5f377f13a1a46ce7f79d`.

My preliminary ranking is **(1) an immutable uncapped influence-sum table, then (2) an immutable activity-pressure-value table**. These are small, separately falsifiable changes to existing pure helpers. The measured source-attribution envelopes are modest: 1.4788% and at least a directly identified 0.5662% of this one profile's simulated instructions. They are worth a bounded experiment because their semantic domains are exhaustive and neither adds mutable state, copying or lifecycle obligations. Neither is a measured speedup, and neither closes the much larger whole-engine gap.

This was a cold review: reads, hashes, and offline text parsing only. No build, rustc, test, engine, profiler or benchmark was executed. No native source was edited. All review commands ran under `taskset -c 0-5,8-13`. No Herdr or other implementation source was consulted. `rg` is unavailable; file/text searches used find/grep after the failed rg invocation.

## Evidence interpretation and exclusions

The retained profile is whole-lifetime **11,603,840,314 simulated Ir** for `profile-01`, collected with cache and branch simulation disabled. The original strict replay reports pass. It does not measure PMU retired instructions, cycles, CPI/IPC, cache behavior or native CPU speed. Timerange `Basic block 0 - 1765145993` describes a simulator block range; zero is not a function-call count. All 43 current native/build source hashes in provenance match this snapshot. Artifact identity is bound by retained provenance; this review did not execute the artifact.

Function-table rows are split by source file through inlining. The 1,162,651,588 activity.rs/compute row and the 245,172,585 influence.rs/compute row are distinct self-attributed source work within the same machine function; they are not inclusive parent/child totals. The 171,595,825 Ir at influence.rs:208 already contributes to relevant function/file rows and must not be added to them as another cost. My offline parsing skipped the cost line following each `calls=` entry, resolved compressed file/function identifiers, and reconciled the line-208 total to the retained annotation. No call frequency was inferred from instruction weights.

The current record already adopts shared evaluation geometry (0003), persistent attack planes after matched local/persistent supply (0004), the compact relation kernel (0005), typed influence enumeration (0006), and static activity kinds (0007). Those are completed directions. The destination-table generation trial remains parked after a 0.231190% generic summed-median improvement with all six ranges overlapping. Positive ordinary-null influence reuse remains parked at the measured 0.767801% map-build opportunity, which is not a CPU savings estimate. Repeated full-evaluation caching, king-coordinate metadata, activity widths, and evaluation-input reuse retain their recorded weak/limited results. I do not propose reopening them.

The old influence-design document explicitly mentions an optional `sum[256]`. That is an existing untested idea, not a completed or parked trial in the audited current decision/research record. The new selection evidence is the current canonical source-line attribution, not an assertion of novelty.

## Rank 1: exact uncapped profile-sum lookup

**Bounded code hypothesis.** In influence.rs:207-209, keep `pub const fn profile_sum(code: u8) -> u8`, but return an entry from an immutable `[u8; 256]` table generated at compile time from the normalized-digit formula. Keep the existing relation CLASS and RELATIONS tables and all consumers unchanged for the first experiment. This adds 256 immutable bytes, no per-evaluation preparation, allocation, influence field, Position/Node field or search scratch. The table is a pure function of the original normalized byte, independent of placement identity, root, side, chronology and prior calls.

The output is the **uncapped** sum `weak + queen + rook + minor + pawn`, in 0..11. The existing 16 relation classes cannot replace it: their capped multiplicities discard information. For example `profile_sum(255) == 11`; a cap at four changes source penalties and search guards. Base wrapping influence construction, adjusted saturated exclusion and relation charge ownership stay with their current code. This experiment does not predecode an entire map or memoize values per node.

**Measured attribution envelope.** influence.rs:208 has 171,595,825 self-attributed simulated Ir, or 1.4788% of the total. Its offline resolved split is:

| Inlined owner | Simulated Ir at line 208 |
| --- | ---: |
| activity::compute | 96,773,645 |
| pawn_terms::structure_terms | 38,023,884 |
| ordinary_policy::king_pressure | 33,150,485 |
| pawn_terms::raw_piece_terms | 2,485,462 |
| pawn_terms::occupied_pressure | 876,525 |
| quiescence::visit_q variant 2 | 229,051 |
| quiescence::visit_q | 56,773 |
| Total | 171,595,825 |

That is a removal ceiling for the identified simulated source arithmetic if it cost zero to replace, not a predicted instruction reduction or an upper bound on native CPU improvement. A real lookup requires address formation and a dependent load, and its cost can be worse under real cache pressure. The activity owner represents only 0.8340% of the lifetime; this is a cross-consumer helper experiment, not an attempt to remove the whole activity row.

**Actual semantic owners.** Activity uses both source sums for the `5A+2` penalty. Pawn advance and occupied pressure use current influence sums, and eligible knight bonuses use the current own sum. ordinary_policy::king_pressure compares previous/current influence for the opponent of the **current** side around the **current** king. Quiescence destination support uses the actual victim color. Preserve these inputs, short circuits, previous/current map lifetimes and existing gate order exactly; computing an invariant scalar differently does not authorize moving a consumer or changing a query/charge decision.

**Proof obligations.** Generate all 256 entries from the formula, never fixture answers. Exhaustively compare with an independent division/remainder decode in radices 2,2,4,4,4, retain zero and 255 witnesses, and preserve const evaluation and u8 range. Keep per-consumer casts and signed arithmetic unchanged. Finite exact scalar equality is the core proof; integration still checks that replacement does not accidentally alter table/class indexing or charge selection.

**Cheap falsification before a long collection.** In a later authorized isolated trial, inspect generated code for representative activity/pawn/guard call sites: the shift/mask/add chain should disappear, the immutable payload should be 256 bytes, and no map expansion or runtime initialization should appear. If compilation duplicates large tables, retains the arithmetic, or introduces extra consumer work, stop and explain that compiler result. After semantic checks, use the established fixed generic six-case balanced pilot; do not broaden the corpus merely to rescue a flat result. If CPU benefit is weak with broad overlap, park it. A lower simulated Ir result alone does not select it.

## Rank 2: exact pressure-mark value lookup

**Bounded code hypothesis.** In activity.rs:388-393 replace only `pressure_value(mark)` with `i32::from(PRESSURE_VALUE[mark as usize])`, using an immutable `[u8; 256]` generated from the current formula. The maximal unmasked value is 112, so u8 stores every result; the helper still returns i32. The callers continue passing `marks[...] & mask` or `marks[...] & 3`, and continue owning their geometry, admission and accumulation. Initial trial scope is activity.rs only.

The marks are eight presence bits for weak/strong knight, bishop, rook and queen combinations. They are not influence profiles or relation classes. Identical marks remain ORed; weak and strong bits may coexist. Zero-category direct destinations still mark weak; additional rays never mark. Orthogonal/diagonal/knight masks, absent-piece gates, exclusion of attacker occupants, inclusion of the first defender occupant, final subtraction of 12 and clamp all remain at the current owners. No mark update, mark lifetime, R charge, rounding or traversal order changes.

**Measured attribution and uncertainty.** activity.rs:389-392 directly attributes 25,021,735 + 13,140,875 + 11,016,706 + 16,525,059 = **65,704,375 simulated Ir**, 0.5662% of the lifetime, to the scalar weighted-bit expression. The raw profile additionally attributes 66,100,236 Ir in activity::compute to Rust uint_macros.rs:85, 33,460,068 at :1816 and 1,641,342 at :572. The first is plausibly the lowered count_ones work; the compiled Rust source path is absent locally, so this review does **not** claim that mapping as established or add the whole 101,201,646 uint_macros function-file row to the helper's envelope. Some of that row belongs to other operations. A source/machine-code mapping in the trial should settle it before assigning a larger removable share.

The 65.7M direct-source figure is a measured attribution envelope for identified rows, not a hard total-cost ceiling for the helper, because intrinsic work can be attributed elsewhere. A table adds a dependent load, and small masked inputs may already compile efficiently. The CPU sign is unknown. Do not claim a 1.44% opportunity by adding the entire uint_macros row to these lines.

**Proof obligations.** Exhaustively compare all 256 entries against a simple independent per-bit weighted sum with weights `[16,24,8,16,8,16,8,16]`; this independently checks the original two popcount masks. Also cover repeated OR of the same mark, coexisting weak/strong marks and each caller mask. Existing broad coordinate-oracle complete-activity comparisons should preserve pieces, pressure, weighted values and exact relation counts, including transparency/own-blocker/reflection cases. Do not fuse table creation with mark accumulation in this experiment: that would introduce different ownership and repeated-mark semantics.

**Cheap falsification.** First inspect the isolated emitted code to establish which count_ones work actually disappears and confirm a small immutable payload with no runtime preparation. If most arithmetic was already folded away for the constant caller masks, the proposed opportunity contracts. Then use the same fixed balanced generic pilot and park a flat/noisy result. Keep this trial separate from rank 1 so a favorable combined number cannot conceal a loser.

## Downstream validation and decision boundary

Neither candidate warrants a layout/restoration redesign. A later implementation should retain exact source/archive and generic artifact identities; run the finite scalar controls, relevant existing native tests and existing broad differential activity controls; then pass all 54 strict work replays, diagnostic/adapter checks relevant to changed consumers and interruption checks under that artifact. Do not create tests that simply reproduce the table generator as their oracle.

For a materially positive generic result, independently train each finalist's own PGO profile and compare complete native lifetimes against the current separately validated control. Record exact artifacts, training/workload identities, matched order, raw samples, per-case distributions, CPU/user+system and wall boundaries, logical work and interference. Use vCPU14 for measurements with sibling15 idle and housekeeping CPUs 0-5,8-13 for helpers, following the repository policy; no measurement was run in this review. PMU instructions/cycles, if available under the existing approved setup, are complementary evidence and must be reported separately from Callgrind Ir. A combined finalist needs its own interaction comparison, fresh canonical build and verification. Generic/isolated gains, historical results and qualification do not transfer to a new artifact.

My priority is rank 1 first, rank 2 only as another small bounded experiment. Neither should be enlarged into a general evaluation cache if the pilot is flat. The parent may instead prioritize remaining conformance/production evidence; the present data supports these experiments' small state risk and finite proof scope, not an assurance that they will be consequential CPU wins.

## Audited identities

Paths below are relative to `/home/legolas/rook2` unless absolute. These are current bytes read or identity-checked during this review. All 43 native/build source entries were checked against the retained provenance with zero mismatches; source-content review concentrated on the listed hot helpers and their consumers. Evidence hashes bind the stored files, not a newly repeated experiment.

```text
92da23830dd55e4073d227f7989339a4933f13a0844f2a50e49884466d12da39  AGENTS.md
05b402b7e0137720d5fb4d2f062601ebf5abf61411fe648531cdc94e2959843e  src/influence.rs
07d1b062f5ce6a4ffb66bd57eb3570f9221f42d7105b1df1f11e3039caf93c38  src/activity.rs
9d44681cf9098548a32ae06463bdb4e769c4e20eff9ac175ba725afae6a0ac50  src/attacks.rs
582a2e8ad2672a937062ae829ae596ee263b69c6ec52103c55c658a6ecc225f1  src/geometry.rs
2a202da079b16b3becb6651427701ec8e40aed88bd19550854c800b842b22feb  src/types.rs
9e645384baf5177697c5125df2e15db70eefac440ed63289435adddf6a514617  src/movegen.rs
8c11bb2a3469c0a431900ff9b7613d30a89913bcb6094dc0cf29f5c61683f6a9  src/tactical.rs
41f5b0c8b5e5923dab8a69c4aa7c9dea80d7401225ed4f82f5e0f6701bf71305  src/pawn_terms.rs
a79ec111e2d34bb9e4a3c2a7953c5b2a82b011016982fd2b63d6769da3036bf6  src/ordinary_policy.rs
07ed6db1af2d7fc21f093aa619f5a931aa32d594f4c1b435968ad95691b8bda4  src/quiescence_policy.rs
41faeff304b6e4ba8d3b577e1036af372313a4b6d3cdc9a95e017b82d6d531c8  docs/decisions/0001-initial-architecture.md
ed5825b220fdf1027130883336a3a88961b8bcf513a5f88f6c32eac32b0e08ac  docs/decisions/0002-geometric-legality.md
11254445adcfc58debd0cffa19dac8837604432a412d42fe7b73a6b99eee9a7e  docs/decisions/0003-shared-evaluation-geometry.md
276967f7032d1bb5fb806061e3782e064befb6e2fa8f80243d2e76cf650b0d3f  docs/decisions/0004-persistent-attack-planes.md
c71e54872caf720ea6b65c2b10c8214fd1eead572c812ca1122888adf518455f  docs/decisions/0005-compact-relation-kernel.md
593cd34688117c51b767c6d5a4700a33b82bfad73a82fe4b8086794e8d53ae1a  docs/decisions/0006-typed-influence-enumeration.md
7cd3c64da13de60ce8a92cae14ccd3be22672098d9701a359d71b7dba3cc97d8  docs/decisions/0007-static-activity-kinds.md
053c6c1702e11e3ceb692c69c6d10a162eaa1e8eeb8e55d0daec47199260775c  docs/research/remaining-performance.md
b09a6f89268b0c09d4ef25ff19ba53dfc370dd92e4c9a3d028d8821a07b13921  docs/research/influence-design.md
858cdbef85adae6c15dba6027470edceb2ba88d8764947344816cb911a9ee7bf  docs/research/evaluation-review.md
9990111619222e74aee3e5d944cd08d7f3a6182eb0ef7c3c1c04d742f52e281a  evidence/callgrind-activity-specialization-20261018/provenance.json
3857965340bdaba2c4761907472a264b658a329f21be4026e590e761c64e5339  evidence/callgrind-activity-specialization-20261018/plan.json
18ba9d53f522ffaa1853bf776208a38f3b675f0748a64a83ad46c308c60b4ee2  evidence/callgrind-activity-specialization-20261018/profile.py
f512b4dc32493ee906694e2593fabaa309f7a0bafba300f9a24c5be341842495  evidence/callgrind-activity-specialization-20261018/profile-01.callgrind
b9038211cf22e0f0ec00372b182002f1a7892dd47a6d3df1e5ae0edf1782213e  evidence/callgrind-activity-specialization-20261018/profile-01.log
452d9430fc065db94fffd2c3ccf0aaa788fb73ad683131dbfafa46d2efbe615e  evidence/callgrind-activity-specialization-20261018/profile-01-oracle.stdout
608b9e0d094beeaaebf8e07184d7f7d4ff000e097184d1ed4503f8709ca72fe4  evidence/callgrind-activity-specialization-20261018/functions.stdout
95ff89f216228faeab64b9187a19e018e9439af721f555b6d91da787f665b065  evidence/callgrind-activity-specialization-20261018/activity-lines.stdout
f31fb8acf5b615708474a73dc760394194f068ce4a3623de9863389bf7cc4344  evidence/callgrind-activity-specialization-20261018/influence-lines.stdout
5b351f4593bffc09749da3620233a093b33e87fb3626e24d1bca524c59899a45  evidence/callgrind-activity-specialization-20261018/movegen-lines.stdout
145970c7305a85423d813c72025526f379d2543db05b4cf9d935abf86a680528  evidence/callgrind-activity-specialization-20261018/position-lines.stdout
f9190835ff5c0a1861195086053285da9a9b3ff55491c1f92afa11d79f11a252  evidence/callgrind-activity-specialization-20261018/shelter-lines.stdout
74b8793052d559de9258f522f62afe2e89b271ac599dd5f48fe136ccd861067b  /home/legolas/imp-perf-mission.md
7d1f7acb4d14f9f6e9cee4eed9c35ddce4edb32e244925adc65857841617aec5  /home/legolas/king-spec/AGENT.md
fcdc2472609d076b6eba7023ccb5b469a3c2a6b100eeff5a087f6908bafc192c  /home/legolas/king-spec/spec/activity.md
e137fe2d998dcd8e7077c08596c88480046a272b871e317ab93207b1e07f7dca  /home/legolas/king-spec/spec/evaluation-relations.md
5a9bc099edf466f9c07bc2b931286eef0f2918f0dac2797483e4d51d7daa4f75  /home/legolas/king-spec/spec/king-pressure.md
5baa58c51eebf8f6bcda855b1ae305525ce88b2344fe8124cf44331c1a1fec74  /home/legolas/king-spec/spec/quiescence-candidates.md
```

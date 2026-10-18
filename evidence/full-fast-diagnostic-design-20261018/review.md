# Full/fast diagnostic family — bounded design review, 2026-10-18

Read-only recommendation from `/root/score_context_transport` to `/root`; parent retains architecture/sequencing decisions. Source reference is `/tmp/imp2-eval-pawn-observers-20261018`, not live root. Parent reported native 135 passed, with the proposed 79-operation / 4521-case / 86-unit diagnostic combination still pending when this review was assigned; live root remains the parent-described native43/old8d baseline. This review independently claims no passes. No source edits, builds, tests, rustc, engines, profilers, Herdr, advisor consultation or subagents. All shell work ran with affinity `0-5,8-13`; only this memo was written.

## Exact required family and observation size

All six operations are mandatory under released spec/README.md: only the two named analysis routes are optional. Each occurs in exactly the complete fixture named below. The family is **6 operations / 768 cases**, with **12,343 expected result records** inside those cases. Result records and nested queries are not additional fixture cases.

| Operation | Whole fixture | Cases | Result records |
| --- | --- | ---: | ---: |
| `evaluation.freshSubtotal` | `evaluation-subtotal-v1.json` | 54 | 585 |
| `evaluation.freshScore` | `fresh-score-v1.json` | 62 | 546 |
| `evaluation.retainedSequence` | `retained-evaluation-v1.json` | 84 | 1818 |
| `evaluation.moveSequence` | `evaluation-moves-v1.json` | 102 | 1894 |
| `evaluation.quiescenceEntry` | `quiescence-entry-v1.json` | 348 | 5704 |
| `evaluation.quiescenceDisposition` | `quiescence-disposition-v1.json` | 118 | 1796 |

FreshSubtotal has 1..512 independent queries, each with root/current placement, rootSide/sideToMove, all eleven own/opponent percentages 0..1000, averageDepth -100..100 and complete explicit current pawnOrder. Placements use the broad bounded pawn-candidate domain, including adjacent kings; no history or supplied phase/check/subtotal is admitted. Output includes both phases, geometric inCheck, all ten components, positional subtotal, base, retained pair/age and R. The 54 fixture cases contain 585 queries.

FreshScore has the same 1..512-query context plus cfd -10000..10000, sop 0..100 and reversiblePlies 0..255. It adds produced current placement identities, primary XOR secondary variation identity, root-produced preference/range, and all finishing intermediates/bounds around the complete nested subtotal. Its 62 cases contain 546 queries. **Do not apply the standalone finalScore +/-10000 late-input admission check to produced fresh scores.** Forced recomputation must bypass even zero/full-identity cache matches; clearing a PawnCache then calling ordinary full is not equivalent.

RetainedSequence has fixed request settings rootSide/percentages/averageDepth/cfd/sop and 1..512 positions. Each position supplies kind full/fast, placement, sideToMove, complete pawnOrder and reversiblePlies. First kind is full and first side equals rootSide; first placement fixes root. No retained pair, phase, identity override, clear or per-position settings are supplied. One native evaluator/cache persists. Full replaces the pair and resets age; fast neither probes nor changes pawn cache and preserves the pair. Age is zero throughout because these artificial position changes are not moves. Full uses identity matches, group replacement and cleared zero identity exactly; supplied order changes affect only misses. Full R is actual current pawn+activity work, fast R=0; pawnEntryReused is the actual full selection Boolean and null for fast.

MoveSequence fixes context from normalized six-field setup FEN and accepts 1..256 legal ordinary/null `{move,kind}` steps. It publishes initial full plus every step. No per-position order/counter/retained inputs are allowed. Native ordinary children inherit pair and increment age modulo256 regardless of capture/pawn counter reset; full resets age, fast preserves it. Null requires neither king checked, preserves placement/order/fingerprints/squares/pair, flips side, clears EP and wraps both counters. State and inherited pair/age are observed before selected evaluation; retained is observed after. Continue through repetition/reversible/age thresholds. Setup/continuation retain the bounded move-sequence per-type capacities and actual legal move/promotion/EP rules.

QuiescenceEntry takes the move-sequence setup/settings, 0..255 history transitions, one mandatory final legal non-null move, and -10000<=alpha<beta<=10000. Final side must be non-check. It publishes initial/history/final records; only the last adds selection `{initialKind,fastScore,refreshed}`. Sparse normalized current material chooses immediate full with null fastScore. Otherwise actual finished fast score controls strict alpha-250/F/beta+250 refresh, with capture exception classified on the **parent before the final move**; promotion qualifies, empty-destination EP does not qualify merely for removing its off-destination pawn. Fast-then-full records selected full and actual preliminary fastScore. R remains selected actual full R or zero, not a cost estimate.

QuiescenceDisposition has exactly the same input and sequence, adds final selection and final disposition. Production priority is lower>=beta, then upper<=alpha, then score>=beta, else tactical; report exact bound/score and reason, including equality, without window clipping. This adds no evaluator/R work and stops before tactical generation.

These six contracts specify position/evaluation records, not recursive node trace or SearchID/work-clock samples. Full R counts repeats, including pawn and general activity; phase/material/check/squares/central/shelter/patterns/finishing add no R. Derive check geometrically using native movegen::in_check/AttackBits, not evaluation influence or pinned-piece legal filtering. Validate every supplied schema/dependency, including ignored king percentages, before stateful selection. No external retained pair is accepted by this family: all reused values must be produced by its earlier full evaluations.

## Native ownership and the actual gaps

- `evaluator.rs:16..93` owns Retained/Node root, ordinary child, null child and incremental nonking squares. Components at line206 own the ten terms and rounded positional/base summation. `Parameters::bind` at169 already fixes root values/weights/preference/range; public new + assigning Parameters + begin_search suffices for controlled initialization. Do not expose private weights/cache merely to reimplement binding.
- `fresh_observed` at294 and `full_observed` at285 share `full_impl` at303. The FRESH constant chooses actual fresh construction versus private cache selection. Existing callback exposes Components; native computes material, pawn terms/progress, activity/shelter, central/patterns, tempo, pair assignments and R. Opening-only progress short-circuit returns the required zero weighted term without R. Keep this shared owner.
- `finish` at398 calls public `endgame::finish`, whose Finished at502 contains adjusted_base, late_score, scaled_score, score/lower/upper. Evaluator currently discards its first three fields. `fast` at425 computes the actual current base internally and reports no base/detail observer. Ordinary full selection Boolean is also private inside full_impl. **These are visibility/observation gaps, not missing evaluator algorithms.** Returned Evaluation.relation_queries is per-call R; avoid cumulative stats as output.
- `select_noncheck` at448 already owns sparse admission, actual fast stage, strict window refresh, lazy influence and replacement full stage; Selection exposes initial/full/fastScore/refreshed. It currently calls unobserved full/fast, so final base/finishing details/reuse are inaccessible along this exact stage path.
- `quiescence.rs:209..217` owns ordered bound/stand-pat returns inline. Parent capture exception is public `quiescence_policy::capture_exception`. The incoming alpha must be used before the later lower=max(lower,score) update.
- Existing frontend positions::{placement,sequence_position,advance_with_move,state} provides bounded parsing, normalized setup, legal move validation and state serialization. For artificial explicit pawn order, validate complete membership once and copy only the pawn prefix of public Position.squares (P,N,B,R,Q,K grouping); Position::validate can check invariants. Native fresh/cache miss then consumes that exact chronology. Board/counts/attack planes/fingerprints stay intact, and cache hits naturally retain their prior descriptor order. A cold position-order helper is sufficient; no new hot cache-order argument is needed.

## Alternatives and preliminary recommendation

**Prefer a narrow native detail observer shared by real full/fast calls.** Keep hot Evaluation and Retained layouts unchanged. Existing full/fresh observation can be extended through a statically dispatched no-op default or a parallel detailed wrapper over the same generic core. Observe the existing computed base, selected reuse Boolean and single native Finished result; keep Components for full. Add an observed fast wrapper over the same base/finish owner. Provide an observed selection wrapper whose actual full/fast stages feed those same details; do not copy the sparse/window rules to the adapter. JSON, arrays and strings remain wholly cold. Expose only native values, with pawn reuse absent for fast. No-op production monomorphs should erase observation, but production code generation/cost must be verified after extraction; this is not assumed from source alone.

A zero-native-change bridge could use Components plus a second cold native endgame::finish call and stats deltas to reconstruct full details; fast would still need a base seam or duplicated arithmetic. It adds unreported actual arithmetic and binds observation to diagnostic stats. It is inferior as the durable design. Reimplementing full/fast composition from public kernels in the adapter would duplicate tempo/base/lifetime policy already owned by production. Exposing evaluator.pawns or adding runtime dynamic callbacks increases ownership/hot-state risk without a contract need.

Extract the three ordered static returns to a small native quiescence-policy helper returning a native action/reason/score enum, consumed by visit_q and the cold disposition route. Keep tactical continuation/window update in visit_q. This extraction touches a hot branch sequence and needs exact return-priority/equality and native conformance/performance checks. Calling search_subtree/run_iterations instead is unsuitable: those enter draw/reversal/terminal admission, charge nodes, touch learned state and can generate/search candidates, beyond these admitted evaluation contracts.

## Smallest useful sequence of batches

1. **FreshSubtotal + FreshScore: 2 routes / 116 cases.** Introduce the shared detail/finishing observation seam and cold explicit pawn-order transport. Use fresh_observed, native geometric check, native Components and actual Finished. Keep root/current contexts independent. Exit checks: all nested components/R, both colors, broad placements, zero/collision forced-fresh behavior, high percentages, late produced bases beyond the standalone diagnostic domain, bounds independent of reversible score scaling.
2. **RetainedSequence: 1 route / 84 cases.** One evaluator initialized once; ordered positions create current nonking square state under fixed root while carrying only produced pair/age. Use ordinary full/observed fast; no begin_search between positions. Verify fast does not populate/evict pawn state, reversed order on hits, collisions/zero identity, pair preservation versus finished scores, and null reuse reporting. Recomputing nonking squares for these independent controlled positions is appropriate; mutating node.position while retaining stale square state is not.
3. **MoveSequence: 1 route / 102 cases.** Reuse the same evaluation record writer, but generate state with Node::child/null_child. Resolve/validate legal native Move without reparsing/rebuilding the final board; existing advance_with_move may be split cold to avoid computing a child twice. Preserve setup normalization, chronology, special moves, modulo counters and inherited/pre/post ages. No search history admission is added.
4. **QuiescenceEntry + QuiescenceDisposition: 2 routes / 466 cases.** Reuse forward-state harness, native parent capture classifier and observed native select_noncheck; add the shared static disposition helper. Check immediate full, fast-only, fast/full strict endpoints, parent/EP capture distinctions, and bound/stand-pat priority. Never run tactical generation for tactical disposition.

Only after actual passes would a 79/4521 baseline become 85 routes / 5289 selected cases. Unit counts are not predicted here. Search.quiescenceTree remains a separate ten-case recursive project: its contract requires enter/leave nesting and per-node arrival/parentRetained/full-fast stages/departure with work samples, including empty stages on early returns and branch-local pair restoration versus shared pawn lifetime. The proposed evaluator observer can support later stage recording, but aggregate Outcome/stats or these six sequence records cannot satisfy that trace contract.

## Hash anchors

SHA-256 identifies files read from the stated source/spec snapshot. Fixture counts were obtained by JSON inventory only. Whole-file exact hashes for the six contract/fixture pairs:

| Contract file / fixture | Contract SHA-256 | Fixture SHA-256 |
| --- | --- | --- |
| `evaluation-subtotal.md` / `evaluation-subtotal-v1.json` | `7371fd7c55ebc428c308bc86d21027dfb4ad577402559cf39069f990c4ab769f` | `503754a1cccce4b01fa63229becc775b5c47e4528e75d88500f5fb92c2717bcf` |
| `fresh-score.md` / `fresh-score-v1.json` | `f617a6596ae7013cc03fe16a58d917648f5e85d0c644e406f00ff291387764a8` | `68ffac23a0ee4fd917b13535af5c1fd5eff6ceffd35bb45f3e36883301f1453a` |
| `retained-evaluation.md` / `retained-evaluation-v1.json` | `074c4557bc48afa10cfc81c31041570824e4dabde95f0050a8f04aa535e621be` | `886b1c03da2724a314c0ea792de56e1f4f964940e8dd79c57477444992a2ca08` |
| `evaluation-moves.md` / `evaluation-moves-v1.json` | `57b43c558541af1abdb78edf28915865fb2cb7c971687a0ee9dbe75727124ac1` | `c1ccbbac5f8579c9f2f07386f1c3691100cc47c27dd322328d40655c3659ec1d` |
| `quiescence-entry.md` / `quiescence-entry-v1.json` | `ed3dd9c21c7e7da047fd0928afb67c3bd438bbaead3f43c36db006c2d1676056` | `ee8307aa06ab68eea80c40b6fcbbd92a08bd8437af9486810f2d0766ffef339f` |
| `quiescence-disposition.md` / `quiescence-disposition-v1.json` | `301834e41320dd92b31b963d6169dd243a6f0e3533ec1b2cf3f341a7330fbd81` | `d488763240987edbbe8a9d319c6736725374128963c5914ad1f38377263cd379` |

Core source anchors (relative to the named source reference):

| File | SHA-256 |
| --- | --- |
| `src/evaluator.rs` | `68e44e7a7af1349934423679f4717c281fc437c050ee0ccb93f66b808296535e` |
| `src/endgame.rs` | `4f382e7b5359f1956a0e155328aad08f35dab74252ee0794d61dafcd1cd2214a` |
| `src/pawn_structure.rs` | `b9d0921514c5ba7ba7532f07501fae7dc38b707f6c2f2f0bb01787be5263be13` |
| `src/position.rs` | `749f9fa1e90684c4df670c115c3c7f7dbdb196cf62b5eb267900ba217143ce3a` |
| `src/attacks.rs` | `9d44681cf9098548a32ae06463bdb4e769c4e20eff9ac175ba725afae6a0ac50` |
| `src/quiescence.rs` | `dddd6a260805a7a53ee61ceb74141cb52f9a3fdc899f2350412ffa86be439e33` |
| `src/quiescence_policy.rs` | `07ed6db1af2d7fc21f093aa619f5a931aa32d594f4c1b435968ad95691b8bda4` |
| `diagnostic/src/positions.rs` | `a3769d0728ba81d9423344e37ccec524a6aac1307ac2cd0b4af4185bbaafb52a` |

Additional reproducible reviewed-file bundle identities use SHA256 of UTF-8 lines `relative-path + space + lowercase-file-SHA256 + newline`, in the following listed order. Source bundle: `8261a2b018af6d3f48fd17a8d4f50d054305d2ff846a6456e2e9a98a551c0068`. Members: `src/evaluator.rs`, `src/evaluation.rs`, `src/endgame.rs`, `src/pawn_structure.rs`, `src/pawn_terms.rs`, `src/pawn_progress.rs`, `src/activity.rs`, `src/shelter.rs`, `src/positional_terms.rs`, `src/position.rs`, `src/movegen.rs`, `src/attacks.rs`, `src/quiescence.rs`, `src/quiescence_policy.rs`, `src/lib.rs`, `diagnostic/src/positions.rs`, `diagnostic/src/pawn_retained.rs`, `diagnostic/src/pawn_subtotals.rs`, `diagnostic/src/scores.rs`, `diagnostic/src/main.rs`.

Spec bundle: `2d7efb5daccc47baf26cf0eccc88c414e5daa33e85f6111089a408b66c6dac9d`. Members relative to `/home/legolas/king-spec/spec`, in order: `evaluation-subtotal.md`, `fresh-score.md`, `retained-evaluation.md`, `evaluation-moves.md`, `quiescence-entry.md`, `quiescence-disposition.md`, `README.md`, `diagnostic-interface.md`, `position-setup.md`, `move-sequence.md`, `position-identity.md`, `retained-pawn-structure.md`, `search-pawn-sequence.md`, `quiescence-tree.md`, `work-clock.md`.

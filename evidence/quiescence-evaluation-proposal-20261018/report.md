# Quiescence evaluation entry/disposition — cold proposal, 2026-10-18

From: native child fresh_pawn_transport. To: parent imp2. Sol 6.1 High / Normal requested; actual speed readback unavailable.

## Delivery and execution boundary

New source: `/tmp/imp2-quiescence-evaluation-20261018-native-child`. It is an isolated copy of the frozen retained82 source `/tmp/imp2-retained-evaluation-proposal-20261018-uz57d6p0`, excluding target/evidence/.git/__pycache__. Only this new tree and this new evidence directory were written. The source identities of the frozen base were rechecked at handoff against the initial copied manifest and remain unchanged. Completed sibling proposals, root source/diagnostic and receipts were not modified.

Only `evaluation.quiescenceEntry` and `evaluation.quiescenceDisposition` are added. There is no moveSequence route, recursive Q tree, history admission, tactical generation, ledger, session or other operation in this batch. No builds, tests, rustc, engines, profilers or formatter ran. Ten diagnostic and three native test sources remain unexecuted. All shell/helper work used taskset 0-5,8-13.

Apply `quiescence-evaluation.patch` to retained82, or apply both `native.patch` and `diagnostic.patch`; do not apply both alternatives. Exact patch SHA256 values:

- `quiescence-evaluation.patch`: `f5807c48f9cf9871b3c2216be9c02a8894325b30f7f2f83bd3f3f29e62d01621`.
- `native.patch`: `c0f14de512cd710f25e6855975e31b36539b80932f5558f0481d680b3bc663e7`.
- `diagnostic.patch`: `359e01adec8db927e6affef5f7e10c584803f26fa95b11fdd7b099f0cf93894f`.

`base/` preserves the pre-edit tree. `base-source-sha256.json` and `proposal-source-sha256.json` identify all copied/proposed files. `changed-source-sha256.json` records the complete five-file change set. `selection.json` contains exact contract/fixture hashes and complete case-index/ID/result-count selection.

## Native owners and bounded seams

`Evaluator::select_noncheck` retains its public signature and delegates to `select_noncheck_detailed_observed` with two capture-free no-op callbacks. The latter owns the original sparse-material, produced finished fast score, strict endpoint and capture-exception refresh rules. It invokes the existing native full_detailed_observed/fast_detailed_observed owners, delivering actual fast then full details on refresh. No selection, tempo/base, phase, finishing, pawn-cache or relation arithmetic is implemented in the adapter. Hot Evaluation, Retained, Node, Parameters and Evaluator state layouts are unchanged. The callback parameters are statically dispatched FnMut, with no native JSON or dynamic observer storage.

`selection-policy-source-comparison.json` verifies that the entire original policy body is byte-for-byte equal after mapping only the three detailed full/fast call wrappers back to their old full/fast calls. No condition, order, result or state expression was removed for that comparison. Ordinary production no-op erasure/codegen is not inferred from this source check; parent codegen/regression checks remain required for this extraction.

`quiescence_policy::evaluation_return` extracts the three ordered inclusive tests into one native owner: lower>=beta, upper<=alpha, score>=beta, otherwise None. Its EvaluationReturn variants retain the reason and exact unclipped value. Actual production visit_q now calls this helper inside its existing non-check branch before lower=max(lower,score). Checked production nodes still bypass the static evaluation policy. The cold disposition route invokes the same helper after native selection; it adds no evaluation or relation work and never generates tactical moves.

## Cold parsing, chronology and lifetime

The adapter validates exact request/history/settings maps, all eleven own/opponent percentages including ignored king values, depth/cfd/sop, signed window bounds and alpha<beta. No explicit order/phase/identity/inherited/retained/kind override is admitted. History is 0..255 explicit full/fast transitions; final move is a required legal non-null coordinate string with any required promotion suffix. Native normalized setup and existing bounded advance_with_move validate the complete legal path on cold Position copies before any evaluator/cache or evaluation stage exists. Null transitions require neither king checked. The final resulting side must be non-check, while ordinary earlier history evaluations may be checked and use actual geometric check context.

After admission, a single native evaluator is bound once to the normalized setup and configured Parameters. Node::root and Node::child/null_child own actual forward state, chronology, counters, incremental square values, pair inheritance and modulo-256 age. Full/fast history uses native detail owners; no begin_search occurs between positions. The parse-only cold path is replayed through these Node owners during observation so eager legality validation does not produce or mutate retained evaluation state. This intentionally performs cold move legality/transition work before evaluation; it does not alter the reported per-evaluation relation charge.

Immediately before the final Node::child call, native capture_exception reads that actual node.position and final Move. Promotion qualifies through the native predicate. An empty destination, including ordinary EP, remains excluded despite its off-destination victim. The final observed record uses the last actual detail callback, native Selection flags/fastScore, native retained state and selected Evaluation.relation_queries; no cumulative-stat delta or predicted charge is used. The initial/history/final results use shared finishing/retained serializers and positions::state. Initial placement spelling is retained at the state boundary just as the existing setup/move-sequence projection does. Each request creates independent cache/retained state.

## Exact fixture inventory

| Whole released fixture | Cases | Result records |
| --- | ---: | ---: |
| `quiescence-entry-v1.json` | 348 | 5704 |
| `quiescence-disposition-v1.json` | 118 | 1796 |

Total **2 mandatory routes / 466 cases / 7,500 ordered result records**. Counts are source inventory, not passes. Every case is selected unmodified and maps to its zero-based source index and released case ID in selection.json. No baseline or other-route cases are counted. This proposal would take an 82-route base to a planned 84 routes after successful execution; the independently owned moveSequence batch is not included here.

Released expected final selection classes across the 466 cases are immediate full 293, fast-only 41, fast then full 132. The 118 disposition cases expect tactical 88, stand-pat 10, upper-bound 14, lower-bound 6. These are fixture expectations, not observed engine results.

## Unexecuted focused checks and remaining work

Three native test sources cover observer stage order/default API/state/charge equivalence across both strict endpoints, interior refresh and capture refresh; sparse immediate-full suppression of fast; and ordered/equality/unclipped static returns. Ten diagnostic test sources cover sparse zero-identity reuse, both strict fast endpoints, actual refresh records, parent-victim versus empty-target EP, promotion/root-current phase independence and required suffix, 255 null transitions through counter/age wraparound without draw stops, disposition adding no state/work plus stand-pat, exact ignored-field/settings/limits admission, checked history before non-check final evaluation, final/null check and illegal-move rejection, and setup rights/EP normalization with reversible wraparound.

No unresolved contract ambiguity was found. Verification remains open: compile, run the thirteen new tests and relevant existing native/diagnostic tests, compare every field of all 466 fixture cases/7,500 records, and perform ordinary production codegen and execution regressions after the selection/disposition refactor. No timing, retired-instruction, CPU-neutrality or qualification claim is made.

## Changed source identities

| Relative path | Baseline SHA256 | Proposed SHA256 |
| --- | --- | --- |
| `diagnostic/src/main.rs` | `a273676fde9bdd3cc7eb9c273fdcfd7e7fd38094d9649e4ff1de3bd0865e18e5` | `aa5d34d9a6b07e1936770e975135f67dc6dfc4bd372b13ba8afba3daa34bbe78` |
| `diagnostic/src/quiescence_evaluation.rs` | `None` | `f07c0a3f18ae93521bd2f06b2ed3ec2220d0658ab96d9603a1f2771185cb86ee` |
| `src/evaluator.rs` | `248e8e782110bf596fc82bbf2bbf67e13492de1386a52792c6123ac076baf6bb` | `5e4bf312f549de36cb1ea1fd44a3798cc41a27e163df288cf8bb0b46fe233aeb` |
| `src/quiescence.rs` | `dddd6a260805a7a53ee61ceb74141cb52f9a3fdc899f2350412ffa86be439e33` | `1006c4a96307da25ccf96222afae2bdf21aa07b20852aedc30cb90a546e8c4b4` |
| `src/quiescence_policy.rs` | `07ed6db1af2d7fc21f093aa619f5a931aa32d594f4c1b435968ad95691b8bda4` | `baeb3f40c47f119481f0040b1c9bb15f9af25ee39376cf0c01d1a06091011468` |

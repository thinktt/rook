# Retained subtotal and fixed-root search pawn sequence — cold proposal

The proposal implements only evaluation.retainedPawnSubtotal and evaluation.searchPawnSequence against frozen85 at /tmp/imp2-move-q-evaluation-combined-20261018. The NEW isolated source is /tmp/imp2-retained-search-pawn-20261018-5hjoji3q. Only diagnostic/src/main.rs and diagnostic/src/pawn_subtotals.rs change. All 43 native manifest/lock/source files are byte-identical to the accepted85 native build reference: d38ff03745c7fba981c22f12fdd7b10b78f539f9541faeb24b92bd263b116d45, receipt 45631ac24e12ce8a1ea067b84665401c00591a10e21d01157afe12ec3367daf5. No native seam, API, field, layout or production owner changes are proposed. Root source, other prototypes and prior evidence remain untouched.

The adapter contains parsing, request-local ownership, native calls and JSON serialization. No pawn/material/phase/central formula or native selection algorithm is copied. native-owner-map.json names each existing owner. The supplied-context route parses all steps before creating its cache, then applies explicit clear immediately before that step's native selection. The search sequence parses every position, percentage and context field and checks first-side/root agreement before creating either context or cache. It binds root material/coefficients once from the first placement. One fresh PawnCache persists across each request's positions. No iteration, legal history or alternative search lifetime is inferred.

Cold sharing is narrow. Fresh::parse_fields shares field admission after each operation checks its exact object schema. selected_output consumes a native selected PawnStructure for both fresh and retained composition, calling compute_with_phase, selected and structure_weighted for all scores, rounding and charged work. ContextBinding extracts prior fresh-context RootContext::new/material and coefficient/central calls for use by fresh context and the new sequence. Complete percentage admission is also shared: every one of the eleven names, including ignored king/mobility/shelter fields, must be present and in 0..1000.

Native PawnCache::select_with_order retains full-identity/group/zero/replacement behavior and supplied order on misses. A later order is fully validated; a native hit keeps earlier descriptors. Native compute_with_phase retains base scores, filters current same-color membership for penalties, uses retained file geometry with current pieces/influence/material conditions, and owns phase gating/scaling and relation charges. Native selected filters retained candidates in retained order, performs current races, ending selection, fallback and weighting. Candidate serialization calls the same uncharged current_candidates owner instead of duplicating its filter. For fresh entries every descriptor still names its current pawn, preserving old fresh output. Every step performs its current native term work even with zero weights; no current result or relation charge is reused.

Search context uses current Position::phase, counts/influence and RootContext::material for every result. Root phase/counts, average depth and root-side coefficient ownership stay fixed. Produced coefficients through 10240 are carried directly instead of reparsing them through supplied weights' 10000 ceiling. The retained route keeps its independent supplied phase/material/signed-weight domains. Root/material/central add no relation charges. These routes report ending after native fallback; retainedPawnCandidates remains unchanged and continues to report raw ending.

| Whole official file | Operation | Cases | Result records |
|---|---|---:|---:|
| pawn-retained-subtotal-v1.json | evaluation.retainedPawnSubtotal | 202 | 8,724 |
| search-pawn-sequence-v1.json | evaluation.searchPawnSequence | 468 | 11,124 |
| search-pawn-piece-sequence-v1.json | evaluation.searchPawnSequence | 192 | 6,144 |
| New total | 2 operations | 862 | 25,992 |

selection.json records exact file hashes, metadata headers and every new case index, ID and record count. fixture-inventory.json unions the 79 accepted85 whole files with these three, yielding 87 operations and 6,151 cases across 82 whole official files, with zero partial files or duplicate case IDs. whole-fixture-case-map.json maps all 6,151 selected IDs to exact original file/index. No fixture is rewritten. The expected diagnostic unit inventory becomes 126: 117 inherited plus nine new test sources. Inherited native 140 library plus two development tests remains 142. These are inventory expectations, not execution results.

Nine unexecuted tests cover retained tied order, clear/request reset; real full-identity collision and stale base/file geometry versus fresh replacement; repeated-hit work across the 16/17 phase boundary with zero weights; both fixed root colors across current side/phase/count changes and produced 10240 weights; current piece movement on collision; pawnless zero reuse; eager late-step and ignored-field rejection; percentage/order/root-side/array limits; and broad artificial placement admission with bounded material rejection. Focused values come from released contracts/fixtures; no expected answer database enters runtime code. new_test_sources.rs and test-source-inventory.json retain exact new test text/names.

Exact identities:

- retained-search-pawn.patch, also diagnostic.patch: 082ba31908ea2ca3dd439f3c42679f47a2c8873b6cdd143f65a8da7056db382e.
- Complete 96-file proposal source manifest: 241ca8aacd3cf89baa7e70f1454f634e197cc58c8cc72b241474c115b006b037.
- Native 43-file manifest: 8fca8e9a0700998c6b2c4022a268e3985f0b852934334e33c076cd4051d905aa.
- diagnostic/src/main.rs: 2166ab1995991ebc4ae2b162050ff0e19e79ca44bce6d7cc2c2a45e48f632591.
- diagnostic/src/pawn_subtotals.rs: 5671ad2e6a045535788ca1e4c1ec14b234ba8cd06c6b5527e97134741c8209d9.

The source-only git apply --check reached actual chunk a5c678 / exit0 against the NEW archived85 base. Base/proposal/native source hashes were rechecked at handoff. No Cargo, Rust compiler, build, unit test, engine, profiler or binary-inspection job ran. All shell helpers used CPUs 0-5,8-13; final-process-check.json records no owned native jobs. Work remains source/text-only through the parent's measurement boundary. Normal/High requested; actual speed control/readback unavailable.

Rust syntax/types and behavior remain unvalidated. Parent-scheduled checks should execute all 126 diagnostic test sources and the exact 82-file/6,151-case union, including old fresh/context routes touched by the cold extraction. No behavioral pass, CPU-neutrality, complete evaluator or search qualification is claimed. Parent owns review, freeze, validation scheduling and integration.

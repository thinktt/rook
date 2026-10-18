# Generation transports: bounded source-only plan

Reviewed 2026-10-18T10:07:35.845217+00:00 on affinity [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13]. Parent is running serial CPU pilots. This task made no implementation or native source edits, builds, tests, engine/profiler/timing runs, binary scans or archives. The only new artifact is this memo. Frozen88 and king-first sources were read, not modified.

The two routes can share existing native producers and orderers. The sole missing native observation is exact semantic check classification for the ordinary-production output; native checker discovery is private. Recommend a narrow read-only classification query around the existing finder, with no production/default-kernel refactor. All other proposed changes are cold parsing/common-state/output extraction. No implementation is authorized in this task.

## Exact schema and domain

`search.produceAndOrderCandidates` requires exactly `fen,moves,ply,values,squareAdjustments,history,hashMove,killers`, with one optional key `orderingMode` whose only admitted value is `"quiescence"` (explicit `"ordinary"` is not admitted). FEN/setup and chronological legal moves follow POSITION-SETUP-MOVE-SEQUENCE, except moves may be empty; moves length0..256. Ranking ply1..62 is independent of move count. Context values are white/black objects with pawn/knight/bishop/rook/queen integers0..10000. Square adjustments have0..768 unique side/type/square keys, no king, signed value-128..127 and material+adjustment in-10000..10000. History has0..768 unique side/type/square keys including king, unsigned32 values, absent keys zero. Killers are exact current/twoPliesEarlier pairs of descriptors/null; the earlier pair must be null/null at ply1/2. Hash/killer descriptors need not fit the position. All fields and remembered descriptors validate even in quiescence ordering mode.

The optional quiescence mode requires moves=[], the normalized current moving side in check, hashMove=null, and both killer pairs null/null. It still derives the complete legal list, including all four promotion choices; it changes only the ordering rule. It is a mandatory domain of the same operation, covered by the3 evasion fixtures, not an additional diagnostic route.

This producer's normalized initial position has two explicit local restrictions: the nonmoving king is not attacked; any retained EP target has the moving color's ordinary target rank and an opposing pawn immediately behind it. Apply them after setup and before history. Do not impose them globally on POSITION-SETUP, ordinary joined ingress or native generation. Retain native setup normalization and move chronology; do not reconstruct order from the final placement. The complete generated list must be <=230; overflow is an error after full production, never truncation. Final check and empty-list terminal classification are semantic output: none/single/double, then none/checkmate/stalemate.

`search.quiescenceCandidates` requires exactly the9 quiescence-disposition fields `fen,percentages,averageDepth,cfd,sop,history,move,alpha,beta` plus `orderingHistory`. Its two percentage objects have the existing exact11 personality keys in0..1000; averageDepth-100..100, cfd-10000..10000, sop0..100. History has0..255 exact `{move,kind}` transitions; kind full/fast and move a legal coordinate or diagnostic null, subject to the existing null safety guard. The final move is legal and nonnull; its resulting side must not be checked. Window is -10000<=alpha<beta<=10000. History length is not recursive ply. The fixed root context, root/current phase separation, retained pair/age, one native pawn cache, actual pre-transition capture exception and full/fast refresh must stay owned by the existing evaluator path.

orderingHistory has0..768 exact `{side,piece,square,value}` entries, unique across2 colors/6 types/64 destinations; value unsigned32. It is separate from the evaluated transition history and does not learn or sum entries. Validate every entry before evaluator/cache creation, including when static disposition later returns. This new consumer additionally applies the same normalized-initial nonmoving-king/ordinary-EP checks, without narrowing the existing quiescenceEntry/Disposition operations. It has the <=230 tactical-list domain and the provisional final-position bound: if the moving side has any penultimate-rank pawn, it has at most8 queens before generation. The plan treats that bound as the stated diagnostic input precondition, checked on cold final state before evaluation; if authority intends it only for a reached producer, that timing needs a domain decision before implementation. This is the only small admission-timing question identified; current fixtures do not decide it.

## Native owner map and missing seam

| Required behavior | Existing owner / proposed use |
|---|---|
| Setup, material limits and chronological legal path | Position::from_fen / positions::sequence_position, positions::advance_with_move, Position::played_unchecked and existing cold bounded_material. Expose admission::consumer_position as a cold shared helper, or extract its exact local checks; do not duplicate or move them into native gameplay. |
| Complete legal order and check-evasion prefixes | public movegen::generate_legal -> generate_bounded::<MOVE_CAPACITY>. MoveList capacity512 is storage, not diagnostic230 admission. Snapshot descriptors before any ranking. |
| Ordinary ranking | public ordinary_policy::priority, Influence::build, tactical::order_by and OrderingScratch. Reuse the exact supplied RootContext/Learning construction in candidate_order.rs. Native rules own all category precedence and wrapping. |
| Non-check tactical production | public tactical::generate; it deliberately keeps pseudo-legal king-exposing candidates. Do not call generate_legal or apply a child-safety filter here. |
| Shared Q preference/ranking | public tactical::order/order_with_scratch already calls private preference and common order_by. It accepts legal quiet evasions and all underpromotions too; no preference visibility change or formula in adapter is necessary. |
| Evaluation choice and static disposition | existing quiescence_evaluation cold replay with Evaluator::select_noncheck_detailed_observed and quiescence_policy::evaluation_return. Extract a cold final-stage callback/result carrying actual Node and evaluator/root context. Do not reconstruct typed state from response JSON or rerun evaluation. |
| none/single/double check label | only movegen::in_check is public; find_attackers::<2> and Checkers are private. Proposed one native read-only `check_classification(&Position)` wrapper using that actual finder at the moving king and returning semantic none/single/double (>=2). Keep finder's algorithm, existing generator calls, default Boolean kernel, Q trace and all layouts untouched. No checker identities or buffer representation need exposure. |

Native Q already chooses full legal generation for checked evasions and tactical::generate for noncheck continuation, then tactical::order_with_scratch. Ordinary already uses full legal generation and order_by(priority). Thus these transports compose current producers; they should not run Search::visit_q or visit_ordinary, whose draw admission, terminal/pre-order scores, candidate eligibility, child preparation, reply probes, king-safety checks and recursion are outside these component contracts.

## Order and lifetime preservation

Complete legal base order is castle long/short, retained pawns, knights, bishops, rooks, queens, king, with existing direction and promotion chronology. EP forms the fixed geometric prefix independent of pawn chronology; in single check the native pawn blocks/captures prefix follows, stably preserving the remaining base order. Copy the full native sequence unchanged into ranking. Native broad joined EP can remove a non-pawn checker while blocking a ray even under double check: do not import the standalone diagnostic's ordinary-EP restriction into that kernel or add a king-only double-check shortcut.

Noncheck tactical production has EP and quiet-pawn-direct-check prefixes; Black's tactical prefix source order differs from the ordinary legal EP prefix. Native tactical generation owns queen-only promotions, quiet-promotion-before-capture chronology, full direct moved-piece checking geometry, and the exclusion of discovered-only quiet checks/quiet king moves/castling/two-square pawn moves. No adapter sorting or legal filtering should disturb it.

Both native orderers preserve priorities0/1 in generated order, collect preferred>1 in reverse generated order, then use ORDER-PRIORITY-SEQUENCE: stable descending inside modulo6 classes, restore positions, then stable descending globally. This is not generic stable descending on the original preferred sequence and not universally later-first tie order. Keep prefix chronology before this composition; do not sort descriptors or replace the native permutation. Supplied synthetic unsigned history can outrank an earlier nominal category; selected priorities wrap and a wrapped zero does not fall through to another category. Q preference remains shared for ordinary evasions, including capture-promotion versus quiet-promotion precedence and original source-piece history keys.

The king-first candidate changes only LIMIT==2 checked probes. Full generate_legal still uses LIMIT512, so its complete observable order remains the frozen88 order. The capped result2 is a threshold witness list, not a prefix or complete candidate inventory. At result0/1 it is complete and is reused by the existing Q `complete_replies`/`replies_available` path; at>1 that child is rejected before recursive list consumption. Do not feed a capped result2 into any candidateList inventory, generatedCandidates, ordering operation or complete evasion consumer. Do not change this Q reuse/trace path to implement the new diagnostics.

## Action order, results and semantic charges

Production/order request: exact schema and context parse -> normalized setup plus local initial checks -> complete cold legal-history validation/replay -> derive check classification -> full legal generation -> reject >230 -> preserve generated descriptors -> selected native orderer -> serialize exact position/check/terminal/generatedCandidates/orderedCandidates/chargedRelationQueries0. An empty checked quiescence-order list is valid checkmate, not an opportunity to invent candidates.

Q request: exact10-key parse and ordering-history validation -> existing complete cold path validation plus this consumer's local guards -> create native evaluator/cache once -> initial full evaluation -> each selected history stage -> capture-exception classification in the actual parent -> final child/inherited capture -> actual full/fast/refresh choice -> native ordered lower/upper/stand-pat disposition -> only on tactical continuation run tactical::generate and shared orderer. Return existing results unchanged, plus top-level tacticalGeneration. On any static return it is exactly {reached:false}: do not execute production/order, and omit list/charge fields. On continuation it has reached:true, both full lists, additionalChargedRelationQueries0 and additionalChargedSearchUnits0. Empty reached tactical list does not classify mate/stalemate. No Node child or Search visit is constructed for candidates.

Generation and ranking add no semantic relation/search units. Ordinary priority's influence/adjusted relation queries are still uncharged at this boundary. Q results keep all actual evaluation relation charges, while the new region contributes zero. Physical CPU work is not inferred from those semantic zeros.

## Cold integration plan and later evidence

After explicit assignment, create a new isolated copy of the parent's selected combined baseline carrying validated king-first source. Extract cold supplied-ranking context/history parsing from candidate_order.rs while retaining its existing exact operation/domain. Add a produced-generation module and two dispatch routes. Extract the quiescence_evaluation final-state callback and candidate-only local admission mode without changing existing9-key schemas or their response values; parse orderingHistory first. Expose the exact existing local setup-consumer helper cold-only. Propose/review the sole native check-classification wrapper before adding it; no new hot observer, default generator switch or production call-site refactor.

Focused unrun test-source plan: exact keys and ignored-field eager validation; duplicate/u32 histories; ply1/2 killer restrictions; optional orderingMode restrictions; normalized local EP/nonmoving-king rejects without narrowing shared setup; chronology after captures/promotions; full checked order where king-first cap2 witnesses deliberately differ; generated empty checkmate/stalemate versus reached empty tactical list; explicit Q quiet-promotion evasions with pawn/c8 history irrelevant and king/b7 history effective; deferred0/1 and mixed preferred ties over6; real king-exposing tactical candidate retained; initial-full/fast-only/refresh results identical to the accepted disposition route; static returns never call production/order; new consumer's provisional queen capacity. Native wrapper test source should cover none/single/double and compare its classification with the actual native finder without replacing full-order checks.

Later parent-scheduled preparation should join all54 exact original case indices to the inherited case map, preserve whole-file headers, freeze native+adapter+tools closure, and independently reconcile original raw responses/exits. Test-unit totals cannot be stated until implementation is selected. No native/DIAG validation, codegen or CPU claim is made by this memo. The frozen earlier boundary proposal remains unchanged, including the two parent-identified raw-rights/stronger-validator defects to fix only in a later composed copy; none of its opaque equality-only flag bits should be reused for these native FEN flags.

## Whole-file inventory

All3 files are absent from frozen88's accepted83-file inventory. Every case in each must be selected. New IDs are unique across these54; the inherited full-ID reconciliation is a future preparation step, not claimed from reading fixtures alone. Against exact frozen88 alone the delta gives90 operations /6215 cases /86 whole files (88+2,6161+54,83+3). This arithmetic does not assume adoption of any other queued proposal and is not a full-goal inventory review.

| Whole official file | Cases | Operation | Header | SHA256 |
|---|---:|---|---|---|
| search-candidate-production-v1.json | 27 | search.produceAndOrderCandidates | `{"version":1}` | `f350490289e967032aeaa31588b69c73127c26cdf2c58abdb229b5e98bb54634` |
| quiescence-evasion-order-v1.json | 3 | search.produceAndOrderCandidates | `{"version":1}` | `790533b5e725a4c0139507d04e5cf06ebd9f94ee0a71a005886969b39be427f9` |
| quiescence-candidates-v1.json | 24 | search.quiescenceCandidates | `{"version":1}` | `206aec57b1f4081b91bf4f99c4aa07b028217ceb78c1f1bd4ef0037bddcf6e6c` |

The30 produce/order cases are27 default ordinary plus3 explicit quiescence evasion cases; the24 Q cases include all3 static returns, fast/full refresh variants, empty reached inventory, promotions/EP/pawn checks, original-backed unsafe candidate, threshold and mixed-tie order. No expected-answer content is copied into any runtime code.

## Exact source and authority identities

Frozen88: `/tmp/imp2-qtree-pawn-combined-20261018-73lk5tii`. Intended king-first source: `/tmp/imp2-king-first88-20261018-daksyrcp`. No other production changes are present in the7 focused native files except movegen.rs; the6 evaluator/order/Q policy sources match byte-for-byte. The movegen source delta is the LIMIT2-only king-early guard/skip plus2 new fixed native tests.

| Native file | Frozen88 SHA256 | King-first SHA256 |
|---|---|---|
| src/movegen.rs | `9e645384baf5177697c5125df2e15db70eefac440ed63289435adddf6a514617` | `be234c8950a0556f28324a7e2a342381534a546c5946777b983393f9dfb3413b` |
| src/tactical.rs | `8c11bb2a3469c0a431900ff9b7613d30a89913bcb6094dc0cf29f5c61683f6a9` | `8c11bb2a3469c0a431900ff9b7613d30a89913bcb6094dc0cf29f5c61683f6a9` |
| src/ordinary.rs | `446b518a5824a8a60b65666d1b841d959ab2964c995739a2bc44d27bd5a9c442` | `446b518a5824a8a60b65666d1b841d959ab2964c995739a2bc44d27bd5a9c442` |
| src/quiescence.rs | `4c5bbe10f07a8431c02dcc1401424f97126b470e9c40cb8e150c9364851b6187` | `4c5bbe10f07a8431c02dcc1401424f97126b470e9c40cb8e150c9364851b6187` |
| src/ordinary_policy.rs | `a79ec111e2d34bb9e4a3c2a7953c5b2a82b011016982fd2b63d6769da3036bf6` | `a79ec111e2d34bb9e4a3c2a7953c5b2a82b011016982fd2b63d6769da3036bf6` |
| src/quiescence_policy.rs | `baeb3f40c47f119481f0040b1c9bb15f9af25ee39376cf0c01d1a06091011468` | `baeb3f40c47f119481f0040b1c9bb15f9af25ee39376cf0c01d1a06091011468` |
| src/evaluator.rs | `11264fe907b8a10f54cb4bff7024266e14dcf345b23a75cc8c30bd2984e4c398` | `11264fe907b8a10f54cb4bff7024266e14dcf345b23a75cc8c30bd2984e4c398` |

| Cold file (frozen88) | SHA256 |
|---|---|
| diagnostic/src/candidate_order.rs | `ff085f7bdb52d13777b40147d3c0b62f69cf9ce33fc4250e6aea9516ffeff6f9` |
| diagnostic/src/quiescence_evaluation.rs | `f07c0a3f18ae93521bd2f06b2ed3ec2220d0658ab96d9603a1f2771185cb86ee` |
| diagnostic/src/admission.rs | `9a2939eb19dfdff9abf1d310a215f25701fdc32bbfff82a00f76569a4927ecf3` |
| diagnostic/src/positions.rs | `b66ce5ab499baa4a0c4605d28ed287704539d4903db5b5ef01c47b13a835a4fa` |
| diagnostic/src/evaluation_common.rs | `3eb352bafb64cf0a6f71d5cf8c69e3884190366f83ea8dc11293ee29e20fde9e` |

| Released authority | SHA256 |
|---|---|
| search-candidate-production.md | `d1e22f64f8a69783f9a88a1e5004e0493ede34bdeea103bf0ebf6e13a17e038e` |
| search-candidate-order.md | `40c319a50b17d4e054511b61a6af628e40a5d064269178fa1c4b068ef8c93798` |
| quiescence-candidates.md | `5baa58c51eebf8f6bcda855b1ae305525ce88b2344fe8124cf44331c1a1fec74` |
| quiescence-evasion-priority-example.md | `8e18d5b0f6c46489cdab3706bc1867a58bc9eec69341c00655675c18c5ae5fb0` |
| quiescence-entry.md | `ed3dd9c21c7e7da047fd0928afb67c3bd438bbaead3f43c36db006c2d1676056` |
| quiescence-disposition.md | `301834e41320dd92b31b963d6169dd243a6f0e3533ec1b2cf3f341a7330fbd81` |
| tactical-capture-order.md | `b34c0342bd6acf728c74d5afb51cbeb506c1d07888e43f51e99ef97e5f33e0e3` |
| position-setup.md | `93d94c7fdf8812b8a3eaabf4b66d796912bf53a994d406a107a6ca8e808cac3b` |

## Case selection appendix

`search-candidate-production-v1.json`: select all indices0..26, preserving original order:

- 0: `search-candidate-production-initial-white`
- 1: `search-candidate-production-initial-black`
- 2: `search-candidate-production-all-directions-white`
- 3: `search-candidate-production-all-directions-black`
- 4: `search-candidate-production-chronology-setup`
- 5: `search-candidate-production-chronology-swapped`
- 6: `search-candidate-production-promoted-queen-setup`
- 7: `search-candidate-production-promoted-queen-history`
- 8: `search-candidate-production-quiet-and-capture-promotions`
- 9: `search-candidate-production-both-castles`
- 10: `search-candidate-production-blocked-long-castle`
- 11: `search-candidate-production-attacked-short-transit`
- 12: `search-candidate-production-pinned-rook-filter`
- 13: `search-candidate-production-illegal-en-passant-self-check`
- 14: `search-candidate-production-dual-en-passant-white-reversed-chronology`
- 15: `search-candidate-production-dual-en-passant-black-reversed-chronology`
- 16: `search-candidate-production-single-check-blocks-and-capture`
- 17: `search-candidate-production-single-check-two-pawn-captures`
- 18: `search-candidate-production-single-check-two-pawn-captures-black`
- 19: `search-candidate-production-single-check-nearby-nonpawn`
- 20: `search-candidate-production-knight-single-check`
- 21: `search-candidate-production-double-check`
- 22: `search-candidate-production-checkmate`
- 23: `search-candidate-production-stalemate`
- 24: `search-candidate-production-ranking-equal-history`
- 25: `search-candidate-production-ranking-hash-killers`
- 26: `search-candidate-production-ranking-capture-preference`

`quiescence-evasion-order-v1.json`: select all indices0..2, preserving original order:

- 0: `quiescence-evasion-derived-omitted-history`
- 1: `quiescence-evasion-derived-pawn-c8-two`
- 2: `quiescence-evasion-derived-quiet-king-history`

`quiescence-candidates-v1.json`: select all indices0..23, preserving original order:

- 0: `quiescence-candidates-static-lower-bound`
- 1: `quiescence-candidates-static-upper-bound`
- 2: `quiescence-candidates-static-stand-pat`
- 3: `quiescence-candidates-opening-refresh`
- 4: `quiescence-candidates-opening-fast-only`
- 5: `quiescence-candidates-sparse-immediate-full`
- 6: `quiescence-candidates-queen-promotion-quiet-before-captures`
- 7: `quiescence-candidates-black-dual-en-passant`
- 8: `quiescence-candidates-white-ep-before-pawn-check`
- 9: `quiescence-candidates-black-quiet-pawn-check-geometry`
- 10: `quiescence-candidates-depth-nine-generation-order`
- 11: `quiescence-candidates-reached-empty-not-terminal`
- 12: `quiescence-candidates-king-exposing-capture-retained`
- 13: `quiescence-candidates-history-priority-one-versus-two`
- 14: `quiescence-candidates-history-priority-zero-versus-one`
- 15: `quiescence-candidates-victim-effective-value-150`
- 16: `quiescence-candidates-victim-effective-value-151`
- 17: `quiescence-candidates-low-attacker-adjustment`
- 18: `quiescence-candidates-fixed-king-attacker-value`
- 19: `quiescence-candidates-victim-square-adjustment`
- 20: `quiescence-candidates-king-capture-quiet-king-excluded`
- 21: `quiescence-candidates-direct-versus-discovered-check`
- 22: `quiescence-candidates-double-pawn-direct-check-excluded`
- 23: `quiescence-candidates-mixed-priority-tie-over-six`

## Source-only terminal boundary

All helpers were synchronous and pinned to0-5,8-13; no persistent job/session was launched. Bounded lookup errors for guessed nonexistent filenames (chunks0d3d2a,29e524,4ab753,exit2) were corrected using actual released/source paths. One inventory helper expected an operation key at the fixture-case top level (chunk77085e,exit1); corrected to request.operation (f3b6e1,exit0). These were text-reader errors with no source edits or runtime conformance attempt. This final memo helper only reads focused source/fixture text and writes this memo, then exits.

Focused source hashes rechecked unchanged after memo assembly. No implementation, patch, source archive, native command or additional route was produced.

# Exact schemas and native ownership

Produced default exact keys: fen,moves,ply,values,squareAdjustments,history,hashMove,killers. Optional additional orderingMode admits only quiescence, requiring moves[], a checked normalized side, null hint and both null killer pairs. Six-field native setup+0..256 chronological legal moves; ply1..62 independent of history length; values white/black5types0..10000; adjustments0..768 unique nonking keys with -128..127 and effective material within-10000..10000; history0..768 unique all6piece keys unsigned32; exact two killer pairs, earlier null/null at ply1/2; descriptors use existing coordinate/kind domain. Local initial normalized nonmoving-king/ordinary EP guards apply, not ancestry requirements. All fields parse before observe, full inventory<=230; final position/check/terminal and complete descriptor sequences serialize native results.

Q exact keys: fen,percentages,averageDepth,cfd,sop,history,move,alpha,beta,orderingHistory. Existing9 fields retain exact quiescenceDisposition domains: both11-key percentages0..1000, averageDepth-100..100,cfd-10000..10000,sop0..100,history0..255 full/fast legal/null transitions, legal nonnull final move to noncheck, window-10000<=alpha<beta<=10000. orderingHistory0..768 unique exact side/piece/square/u32value keys. New local initial guards apply before history; final penultimate-pawn implies at most8 own queens before any evaluation/cache. Original entry/disposition do not receive these new guards or field. Tactical list<=230; reachedfalse has no charge/list fields; reachedtrue contributes relation/search0/0, without child safety/eligibility/recursion or terminal classification.

| Region | Actual owner |
|---|---|
| Setup/placement/native flags | Position::from_fen via positions::sequence_position; cold unchanged consumer_position adds explicit local contract guards. |
| Path and chronology | positions::advance_with_move -> native full legal resolution + Position::played_unchecked; bounds checked at every stage. |
| Complete legal order/prefixes | movegen::generate_legal, never capped reply witnesses. |
| Semantic check label | new narrow movegen::check_classification -> existing find_attackers::<2>. No Boolean kernel replacement. |
| Supplied ordinary priorities/permutation | Context extraction -> Influence::build, ordinary_policy::priority, tactical::order_by/priority_sequence. |
| Explicit Q evasion ordering | actual same full legal sequence -> tactical::order with supplied RootContext/Learning. |
| Fixed root/evaluation/retention | unchanged native Evaluator begin_search + original cold evaluation replay and select_noncheck_detailed_observed, invoked once. |
| Static disposition | existing quiescence_policy::evaluation_return, same typed result both serialized and consumed by callback. |
| Noncheck pseudo-legal tactical order | tactical::generate then tactical::order with actual fixed evaluator.root and supplied orderingHistory; no safety/recursive consumer. |

Native ordinary/Q candidate-list and complete-evasion consumers stay unchanged. King-first LIMIT2 may return threshold witnesses in different order; only complete0/1 probe inventories are reused by current Q. Complete diagnostic lists always use full generation. Broad joined non-pawn EP and double-check interposition remain supported by untouched production kernels. Parent's earlier boundary-proposal raw-rights/stronger-validator corrections are already part of frozen95 and are not reimplemented here.

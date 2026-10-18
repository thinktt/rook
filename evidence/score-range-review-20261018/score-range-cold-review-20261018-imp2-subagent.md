# Scoped production score-range review, 2026-10-18

For imp2, from implementation review subagent. Cold source/algebra only: no engine execution, build, tests, profiling, simulation, source changes, or new agents. Every shell/helper invocation used affinity 0-5,8-13. Requested Normal/Fast OFF has no available speed control/readback; actual runtime speed is unverified.

## Conclusion

No reachable public defect established and no implementation change recommended from an unproved bound. The selected queen fortress endpoint cannot expand beyond the initial +/-10000 interval because selection uses the sign of the material-blended score. A conservative material-specific bound also keeps FULL selected pawn-race endpoints inside +/-10000. Selected pawn-only FAST endpoints are produced at the ply63 tactical boundary, but that caller returns only the clipped score and discards bounds. Unconditional fast endpoint and global upstream intermediate capacity remain open. TT conversion is safe on the stated store-domain/ply invariant; this review is not a complete induction over every search/table lifecycle caller.

## Identity and authority

Build reference: evidence/production-eval-kernels-use-build-20261018/receipt.json, SHA256 0d064e97df28bd6dc80cfaba72ac8f6bae77f4f8f4753712ed52e67b410b5618. It records binary SHA256 8c4619a7c3f33bed6eb17c396a7d9d8d223262dd1595c4f23812e5de17809953 and stable before/after source identity. Reviewed files below were independently hashed and match its source_sha256_before map. Historical depth-range-review.md and scalar-production-review.md were read for scope, not substituted for current binding. Only rook2 and released king-spec material was examined.

Released final-score.md restricts the standalone late-endgame supplied A to +/-10000 but explicitly says this is not a production restriction. fresh-score.md explicitly removes that extra restriction for produced subtotals. Neither restriction is assumed below.

## Current owners and selected endpoints

endgame.rs:224 material_blend; :280 race_bounds; :370 queen_pawn; :446 adjust; :511 finish. finish forms A from root-owned preference and deterministic variation, initializes endpoints [-10000,10000], applies adjust at E>=192, clips only score to +/-7900, applies reversible scaling only to score, then exchanges/negates endpoints for Black. The returned endpoint fields are i32, as are evaluator::Evaluation fields (:108); there is no i16 endpoint field at these owners.

In adjust the rule side is selected from S=material_blend(...) before the geometry dispatch. Selected queen-versus-pawn has white S>=0 and upper=min(10000,floor(3*S/32)), or black S<0 and lower=max(-10000,floor(3*S/32)). Therefore endpoints stay inside [-10000,10000], without any A admission ceiling. This assumes the 3*S i32 multiplication itself is valid; that global intermediate proof is not supplied here. The selected rule is queen only versus one pawn only, rather than a general material configuration.

Selected pawn race requires pawn(s) only versus bare king. Geometry either uses a single pawn or multiple pawns all on a/h file, so at most six current pawns participate and current E=256. Pawn-spread span=1 gives S=floor((27*A+16)/32), with no further material blending in this selected case. Winning endpoints are floor(S/4)+700 for White and floor(S/4)-700 for Black; losing endpoints have magnitude <=9. Expansion outside +/-10000 begins at positive S>=37204 or negative S<=-37201. These thresholds concern interval expansion, not i16 exhaustion.

For FULL evaluation a deliberately loose directional bound is |A|<=32126 when the score sign selects the actual pawn owner. Components used for this local bound:

- material <=7000; root draw preference <=10000; variation <=2650 (range<=5300).
- square magnitude <=1584: six pawn squares and two king squares, absolute basis<=99, then pawn-only doubling. Current source basis extrema are -99 and 35 (1152 values).
- selected pawn structure contribution toward the pawn owner <=3705: every cached base per color lies [-296,16] (eight descriptors, support [-3,2], doubled penalty <=34 each, production doubled coefficient 1024). Current penalties are nonnegative; the bare side matches no descriptors. At E256, piece pawn terms vanish and max weighted directional structure is (16+296)*10*19/16=3705. This permits retained hash-collision classifications; it does not assume fresh descriptors.
- progress <=7005: no rooks/queens or pawn support on the same file, so raw measure<=5, raw<=185, candidate intermediate<=262, candidate score<=298, two-leading score<=522. Weight after material adjustment<=12.5, ending<=480, hence <=6525+480. Candidate cache collisions cannot exceed the two-leading aggregate bound. The +400 lone-rook bonus is absent.
- activity and central are zero; bishop/opening patterns zero; tempo<=2. Shelter bound 180 is loose: no heavy ring/marks/screen or E256 shelter term; file pressure per side<=54, composed magnitude<=14 and weighted magnitude<=175.

Their sum is 32126. Thus |S|<=27107 conservatively, and winning race endpoint magnitude<=7477. Rounding asymmetry is covered by these loose integer bounds. This proves FULL selected-race endpoints remain within +/-10000 over admitted personality coefficients and produced pawn-cache descriptors; it is not a global subtotal bound.

## FAST producer and consumer restrictions

Node::child (evaluator.rs:38) and null_child (:83) copy positional/progress, update nonking squares, and increment age. FULL (:304-397) refreshes positional/progress and sets age zero. There is no age-based admission/refresh limit in these paths.

ordinary_policy.rs:47 fast_admitted requires a quiet incoming Ordinary move (empty destination in parent), current nonpawn measure>=2 for at least one color, and depth<=adjustment. Thus ordinary FAST cannot select pawn-only race or queen-only versus pawn-only. Its consumer ordinary.rs:530-550 reads fast.score only.

evaluator.rs:449 select_noncheck forces FULL when each color's nonpawn measure<=1. Both selected endgames meet that predicate. Otherwise FAST can supply endpoints, but the selected race/queen rules are then unavailable. Ordinary full-bound acceptance is ordinary.rs:560-569; tactical noncheck bound acceptance is quiescence.rs:209-213.

quiescence.rs:184-188 unconditionally FAST evaluates at ply63, before noncheck selection, and returns only value.score. Therefore a checked/capture chain may inherit P/G from an earlier heavy FULL producer into pawn-only ply63; age gives no tighter numeric bound. The potentially expanded FAST endpoints are discarded here. All retained-path score results still receive the +/-7900 clip (assuming upstream arithmetic has completed correctly).

Minimal remaining proof for unconditional FAST endpoints: bound the inherited P+G from all admitted FULL ancestors, or prove a tighter ancestor relationship at the ply63 boundary. Current code does not justify replacing that producer with fresh current pawn-only terms. No reachability or violating magnitude is claimed.

## TT normalization: proved capacity and remaining induction

remembered.rs:62 owns score:i16; :72-88 from_store uses i64, adds ply for score>=9000, subtracts ply for score<=-9000, then checked i16::try_from. :109-135 consider decodes using the normalized threshold and current ply; it does not enlarge stored score. A successful mate query mutates only depth.

For each store with |score|<=10000 and ordinary ply 1..62, normalized magnitude<=10062. This fits i16 with more than 22k margin. The standalone remembered-results domain includes ply0..63 and gives <=10063, also safe. Ordinary owner is ordinary.rs:418-431 store_ordinary, called for fast cutoff (:548), shallow/null cutoff (:610), quiet mate proof (:687), and final main best (:845). Ordinary delegates at ply63/depth<=0/personality cutoff before any table operation (:460).

Mate leaf values ply-10000 normalize exactly to -10000 when stored at their own ply. Propagating a remembered mate result to an ancestor and re-storing it cannot increase normalized magnitude: decode at child q subtracts q from positive magnitude, parent p<q adds only p back. The analogous negative case is symmetric. This remains true when a hash collision changes which position matches; identity equality does not change numeric formulas. Nonmate records have magnitude<=8999. Under the stronger semantic invariant that all mate-band values arise from the bounded mate producers and nonmate values stay below that band, normalized magnitude is <=10000.

These are conditional invariants, not an assertion every current production store has been exhaustively proved in-domain. In particular a raw interval-wide proof must account for TT reuse at different plies, root score_add/aspiration behavior (timed.rs:188-207, :483-571), synthetic frontier estimates, and table/session lifetime. A generic claim that a decoded TT score is always <=10000 is false for arbitrary diagnostic-origin records: store 10000 at ply62 gives normalized10062 and a query at ply1 can return10061. Actual production reachability of such an origin is not established here. The component +/-10000 input domain cannot itself close this production induction.

Ordinary frontier skips use estimates only when estimate<=max(best,lower) (ordinary.rs:750), and best starts at effective lower and is capped at effective upper (:702,:841). Tactical optimistic updates likewise occur only below their current threshold (quiescence_policy.rs:111-137) and final result caps at evaluator upper (quiescence.rs:408). These guards support a bounded-return induction once valid effective endpoints, request intervals and TT-origin invariants are supplied. Complete arithmetic capacity of synthetic estimates/threats and all root/table transitions is outside this bounded review.

Minimal further work: explicitly prove store-origin and root-window induction (or supply a proven larger invariant closed under all actual transitions), and separately bound global FULL-produced retained P/G and i32 intermediates. No implementation change follows solely from these remaining proof gaps.

## Bound current source hashes

- `src/endgame.rs`: `3b50609fc5671891ac74d79bbb12c5bd0ed98c3a51f302dcf7b5750373948176`
- `src/evaluator.rs`: `2b638e19566a69899e46cf6bf780271f07a9ac6d80cf1a3d51538b21a6558146`
- `src/evaluation.rs`: `16f26f211a09ab3aa85045c58542f4b841fd6520381214db62bed4f6363b9b3c`
- `src/eval_basis.rs`: `5b369b122dc69aa40e5f8b81c3153173e633c9cfec89f160cef49886b5c36647`
- `src/pawn_structure.rs`: `64473dc7b7d3d235b86caec1e8755d7edb0deae895de26b7129a65b1202bf04c`
- `src/pawn_terms.rs`: `41f5b0c8b5e5923dab8a69c4aa7c9dea80d7401225ed4f82f5e0f6701bf71305`
- `src/pawn_progress.rs`: `efb62166204229ad18c319eca2c6dc2bf0aad60bff8e57c2eff3d580b3b64934`
- `src/activity.rs`: `d150a53f80676d98bff41380e94d7b10395af34c633bef0154acd0b927dfa93b`
- `src/shelter.rs`: `fbef039d833ab726eae109f5fef40793a5ab6587838463bbff105b376e8c24de`
- `src/positional_terms.rs`: `053b04b8f434db2ddadda71686831b40baf3c59d09be6cde5895af1b7d430260`
- `src/ordinary.rs`: `446b518a5824a8a60b65666d1b841d959ab2964c995739a2bc44d27bd5a9c442`
- `src/ordinary_policy.rs`: `a79ec111e2d34bb9e4a3c2a7953c5b2a82b011016982fd2b63d6769da3036bf6`
- `src/quiescence.rs`: `dddd6a260805a7a53ee61ceb74141cb52f9a3fdc899f2350412ffa86be439e33`
- `src/quiescence_policy.rs`: `07ed6db1af2d7fc21f093aa619f5a931aa32d594f4c1b435968ad95691b8bda4`
- `src/remembered.rs`: `af2eb6046fd7e58b1a35e7ed3051936559b7f739224ed698b54c49317faec293`
- `src/timed.rs`: `1aca5ca308e2fc92b8a2b144dcc12f49e14990c9e5f34ce941fc37bfb4182f45`
- `src/first_iteration.rs`: `713830b62783a81033e1355687534783647b243c51e10f829546d080ce157722`
- `src/position.rs`: `749f9fa1e90684c4df670c115c3c7f7dbdb196cf62b5eb267900ba217143ce3a`
- `src/parameters.rs`: `30dd03e5ead3df289b25929c7bea81e72d1e2b9a2250916883107f0cfaf7f42e`

Released contract hashes:

- `spec/final-score.md`: `e1eb4708d3a02aeccca0c2fbaab6990e78c222eaea48a28be21e1fc7ce740d9e`
- `spec/fresh-score.md`: `f617a6596ae7013cc03fe16a58d917648f5e85d0c644e406f00ff291387764a8`
- `spec/endgame-adjustment.md`: `2ddb1c1e03c37d94c64092123b1c7f80118b77bb861a4d8a2ac1dfb5ee236772`
- `spec/fortress-bounds.md`: `8d658be2c27ddd78c76e91e2e00d2da1fe6571add9360f999c802dca905234a1`
- `spec/remembered-results.md`: `52439afdf6c2c54f87bfebf6922f6ce31f69e1543dfca2eb950f3f10970ce180`
- `spec/retained-evaluation.md`: `074c4557bc48afa10cfc81c31041570824e4dabde95f0050a8f04aa535e621be`
- `spec/evaluation-bounds.md`: `9a917c752a800282c8a2d547c1a413d2c6f0e58332b3ee9cea662715aeb34952`

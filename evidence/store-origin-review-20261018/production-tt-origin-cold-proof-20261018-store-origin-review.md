# Production TT store-origin and root-window induction, 2026-10-18

Cold source/algebra review by imp2 implementation subagent store_origin_review. No builds, native tests, engine executions, profiling, simulations, source edits, Herdr commands, or other agents. All shell/helper commands used taskset affinity 0-5,8-13. Requested Normal/Fast OFF has no exposed speed control/readback, so actual runtime speed remains unverified. The only write is this uniquely named report.

## Result and prerequisites

The production TT score capacity induction closes with normalized magnitude **10062**, fitting i16. This is stronger than the earlier conditional statement that an individual raw +/-10000 store at ply<=62 fits. It permits actual production TT hits and null propagation outside raw +/-10000 and closes all ordinary store sites and actual fixed/timed root window transformations. It does not assert that every production raw score stays inside +/-10000, nor establish reachability of any extreme bound.

The theorem is about produced search control flow and completed integer computations under admitted positions/personality parameters. It imports the previous reviewed results that (1) every consumed FULL endpoint and every FAST endpoint consumed below ply63 lies inside [-10000,10000], and (2) every finished evaluator score lies inside [-7900,7900]. The unconditional FAST endpoint fields at ply63 are irrelevant: that caller discards them. It also uses the direct source fact that material_threat returns a nonnegative value, initialized zero and updated only with max. A separate global i32-intermediate/cast validity proof is still required for complete engine arithmetic safety; in particular this report does not prove that raw threat, retained P/G, allowance, or synthetic estimate computations never overflow before their gates/clamps. The current proof does not need a new magnitude bound on those raw values once their arithmetic has completed correctly.

The scoped prior evidence is `evidence/score-range-review-20261018/score-range-cold-review-20261018-imp2-subagent.md` and `parent-review.json`. Its selected endpoint theorem is preserved by the current source binding below. No native change is recommended merely because the separate global intermediate proof remains open.

## Invariant

Set M=10062 and B(p)=M-p. At every actual ordinary node that accesses/stores the production table, 1<=p<=62, hence 10000<=B(p)<=10061.

Maintain simultaneously:

1. Every valid production TT record has normalized score n with |n|<=M.
2. Every ordinary result at ply p<=62 has |s|<=B(p).
3. Every actual ordinary request at p<=62 has upper>=-B(p). A root child has lower<=10000; every recursively produced ordinary request has lower<=9999.
4. For p<=61, the main-loop local best and local lower, before every child request, are at most B(p+1). The IIO local best before every child has the same ceiling. Their best values are always at least -10000.

Q independently returns |s|<=10000 for p<=62, and |s|<=7900 at p63, without requiring an ordered request window. These Q bounds imply |s|<=B(p) whenever ordinary delegates at p<=62, and at p63 imply |s|<B(63)=9999.

The invariant intentionally tolerates equal or inverted windows, including ones an extreme remembered score could create. No assumption that aspiration necessarily preserves lower<upper is needed for capacity.

## Q result lemma

`quiescence.rs:175-188` returns zero for repetition/reversal or clipped FAST score at ply63. Below ply63, noncheck evaluator-bound returns are inside +/-10000, and standing-score returns are inside +/-7900 (:193-219). Checked initialization is best=-10000 and upper=10000. Noncheck initialization is a clipped standing score with an evaluator upper endpoint inside +/-10000.

No-move returns (:237-241) are either the clipped standing score, zero, or ply-10000; the checked mate-distance cutoff is ply-9998. All lie inside +/-10000. Recursive children have greater ply and bounded Q results. Ordinary-capture optimistic updates only raise best (`quiescence_policy.rs:111-138`); they can never lower best below -10000. Even if an optimistic update were above 10000, the final result is `best.min(evaluation_upper)` (:408), whose upper is <=10000 and >=-10000. Thus returned best is inside +/-10000. This proof does not require estimates themselves to be inside the returned range. The no-move branch precedes all optimistic updates, so it cannot bypass the final cap with an optimistic value.

## Why recursive windows have bounded lower endpoints

Every ordinary node that proceeds past FULL bound acceptance has effective_lower<request.upper and effective_upper>request.lower (`ordinary.rs:560-569`). Since both effective endpoints lie in +/-10000, integer request.upper>=-9999 and request.lower<=9999 at such an active node.

Main full-window, refreshed-scout retry, and IIO child lower are -request.upper, hence <=9999 (:771,:803,:906). Scout lower is -min(best+1,request.upper); because best>=-10000 and the active request.upper>=-9999, both terms inside min are >=-9999, giving the same ceiling (:773). Null child lower=-request.upper also has that ceiling (:595).

For null requests, the additional gate evaluation.score>=request.upper forces request.upper<=7900 (:577). Therefore the null child's endpoints are lower in [-7900,9999] and upper=1-request.upper in [-7899,10000] (:595-596). In particular its upper is >=-B(p+1) when p+1<=62. Null cannot carry a low request.upper past the effective-lower gate and thereby create an ever-growing 1-upper sequence.

## Main/IIO child upper and intermediate best

For a parent p<=61, B(p+1)>=10000. Main best starts at effective_lower<=10000; IIO best starts at -10000. Main local lower starts at request.lower<=10000 at the root child, or <=9999 recursively. Thus both are initially <=B(p+1).

A skipped frontier estimate is accepted only if estimate<=max(best,local lower) (`ordinary.rs:750`), so it cannot raise either maintained variable above B(p+1). A searched child at p+1 returns at most B(p+1), by the ordinary/Q result invariant. Negation preserves its absolute bound. The refreshed-scout retry uses the same ply and has the same result bound. Updating best/local lower from such a result preserves the ceiling. Consequently main full-window upper=-max(best,request.lower), scout/retry upper=-best, and IIO upper=-max(best,request.lower) are all >=-B(p+1) (:775-779,:804,:907). IIO ordering/permutation and extension metadata do not alter numeric values; its shallower target changes depth only.

At parent p62 all children are Q at p63, with no table store or ordinary recursive continuation. Their windows need not satisfy an ordinary child precondition. Main p62 best still lies in +/-10000 after the final cap, and that already fits B(62)=10000.

## Every ordinary return/store origin

The delegation at depth<=0, p63, or configured cutoff occurs before table access (`ordinary.rs:460`). Its Q result obeys the lemma. At p<=62 all zero/draw returns obey B(p).

- TT hit (:508-512): |n|<=M. Decode is n-p if n>=9000, n+p if n<=-9000, otherwise n. Since p<=62, sign cannot flip for a mate-band normalized value; its magnitude is <=M-p=B(p). A nonmate decoded value has magnitude<=8999<B(p). TT probing only mutates depth, never score.
- Fast cutoff store (:530-550): adjusted evaluator score is score-100 or score-150, hence <=7800. Subtracting nonnegative material_threat cannot increase it. It is stored/returned only when trial>=request.upper>=-B(p). Therefore |trial|<=B(p). No upper bound on threat is needed for this output-range inference, subject to completed arithmetic validity.
- Effective-bound returns (:565-569) are inside +/-10000, hence inside B(p), and are not stored.
- Direct shallow cutoff (:577-611): clipped evaluation score minus nonnegative threat minus25/40 is <=7875; successful trial>=request.upper>=-B(p), so it fits B(p). Null trial is a negated deeper ordinary/Q result, hence magnitude<=B(p+1)<B(p), or <=7900 for a p63 Q child. Its successful store also fits.
- No-legal-move and mate-distance returns (:621-624) are bounded by10000 and do not store.
- Quiet checking-mate probe store (:661-687): negated child Q is bounded by10000, or7900 at child p63. Its score>=9000 admission and request-upper condition add no magnitude. It fits B(p).
- Main final store (:702-845): best never falls below effective_lower>=-10000, and final min with effective_upper<=10000 gives raw best in +/-10000. Synthetic frontier estimates can affect best only through its guarded update; final endpoint cap also prevents their positive magnitude from enlarging this store. Thus |best|<=10000<=B(p).

For any such raw store |s|<=B(p), normalization either leaves |s|<9000 unchanged or adds p to its magnitude. Therefore |normalized|<=B(p)+p=M. This closes the table invariant for all four production store-origin categories and every intermediate store within a search, including collisions, retries, null trials, and IIO phases. Threshold crossing between normalized mate-band and decoded ordinary-band values only reduces or preserves the bound.

The normalized capacity margin is 32767-10062=22705 on the positive i16 side. A tighter +/-10000 normalized theorem is unnecessary and is not claimed.

## Timed and fixed roots close the induction

`score_add` (`timed.rs:189-195`) leaves any mate/sentinel-band input unchanged; for an ordinary-band input, i64 addition is clamped into +/-8999. Thus it preserves any enclosing interval [-C,C] with C>=8999, independently of random adjustment magnitude. Production random adjustment uses admitted randomness<=i32::MAX; its subtraction is inside i32 and its negation cannot be i32::MIN. Arbitrary direct calls to score_add still use i64, but arbitrary direct calls to aspiration with i32::MAX are outside this production theorem because its max(...)+1 is plain i32.

Timed root child results at p1 have magnitude<=B(1)=10061. Negation, score_add(random adjustment), and ranking_score(score_add -2) preserve that ceiling (:531,:571). Each iteration best begins -10000 and only rises, so best and carried previous_best are in [-10000,10061] (:477,:483,:588,:680); individual ranked root scores can be as low as -10061.

For unrestricted root passes, window is [second or -10000,10000] (:496-500), hence window[0] is in +/-10061 and window[1]=10000. Restricted aspiration gives first endpoint score_add(best,2), in [-10000,10061]; second endpoint score_add(min(10000,max(best,previous_best)+1),2), inside [-9999,10000]. The unclamped addition max(...)+1 is <=10062, safely i32. Retry replaces only the second endpoint by10000 (:566). Applying score_add(endpoint,-adjustment) preserves these enclosing bounds. Therefore actual child lower=-adjusted window[1]<=10000, and upper=-adjusted window[0]>=-10061=-B(1) (:516-517). This establishes the root request invariants even if an extreme lower window exceeds its upper window.

Fixed `run_iterations` root children have lower=-10000 and upper=-second (`ordinary.rs:343-366`). The returned/ranked score ceiling is10061, so upper>=-10061. First-root iteration uses Q only (`first_iteration.rs:48-117`), whose stronger +/-10000 return bound establishes the same base. No root owns a TT store at ply0.

For extra window arithmetic context, ordinary root upper is at most10061; recursively formed ordinary upper is at most10000 because main/IIO best>=-10000, or by the null gate above. Full/IIO child lower is therefore >=-10061. Scout best+1 is <=10061 for parents p<=61, and <=10001 at p62, so scout lower also stays >=-10061. Both ordinary endpoints stay inside +/-10061. Q children negate endpoints and use a local lower raised only by bounded standing/actual child scores; optimistic best is not copied into lower. Thus window negation, best+1, null1-upper, and select_noncheck's lower-250/upper+250 do not approach i32 limits. This does not bound the upstream estimate/threat formulas themselves.

## Table/session lifetime and diagnostics

`run_iterations` calls ensure_table then prepare_root_with_influence (`ordinary.rs:330-331`); `run_work_timed_inner` does the same (`timed.rs:446-447`). Preparation clears remembered records by generation and resets learning/evaluator search state (`quiescence.rs:106-115`, `evaluator.rs:253-265`). Table allocation begins zeroed (`engine.rs:116-122`, `remembered.rs:155-171`). Logical clear excludes old generations; generation wrap physically clears before reusing generation1 (`remembered.rs:177-184`). Thus the induction starts with no valid records and spans the actual iteration/root lifetime. begin_sequence alone does not clear the table; production root entry already did. Session go/go_live use this timed path (`session.rs:501,:565`); map_host transfers existing storage but next preparation clears it. Stops leave only invariant-preserving prior stores, and the next production search prepares/clears again.

Standalone public RememberedTable/Store/Query are separate diagnostic/library inputs. A caller can directly store10000 at ply62, obtain normalized10062, then decode10061 at ply1. That is consistent with this theorem's numeric ceiling, but is not evidence that this origin is reachable in actual production, and it invalidates a naive raw +/-10000 claim. Arbitrary public diagnostic stores/plies can exceed this theorem and can deliberately trigger checked conversion failures. The engine's remembered field is pub(crate), and production prepare clears it; there is no external standalone-table injection assumed in this theorem. Similarly arbitrary direct aspiration inputs do not establish production root reachability.

## Remaining scope

TT store-origin and root-window score capacity is closed under the stated imported endpoint/finished-score theorem and completed integer arithmetic. Remaining separate work is global i32/cast capacity of evaluator/subtotal, retained P/G, threat/allowance/estimate producers, and any unrelated depth/target capacity theorem. This report makes no reachability claim for the worst-case numeric bounds and identifies no reachable defect requiring a source change.

## Current source identity

Canonical reference: `evidence/production-activity-specialization-instrumented-build-20261018/receipt.json`, receipt SHA256 `c038754a2b392e6f53624a375e6840299000ee128e031cd6295d822338e14f54`, binary SHA256 `12c2af4cbe01bf47fa29c5ecb8282ca2298b585795b995128f51dead11d5b3b7`. Every reviewed file below independently matched both source_sha256_before and source_sha256_after in that receipt. This binds the prior arithmetic source to current native43 activity specialization; current activity.rs differs from the older checkpoint, and no activity arithmetic theorem is newly asserted here.

- `src/ordinary.rs`: `446b518a5824a8a60b65666d1b841d959ab2964c995739a2bc44d27bd5a9c442`
- `src/ordinary_policy.rs`: `a79ec111e2d34bb9e4a3c2a7953c5b2a82b011016982fd2b63d6769da3036bf6`
- `src/quiescence.rs`: `dddd6a260805a7a53ee61ceb74141cb52f9a3fdc899f2350412ffa86be439e33`
- `src/quiescence_policy.rs`: `07ed6db1af2d7fc21f093aa619f5a931aa32d594f4c1b435968ad95691b8bda4`
- `src/timed.rs`: `1aca5ca308e2fc92b8a2b144dcc12f49e14990c9e5f34ce941fc37bfb4182f45`
- `src/remembered.rs`: `af2eb6046fd7e58b1a35e7ed3051936559b7f739224ed698b54c49317faec293`
- `src/engine.rs`: `2e3105e7a7802c4061c0d0cd0ddc4d4629a2c362297fb1f4e18ddc7e7d566e08`
- `src/session.rs`: `9cb1c85ee9e11452a980233b66c0e817d0e6309dd6d425ae90721f04cc46c19b`
- `src/evaluator.rs`: `2b638e19566a69899e46cf6bf780271f07a9ac6d80cf1a3d51538b21a6558146`
- `src/evaluation.rs`: `16f26f211a09ab3aa85045c58542f4b841fd6520381214db62bed4f6363b9b3c`
- `src/endgame.rs`: `3b50609fc5671891ac74d79bbb12c5bd0ed98c3a51f302dcf7b5750373948176`
- `src/activity.rs`: `07d1b062f5ce6a4ffb66bd57eb3570f9221f42d7105b1df1f11e3039caf93c38`
- `src/first_iteration.rs`: `713830b62783a81033e1355687534783647b243c51e10f829546d080ce157722`

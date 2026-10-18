# Cold root-material opportunity review

Date: 2026-10-18. Parent owns the experiment and storage decision. No implementation proposed as selected.

The measured target is modest and concentrated in count-only capture hypotheticals. Exactly identified material source rows account for **291,311,269 simulated Ir, 2.510473%** of canonical8d profile01. Capture allowance owns 175,526,185 of those instructions, **60.253826% of the identified material cost**. A Node scalar used only by full/fast evaluation would not reach that majority. Weighted pawn/heavy accumulation rows account for just 82,616,199 Ir (0.711973% of the lifetime), of which 29,593,684 Ir (0.255034%) is outside allowance. These are source-attribution budgets, not predicted savings.

My preliminary judgment is **measure local redundant material demand first and avoid selecting persistent state yet**. A per-Q-call lazy endpoint cache has a narrower ownership/proof scope than updating every produced child. One raw scalar can be maintained exactly, but cannot replace nonlinear material evaluation, and its update/copy tax applies to children that never request material. Appended-field Node184, packed raw/nonking Retained16, and a clamped-material i16 in existing padding are consequential, unselected alternatives. This review implements none.

## Frozen evidence and arithmetic attribution

All source line references below bind immutable `/home/legolas/rook2/evidence/production-activity-specialization-use-build-20261018/source-before/`, whose entire43 native/build hash map matches the profile provenance. Initial reads of root sources were independently checked against that same map before integration; final identities were rechecked against the immutable tree. The source-authorized later79 API/helper integration is not this profile's source. Its extraction may share arithmetic, but canonical8d line numbers, inlining ownership and cost cannot be attributed to its new helpers.

Artifact identity: `8d9dddc58d3b5dd1128bc7cedb4ee83a0df6310d33fb5f377f13a1a46ce7f79d`. Profile01 total: **11,603,840,314 simulated Ir**, whole lifetime, cache and branch simulation disabled. Original strict replay passed. This is not PMU retired instructions, cycles, CPI/IPC or native CPU time.

An offline parser resolved compressed file/function names, consumed line-position deltas, and excluded each cost row immediately following `calls=` (inclusive call-edge work). Its sum of all remaining self costs exactly equals 11,603,840,314. Material-only attribution uses evaluation.rs:94–132. The retained source annotation independently provides the same13 identified rows. No function/file inclusive total is added again. Unknown source-line0 costs and shared floor_div/core arithmetic are not assigned to material without a unique mapping. A prior LLVM IR counter0 and Callgrind basic-block counter0 are **not function-entry counts**; no invocation counts are derived from either or from source-row instruction weights.

| Exclusive identified rows | Simulated Ir | Lifetime share |
| --- | ---: | ---: |
| 101 pawn totals +106 non-pawn weighted totals | 82,616,199 | 0.711973% |
| 103 current counted population +104 root counted population | 78,567,432 | 0.677081% |
| 107 actual non-pawn presence | 28,980,397 | 0.249748% |
| 112 average-depth numerator +115 balance +118 fixed-root sign | 36,902,261 | 0.318018% |
| 119 advantage gate +122–125 adjustment arithmetic | 64,244,980 | 0.553653% |
| Total | 291,311,269 | 2.510473% |

| Inlined machine-function owner of those rows | All material rows | Weighted rows101+106 |
| --- | ---: | ---: |
| quiescence_policy::allowance | 175,526,185 | 53,022,515 |
| ordinary::visit_ordinary variant2 | 48,385,602 | 11,921,508 |
| quiescence::visit_q variant2 | 40,018,775 | 10,243,167 |
| quiescence::visit_q | 20,524,072 | 5,238,288 |
| evaluator::full_impl | 6,819,818 | 2,180,520 |
| ordinary::visit_ordinary other variant | 36,817 | 10,201 |
| Total | 291,311,269 | 82,616,199 |

These rows are exclusive **source instruction attribution**, not complete exclusive runtime cost of a semantic helper. Inlining folds material into both evaluator and search owners; the search-owned rows do not split uniquely into full versus fast requests. Additional material operations may be attributed to shared/core/unidentified lines. Conversely, all identified rows cannot be removed by caching one raw sum: count/depth/presence, losing-side material, favored pawn contribution, advantage and clipping remain necessary. The 2.51% figure is a deliberately optimistic deletion envelope for the identified old body, not a formal bound on CPU speedup. The weighted-row budget is more directly relevant to a raw scalar, but still includes subtotals needed by the adjustment.

## Actual material formula and every native demand path

RootContext::new fixes root phase, root-owned White/Black values, root counts, root side and average_depth. Material does not recompute values from descendant phase and does not switch root ownership with side to move. It forms current pawn totals P[2], current non-pawn weighted totals H[2], actual non-pawn presence, and root/current counted populations over pawn/knight/**bishop**/rook/queen. Kings are excluded. Actual counts, not phase's promotion-heavy nibble normalization, feed material.

Let raw `W = Hwhite + Pwhite - Hblack - Pblack`. The initial B is `W - s*floor(((root_count-current_count)*average_depth+1)/2)` with root sign s. The adjustment is selected by **this B's** sign and abs(B)>50, plus presence of any non-pawn even if it has zero material value. It needs H[losing] and P[winning], with floor of potentially negative `(2400-Hlosing)/16`, the min/max caps, and the final [-7000,7000] clamp. A bishop capture changes the actual population and H/presence; it must affect the average-depth and nonlinear terms exactly. Promotion changes type totals and H/P but preserves the total population. There is no separate bishop-count average-depth shortcut in this material function; bishop-coordination scoring belongs elsewhere and is outside this proposal.

Native production demands are:

- evaluator.rs:313 full_impl requests material once, then shares its produced value with activity, shelter and selected pawn progress and includes it in the base. FRESH/full observation variants share this producer; they are not permission to use a stale final material score.
- evaluator.rs:438 fast requests current material while preserving the full-produced positional/pawn-progress pair. Ordinary admission may request fast then full; Q select_noncheck may request fast then refresh full. Root preparation also performs a full evaluation. Ply63 FAST is another actual demand. Material remains current even if retained evaluation age is nonzero.
- quiescence_policy.rs:61/66 allowance computes **two complete material endpoints**: current counts and a copy of Position with exactly the actual victim's count decremented. It intentionally changes no board/list/fingerprint. The normal non-check Q candidate path invokes it for ordinary non-promotion/non-EP captures before later check/eligibility/king-safety screens; rejected/pruned candidates can still demand these endpoints. ordinary_policy::frontier_estimate also invokes the same allowance for eligible ordinary, nonchecking captures, even if it subsequently skips producing a child. Parent and hypothetical endpoint remain independent of any later child production.
- Development-only RootContext::development_score, development::Search leaf evaluation and rook2-dev inspection/activity fallback also call material. Unit tests call it directly, including count-only states and clipping witnesses. These cold/API demands are not all Node consumers and cannot silently acquire a coherent cached scalar from a nonexistent Node.

The allowance's gain is the difference of the **adjusted and clipped endpoint scores**, signed for the victim. Nominal victim value, a delta of clipped cached material, or removal of a raw scalar without rerunning the nonlinear endpoint formula is wrong. Existing allowance tests explicitly witness a gain unequal to nominal value and equal clipped endpoints. A scalar living on Node does not automatically reach an allowance taking only `&Position`. Any future explicit input must supply raw-before from its owner, derive raw-after by actual victim removal, and pair each with the corresponding counts; standalone count diagnostics still need a fresh valid origin. No such API change is implemented here.

## Conservative one-scalar hypothesis and ownership proof obligations

The narrow invariant would be an i32 **raw White-relative root-valued nonking material sum W**, independent of retained positional age. It is not adjusted B, finished material, phase, square sum or final evaluation. It belongs to one produced placement under one RootContext. It must be initialized in Node::root **after** begin_search binds the root; every new personality/root lifetime establishes a new invariant. Arbitrary mutation of public root values after Node creation would invalidate it, so admitted helper origins require an explicit audit.

The exact delta is `Wchild = Wparent - signed_value(actual victim) + signed_value(promoted result) - signed_value(original mover)`, with empty/king values0 and White positive/Black negative. Same-kind ordinary motion cancels the mover terms. The actual move cases are:

| Construction | Required raw update |
| --- | --- |
| Quiet ordinary | Preserve W |
| Ordinary capture | Remove the actual captured color/type's signed root value |
| Promotion, with or without capture | Replace the moving pawn's root value with promoted type; also remove actual victim |
| Joined EP | Remove actual behind-target victim color/type, which may be knight/bishop/rook/queen; do not assume pawn |
| Castling | Preserve W; king/rook relocation changes no counted material |
| Null | Preserve W and absolute color orientation; side/EP/halfmove/age changes do not change raw material |
| Exceptional EP king-victim ingress | Remains the existing cold terminal Position path, not a newly admitted normal Node child; normal apply_unchecked rejects king victims |

RootContext-generated nonnegative values are bounded (production max9000, count-only diagnostic max10000), with at most30 counted pieces in the admitted domains. A loose raw magnitude bound300000 fits i32. Update arithmetic should remain wide enough for intermediate sums and narrow only under proved bounds. No root phase/material rebind is allowed along descendants.

Node::child already reads actual mover/victim/promoted tags for the independent nonking-square sum. Reusing these reads may reduce a future update's marginal arithmetic, but is a compiler/code hypothesis, not a free update. Null preserves the raw scalar. Scout/full retry uses the **same produced child** and can have repeated demands with no extra construction; IIO, main search, mate probes and later root attempts construct separate children. Retained full refresh updates positional/progress/age and must not overwrite root-derived placement material. Parent/sibling invariants must survive retries, interruption and history push/pop without a mutable undo mechanism.

One raw scalar does **not** encode each side's H and P. A conservative consumer can first use W and the count-derived depth term to select the nonlinear branch, then compute only the losing side's four weighted non-pawn counts and the winning pawn total when needed. That is potentially less work than two complete subtotals, but it remains real per-demand work. Presence still follows counts, including zero-valued bishops/non-pawns. Count-only allowance's before/after selection may flip the winning side or cross50/clipping boundaries; reuse of one endpoint's subtotals needs its own exact proof. This review does not select or implement such restructuring.

## Construction/copy tax and the missing denominator

Current source owns Position160 and Retained16 in Node176 (the existing native test asserts176). Appending i32 raw material naively suggests180 bytes rounded to184 at alignment8. That is an **8-byte, 4.545455% Node footprint increase**, not a measured 4.55% CPU tax. Actual compiler moves, registers, stack slots and copy elision require observation; no whole memcpy/libc profile row can be apportioned by this ratio.

The scalar update/copy path would apply to **every actual Node construction**, including quiet children, root/first/timed candidates, IIO children, shallow mate probes, Q check-reply probes later discarded, and null children. Some return on repetition/reversal/TT/mate/eligibility without a full/fast material demand; some checked Q nodes do no static evaluation at all. Conversely fast/full refresh and scout retry may consume one child more than once, and repeated capture estimates consume a parent's raw state without constructing any child. Existing semantic N, `stats.children`, IIO counts or full/fast totals do not by themselves reconcile all these productions and hypothetical demands. No current measured demand-to-production ratio is established here.

A bounded **diagnostic-only source demand counter** would resolve the main uncertainty. It should count actual source events, compile out of production, preserve work and pass strict replay; its instrumented runtime must not be used as a performance result:

1. Count Node::root, Node::child and Node::null_child, separating construction call sites (root/first/timed, ordinary main, IIO, mate probe, Q reply probe/final). Classify actual child deltas as quiet/capture/promotion/castle/EP and record actual EP victim kind. Avoid doublecounting a Q prepared_child later reused.
2. Count full and fast material requests separately, including root preparation, fast→full refresh and repeat scout/root attempts on the same produced child. Count allowance invocations by Q versus ordinary frontier and its before/after endpoints separately. These are semantic **source requests**, not claims about calls emitted after inlining/CSE.
3. Correlate request counts with a diagnostic-only produced-node lifetime so 0,1,2,3+ material demands per child, discarded probe children and parent allowance-only demands can be reconciled. The instrumentation must distinguish repeated visits of the same produced child from separately reconstructed equal placements. It must not introduce a production field/cache keyed by fingerprint.
4. Record existing branch selections (any-heavy, abs(B)<=50, advantage selected, clipping) and average_depth==0/nonzero at the actual producer. This determines how often one raw scalar could bypass weighted-subtotal work, instead of assuming every old body operation disappears. Retain per-workload counts, not only one aggregate.

For notation, material source requests are roughly `Dfull + Dfast + 2*Aallowance + Dcold`, while maintenance events are `Croot + Cchild + Cnull`. This is an accounting identity at the source-demand level, not a machine-operation prediction. The critical measurements are D/C, allowance share, zero-demand constructions and delta categories. A future matched native pilot remains necessary even with favorable ratios, because update/register/copy traffic competes with a small candidate budget.

## Narrower alternative: lazy material endpoints within one immutable candidate loop

This is my preferred **next demand question**, not an implemented or timed cache. Limit reuse to the complete `root.material` results used by allowance in one non-check Q invocation/candidate loop. The local parent Position/counts and root context remain fixed throughout that loop; child recursion changes shared pawn/history/learning state but does not rebind root material values/counts/side/average_depth or mutate the parent placement. Discard local entries on invocation return. Do not reuse across an equal fingerprint, another produced child, later root, or arbitrary supplied diagnostic request.

Actual caller admission is narrower than actual child transitions: Q sets `special` for **both promotion and EP**, makes them forced, and runs allowance only when `!special && !victim.is_empty()`. Ordinary frontier returns10000 before allowance for nonordinary moves or checking moves, and otherwise calls it only at occupied destinations. Thus a material-endpoint cache for allowance must not add promotion/EP queries or treat EP's behind-target victim as an ordinary destination victim. The promotion and joined-EP delta obligations above concern a persistent child invariant, not this allowance-only local scope. The standalone allowance helper asserts ordinary and a nonempty non-king victim; preserve those admitted helper semantics too.

For one fixed parent/root, the `before` material score is constant. The count-only `after` state removes exactly one unit from `counts[actual_victim_color][actual_victim_kind]`. It is therefore identical for every eligible ordinary capture of the same actual color/type, independent of source/destination square or which physical piece is captured. Root values and all nonlinear depth/advantage/clamp math see the same counts. The safe abstract key is `(victim.color, victim.kind)` from the occupied destination, excluding empty/king; in a correctly produced native capture list the victim color is the fixed opponent, permitting five kinds only after that producer invariant is proved. Do not infer victim kind from move spelling, assume a pawn, or omit color at a broader supplied helper boundary.

A local proposal could lazily obtain `before` at the first existing allowance demand and lazily obtain the **fully adjusted and clipped after score** once per encountered key. It would still compute each allowance's victim sign, retained contribution choice, capture exception and final sum at the existing admission site. The explicit contract allows material reuse because it is pure; it does not authorize caching the entire allowance, moving capture eligibility, deduplicating semantic charges, suppressing selected support queries or changing the later best/threshold/check/king-safety order. Existing material construction/observation has no relation charge; every other caller-owned charge/gate stays intact.

For A actual allowance calls in a Q invocation and K distinct encountered victim color/type keys:

- A=0: no material endpoint should be computed for this cache.
- A>0: original source requests2A complete material endpoints; lazy reuse requests `1+K`.
- Exact avoided **source endpoint demands** are `2A-1-K`. K<=A, and K<=5 under the normal fixed-opponent capture producer. A=1 gives zero avoided requests; repeated captures of the same type produce larger opportunity.
- Across frames with demands, total saved requests are `2*sum(A) - number_of_nonempty_frames - sum(K)`.

This is a rigorous redundant-demand count under the immutable inputs, not a CPU or machine-call bound: LLVM can inline/CSE portions of the original endpoints, and the cache introduces key checks, stores, initialization and frame pressure. A naive Option array may grow/initialize the recursive frame even for no-demand calls; any later trial must include that real cost. Local state avoids Node enlargement, maintenance on unrelated child production and restoration invariants, but is not free. Q can recurse while the parent cache remains live, so stack/register spills and recursion depth matter.

Full/fast evaluation has already computed current-parent material before a non-check Q loop, but the current Evaluation object returns finished score/bounds, not the material component. **Standing score is not material.** Reusing that existing pure value would require an explicit correctly owned handoff; inferring it from standing, retained score or post-finish output is invalid. The narrow lazy proposal can first recompute before once at its original first allowance use, avoiding any evaluator API expansion; whether exposing the existing value is worthwhile is a later separate scope choice. The analogous ordinary-frontier loop can be counted separately because its original current evaluation also includes material and its admission differs; no cross-frame shared cache is implied.

The first scoped diagnostic should therefore add, per Q loop (and separately per ordinary frontier loop), A, K by actual occupied victim color/type, histograms for A=0/1/many and repeated same-key requests, and totals for `2A` versus `A>0 ? 1+K : 0`. Log one existing `before` material request and the number of distinct hypothetical after states without invoking extra material computations merely to count. Preserve original event ordering; counters should observe actual allowance admission, not all generated captures. Reconcile these counts with full/fast and construction counters above, and retain per-case results. This identifies a local-reuse denominator directly before any persistent maintenance hypothesis needs selecting. A future correctness trial must compare full allowances/work/candidate outcomes and witness sign flips,50-point gates, clipping, zero-valued bishops/non-pawns, root asymmetry, and different destinations sharing one victim key.

## Unselected Retained16/Node176 storage alternative: bound and consumer audit only

Parent identified a possible packing: keep positional:i32 and pawn_progress:i32, add raw_material:i32, narrow the placement-derived nonking_squares to i16, retain age:u8 and padding. Nominal payload `3*i32 + i16 + u8 + pad` is16 bytes, preserving Node176 without moving ownership into Position. This is an unselected alternative, not permission to flatten state or modify storage. Rust layout and emitted code would need verification if parent later chooses it.

A cold static extraction of the exact canonical SQUARE_BASIS found **nonking entries in [-16,35]**, across3 phases×5 types×64 squares. Root square tables use convex root-phase weights summing256 and `(sum+128).div_euclid(256)`; that rounding preserves these integer endpoints. Color orientation changes rank only. With at most15 nonkings per side, the deliberately loose absolute sum bound is `30*35=1050`, well within i16. Node::root sums this actual placement; child capture/promotion/castling deltas preserve the mathematical invariant; null preserves it; full/fast merely consume it. This bound concerns the stored **nonking** sum, before current king blend and pawn-only doubling, not the entire square balance or larger retained positional subtotal.

Narrowing would still require: prove the root-table origin and admitted Node inputs, retain i32 widened update intermediates before casting a proved final value, audit every producer/consumer (Node root/child/null, square_balance_from, equality/copy and tests), and preserve public helper behavior. RootContext.squares is a publicly mutable i16 table; Retained.nonking_squares is publicly writable i32. Arbitrary such Rust values can exceed the bound and cannot be silently cast. Current supplied candidate-order/threat adapters modify square entries within[-128,127] but do not create Node; this audit found no direct nonking_squares consumer in those adapters. Their bounded entries alone are not proof for every external native/helper caller. A later79 arbitrary-placement evaluator can require a wide sum even while the production Node invariant fits i16; its helper/API origin must be reviewed separately before changing public representation. The parent should keep this storage alternative a distinct decision from choosing whether incremental raw material has enough demand.

## Other unselected storage alternative: clamped material in existing padding

The complete admitted material result is clamped to[-7000,7000], so its **stored result** fits i16. Retained's existing threei32 fields plus age:u8 have three nominal padding bytes; adding an i16 material field can in principle retain Retained16/Node176 without narrowing nonking_squares. Actual Rust layout remains unverified until an explicit later candidate; this is a bound/ownership observation only, not a storage selection or permission to repurpose fields.

This would maintain a different invariant from raw W: the complete root-specific material score for the produced placement, independent of retained positional age. Quiet ordinary, castling and null preserve it because actual material counts and root context do not change. Captures, promotions (including quiet promotions), and actual joined-EP victims require the complete adjusted/clipped material score recomputed from the resulting actual counts; adding/subtracting nominal values from an already clamped result is invalid. A bishop capture can cross non-pawn-presence/depth/advantage gates, and a promotion can change H/P without changing population. The already measured material body is therefore moved to each **material-changing produced child**, including early-return/discarded children that may never demand it, instead of eliminated. Root initialization/rebinding and standalone count-only helpers retain separate owners.

A future denominator would distinguish material-changing constructions versus actual full/fast and allowance demands, with repeated demands and zero-demand children. Even a size-neutral field has recompute, branch and copy/register costs; fitting i16 does not select the cache. It also would not automatically cache the hypothetical after endpoints that dominate allowance, since those states are not produced children. Given current evidence I prefer measuring the local redundant endpoint opportunity above before choosing either persistent raw or persistent clamped material. Raw+nonking narrowing remains unselected.

## Decision boundary and validation

No source was edited and no proposal tree was created. No builds, rustc, tests, engine, profiler or benchmark were run; all commands used housekeeping `taskset -c 0-5,8-13`. The prior proposals/reports were not changed. The pressure-value lookup's later parked CPU result does not change this material accounting, and profile-sum PGO work is a separate experiment.

My recommendation is a scoped diagnostic census of **local repeated allowance endpoints first**, alongside the construction/full/fast denominator. Parent can then decide whether to prototype invocation-local reuse; persistent raw or clamped material should not be selected from the present attribution alone. Required future semantic checks include both root colors/asymmetric values, zero-valued non-pawn presence, average-depth signed odd rounding, bishop captures, all promotion types including capture, actual non-pawn joined EP, castling/null, count-only before/after endpoints at50/cap/clamp boundaries, root rebind, parent/sibling/retry preservation and exact full/fast/work replay. Any size-preserving narrowing needs the additional helper-domain proof above. Neither this source proof nor counters qualify native CPU benefit; final comparison must use exact separately verified artifacts, balanced complete lifetimes and disclosed uncertainty. No advisor/Herdr consultation or storage selection is claimed.

## Exact anchors

Native paths below are relative to the immutable old8d source-before tree; other paths are absolute. All43 native/build entries were independently matched to provenance. Listed source files were read to trace actual demand/ownership; the annotation/profile source-line mapping is exclusively old8d.

```text
6199772414ef5972898842d76472301d256e42f9dd2181fa421ff5cbc21c85d1  Cargo.toml
d34b5888f77c0319fb614ba5701a4a1177af31b803054ad3a8251926ba237c97  Cargo.lock
16f26f211a09ab3aa85045c58542f4b841fd6520381214db62bed4f6363b9b3c  src/evaluation.rs
2b638e19566a69899e46cf6bf780271f07a9ac6d80cf1a3d51538b21a6558146  src/evaluator.rs
07ed6db1af2d7fc21f093aa619f5a931aa32d594f4c1b435968ad95691b8bda4  src/quiescence_policy.rs
a79ec111e2d34bb9e4a3c2a7953c5b2a82b011016982fd2b63d6769da3036bf6  src/ordinary_policy.rs
dddd6a260805a7a53ee61ceb74141cb52f9a3fdc899f2350412ffa86be439e33  src/quiescence.rs
446b518a5824a8a60b65666d1b841d959ab2964c995739a2bc44d27bd5a9c442  src/ordinary.rs
713830b62783a81033e1355687534783647b243c51e10f829546d080ce157722  src/first_iteration.rs
1aca5ca308e2fc92b8a2b144dcc12f49e14990c9e5f34ce941fc37bfb4182f45  src/timed.rs
749f9fa1e90684c4df670c115c3c7f7dbdb196cf62b5eb267900ba217143ce3a  src/position.rs
5b369b122dc69aa40e5f8b81c3153173e633c9cfec89f160cef49886b5c36647  src/eval_basis.rs
e25b082c342df61b2aa8c30e2970e65007ad3e99750807724bda42ab59a3045f  src/development.rs
1eea8e56f268a3fd943d1dc2d2ccd0c7607c80793c1a8f41eb464bdc53853c34  src/bin/rook2-dev.rs
2a202da079b16b3becb6651427701ec8e40aed88bd19550854c800b842b22feb  src/types.rs
9990111619222e74aee3e5d944cd08d7f3a6182eb0ef7c3c1c04d742f52e281a  /home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/provenance.json
f512b4dc32493ee906694e2593fabaa309f7a0bafba300f9a24c5be341842495  /home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/profile-01.callgrind
d463ef44a8a05f6b1338f76ae44672da67d62ae5c0a444147a0bf3b6c69fdb4a  /home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/evaluation-lines.stdout
51cef5e7c748e8c25bd662ad32f5b7bcb9915a0cccf34d10bb3fa1f265d4cfac  /home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/evaluator-lines.stdout
608b9e0d094beeaaebf8e07184d7f7d4ff000e097184d1ed4503f8709ca72fe4  /home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/functions.stdout
452d9430fc065db94fffd2c3ccf0aaa788fb73ad683131dbfafa46d2efbe615e  /home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/profile-01-oracle.stdout
0bf78b16b6fcd5ea553b099a294d924919e54bff5cdfd579d742c9866a959b8d  /home/legolas/rook2/docs/research/production-score-capacity.md
858cdbef85adae6c15dba6027470edceb2ba88d8764947344816cb911a9ee7bf  /home/legolas/rook2/docs/research/evaluation-review.md
ff085f7bdb52d13777b40147d3c0b62f69cf9ce33fc4250e6aea9516ffeff6f9  /home/legolas/rook2/diagnostic/src/candidate_order.rs
5ea51bb3b861bdb1f9c5ddd427702b0c2ac966839520f3d33a9a9c046b033a01  /home/legolas/rook2/diagnostic/src/threat.rs
ec81afa0660683ccf12389df3eba8b6b7e5676fc7c8d1fd3a8fdc881df663666  /home/legolas/king-spec/spec/material-balance.md
6608d35bf643cca6880342193b63fa10961de424621bd9e44cb637b11c318220  /home/legolas/king-spec/spec/quiescence-capture-allowance.md
86959d1c5d545737f03a0252d8c34e26a53ea67cca0549d926206263c1ffa302  /home/legolas/king-spec/spec/root-material-context.md
074c4557bc48afa10cfc81c31041570824e4dabde95f0050a8f04aa535e621be  /home/legolas/king-spec/spec/retained-evaluation.md
```

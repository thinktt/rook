# Search intermediate capacity review, 2026-10-18

Focused cold source/algebra review for imp2 by implementation subagent store_origin_review. No source edits, builds, tests, engine executions, profiles, simulations, new agents, or Herdr. Every shell/helper command used taskset affinity0-5,8-13. This new memo is the only write in this review. Normal/Fast OFF requested; available controls expose no live speed setting/readback, so actual speed is unverified.

## Finding

Production depth/target/extension arithmetic closes independently, with ordinary table target<=428 and remembered remaining depth<=366. Search score intermediates material_threat, ordinary-capture allowance, capture estimates and defended deductions are safe given the explicitly stated retained producer premise below. Quiet frontier_estimate is safe even for every i32 positional input. No violating production witness or source change is established.

A sufficient common retained premise is **|P|, |G| <= K = 2147460897 = i32::MAX-22750**, where P/G are produced retained positional/pawn-progress values. This is a very generous *proof obligation*, not a proved producer bound or new runtime admission rule. One can instead supply separate directional bounds for the formulas below. Establishing all FULL retained P/G producers is explicitly outside this review. The lemma also assumes those producer computations themselves completed correctly; a small resulting value cannot establish that earlier multiplication/casts did not overflow.

The earlier `evidence/store-origin-review-20261018/production-tt-origin-cold-proof-20261018-store-origin-review.md` closes completed search return/window/TT capacity using consumed endpoint bounds and clipped evaluator scores. This memo addresses the missing bounded group of search formulas before their cutoff gates, rather than assuming that a later gate repairs overflow.

## Common produced context and material delta

Released POSITION-SETUP admits at most16 pieces per color including exactly one king, at most8 pawns per color, and no end-rank pawns. Ordinary captures/null/promotions never increase total counted nonking pieces above30. A valid ordinary destination victim has a positive count, so allowance's hypothetical count decrement cannot underflow. Exceptional king-victim continuation is fatal before another ordinary search and supplies no production root context here.

`evaluation.rs:25-79` constructs root values with percentages0..1000 and nonnegative phase weights summing256. Fixed bases are at most900, the converted weight is at most10240, and the largest multiplication plus rounding offset is10240*900+512=9216512. The phase blend numerator is <=256*900+128=230528. All fit i32; the blend itself uses i64. Produced per-kind values are bounded by pawn1000, knight3000, bishop3100, rook5000, queen9000. They are nonnegative. This is tighter than the component helper's supplied0..10000 value domain.

All normative positional basis entries range[-99,35]; nonking entries range[-16,35]. These extrema were read from released positional-value-basis.json; current generated eval_basis.rs is bound below. A nonnegative phase blend preserves that range, so the cast to i16 for root squares is safe. For the scoped threat formula even the looser[-99,35] bound suffices.

`RootContext::material` (`evaluation.rs:94-144`) is safe on these contexts: counted totals are <=30, weighted counted material sum is <=270000, root/current count difference is inside[-30,30], and the average-depth numerator is inside[-2999,3001]. The signed D term is inside[-1500,1500]. A loose bound on each pre-adjustment balance prefix is271500, so abs() cannot encounter i32::MIN. The nonnegative losing-heavy factor is at most150; the winning-pawn factor is at most100. Thus the extra magnitude is at most250, computed in i64 then safely cast to i32. `3*pawns[winning]` is <=90000 even using the loose30-pawn upper bound; the actual eight-pawn bound is tighter. All intermediate +/- terms are small, and final material clips to[-7000,7000].

Allowance calls material before and after removing one victim. Therefore each material result is inside[-7000,7000], the difference is inside[-14000,14000], and the capturing-side gain g=-sign*(after-before) is inside[-14000,14000]. This proof deliberately does not assume gain>=0 or material monotonicity with arbitrary asymmetric personalities/avd.

## material_threat and its subtractive consumers

`ordinary_policy.rs:112-175` scans nonking piece candidates and starts result.value at zero. A contested piece contributes square+20; an unfavorable piece contributes square+root value; optional sparse addition is600. Hence all piece candidates are <=35+9000+600=9635, and their negative extrema are harmless because max starts at0. Each candidate addition independently fits i32. No accumulation of candidates occurs, only maximum. Per-call relation-query count is <=15 and stored in u64.

The near-promotion pawn contribution is750+max(0,-G) or750+max(0,G). Under |G|<=K, negating G is safe, and the resulting threat T satisfies

`0 <= T <= max(9635, K+750)`.

Its piece-count sum uses u16 and <=15 nonking units; coordinates are bounded board offsets. No other retained quantity enters threat.

Fast finished score is in[-7900,7900]; its margin gives adjusted score in[-8050,7800]. Thus the raw `adjusted-T` arithmetic is inside

`[-8050-max(9635,K+750), 7800]`.

At the stated K the lower endpoint is-2147469697, greater than i32::MIN by13951. The direct shallow trial is staticScore-T-25/40, bounded below by-7940-max(9635,K+750), also safe. This closes the actual subtractive expressions before `trial>=request.upper`, rather than relying on the successful cutoff to prove their computations safe. The later store gate still supplies the much tighter returned-score bound in the prior TT proof.

A separate sufficient progress-only premise for the fast subtraction would be |G|<=2147474848; the common K below is stricter because capture estimates add more positive terms. Neither is claimed as the actual producer maximum.

## Capture allowance, estimate, defense and optimistic best

`quiescence_policy.rs:53-91` selects G only for a captured pawn when sign*G>0, otherwise P. Its sign is +/-1. Under |P|,|G|<=K, both sign*G and sign*selected retained are safe, and the selected nonnegative max is in[0,K]. With g in[-14000,14000], base50 and exception e in{0,800}, allowance A satisfies

`-13950 <= A <= K+14850`.

Source left-association is also safe: g+50 lies[-13950,14050]; adding the retained max reaches at most K+14050; adding e reaches K+14850. There is no hidden multiplication by a personality coefficient in this combination.

Actual ordinary/Q static standing scores are in[-7900,7900], so the initial ordinary-capture estimate E=standing+A lies

`-21850 <= E <= K+22750`.

Our K makes that upper endpoint exactly i32::MAX. The same expression is used by ordinary frontier capture and Q capture estimation (`ordinary_policy.rs:189-192`, `quiescence.rs:268-280`). Both therefore fit i32 before the skip/search decision. No +/-10000 restriction on P/G has been imported from standalone diagnostic domains.

The moving-piece deduction V is50 for a king, otherwise a nonnegative produced root material value<=9000 (`quiescence_policy.rs:95-102`). Thus E-V lies inside[-30850, K+22750]. Subtraction cannot enlarge the positive upper bound and cannot underflow at its lower bound. It is evaluated only under the short-circuit defense gate, but this wider interval already proves capacity without relying on that gate. Capture-policy returned estimates remain in this interval.

The actual optimistic best does not inherit an unbounded estimate. Under the existing window proof, Q endpoints lie inside+/-10061, its running alpha is raised only by clipped standing/actual Q children, and hence alpha<=10061. Best begins at a clipped standing score or-10000. A forceSearch estimate leaves best unchanged; any optimistic update has estimate<=max(best,alpha). Consequently best remains in[-10000,10061] until final cap. This proves comparison/update capacity separately from the potentially much larger raw estimate. Final Q results remain inside+/-10000, as established in the prior memo.

## Quiet frontier arithmetic needs no retained-magnitude premise

`ordinary_policy.rs:177-202` returns10000 immediately for a special/check move. An ordinary quiet move starts with clipped staticScore+30 in[-7870,7930]. For White, negative P<-1 is divided with floor first, then negated. Even P=i32::MIN yields -floor(P/2)=1073741824, safely representable. For Black, P>1 yields floor(P/2)<=1073741823. Thus for **every possible i32 P**, this quiet estimate lies

`-7870 <= quietEstimate <= 1073749754`.

Its additions and negation cannot overflow. The quiet rule does not inspect G. The common retained premise is needed by sign selection in capture allowance and near-promotion threat, not by this half-P expression. The frontier estimate's consumption guard alone would not establish its producer capacity, but here the producer is bounded directly.

## Production depth, target and narrowing

Ordinary terminal stopping runs after every completed iteration and stops at D>61 (`iteration-terminal-stop.md`; `timing.rs`). Thus an actual ordinary timed search enters only1<=D<=62, including default md999. The current timed API admits maximum entered iterations1..62 (`timed.rs:440`) and production binary supplies62 (`src/bin/rook2.rs:113`); fixed development iterations enter at most8. The released scalar terminal diagnostic's D<=64 is independent of actual search recursion. The following production bounds use D<=62, not a helper's arbitrary depth argument or personality md as a recursion depth.

Fresh extensions are0..6: sparse victim value2..4 plus low-pawn additions0..2 plus allowance0..2 minus2; its minimum is0 and maximum6. Other extension branches are0..2. OR accumulation therefore stays0..7. Previous-extension conversion to i32 is0..7; allowance=max(0,2-previous_extension) stays0..2. The extension `as u8` cannot wrap on actual inputs. Importantly main depth uses fresh extension, not accumulated OR flags.

At root child ply1, remaining depth d=D-1<=61. Every main descent increases d by at most5 (`d-1+fresh`, fresh<=6). An IIO child uses d-offset+fresh-1 with offset>=2, increasing by at most3. A null child decreases d by3/4. Every actual child increases ply by1. Thus

`d(p) <= D-1+5*(p-1)`, and `target(p)=p+d(p) <= D+6*(p-1)`.

An ordinary node only expands when d>0 and p<=62. A null child can have d=-2 at minimum; main children have d>=0, and admitted IIO children have d>=1. Therefore all ordinary-entry depth computations lie in[-2,371], including p63 delegation. Plys and their i32 casts lie1..63. Largest target at p63 is434; largest table-access target at p62 is428. The remembered required/stored depth is exactly target-p=d, so **1..366**, safely inside i16. Probe mate upgrades take max with another value in that same range; standalone arbitrary Query inputs are not an actual production counterexample.

IIO target-offset lies inside[-18,426] before its admission check, offset is2..20, and all subsequent target+fresh-p-1 prefixes are within a few hundred. target/2, target-3, p+1, p+2, d-2 and null depth subtraction are equally small. Material encodings use u32 with nonnegative total<=30 and largest coefficient65536, so even a loose bound1966080 fits before division/modulo.

Q receives target=max(0,p+d) on ordinary delegation. If entered at p0 and recursing to p, its target increases by at most p-p0, because only checked parents add1. Therefore its target is at most D+6*(p0-1)+(p-p0)<=434 over p<=63. Checking-mate probes start at p0 with target=p0 and have target<=63. First-iteration Q likewise stays<=63. The largest target+iteration is434+62=496, and defense boundary target+(iteration-1)/2 is at most434+30=464. These plain i32 additions cannot overflow.

`selective_depth` deliberately uses wrapping_sub/add on its signed32 sel intermediates, exactly as the released rule requires. For production D in1..62, its final min(D,max(1,...)) always gives margin1..D regardless of wrapped sel; adjustment=D-margin is0..D-1<=61. The final plain target-adjustment therefore stays within[-61,434] under the broader target bounds. Default/new or arbitrary stored signed32 sel does not create an unbounded adjustment. Actual root depth token1000*D+margin<=62062 also fits i32.

The positive depth as-u32 cast used by Learning::record is safe at actual ordinary store/update sites: d<=366 and increment8*(d+1)<=2936. This is a bound on the depth-derived conversion; no arbitrary negative helper-only depth is admitted there. No source issue follows from manually calling this helper with an invalid negative value.

## Scoped remaining inputs

Search-local arithmetic above closes once the FULL retained producers and inheritance lifecycle establish the generous common |P|,|G|<=2147460897 premise (or appropriately separate directional bounds). Existing standalone capture/threat/frontier component domains of +/-10000 cannot substitute for that producer proof. Current finished-score clipping likewise does not establish retained P/G magnitude, because large terms could cancel before score finishing.

This memo does not derive every evaluator retained producer or its upstream i32/i64/cast prefix. It does not claim that arbitrary public Rust helper arguments are production-reachable. It identifies no concrete admitted production overflow witness, and recommends no source edit solely because an external producer premise remains open.

## Identity

Canonical reference `evidence/production-activity-specialization-instrumented-build-20261018/receipt.json`: SHA256 c038754a2b392e6f53624a375e6840299000ee128e031cd6295d822338e14f54; instrumented binary 12c2af4cbe01bf47fa29c5ecb8282ca2298b585795b995128f51dead11d5b3b7. All native files below independently match both source_sha256_before and source_sha256_after in that receipt. This includes current activity specialization; no new activity producer proof is asserted.

- `src/ordinary_policy.rs`: `a79ec111e2d34bb9e4a3c2a7953c5b2a82b011016982fd2b63d6769da3036bf6`
- `src/quiescence_policy.rs`: `07ed6db1af2d7fc21f093aa619f5a931aa32d594f4c1b435968ad95691b8bda4`
- `src/ordinary.rs`: `446b518a5824a8a60b65666d1b841d959ab2964c995739a2bc44d27bd5a9c442`
- `src/quiescence.rs`: `dddd6a260805a7a53ee61ceb74141cb52f9a3fdc899f2350412ffa86be439e33`
- `src/timed.rs`: `1aca5ca308e2fc92b8a2b144dcc12f49e14990c9e5f34ce941fc37bfb4182f45`
- `src/remembered.rs`: `af2eb6046fd7e58b1a35e7ed3051936559b7f739224ed698b54c49317faec293`
- `src/evaluation.rs`: `16f26f211a09ab3aa85045c58542f4b841fd6520381214db62bed4f6363b9b3c`
- `src/evaluator.rs`: `2b638e19566a69899e46cf6bf780271f07a9ac6d80cf1a3d51538b21a6558146`
- `src/eval_basis.rs`: `5b369b122dc69aa40e5f8b81c3153173e633c9cfec89f160cef49886b5c36647`
- `src/parameters.rs`: `30dd03e5ead3df289b25929c7bea81e72d1e2b9a2250916883107f0cfaf7f42e`
- `src/bin/rook2.rs`: `26849c997a5c564076dc5c6703dcdce783e900b0c221d7938f540664edd1a3b8`
- `src/timing.rs`: `fb7c256ececf164c1ce3bd476b997b9cd2b20aef1eaf4b22776c6f6b33efd5b8`
- `src/activity.rs`: `07d1b062f5ce6a4ffb66bd57eb3570f9221f42d7105b1df1f11e3039caf93c38`

Released king-spec files read for this review:

- `spec/material-threat.md`: `5052da3592b9357218753534dee0a43dcca64988b7090be7b42de8acb7fd94f4`
- `spec/quiescence-capture-allowance.md`: `6608d35bf643cca6880342193b63fa10961de424621bd9e44cb637b11c318220`
- `spec/quiescence-capture-policy.md`: `ed3ba0fad8a981bc999be761e386d883b9a3ed292e5429a24953a6b2407ab619`
- `spec/frontier-estimate.md`: `7a2034997235aac6e188e00337df0116b658d69f9857ff06892e5b2df49eb155`
- `spec/move-extensions.md`: `fc20c831cde92637229b19625b3a0cac90d7b9ec18187d991ce4a3b25b30a6fe`
- `spec/selective-depth.md`: `cbd9563541d7620c908ee606aa5562680774f53d5513145b4c5115ead77b7833`
- `spec/root-material-context.md`: `86959d1c5d545737f03a0252d8c34e26a53ea67cca0549d926206263c1ffa302`
- `spec/material-balance.md`: `ec81afa0660683ccf12389df3eba8b6b7e5676fc7c8d1fd3a8fdc881df663666`
- `spec/positional-value-basis.json`: `33f1b39c468b9e3e39ef0b335a75d5c0ea1ac989533fe525e191d87486636bb7`
- `spec/position-setup.md`: `93d94c7fdf8812b8a3eaabf4b66d796912bf53a994d406a107a6ca8e808cac3b`
- `spec/ordinary-xboard-wire.md`: `5292029af4fca1299e8600194b197720d625cb5231d0672f804e788d0b9961f5`
- `spec/ordinary-iterations.md`: `a16d33b123d67f0ae82384bd6d24dba4163685400b00f188f46f13c511fcaafb`
- `spec/iteration-terminal-stop.md`: `856708d81584a7a48ad112f7289ea2d7e17cd5590356dde4dc1ac5bd3b6b85d3`

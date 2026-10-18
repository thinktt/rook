# Production retained producer and principal evaluator bounds, 2026-10-18

Cold source/algebra review for imp2 by its retained-arithmetic child. No engine execution, build, test, profiling, simulation, source edits, Imp1/Rook access, Herdr calls or further agents. All shell/helper commands used `taskset -c 0-5,8-13`; measurement CPU14 and sibling15 were not used. Requested speed Normal; available controls expose no speed readback, so actual speed is unverified. This is the only written artifact.

## Finding

For the production producer domain and lifecycle prerequisites below, conservative bounds are:

| Produced quantity | Absolute bound |
| --- | ---: |
| Retained positional subtotal P | 270000 |
| Retained pawn progress G | 36000 |
| Root-valued current material M after clamp | 7000 |
| Combined current/root square contribution Q | 6336 |
| Full tempo | 78 |
| Full or fast base | 320000 |
| Adjusted base A after preference and variation | 333000 |
| Late material-blended score, including inherited G | 350000 |

In particular both retained bounds are substantially smaller than the parent's independently established sufficient search-consumer limit 2147460897. This closes the P/G producer prerequisite of that conditional search arithmetic result. It does not prove all search arithmetic or source-global capacity.

## Native identity and released scope

Reference native43 is the supplied activity-specialization instrumented build receipt. Its binary output SHA256 is `12c2af4cbe01bf47fa29c5ecb8282ca2298b585795b995128f51dead11d5b3b7`. The receipt records a generic x86-64 PGO-generate build; this review performs no build or execution. Every native file hashed below matches both receipt source maps. Receipt SHA256: c038754a2b392e6f53624a375e6840299000ee128e031cd6295d822338e14f54.

The producer bound uses the broader POSITION-SETUP admission: one king/color, at most sixteen total pieces/color and eight pawns/color, with no pawn on ranks1/8. There is no legal-history inference limiting knight/bishop/rook counts to ten or queens to nine. Those narrower counts in some standalone helper schemas are not production assumptions. Up to fifteen nonking pieces of one type/color are allowed here.

Effective evaluation percentages are 0..1000, avd -100..100, cfd -10000..10000, sop 0..100. `parameters::bind` enforces the native effective domains; stored opk is excluded and is not consumed by these expressions. Arbitrary signed-i32 percentages admitted by the standalone personality conversion diagnostic are a different domain and do not enlarge admitted producer coefficients. `coefficient(p)` deliberately wraps its multiply/add, but for production p, 0 <= 1024p+50 <= 1024050, so no wrap occurs and coefficients lie in 0..10240. Production cached doubled-pawn coefficients are fixed at 1024.

The supplied-input final-score diagnostic's late A limit of +/-10000 is explicitly not a production restriction. No such limit is used here.

## Input invariants robust to collisions and wrapping

`Position::phase` normalizes total minor/heavy counts with base16 carries and clamps its opening/endgame calculations. Regardless of material distribution its O,M,E are nonnegative and sum to256. No orthodox material-total assumption is needed. Consequently O+M<=256, M+2E<=512, O+2M+E<=512, 13O+14M+19E<=4864, and 5O+4M+2E<=1280.

Evaluation influence addition intentionally wraps in u8. This proof permits every influence byte in0..255, including normalized category carries that are not literal attacker counts. `profile_sum` sums its five encoded digits, so it is <=11. Relation categories are0..2, raised by capture priority to at most3. Activity marks are arbitrary u8 bitsets for the purpose of the bound. The proof never substitutes the actual number of attacking pieces for a wrapped digit.

Every pawn cache entry is either initial empty or a fresh result from an admitted producer, with <=8 unique valid interior-rank descriptors/color. Replacement, group collision, full-identity collision, zero-identity equality and clear preserve that union. A full fingerprint collision can retain the complete old base score, descriptor order and geometry. The bound permits this without demanding matching current pawn sets. Current structural penalties and progress filter actual same-color pawn membership; raw pawn-related piece activity intentionally consumes the stale descriptor geometry without that filter. Initial empty equality is allowed, including a possible nonempty pawn placement with fingerprint zero.

## Pawn structure: <=31000

For each cached color, support is in[-24,16] and doubled penalty in[0,272], giving base in[-296,16]. Each current matched descriptor receives a nonnegative structural penalty. Occupied pressure is <=50 (table maximum10 plus rook-line maximum40); advance pressure <=25; exposed row <=6; isolated row <=10. Every branch is therefore <=81. Thus current structure/color is in[-944,16], even with stale cached base and at most eight current matches.

Pawn-related raw knight factor is <=4+11+1+3+2=21 and table value<=20, so each piece contributes <=105; bishop/rook values<=15. With <=15 nonking pieces/color, raw and phase-scaled piece totals are each in[0,1575]. Thus each `(structure - opposite_piece)` lies in[-2519,16]. Its signed two-color weighted numerator, with weights in[0,10240], gives a first rounded score in[-25350,25350]. Applying the maximum4864/4096 phase multiplier and final half rounding gives magnitude <=30104, covered by31000. The i32 subtractions happen before i64 conversion but are already within these bounds.

## Activity: <=52000; full tempo <=78

Per activity piece, curve contributes0..36. Attack deduction is <=5*11+2=57. Low mobility deduction is <=12*3+6+15=57, since mobility category totals are nonnegative. Therefore raw piece score is in[-114,36]; <=15 pieces/color yield raw color in[-1710,540]. Scaling by276/256 with half rounding gives absolute activity piece score <=1844 (positive endpoint is only582).

The material-adjusted coefficients are nonnegative and <=12800. Using the symmetric absolute piece bound, the weighted color difference has magnitude <=46101, including rounding slack. The final multiplier is <=9*512/4096=9/8, giving <52000. All mobility destination/category accumulations are nonnegative and bounded by finite board rays; the curve index clamp at119 is applied to a nonnegative value, so no negative index is hidden in this argument.

Full tempo uses the current color's activity piece score, not weighted activity. Its absolute numerator is bounded by(1844+140)*1280+16384, so magnitude<=78. Fast tempo is0 or +/-6.

## Shelter: <=185001

This deliberately loose bound allows arbitrary marks and influence bytes. For one ring square the maximum is66, so ring<=528. File scans examine at most21 squares, each contribution<=22, hence files<=462. Screen is in[-16,14]. Shelter pattern is <=29 and exposure is >=-44, so absolute shelter term<=44.

`pressure_value` over an arbitrary byte is <=16+24+3*8+3*16=112. King pressure can visit at most8 rays*7 squares plus8 knight squares; knight mask3 contributes at most40. Discarding the subtract12 only enlarges the bound, so activity pressure<=56*112+8*40=6592. Masks, ray lengths, occupancy and material gates would tighten this bound but are unnecessary.

Composed pressure is <=528/2+462+6592=7318. Its pressure phase scale, middle phase and shelter phase scale are each<=256. Thus absolute composed shelter/color is <=7318+16+44+1=7379, covered by7400. The material-adjusted weights are <=12800; two independent absolute color terms give <=185000 plus rounding slack, covered by185001.

## Central, bishops, patterns and P

The24 central square weights sum to408. The magnitude map is <=225, giving each nonnegative color score <=floor(408*225/1024)=89. Independent nonnegative color weights<=10240 bound the signed difference by890. Final central phase factor<=512 cannot enlarge it, so |central|<=890.

Bishop base coordination has magnitude<=44. A color's sole-bishop pawn penalty has pawn sum<=8*14*2=224, multiplier<=8, and result<=floor((8*224-80)/16)=107. Permitting both colors independently gives |bishops|<=44+2*107=258. A loose opening raw bound is2*(7+12+7+18)=88; opening gating and rounding preserve that absolute bound.

Therefore |P| <=31000+52000+890+185001+258+88=269237 <270000. Every partial sum in `Components::positional` satisfies the same sum-of-absolute-components bound, so i32 additions cannot overflow before the final subtotal.

## Progress G: <=36000

Only current same-color pawns surviving the stale candidate-descriptor filter are evaluated; each still has normalized rank2..7. Start measure rank-4<=3. The first behind piece adds at most2. At most six forward squares each add at most2 for rook occupancy (<=12 total); own-control awards add at most one/square plus one extra terminal award (<=7 total). Hence measure<=24. Negative measure is clamped to-2 before multiplication, so raw is nonnegative. Using table maximum120 and support multiplier<=11/8, raw <=floor(floor(120*28*11/64)*11/8)=793, covered by800. This bound deliberately ignores rank/path correlations.

Candidate intermediate <=floor((800*83+1440)/64)=1060. King-distance factor<=73, then lone-rook bonus<=400, giving candidate score<=1609, covered by1610. Nonnegative leading scores are at most1610, so `(16*highest+12*second+8)/16` is <=2818, covered by2820; at most two leaders are summed regardless of eight candidates.

Pawn ending is0,+/-400 or+/-480. Queen ending has magnitude<=520 even before its pawn-count divisor; fallback magnitude<=160. Thus |ending|<=520. Adjusted progress weights are in[0,12800]. Because path scores are nonnegative, the difference of their two products has magnitude <=12800*2820 (not twice that). Dividing by1024 with half rounding and adding ending gives <=35250+520=35770. Final phase factor<=512 preserves this bound, covered by36000. All raw/path/candidate i32 products are consequently small (largest per-candidate numerator here is67840), and the weighted i64 results safely fit their final i32 casts.

## Material, updated squares, subtotal and final-stage capacity

Root material phase interpolation stays between pure-phase bases, at most900; coefficients<=10240 give effective values<=9000. Each side has<=15 nonkings, so its current material total<=135000. Root/current nonking counts each lie0..30, giving |d|<=1500 for avd. Raw signed balance magnitude<=136500. Losing-heavy correction<=150, winning-pawn correction<=100, and the common gain factor<=1 give extra<=250. Hence preclamp material magnitude<=136750, then M is explicitly clamped to7000. Root coefficient/base multiplication is <=9216000+512, far below i32 capacity. Pawns<=8 with value<=1000, so `3*pawns` is also safe.

The1152 current native square-basis literals were counted and checked: minimum-99, maximum35. Convex phase interpolation and half rounding keep each square magnitude<=99. At most30 nonkings give |nonking_sum|<=2970. The two current king differences have magnitude<=198 and their single phase interpolation preserves198. Thus combined square magnitude<=3168, doubled at most once in pawn-only material, giving Q<=6336. This permits root-phase nonking values after current captures/promotions. Node child subtraction/addition and the castle rook correction preserve the exact current-board root-valued nonking sum; even transient update expressions have magnitude<3500 under that invariant. Null copies it.

Full `Components::base` and fast `M+Q+P+G+tempo` have magnitude<=270000+36000+7000+6336+78=319414, covered by320000. Their intermediate addition order is covered by the same absolute sum. Root preference magnitude<=10000; sop gives range<=5300 and deterministic variation magnitude<=2650, so adjusted base magnitude<=332650, covered by333000. No estimate of attainable score is needed.

At E192..256, pawn-spread scale is between3456/4096 and4288/4096, giving magnitude<350000. Pawnless potential is a reduction of absolute score, minor mate has magnitude<=825, selected progress substitution reduces magnitude, and material blending is a convex combination of the adjusted score and |G|<=36000. Therefore its output is bounded by350000. `3*score` in pawnless potential and queen fortress is <=1050000. Race endpoint division plus700 has magnitude<=88200; literal fortress endpoints are small, so all these i32 values/negations are safe. This is a capacity bound, not a proof these loose unconditional endpoints stay within +/-10000 or i16. The tighter selected-FULL-race proof and caller-discard argument remain in the earlier bounded score review.

The largest loose principal product here is the explicitly i64 pawn-spread numerator333000*4288+2048=1427906048; reviewed component weighting products are smaller. Final score clip precedes reversible scaling, keeping final score within7900 for h0..255. The halfmove and evaluation-age increments intentionally wrap in u8; no argument relies on an age refresh limit or a reversible count beyond its byte domain.

## Retained-state induction and remaining obligations

`Node::root` starts P=G=0. `full_impl` is the only non-test producer writing them in src: it replaces them with the bounded components above. `Node::child` and null child copy both unchanged, while updating squares and wrapping age; restoration/copying of a valid Node cannot enlarge them. Fast reads without mutation. Therefore arbitrary stale inheritance, including an earlier heavy ancestor followed by pawn-only material, remains bounded. This does not require age<256, a recent FULL ancestor, or the current position to share the producer's material. `begin_search` binds a fresh root and clears pawn entries; even omitted clears would preserve these numerical cache bounds if all entries have admitted origins. The source scan found no non-test arbitrary P/G assignment elsewhere in src; public fields in Rust are not themselves a production wire input.

Prerequisites are internally consistent admitted position lists/counts/board, exactly one extant king/color when evaluation runs, retained square maintenance using the same fixed root context, and effective production coefficient admission. Legal move transitions preserve total piece/pawn capacities; promotion changes kind but not total count, while capture removes pieces. This bounded review checks arithmetic under those invariants, rather than reproving all session admission/move generation/undo semantics. The released exceptional king-victim EP continuation is fatal on subsequent go and is not an admitted ordinary evaluation of a kingless board.

Independent helper schemas accepting supplied coefficients, raw structures, arbitrary retained values, supplied phase/material/subtotals or negative/extreme personality percentages must be assessed on their own domains. They are not covered by this production induction. No complete source-global arithmetic audit, search/TT/window induction, diagnostics audit, performance qualification or conformance result is claimed. No defect or implementation change is established by this conservative range proof.

## Reviewed native SHA256

- `src/activity.rs`: `07d1b062f5ce6a4ffb66bd57eb3570f9221f42d7105b1df1f11e3039caf93c38`
- `src/evaluation.rs`: `16f26f211a09ab3aa85045c58542f4b841fd6520381214db62bed4f6363b9b3c`
- `src/evaluator.rs`: `2b638e19566a69899e46cf6bf780271f07a9ac6d80cf1a3d51538b21a6558146`
- `src/pawn_progress.rs`: `efb62166204229ad18c319eca2c6dc2bf0aad60bff8e57c2eff3d580b3b64934`
- `src/pawn_structure.rs`: `64473dc7b7d3d235b86caec1e8755d7edb0deae895de26b7129a65b1202bf04c`
- `src/pawn_terms.rs`: `41f5b0c8b5e5923dab8a69c4aa7c9dea80d7401225ed4f82f5e0f6701bf71305`
- `src/shelter.rs`: `fbef039d833ab726eae109f5fef40793a5ab6587838463bbff105b376e8c24de`
- `src/positional_terms.rs`: `053b04b8f434db2ddadda71686831b40baf3c59d09be6cde5895af1b7d430260`
- `src/influence.rs`: `05b402b7e0137720d5fb4d2f062601ebf5abf61411fe648531cdc94e2959843e`
- `src/position.rs`: `749f9fa1e90684c4df670c115c3c7f7dbdb196cf62b5eb267900ba217143ce3a`
- `src/parameters.rs`: `30dd03e5ead3df289b25929c7bea81e72d1e2b9a2250916883107f0cfaf7f42e`
- `src/endgame.rs`: `3b50609fc5671891ac74d79bbb12c5bd0ed98c3a51f302dcf7b5750373948176`
- `src/eval_basis.rs`: `5b369b122dc69aa40e5f8b81c3153173e633c9cfec89f160cef49886b5c36647`

## Reviewed released SHA256

- `spec/position-setup.md`: `93d94c7fdf8812b8a3eaabf4b66d796912bf53a994d406a107a6ca8e808cac3b`
- `spec/ordinary-xboard-wire.md`: `5292029af4fca1299e8600194b197720d625cb5231d0672f804e788d0b9961f5`
- `spec/ordinary-play-ingress.md`: `772224e1bc51bfcd7a248d36511367bd52f5aeb7da6579f7d83ac175f65d3959`
- `spec/personality-configuration.md`: `365cbde8dddf0fbcbc6b714aee8e7fd1c88138513dbc5d892d5364ce02493afc`
- `spec/personality-evaluation-weights.md`: `d15a0896cec90da4bd50144a302eefe7bbfd7c81e2eeeb41551663c209ea3e38`
- `spec/root-material-context.md`: `86959d1c5d545737f03a0252d8c34e26a53ea67cca0549d926206263c1ffa302`
- `spec/positional-values.md`: `013e936be36c077f8a35350a36df06e86a0f9ca1cf93756d246cbbda4e9a1628`
- `spec/evaluation-subtotal.md`: `7371fd7c55ebc428c308bc86d21027dfb4ad577402559cf39069f990c4ab769f`
- `spec/retained-evaluation.md`: `074c4557bc48afa10cfc81c31041570824e4dabde95f0050a8f04aa535e621be`
- `spec/retained-pawn-structure.md`: `c4a36885c2d7da4e4740e1af5bf79a50874b47f874f1ed015fd93fb4ee6b4ecb`
- `spec/fresh-score.md`: `f617a6596ae7013cc03fe16a58d917648f5e85d0c644e406f00ff291387764a8`
- `spec/final-score.md`: `e1eb4708d3a02aeccca0c2fbaab6990e78c222eaea48a28be21e1fc7ce740d9e`
- `spec/positional-value-basis.json`: `33f1b39c468b9e3e39ef0b335a75d5c0ea1ac989533fe525e191d87486636bb7`

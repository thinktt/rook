# Candidate26: full-evaluation phase sharing

**Recommend a narrow, stateless full-evaluation phase-sharing trial only. Leave fast→full material/phase transport out initially.** Current51529 source and actual emitted code retain repeated phase normalization in four full-only leaf consumers despite `full_impl` already holding the same current-position Phase. A bounded instruction envelope is material enough to test and smaller/more concrete than broad evaluation-owner totals. No implementation or gain is selected by this review.

## Exact current evidence and attribution

Current own-PGO image is51529cebf24ad91b0cf86e4ae497bc32bb7ad7a819f8b300f8b86028326b254a; candidate69graphd4bb0f94, native source46. [Current profile proof](/home/legolas/rook2/evidence/candidate25-callgrind-20261018-01/independent-verification.json) and [absolute annotation receipt](/home/legolas/rook2/evidence/candidate25-callgrind-absolute-annotation-20261018-01/receipt.json) bind the two original workloads. Relative old reports are not used. Totals are45,762,253,122 Ir(case35) and3,967,850,732 Ir(case08). Ir is **simulated instructions**, not PMU, CPU time or cycles; old79d/6a shares do not transfer.

The raw profiles are only352,972 and308,255bytes. One bounded offline extraction reconstructed compressed file/function/line identities, excluded the inclusive cost record after every `calls=`, and summed all remaining self-cost rows. Both exact sums equal their raw profile summaries. It also matched the published exclusive `position.rs`/`evaluation.rs` file:function rows. Results are in [case35](profile-35-basis-attribution.json), [case08](profile-08-basis-attribution.json). These retain each selected source/function/line cost. No entry count was inferred from Ir, block0 or unidentified lines. The new captured own-image source-line regions are bounded to full4936B, activity9064B, shelter6187B, phase217B and square helper624B, using read-only objdump only; [capture identities](static-capture.json) bind exact51529 and the tool. No engine/profiler/build was run.

## Surviving duplication and existing CSE

[Full owner](/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src/evaluator.rs:361) computes actual current Phase and material before unchanged PawnCache selection. Its named leaf calls then independently derive phase from the same immutable position:

| Consumer | Existing input and smallest useful addition | Current source ownership |
| --- | --- | --- |
| activity | pass current endgame phase, or Phase to a private helper; keep public `compute` deriving it | [activity.rs:94](/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src/activity.rs:94), phase101 |
| shelter | pass actual current Phase to composition helper; keep public `compute` deriving it | [shelter.rs:52](/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src/shelter.rs:52), phase61 |
| pawn terms | use **existing** `compute_with_phase(position,influence,selected,phase)` | [pawn_terms.rs:364](/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src/pawn_terms.rs:364) |
| opening patterns | pass current opening component to private helper; public `patterns` remains self-sufficient | [positional_terms.rs:172](/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src/positional_terms.rs:172) |

No material value needs precomputing or transporting to enable these four changes. Phase depends on the actual position counts and starting units; the exact six-byte source value can remain an invocation local. The four public/self-contained wrappers continue serving independent component and synthetic diagnostic callers. Existing explicit phase APIs must continue honoring their supplied independent phases; do not replace them with a derived root/current phase.

This is not merely counting source `.phase()` spellings. Actual activity115cd–116eb and shelter2841d–284fc contain count loading/carry normalization/material/phase arithmetic; they are separately outlined bodies, so caller CSE has not erased those prefixes. Their source-phase rows execute in the closed profiles. `full_impl` also retains distinct phase arithmetic clusters at36869–36966,3721a–3730c and37597–37660, with surrounding source contexts in [full source lowering](full-source-lines.asm). These clusters mix the full producer's initial phase, current-phase kings and finishing/late-flag uses; do not assume all of their cost is redundant. Some loads are common with material and other work, and the compiler already folds/changes the threshold arithmetic.

There is also positive CSE evidence: the separately emitted [fast body](/home/legolas/rook2/evidence/ordinary-projected-bits-pgo-codegen-review-20261018-01/candidate/body-fe40.asm) calls phase atfede, keeps endgame inr12 and reuses it for the finishing argument and final `>=192` flag atff21. It does **not** execute two full phase calculations merely because finish source has two `.phase()` calls. The actual full body already inlines material rather than calling a second material producer inside full. A source rewrite passing phase must therefore be judged by new lowering, not the number of source calls removed.

## Conservative nonoverlapping envelope

Only raw self-cost rows under `position.rs:356–379` **and these four leaf function owners** are summed below. All other position, evaluation, recursive, compiler-core, unidentified and call-edge costs are excluded. Do not add these rows to activity/shelter/whole-full totals; they are subsets.

| Disjoint phase source/function rows |35 Ir |08 Ir |
| --- | ---: | ---: |
| activity |108,640,638 |24,966,615 |
| shelter |100,768,128 |23,157,440 |
| pawn terms |69,278,088 |15,920,740 |
| patterns |51,958,566 |11,940,555 |
| **Broad selected envelope** |**330,645,420 (0.7225%)** |**75,985,350 (1.9150%)** |
| **Tighter arithmetic subset** |**217,281,276 (0.4748%)** |**49,933,230 (1.2584%)** |

The tighter subset keeps only lines362,363,366,367,373,376 (carry/modulo/material/phase arithmetic), excluding count loads/accumulation359 and return379. This reduces the risk of calling shared count loads removable. Even that subset is an affected-instruction envelope, **not a guaranteed saved-instruction lower bound**: address attribution can bundle shared work, new argument transport may cost instructions, and compiler factoring/spills can move. No CPU saving is predicted. The unused full_impl phase envelope82,613,877/19,091,635 is intentionally not credited; at least the original phase calculation is required. No net material, king blending, endgame arithmetic or entire caller is credited.

## Why fast→full is deferred

There are two actual source routes: [ordinary768–796](/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src/ordinary.rs:768) performs a gated fast evaluation, optional pressure/threat/cutoff work and full evaluation on fallthrough; [noncheck selector641–657](/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src/evaluator.rs:641) performs fast, tests strict lower−250/upper+250 or capture exception, and optionally full. Sparse admission starts full without fast. Position and root remain unchanged between a reached fast and full on these paths, so reusing already produced scalar inputs is semantically plausible. Checked Q at high ply may only fast-evaluate, and other Q paths skip evaluation entirely; none should eagerly compute a basis for a hypothetical future full.

The closed profile has nonzero selector refresh-arm attribution (evaluator649:1,184,778/2,112 Ir) and fast/material work in recursive owners, but those aggregate source costs are not a complete same-invocation fast→full transition count. They do not establish how much of ordinary/Q material work belongs to successful refreshes versus fast-only/cutoff paths. No overlap frequency or associated recoverable material cost is claimed. Public `RootContext::material` retains nonlinear winning-side adjustment, rounding, root-depth adjustment and clamp; sharing must use the exact produced result, never clamped deltas. Q allowance computes parent/hypothetical victim-removed endpoints and is outside this ownership problem.

For context only, raw material rows120–159 under the two Q owners are388,675,857+384,766,199(case35) and3,018,472+1,814,640(case08); outlined allowance adds162,498,827/2,236,789. Those large numbers are explicitly **excluded**. They cannot be converted into refresh savings or used to reactivate parked Q/material-cache trials. Likewise ordinary's material-row total217,502,518/18,123,506 includes fast and other actual inlining scope; it is not a pure duplication denominator. The selected experiment needs no D=true frequency probe or new counter.

## Minimal stateless trial and gates

Use `full_impl`'s existing actual Phase. Preserve the native arithmetic in each owner and add narrowly named private/shared phase-taking helpers only for activity, shelter and patterns; call existing pawn `compute_with_phase`. Public wrappers derive phase as before. Invoke these at the exact existing call sites: do not move PawnCache select/fresh, descriptor traversal, structure terms, relation-query increments, retained writes, observers or finishing. No Position/Node/Evaluator/Search fields, new cache, eager fast basis, persistent key, learned state or dynamic observer is needed. Phase is current-position input, not root phase.

A first trial can stop at the four leaf consumers, making its envelope easy to audit. Reusing phase in `square_balance_from_phase` and a private finish helper is also source-valid but should be a separately explicit scope choice; the existing helper is available at evaluation185. Do not simultaneously redesign fast/selection APIs or forward material across caller boundaries. All old public component/detailed/forced-fresh APIs stay behaviorally compatible and self-sufficient. No new arithmetic formulas, cast widths, divisions, sum/rounding order or synthetic outputs are needed.

Meaningful validation should compare native old public wrappers with the phase-taking owner over coherent varied phases/count carries/opening material gate and both colors, plus full/fresh retained/pawn-cache/Components/Finished/R observations on the same requests. Required mandatory full-evaluation routes and full117 must retain exact outputs. Backend gates must inspect actual default full and leaf argument lowering, live Phase storage, full/leaf frames and caller call/copy/spill changes—not infer no ABI cost from source locals. Shelter already has a large argument footprint, so an added Phase can spill to the stack; even stateless transport is not free. Only a separately declared matched own-source PGO CPU trial can judge benefit; parent retains experiment naming/selection.

This review performs no implementation, native engine execution, build/test, new profile, Git mutation or source edit. All writes are confined here. Normal speed is requested policy with no runtime speed-control/readback claim.

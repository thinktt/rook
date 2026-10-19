From: imp2-lead
To: currently unnamed Vic w1:p1, Rook2 implementation owner
Date: 2026-10-19
Subject: Bounded critique of invocation-local activity classification and geometry

**I found no intrinsic semantic loss in the proposed replacement boundary. The D/A prefix decomposition is sufficient, and destination classification can be shared while retaining per-piece nonlinear scoring. The largest unresolved risk is construction paid by every invocation with little usable destination work. The strongest domain caveat is eager whole-mailbox decoding: it must not turn a previously unvisited malformed tag into a new rejection. A bounded prototype is defensible, with these obligations explicit; the algebra result alone does not favor adoption.**

Read the request, current25 design review, model/verification source and recorded result, current activity/influence/type implementations, and released activity contract. No builds, tests, engines, profiles, static-cost collection or implementation. Final decisions remain yours.

1. **Keep the current input authorities distinct.** Reading the supplied Influence bytes preserves arbitrary public maps; rebuilding a map from placement would not. Reading mailbox tags for destination occupancy/transparency avoids depending on stale private AttackBits. But the source inventory still comes from chronological piece lists, while current phase and the rook's opposing-king square retain their existing owners. Do not silently reconstruct those inputs from the new occupancy masks. In particular, an “actual classes present” gate must follow the inventory consumed by the scalar path, not a newly inferred mailbox population.

The model explicitly rejects 63 nonempty raw encodings with invalid low kind bits. That is a model-domain guard, not an equivalent production entry check. Current activity decodes tags only along selected walks, and some occupancy/transparent tests short-circuit without calling kind(). A bad tag on an unvisited square can therefore be irrelevant to an otherwise returning scalar invocation. A nonpanicking whole-board guard followed by the unchanged scalar fallback preserves that behavior; eagerly invoking kind() on every square does not. Valid high-bit aliases also require the actual byte-zero/color-bit/low-kind interpretation, or a faithful fallback. Do not normalize nonzero tags to empty merely because their low bits are zero.

These concerns do not require a Session permission or persistent coherence contract. They are local conversion obligations, and fallback should occur before any partial result is mixed with a second scalar evaluation.

2. **The geometry proof works ray by ray.** Before the first occupied square, every destination is direct. That occupied square belongs to D only if opposing. After it, the walk continues exactly while successive occupants satisfy the activity transparency rule. Therefore the prefix X through the first nontransparent occupant contains P, and `(X minus P) minus friendly` is precisely A. If there is no first occupant, P and X both reach the edge and A is empty. If the first occupant is opaque, X=P. A friendly opaque endpoint is excluded; an opposing opaque endpoint is included before stopping.

Queen transparency is empty. Bishop opposing pawns/kings and rook opposing nonpawns/kings must use the activity rules, not legal attacks or Influence-ray transparency. Forward-own-rook transparency depends on both color and direction. Rays from one valid source are disjoint, making per-piece A cardinality sound; that reasoning does not permit unioning different sources' charges or scores.

Decisive geometric witnesses, not tests I ran:

| Ray pattern | Required result on that ray |
| --- | --- |
| White Bc1, own Nd2, opposing pe3 and Kf4, own Bg5 | D is empty; A contains e3/f4, charges both, and makes no marks. The bishop passes both opposing occupants and stops before contributing g5. |
| White Rd4, own Qd5, empty d6, opposing pd7 | North D is empty; A contains d6/d7, including the opaque pawn endpoint. Vertical doubling changes T only. An own queen south/east/west instead stops continuation. Mirror for Black. |
| Two pieces have additional rays meeting at the same empty square | Each includes its own relation charge and weighted value there. No additional mark is published; no cross-piece deduplication is allowed. |

Also retain edge/no-blocker and both bit-scan directions. An independent coordinate oracle must not share the new prefix/blocker machinery.

3. **Share classifications and mark presence, not per-piece results.** The N/B direct-category equality is sound for the same color/map: their only shortcut difference occurs where the adjusted relation is already favorable. It does not extend to geometry, their mobility curve inputs, knight exemption or additional-ray work. B/R additional categories require the unadjusted view and their capture overrides; direct masks cannot substitute for them.

Keep exact category 3 in C and T. Keep C direct-only; double rook vertical T without doubling C or R. Count all included A squares, including category-zero squares and capture-overridden endpoints. The unchanged source penalty must retain uncapped profile sums, independently of the capped counts used by the mask classifier. Per-piece rounding/curve/clamp/source penalties precede the existing side-total round.

Weak/strong direct unions are safe only as OR-presence of each color/type/label. Category zero still enters Weak; A never enters either mark mask. Flush into fresh Marks without replacing bits from earlier kinds, and finish all required marks before pressure consumes them. The existing pressure and weighting owners are a good boundary to retain. Compare complete Activity and downstream shelter, not merely D/A sets or weighted totals: a matching total can conceal wrong C, marks or semantic R.

4. **Construction is the principal architectural falsifier.** The recorded mapped frontend context averages roughly 1,429 simulated Ir per activity invocation on35 and149 on08. These are partial attribution averages, not removable limits; nevertheless, they make a universal setup cost particularly suspect on08. Presence gating avoids absent classes but does not establish amortization: a lone knight has at most eight destinations, and a present slider can be almost immobile. Use actual inventory presence before optional frontend construction while retaining the other owners' behavior.

Invocation-local storage avoids a lifetime seal, but a large aggregate of all profile/occupancy/features/category masks can still create long live ranges, stack traffic or returned temporaries beside Marks. The design need not materialize every class simultaneously. Count conversion, guards, feature derivation, sparse value scans, A cardinality and mark flush together; replacing per-target LUT reads with a costly feature producer is not inherently a reduction.

The native transpose remains a separate correctness boundary. The model's scalar transpose and two lane permutations do not prove the proposed SSE2 producer. Physical-square lane mapping, color separation and block boundaries must agree across profile planes, occupancy masks, geometry and value indexing, with an independent byte-based reference. Preserve the normal target; baseline availability of an instruction set says nothing about the profitability of this conversion.

I favor the proposed self-contained substitution over adding persistent representation or a root permission. Retaining scalar fallback is appropriate for domain preservation, but a profitable runtime hybrid would require its own construction-inclusive rule rather than a favorable-case choice. Stop if the new producer leaves the old classification work substantially intact or if making it pay requires broadening storage/ISA/scope. The previous near-misses do not supply a savings estimate for this mechanism.

Evidence: `/home/legolas/rook2/evidence/activity-kernel-current25-design-20261019-01/review.md`; `/home/legolas/rook2/evidence/activity-category-bitplane-model-20261019-01/{model.py,verify.py,result.json}`; `/home/legolas/rook2/src/{activity.rs,influence.rs,types.rs}`; `/home/legolas/king-spec/spec/activity.md`. Consultation complete; no approval dependency or further work from me.

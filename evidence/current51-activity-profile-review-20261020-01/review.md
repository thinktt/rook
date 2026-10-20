# Current51 Activity: lazy source-support counting

Recommend one bounded source/compiler question: in `activity::piece_score_kind`, specialize the existing source-support penalty for **opponent byte zero**, while leaving its nonzero branch and every later consumer unchanged. This removes no destination, mark, relation charge or pressure work. No implementation, candidate selection or timing authority is supplied here.

## Current evidence, not an avoidable-cost estimate

The closed exact51 profile35 has44,100,272,048 simulated Ir. Activity's exclusive recorded function SELF, summed across all inline file partitions, is9,154,116,962 (20.757507% of the lifetime). It is not a removable envelope. The profile's SELF sum and Activity's file partitions reconcile exactly. `source-row-proof.json` preserves the selected original raw row IDs/text, object/function/file identities and disjoint costs.

Within that Activity function only, `influence.rs:219` (`profile_sum`) is588,605,983Ir (1.334699% whole). Current Activity has just the two production uses at365–366: opposing count and own count for each piece's source-support penalty. The comparison context at `activity.rs:366` is another150,296,832Ir (0.340807%), a separate row subset. These contexts identify a substantial source owner; neither gives the frequency of opposing byte zero or the cost conditional on that value. Do not add the complete support context to a presumed saving.

The selected types display aggregates inline types across *all* functions. This review instead selects Activity's raw rows: its types partition is1,146,211,929Ir, not the display's whole-program types total. Activity's own source line0 alone holds1,128,837,815Ir; it is unidentified, not assigned to this proposal. Destination traversal, victim decoding, classification, marking, arithmetic and pressure remain required context. No caller-inclusive arc is added to SELF, no Ir-to-call-count inference is used, and no43/40 proportion is transferred.

## Exact all-byte identity and minimal owner

Released `activity.md:123–125` requires uncapped own/opposing normalized sums and subtracts `5A+2` if own sum≤A, including subtraction2 when both are zero. Current source is `activity.rs:363–368`; the pure count function is `influence.rs:216–219`:

`S(x)=(x&1)+((x>>1)&1)+((x>>2)&3)+((x>>4)&3)+(x>>6)`.

For every u8, these five nonnegative fields cover bits0–7 and sum to at most11, so no u8 overflow occurs. The sum equals zero iff every field is zero iff the entire byte is zero. Therefore opposing byte0 implies A=0 and the exact penalty is **2 iff own byte0, otherwise0**. For nonzero opponent retain the existing two-count comparison and `5A+2` arithmetic. This is a written finite-domain proof, not a new enumeration or executed test.

The minimal change belongs solely inside the private piece-score penalty block, following the existing own/opponent loads. On a zero-opponent path it can replace two five-field count evaluations, their sum comparison and generic penalty arithmetic with zero tests and the exact optional subtraction2. Those are expected removed operations **only if actual baseline lowering currently evaluates them on that path and the candidate compiler leaves them bypassed**. The current aggregate source rows do not prove that path's machine behavior; LLVM may already make some deductions. A matched actual compiler gate must reject an absent/relocated mechanism rather than assume savings from source spelling.

Keep both original bytes live for the later knight exemption (`own>>6`) and unadjusted source relation. Preserve C/T, raw mobility/curve, signed rounding, phase, per-color weights, return/work ordering and every query charge. In particular `C<2` still increments R and evaluates the normative source relation, even when opponent0 makes the relation favorable. Never turn the zero-opponent case into unconditional *no penalty*: both-zero still subtracts2.

## Domain, history and risk

This identity holds for every supplied Influence byte, not just physically plausible maps. It requires no coherent placement permission, no new public/private entry, no rebuilt map and no cache/state. Public `activity::compute` and evaluator full/custom-map routes can share the same private numerical owner unchanged. It is consequently distinct from parked52's borrowed-plane separated consumers:52 failed its generic screen by0.198734% with2/7 lower, no PGO; its dispatcher, geometry setup, frame and extra evaluator argument are unnecessary here.

It is also distinct from the historical256-byte `profile_sum` LUT. That table's generic improvement did not survive its own-PGO screen (0.040183% higher); do not revive or compose it. Keep the existing nonzero arithmetic, not a new table. Failed35 global mask/class production,31 mark-byte arithmetic and46 forced-capture relation bypass are not selected alternatives. Their setup/code/frame/branch tradeoffs caution against treating this1.334699% context as free savings.

The new zero test may add a branch/dependency to every piece, worsen prediction or code layout, or duplicate count instructions across kind/color instantiations. Eligible zero-opponent frequency, per-kind balance and current branch predictability are unknown. Added frame/spills or callers changing shape could erase the benefit. No statistical significance, CPU gain or PMU claim follows from this simulated-Ir profile.

## Required falsifiers and focused checks

Before timing, compare the exact baseline/trial whole emitted Activity consumer: prove zero-opponent count bypass on actual per-kind/color paths, unchanged nonzero count/penalty and live bytes for later uses; disclose instruction/code/frame/spill/call tradeoffs. Retain public false/custom-map behavior without introducing any permission or variant body. Generic lowering/gain does not establish own-PGO behavior; each future profile-use decision needs its own actual gate and preset screen.

Meaningful future tests should compare full piece-score results/work with the preserved old arithmetic owner across all256×256 source bytes, N/B/R/Q and mobility/phase boundary witnesses. Discriminating cases include both-zero subtract2, nonzero-own/opponent0 subtract0, equal nonzero sums, and own/opponent maximum counts. Preserve low-C charged source relations and pawn-supported knight exemption. Add complete Activity differentials on arbitrary supplied maps through public/full callers, checking pieces/pressure/weighted/R and unchanged marks/destination policy via existing independent oracles. No test was added or executed here.

This supports only the isolated lazy-count hypothesis. It supplies no eligible-work fraction, predicted speed, automatic runtime admission or implementation. Production remains exact51.

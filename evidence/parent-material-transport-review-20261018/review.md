# Caller-owned final material transport: source-only study

Current root source read on2026-10-18 during the live12 window96272/PID480262. Source/text only, all helpers0-5,8-13. No source edits, hashes, binary/archive scan, Rust parsing, builds, tests, engine, profiler or measurement. No layout or speed claim. No implementation selected.

## Judgment

**Worth a small demand census; not enough evidence to select a production representation.** This is broader than reusing inputs inside FAST->FULL and different from the parked Q victim-endpoint cache: a material scalar already computed at a root/ordinary/Q parent can reach count-preserving descendants and ordinary->Q handoff without recomputation. The same scalar can optionally replace allowance's current-before endpoint, but hypothetical after endpoints still require the native nonlinear producer. Keep that extension separately counted rather than silently bundling the old cache.

The promising representation is a caller-owned **optional final i16 material hint**, not a raw incremental material balance and not a Node/Retained field. RootContext::material always clips its final result to[-7000,7000], so a distinct i16 sentinel such as MIN can represent absent without colliding with zero. This is only a source-level representation alternative. Whether it fits Predecessor/Evaluation padding and whether any production calls/frame actually improve requires emitted layout/backend evidence and matched performance later.

## Earlier experiments read first

- `root-material-opportunity-review-20261018/review.md` mapped old8d material attribution and proposed measuring before choosing persistent raw/clamped state. Its identified material source rows were2.51% of simulated profile01 Ir;60.25% of those rows belonged to allowance. These are old source-attribution figures, not current CPU costs or removable-instruction forecasts. It already warned that exporting current material from evaluation is a separate ownership decision.
- `evaluation-inputs-build-20261018/README.md` and `evaluation-inputs-cpu-pilot-20261018/README.md`: isolated phase/material sharing within one invocation, FAST->FULL and finishing. Generic six-case pilot was0.74948% lower with overlapping ranges, parked. It did not transport parent material to a newly produced child. Do not relabel this experiment or inherit its gain.
- `material-allowance-census-20261018/RESULTS.md`: old79 all54 segments had37,094,821 FULL,44,684,035 FAST and81,804,410 allowance endpoint demands. Root preparation excluded. Its local Q1+K model avoided27,771,603 source requests, not measured machine calls.
- `q-material-reuse-proposal-20261018/README.md` and `q-material-reuse-cpu-pilot-20261018/README.md`: one before plus keyed after endpoint cache per Q frame. Despite those source opportunities, generic six-case medians were only0.0086626% lower, all ranges overlapped; Q frame grew96B and code277B. Parked, including inline/victim follow-ups. New scalar transport must not inherit a claim that the old cache paid off.

Current117 source differs from these historical owners. None supplies a current count-preserving-edge/actual-demand denominator or an own-PGO benefit.

## Exact purity and invalidation

`src/evaluation.rs120-157::RootContext::material` reads only `self.values`, `self.counts`, `self.average_depth`, `self.side`, and current `position.counts[..][0..5]`. It does not read the descendant's side, placement, current phase/starting squares, rights, EP, identity, history, halfmove, check, P/G or age. `self.values` already belong to fixed root phase/personality. A quiet move or castle may change current phase; that does **not** invalidate material, but current phase itself must still be produced independently as before.

The exact final scalar is White-relative. Do not negate it for a side flip or null move. It includes the signed root/current population term, nonlinear winning/losing side selection and heavy/pawn corrections, and final clamp. It may be reused iff that fixed root context and all relevant current counts are unchanged. It cannot be updated by adding a nominal victim/promotion delta to a clamped result. Equal total population alone is insufficient: promotion changes pawn/nonpawn values/presence. Coincidentally equal clamped endpoints do not establish reuse without calculating the new endpoint.

| Actual coherent transition | Incoming known material |
| --- | --- |
| Ordinary quiet move, including pawn push | Preserve unchanged; no destination victim or promotion |
| Castle | Preserve only on the actual coherent castle transition; rook/king relocation changes no counts |
| Null | Preserve unchanged; side, EP and halfmove changes do not enter material |
| Ordinary capture | Invalidate, including zero-valued victim/last nonpawn |
| Promotion, quiet or capture, every kind | Invalidate despite unchanged total population |
| Joined EP | Invalidate; actual behind-target victim may be any opposing nonking, not just pawn |
| Exceptional king-victim EP | Not an eligible normal Node/evaluation transition; preserve the existing fatal ingress boundary, not a hint |
| New search/root/personality binding | Invalidate all old hints, even if current counts match |

A count-array equality check is an exact conservative test in the coherent native domain; a movement classifier can be cheaper only if it checks promotion/EP before ordinary destination vacancy and uses the actual victim square. Null is known from its native caller, not inferred from an arbitrary missing move. Do not narrow setup/EP/history domains to simplify this proof.

## Current owners and missing transport

- `evaluator.rs363` computes material once for FULL, shares it with activity/shelter/progress and includes it in Components. `Components.material` and cold FullDetails expose the exact value; the ordinary returned Evaluation does not. FULL433-445 mutates retained P/G/age and charges R independently of material. `fast_impl~500-529` separately computes current material and returns only finished score/bounds/R metadata. Its finished score/base/retained pair cannot reconstruct material.
- `evaluator.rs616-664::select_noncheck_impl` calls sparse FULL or FAST then optional FULL. This same-position repeat is the old within-invocation opportunity. Material used for a parent-to-child hint should be exported from an actual demand, not computed early merely to create a hint.
- `quiescence.rs137-156` FULL evaluates the fresh root once after begin_search binds/clears. That existing root material could feed quiet root children. `timed.rs610-630`, `ordinary.rs574-609` and first_iteration.rs51-87 currently construct children without exporting root material. Root dispatch/ActualEffects would need a caller-owned scalar with that root lifetime; Predecessor padding alone does not recover the already discarded value.
- `ordinary.rs512-517::Predecessor` carries parent position/influence/check/movement. Current Predecessor805 is created after actual FULL/bound gating; it could carry the now-known current material into null, main, IIO and checking-Q-probe children. Root/scout retry uses the same child, but a by-value incoming hint does not automatically export a newly computed child value back to its caller when the initial hint was absent. Do not claim capture-retry reuse unless a separate caller slot/return path is designed and measured.
- `ordinary.rs695-722` hands off to Q before the ordinary charge/admission/evaluator. An inherited hint must already refer to the **current node**, or carry an explicit pending parent-edge proof; forwarding a parent value unconditionally here would be stale after captures/promotions/EP. It is not valid to compute material at handoff just to cover Q.
- `quiescence.rs243-283` demands material at ply63 FAST or nonchecked selection. Checked Q can bypass all static evaluation, and draw/empty/mate exits may never demand it. If a checked frame inherited a valid hint, it can propagate it through quiet evasions; if it inherited none, it must remain unknown until an actual material demand. No eager calculation to make checked propagation convenient.
- `quiescence.rs320-449` constructs selected tactical children, including prepared reply-probe children. Special/capture edges invalidate. Quiet checking moves and quiet checked evasions can preserve a known parent scalar. Prepared/discarded children still create possible transport/ABI costs even when no child ever asks for material.
- `quiescence_policy.rs98/103` ordinary capture allowance computes complete current-before and hypothetical-after endpoints. The latter decrements only actual victim counts, deliberately not board/lists. A known current hint can replace **before only**; after remains a complete native call unless separately selected pure-key reuse. `ordinary_policy::frontier_estimate` shares this allowance. Standalone diagnostics/development calls lacking a proved hint retain the original wrapper/fallback.

## Lazy design alternatives, not a selected patch

A clean ownership invariant is: **MaterialHint belongs to the current node's counts under this evaluator.root**, contains either an exact native-produced final value or absent, and is never stored on Node/Position/Retained. Prefer that meaning over an ambiguous field named parent_material in a record whose other fields describe the predecessor.

1. At actual material-demand sites, consume an inherited valid hint or call unchanged RootContext::material. Resolve no earlier than the original FULL/FAST/allowance point. Export the exact result to the current caller-owned local. Root preparation can export what it already computes. Reusing it changes no numerical formula, R, pawn-cache access, retained write, influence construction, finishing count, observer event or virtual-clock observation.
2. When producing a child, copy the current optional value only on proven count-preserving transitions; otherwise pass absent. Ordinary->Q forwards that current-node hint without an extra material calculation. Checked Q passes known/unknown lazily; neither draw/TT/zero-budget nor checked-only traversal creates material just for caching.
3. Scope the local through one immutable current position/fixed root. Same-child retries retain Node P/G exactly as now. A by-reference caller material slot could retain a newly resolved value across retry, but adds a recursive argument/alias and stack lifetime; a by-value hint is simpler and must count that missed reuse honestly. Neither needs mutable undo of shared material or cross-root lookup.

Classifying count preservation at child production taxes every relevant child, including zero-demand ones. Deferring classification until the first demand avoids some tax but then Q needs the edge proof/parent counts as well as a scalar, complicating its signature and ordinary->Q handoff. This tradeoff belongs in the denominator/backend experiment, not hidden behind a cache hit statistic.

### Padding/ABI alternatives

The currently presumed24B Predecessor has two references, bool and Option<Move>. Move is transparent u16 with no declared niche (`types.rs168-169`); if Option<Move> occupies4B and references8B, payload is21B, leaving nominal3B at alignment8. An added **i32 cannot be assumed to fit**; an i16 sentinel payload could plausibly fit while preserving24B. Option<i16> commonly needs4B, so is not the same space claim. A nonzero encoding can express validity in2B but adds encoding/decoding; MIN sentinel uses the proven[-7000,7000] final range directly. Do not infer actual Rust size/offsets/register passing from this arithmetic.

Evaluation similarly has threei32, oneu64 and bool: nominal21B payload/24B size could admit i16 in padding. Adding a material field would change a public native return and all its constructors/observed variants. Same total size would not prove unchanged offsets, return classification, copies or call lowering. Wrapping an existing Evaluation in a tuple/new struct with i16 does not automatically reuse the inner object's tail padding. No representation, ABI or assembly was inspected now.

Alternatives are an internal demanded-input/output helper, a static scalar extraction from the existing FULL Components observer, or an extra caller-owned out slot. Each can preserve the old public wrappers but may add a returned aggregate, callback capture, pointer argument, liveness or outlined transfer. Fast still needs its actual material exported; reading FullDetails is not a substitute. A private adapter must call the same native material producer, never duplicate its formula. First review actual default full/fast, selection, ordinary/Q recursion and root frames/call transfers under false/default instantiations; symbol absence or unchanged struct byte size would be inadequate evidence.

## Minimal demand experiment before production selection

An isolated **diagnostic-only shadow census** is worthwhile; no implementation is authorized by this memo. Keep the current baseline material calls/arithmetic and all semantics unchanged. Track availability/provenance, not a second formula or speculative material recomputation. A feature-gated external census owner/per-ply shadow stack can avoid adding production Search/Node fields; false/default ABI/counter erasure must still be checked later. Do not time this instrumented image as the optimization.

Observe actual FULL, FAST, allowance-before and hypothetical-after requests separately. Shadow availability starts absent on a new root, becomes known only when an existing real producer requests material, follows only count-preserving edges, and invalidates on count changes. Root preparation establishes a known root shadow; begin_sequence resets measured counters but must not erase that known origin. Distinguish inherited first-demand opportunity from repeated same-frame FAST->FULL and allowance-before opportunities, so the new mechanism is not credited with the parked within-invocation optimization.

A minimal per-case table should report:

- Actual demand totals by FULL/FAST/allowance-before/after; first-demand hits with known count-preserving parent, split ordinary/null, ordinary->Q and Q->Q.
- Entered eligible edges with known parent, alongside how many return/error without any material demand; these are the construction/transport-tax denominator, not saved computations.
- Unknown checked-Q chains and first later demand; no extra computation may be introduced to count them. Captures/promotions/EP invalidations, and same-child retry first versus repeated demands, remain separate buckets.
- Same-frame repeated-input opportunities and optional allowance-before savings as separate numbers; hypothetical after demands are never credited to count-preserving transport.

One boolean/provenance token per active diagnostic frame is enough for availability counts. Actual value-carry correctness is then tested in a separate source proposal against the unchanged native material function, not validated by counters alone. Wrapper/exit accounting must include early returns and interruption; no generated-but-rejected candidate is silently counted as an evaluated child. Dedicated feature-gated global counters can be acceptable for the untimed census, but production false specialization must retain no observer storage/dispatch; do not grow shared Stats just to get counts without a reviewed layout decision.

If inherited first-demand hits are substantial relative to all material requests and zero-demand edge tax is modest, a small final-scalar transport prototype is justified. If nearly all opportunity is same-frame/allowance-before, this proposal is not the next broad optimization; revisit a narrower export design with the old cache's frame lesson explicit. The historical81.8M evaluator demands show a potentially broad target, but provide no current eligible-hit ratio and no CPU gain. A current census and emitted default-path costs must decide. No persistent material state or new arithmetic is selected here.

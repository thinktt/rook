# Current25 Influence build edges and ordinary delta feasibility

**The ordinary pool is large enough to justify bounded architectural/semantic feasibility work.** Existing ordinary recursion already carries the exact borrowed parent position/map/move at the reached map-construction seam. This supports investigating the parent's stateless ordinary-two-square delta algorithm before spending more effort on tiny scalar/copy cases. It does **not** establish eligibility fraction, algorithm profitability, instruction savings, CPU benefit or implementation/adoption authority. Q/root/null/special/synthetic entries stay fresh in the proposed first scope.

## Exact recorded cost pools

| Lifetime/caller group | Actual build calls= | Actual inclusive build-edge Ir | Whole-lifetime simulated Ir share |
|---|---:|---:|---:|
|35 ordinary |1,476,614|3,123,695,252|6.825921%|
|35 Q |610,121|1,278,348,688|2.793457%|
|35 root run |1|2,189|0.000005%|
|08 ordinary |222,480|94,074,550|2.370920%|
|08 Q |139,355|65,130,592|1.641458%|
|08 root run |1|560|0.000014%|

These are sums of **recorded individual arcs**, never a callee-total weighted average. Influence::build has no recorded outgoing call arcs in either profile; its exclusive self Ir across all inlined source partitions equals the sum of all incoming arc Ir exactly:4,402,046,129/159,205,702. Recorded build invocations total2,086,736/361,836. Thus the caller split partitions this reached leaf owner without doublecounting it. Do not add its self total again to the edges. Whole-lifetime totals are45,762,253,122/3,967,850,732.

All arcs below identify the caller's inlined evaluator.rs302 site and exact callee`rook2::influence::Influence::build`. Repeated rows are separate recorded edges, not averaged or collapsed. Suffix`'2` is retained as supplied, without guessing generic parameters. Source-level fast/full/support roles are not assigned solely from edge ordinal.

### Raw profile35 edges

| Raw line | Recorded caller | calls= | Inclusive Ir |
|---:|---|---:|---:|
|23188|ordinary|24|52,509|
|23324|ordinary|182|398,796|
|25617|ordinary′2|615,628|1,289,847,397|
|25909|ordinary′2|860,780|1,833,396,550|
|28384|Q|335,243|721,152,269|
|30061|Q|204|419,830|
|30621|Q′2|267,777|543,818,828|
|32380|Q′2|6,897|12,957,761|
|5237|root run|1|2,189|

### Raw profile08 edges

| Raw line | Recorded caller | calls= | Inclusive Ir |
|---:|---|---:|---:|
|4042|ordinary|48|26,464|
|5799|ordinary′2|222,432|94,048,086|
|30002|Q|558|399,654|
|31490|Q|86,516|38,984,959|
|32218|Q′2|1,042|904,481|
|33709|Q′2|51,238|24,840,619|
|34007|Q′2|1|879|
|11207|root run|1|560|

No other incoming build caller is recorded in these two complete lifetimes. This is not a universal statement about other54 workloads, exported helpers or component diagnostics. `ensure_influence` has **no separately recorded call edges**: it is inlined. That absence is not zero ensure invocations or zero scratch hits; the profiles expose actual builds only. They do not expose move-kind, trusted-linkage, affected-slider counts or the source-level reason for each miss. Ordinary-function calls are not synonymous with MoveKind::Ordinary.

## Current native ownership/dataflow

`evaluator.rs296–307` owns lazy construction: only an empty caller-owned Option gets built; an existing map is returned unchanged. DIAGNOSTICS increments influence_builds once on that same empty→Some event. Ordinary begins a new local scratch=None atordinary763 after handoff/charge/early-draw/TT admission. Fast-cutoff pressure may first demand it at782; full evaluation demands it at795, reusing Some if already produced. A delta factory must live at that **same first demand**, not precompute for every produced child or on a scratch hit. Keep all existing map-build statistic events, N/R charges, observer order and cache/pawn effects unchanged; no new cache event/state is justified.

Ordinary's Predecessor512 contains borrowed `position`, `influence`, checked fact and optional movement. Actual producers supply coherent linkage:

- Timed root: ActualEffects::begin_candidate constructs one actual root.child at timed609; execute616–622 passes root position/map and that movement. Fixed-completion iterations construct root.child580 and predecessor594–599 similarly.
- Main recursion: after current map/full evaluation, ordinary805 retains current position/map. Main990 constructs child;992 adds its actual movement;1020 searches it. Scout retry1033 uses the same child and same predecessor after Retained refresh, with unchanged Position. The parent map stays borrowed/immutable throughout.
- IIO: ordering_phase accepts &Node, receives current map, constructs real child1135 and supplies parent position/map/move1152. No new parent reconstruction is needed.
- Null: ordinary821 uses null_child and the current predecessor with movement=None. It must take fresh fallback in the selected first scope; this is not a revival of the parked null-map opportunity.

The proposed builder can therefore consume borrowed parent/current placement plus move while the caller already owns a new local output map. It needs no Node field or persistent cache. Retained evaluation changes do not mutate Position or the parent's Influence. Every new ordinary invocation, including a scout retry, currently starts scratch=None again; do not silently introduce cross-entry memoization or change the counted construction event.

**Trust is a required new private boundary, not implied by these fields.** Controlled/component diagnostics can construct a synthetic Predecessor whose Some(move) does not attest `current == parent.played(move)`. Parent requires explicit private trusted-child linkage/internal wrapper: enabled only at actual Node::child recursion/root/retry ownership, false for public/synthetic entry. Do not use hash equality or an optional movement alone as admission. The profile cannot quantify that future trusted MoveKind::Ordinary subset. Null, promotions, EP, castles, absent linkage and other default entries must retain fresh construction. Source-level linkage proof and correct false/default admission precede any optimization.

## Why Q is outside the first cost pool

At ordinary entry, Predecessor is still available **before** the early quiescence handoff705. That API call passes node/history/window, checked and capture_exception; it does not pass parent position/map/move. The later shallow-Q call898 also has current map in the ordinary frame but does not forward it. Neither pool is automatically covered by an ordinary-only constructor seam.

Within Q, fresh per-entry influence=None is created atquiescence255. Noncheck selection may demand it through evaluator627(initial full) or650(refresh); capture_policy's destination-support closure may demand it lazily atquiescence356. Checked or fast-return paths may never construct a map. Recursive Q443–446 passes no parent Influence context; observer parent metadata contains Retained, not the map. A parent's map may not exist. Do not build one eagerly to enable a delta, and do not credit Q's1.278B/65.131M Ir to the first ordinary-only prototype. Root preparation atquiescence140–155 deliberately clears/binds search state, ensures one fresh map and fully evaluates the root; it lacks a predecessor and remains fresh.

## Semantic and performance obligations

Influence is placement-only (evaluation-relations.md46–80), not legal-attacker membership. Its wrapping profile contributions commute, so piece chronology does not affect this map, even though chronology remains required elsewhere. Existing influence.rs35–102 walks actual piece lists; add154–157 wraps modulo256; ray159–204 adds old weight before blocker classification, sees an opposing king as transparent, weakens beyond friendly queens, retains compatible friendly sliders, and includes the forward friendly-pawn extra square with current weight. An affected-ray algorithm must preserve these full old/new contributions and deduplicate affected ray work; clipping to a nearest ordinary blocker or Boolean attack route is not established by this census. Exact all128 profile bytes matter, including wrapping/carry outcomes and unusual admitted positions.

The first ordinary scope provides a **baseline cost pool**, not a profit bound. Its eligible count and associated edge Ir are unknown because the raw records contain no move/admission tags. Delta must copy the128-byte parent map, identify affected work and subtract/add exact old/new contributions; these costs replace part of fresh construction rather than vanish. A small affected set is plausible but unmeasured. Repeated fallback tests, extra return transport, altered frames and unfavorable cases can erase any gain. No whole9.6% claim, root/Q transfer, callee-average allocation, CPU/PMU inference or favorable workload extrapolation is made.

Parent can now decide whether to invest in a narrow proof/prototype: explicit trusted ordinary-child admission, fresh fallback, exact differential whole-map tests over legal/synthetic edge domains, then actual backend and unchanged functional/paired CPU gates. If eligibility needs measurement, it must be counted at the actual empty-scratch construction seam by move/linkage—not inferred from these totals. This report prepares no new census or run, and contacts no advisor.

Exact production image:`51529cebf24ad91b0cf86e4ae497bc32bb7ad7a819f8b300f8b86028326b254a`. Audited compiled source hashes match its existing frozen identity and six current-root native owners. input-pins.json binds source/spec/raw profiles/provenance/parser; census.json retains all17 original edge records and reconciliation. All inputs rechecked unchanged. Helpers ran housekeeping0-5,8-13/HOME TMPDIR; primary analysis ACTUAL084b1f/0, sessionless. No source edit, native/binutils/build/test/profile/Git/archive/timing run occurred. All owned jobs terminal.

# Remaining performance investigations

Current117 integrates the full-byte relation table after178 native/209 diagnostic
units and fresh7673-case/117-operation success. Own-PGO79d19ebe passes its own
54/eight-wire and a matched seven-case pilot0.702652% lower than activityd5ee1f3f
in summed medians; final-artifact full54/12 costs and12-game pre-gate remain.
See [decision0013](../decisions/0013-full-byte-relation-table.md). The separate pawn
fusion541d324c passes178/54/eight-wire with independent closure; its fixed
seven-case generic pilot is0.210939% lower in summed medians, missing both
predeclared advancement branches. It is parked without own-PGO or composition.
See [decision0012](../decisions/0012-activity-destination-values.md).

Previous complete117 has mandatory7673-case/117-operation success and a generic12-game
pre-gate pass. Its own-PGO6a5ce6e2 also passes its own fresh54/eight-wire and12-game
pre-gate checks. Its54 CPU collection independently reconciles216 lifetimes,
76.090895s summed medians versus published63.431779s: raw cross-hardware
ratio1.199571. Its12-game CPU collection also independently reconciles all48
lifetimes at768.200873s versus644.222971s, raw ratio1.192446. These are
cross-hardware reported-only comparisons; optimization remains. The bounded codegen review
is complete; none of the historical measurements below transfers to that source. CPU-only
opaque calibration passes216 lifetimes with per-case local/reference ratios
0.906–0.972; this is fixed-program hardware context, not engine acceptance.

Date: 2026-10-18. Statuses below distinguish adopted experiments from hypotheses; none promises
a qualified speedup. The historical complete54 collection on frozen8d9dddc5
has full local PGO CPU costs totaling
81.131004s versus the published63.431779s sum(raw uncalibrated ratio1.279028).
Previous8c4619a7 totals81.828432s; the new sum is0.852305% lower, with41
case medians lower and13 higher in this sequential historical comparison.
The previous915f83e4 collection totals88.486549s; all54 new medians are lower,
with a7.524440% lower aggregate in this sequential historical comparison.
The earlier3660 collection totaled97.685122s. Calibration/profile differences
remain unresolved. The historical8d9dddc5 profile-01 simulated total is11.604B Ir, versus12.027B
on previous8c and13.607B on earlier3660fecf; activity remains prominent after
the adopted kernels. This is whole-lifetime instruction simulation, not PMU counting.
Function attribution changed through inlining, so source-line evidence matters.

1. **Shared immutable evaluation geometry.** An isolated prototype moves the
   existing legal-attack tables into a crate-private shared module, and consumes
   valid target sequences in influence rays/leapers and activity destinations.
   It preserves traversal along each ray, pawn forward extras, transparency,
   category wrapping and relation charges.10,000 broad constructed placements
   match our prior coordinate loops for complete influence bytes, all activity
   fields and relation counts. Native tests and all54 replays pass. A fixed
   six-case generic/non-PGO CPU pilot gives ratio0.977538, supporting adoption
   under decision0003; a separately trained production PGO six-case pilot also improves by3.19% (ratio0.968078). Position/Node
   layout, copied-child ownership and mutable search state remain unchanged.

2. **Repeated full evaluation: measured and rejected as next cache target.**
   A diagnostic-only D=true ordinary derivative matches all54 replays and counts
   18,569 age0 entries out of37,094,821 full evaluations (0.050058%, including
   first-root calls). Evidence is under `evidence/evaluation-opportunity-20261018/`.
   That is too small an opportunity for the proposed same-produced-node cache.
   No cache was implemented. The broader theoretical validity constraints below
   remain relevant to any different future cache proposal. Root initialization is an exception; prove the scope
   before interpreting it. The existing evaluator shares influence within one
   invocation but local derived state does not survive every scout/full or IIO
   revisit of the same produced node. A pure-component cache could reuse activity,
   shelter or other placement/root-owned terms only with exact lifetime and
   board/root/side validity. Pawn-cache accesses/replacements/collisions must
   still occur, and every consuming semantic R charge must remain exact. Caching
   a complete final score solely by fingerprint is invalid. A persistent-cache
   ownership decision would merit bounded architectural critique after evidence.

3. **Formula-derived relation lookup.** Four tested-piece tiers over two
   normalized8-bit profiles form a262144-byte direct table. A smaller isolated
   prototype instead maps each profile to its capped-multiplicity/least-tier
   pair:16 states, a256-byte map and1024-byte outcome table. It retains the
   common opponent-zero shortcut and adjusted subtraction on the original byte.
   The generator uses the general formula, never fixture answers. Source/archive
   preparation is complete under `evidence/relation-states-preparation-20261018/`;
   a fresh isolated preparation now uses the integrated attack-plane source
   under `evidence/relation-states-bitplanes-preparation-20261018/`. Compilation,
   the existing exhaustive digit-model oracle and all133 native units pass.
   Both generic artifacts pass54 strict replays. Its independently reconciled
   six-case/60-lifetime pilot sums16.2258485s baseline versus15.7125745s lookup,
   ratio0.968366893(3.163311% lower), with profile29 ranges overlapping.
   Own-PGO1e5d075d also passes54 replays/eight interruption fixtures. Its separate
   matched60-lifetime pilot sums14.361971s versus14.8805095s canonical915f83e4,
   ratio0.965153176(3.484682% lower); profile02/29 ranges overlap. The kernel is
   adopted under decision0005; production source integrates the exact combined
   kernels after the measured
   interaction comparison in item9. Canonical timing cannot inherit
   trial results. Two dependent class loads still need complete pipeline cost.

4. **Placement bitplanes/other representations.** The independently developed
   four-u64 Piece-tag representation has now passed a matched storage comparison
   and is adopted under decision0004. The mailbox and chronology retain their
   other consumers. Item7 records the measured scope and limits; other layouts
   remain alternatives requiring their own complete maintenance/copy/query cost.

The reported-only full12 collection on1dc996b2 now reconciles48 lifetimes/
2528 searches, summing941.928787s in game CPU medians (raw uncalibrated
ratio1.462116). Its helper-affinity limitation remains disclosed. Final qualified
54/12 costs, external full-game handoff and production review remain
requirements alongside optimization; mandatory117 fixture coverage is now complete.

5. **Pure inputs within one evaluation invocation.** An isolated prototype at
   `/tmp/imp2-evaluation-inputs-20261018` reuses current phase and root-valued
   material between fast evaluation and its full refresh, and passes the same
   phase into king-square balance/finishing. Position and root context are
   unchanged throughout that call; PawnCache activity and R charges remain live.
   No persistent cache or mutable key is added. All130 native tests pass; the
   frozen generic build/check is under `evidence/evaluation-inputs-*20261018/`.
   All54 strict replays pass. A six-case/60-lifetime generic pilot gives
   sum-of-medians ratio0.992505 (0.74948% lower), with overlapping samples in
   several cases. It remains isolated: no production adoption or inferred PGO
   benefit. See `evidence/evaluation-inputs-cpu-pilot-20261018/`.


6. **King-coordinate metadata within existing padding.** An isolated prototype
   consumes two previously unused bytes of the128-byte Position for direct king
   access. Node remains144 bytes. Constructors/recompute, ordinary/castling king
   transitions, null copies and exceptional terminal king removal maintain this
   placement-derived metadata; chronological lists remain independent.130
   library tests plus two development-CLI tests and all54 strict replays pass.
   New mailbox-oracle legal histories and exceptional-child checks validate the
   invariant. A fixed six-case/60-lifetime generic CPU pilot is essentially flat:
   sum-of-medians ratio0.998770 (0.12298% lower), with overlapping ranges and
   two increased case medians. Production adoption is rejected. The unchanged
   representation remains; avoiding prefix sums alone did not select this
   change. See `evidence/king-square-cache-cpu-pilot-20261018/`.


7. **Matched derived-bitplane storage experiment: generic trial complete.**
   An identical Boolean kernel was tested with persistent Position160/Node176
   versus local Position128/Node144 supply. The initial consumer scope leaves
   ordered checker identities and quiescence mailbox reuse intact. Constructors,
   reflection/recompute and all copied placements are part of the invariant/cost
   audit. A bounded architectural critique prompted a matched local comparison
   before choosing storage; ownership and final decisions remain Imp2's.
   Both pass133 native tests and all54 strict replays. The independent90-lifetime
   six-case generic pilot sums16.7270585s baseline,16.3704720s persistent and
   16.8066150s local: persistent/base0.978682, local/base1.004756. All six persistent
   medians are lower, with substantial overlap in profile04. Its own PGO trial
   then passes54 replays/eight interruption fixtures and60 CPU lifetimes:
   trial14.805304s versus baseline1dc996b2 sum15.296771s, ratio0.967871193.
   Persistent source is integrated after133 native tests and25 adapter units/
   1214 cases; this explicit local strategy is parked. Canonical repository
   PGO915f83e4 has its own54-case profile and passes54 replays/eight interruption
   fixtures. Its own60-lifetime pilot sums14.907624s versus15.388885s baseline,
   ratio0.968726714(3.127329% lower), with profile04 ranges overlapping. A complete
   canonical54 CPU collection now independently reconciles216 lifetimes,
   summing88.486549s. No final54/12 qualification follows yet.
   See `evidence/bitplanes-20261018/` and its exact preparation/source archives.

8. **Counts-guided mailbox Boolean attacks: alternative kernel hypothesis.**
   The old Boolean query always walks potential pawn/knight/king/slider routes;
   the bitplane kernel can stop when a slider class is absent. A separate
   layout-preserving control could supply the existing opponent counts to a
   Boolean mailbox query, check king neighbors directly, and skip absent knight,
   diagonal or orthogonal classes. Original counts remain a conservative
   absence guide after an own-move safety projection: ordinary moves, promotions,
   castling and joined EP cannot create an opposing piece. Removing any actual
   victim only makes a nonzero count overestimate possible presence. All actual
   geometric matches would still read the projected board, including a removed
   king victim; no enemy-king coordinate or legal-ancestry shortcut is implied.
   Ordered capped checker identities and quiescence's existing mailbox reuse
   would retain their current owners. This differs from the common bitplane
   query kernel and cannot isolate storage cost. It is unimplemented/unmeasured;
   investigate only after the matched bitplane results, with broad independent
   Boolean/projection comparisons and whole-native timing before adoption.

9. **Typed-list influence construction.** A separate pure enumeration prototype
   walks existing coherent per-type lists instead of scanning64 mailbox squares
   and classifying each source. It retains the exact targets/ray geometry,
   transparency, weakening, pawn extension and wrapping sums. Chronology is
   immaterial to these commutative bytes. The old mailbox builder remains a
   test oracle;10,000 broad placements also match the target-centric coordinate
   oracle after per-type order reversal. All134 native tests and54 strict
   replays/eight interruption fixtures pass on generic10634820. Its matched
   generic60-lifetime pilot independently reconciles all samples and gives
   sum15.4118105s versus16.181479s baseline, ratio0.952435219(4.756478% lower).
   All six candidate maxima are below their baseline minima, a finite observation
   rather than a confidence band. A fresh combined lookup/list source passes134
   tests and its own PGOb17776fb passes54 replays/eight interruption fixtures.
   The complete90-lifetime baseline/table/combined comparison gives13.7237695s
   combined versus14.7940530s915f and14.3190285s lookup:7.234552% and4.157119%
   lower respectively, with all combined observed ranges below both controls.
   Exact source is integrated under decision0006 and passes134 canonical tests
   plus36 adapter units/2215 cases. Canonical8c4619a7 has its own54-case profile
   and passes54 strict replays/eight interruption fixtures. Its own complete54
   CPU collection independently reconciles216 lifetimes, summing81.828432s in
   case medians. Trial timing does not transfer; final qualification remains.

10. **Private activity arithmetic widths: measured and parked.**
    An isolated source uses three u32 mobility accumulators in place of
    i64/i64/u64, plus bounded u32 category/index arithmetic and i32 raw piece
    score. Public activity fields and outer signed evaluation arithmetic remain
    unchanged. The source-bound component range review proves destination,
    category, total mobility, phase index and raw piece-score bounds over the
    admitted placement/phase domain; it is not the global score audit.
    All134 native tests and10,000 constructed placements against our independent
    prior coordinate oracle pass. Generic candidate73ad8177 and baselinee7168491
    have stable build receipts and both pass all54 strict replays. The fixed
    six-case60-lifetime pilot independently reconciles14.947846s baseline
    versus14.9086955s candidate in summed medians:0.261914% lower. Every case
    has overlapping observed ranges and three medians increase. This does not
    support adoption or a further PGO trial. Canonical8c source remains unchanged.
    See `evidence/activity-widths-preparation-20261018/`.

11. **Static piece-kind activity traversal: adopted measured specialization.**
    The next isolated candidate exposes fixed Knight/Bishop/Rook/Queen kinds to
    destination and piece-score kernels through four private instantiations.
    Currenti64/u64 arithmetic, per-type chronology, mark/charge order and all
    outer ownership remain unchanged. The current source-line simulation makes
    activity a material target, but does not predict this transformation's gain.
    Branch simplification may be offset by additional machine-code size.
    Candidatec946104a now passes134 native tests,10,000 coordinate-oracle
    placements and all54 strict replays. Control e7168491 is the identical
    already-validated generic source/artifact; its previous replay is explicitly
    reused. The candidate compute symbol grows from4890 to8975 bytes; whole
    text grows4120 bytes. This is static size evidence, not a timing prediction.
    The fixed60-lifetime matched CPU pilot independently reconciles all original
    samples, strict results, exits and hashes after other native work terminates.
    Summed medians are15.0116965s control versus14.605204s candidate, ratio
    0.972921615(2.707839% lower). All six medians are lower; four observed ranges
    are disjoint, with profile02/29 overlapping. It advances to an isolated
    own-profile PGO trial; canonical source is unchanged and no PGO benefit
    is inferred from generic timing. Own-PGOb8cee321 then passes54 replays/eight
    interruptions and independently reconciles60 matched lifetimes against8c:
    13.7566335s versus13.453188s,2.205812% lower. All six medians are lower;
    five ranges are disjoint, with profile29 overlapping. Exact source is
    adopted under decision0007; fresh canonical verification/profile/cost is
    separate. Canonical8d9dddc5 now passes134 native tests, verified54-case
    training,54 strict replays and eight interruption fixtures. Its fresh balanced
    60-lifetime pilot gives2.052997% lower summed medians against8c; five medians
    improve, while profile29 is slightly higher with overlapping samples.
    See `evidence/activity-specialization-preparation-20261018/`.

12. **Null-transition influence opportunity: measured positive scope parked.**
    A D=true derivative of frozen8c counts positive ordinary null entries after
    table admission where influence will be built, plus null-to-quiescence
    boundaries. All54 strict replays pass; original counts reconcile independently.
    Positive null entries build354565 maps out of46179283,0.767801%. Park this
    narrow reuse path before adding admission/copy cost. Another2650437 null
    entries delegate to Q, but those are not direct map-build counts and establish
    no reuse benefit. No cache/reuse is implemented or CPU gain inferred.
    The probe is tied to8c source, not a timing artifact for new specialization.
    See `evidence/null-influence-opportunity-20261018/`.

13. **Destination-table non-pawn generation: measured and parked.**
    Current pieces() repeatedly derives coordinates for each candidate. An
    isolated source uses existing ordered knight destinations and attack rays,
    preserving runtime kind dispatch, occupied-square stops, king-victim
    exclusion, chronological lists, caps and all special/pawn routes. It changes
    only movegen.rs, with the prior coordinate producer retained under cfg(test)
    for independent full/capped ordered comparisons. All134 native tests and54
    strict replays pass on generic125d7446. Exact generic controlc946104a already
    has its own54 pass, explicitly reused. Table loads/slices can offset saved
    coordinate operations; no benefit, PGO result or adoption is claimed.
    See `evidence/generation-rays-preparation-20261018/`.

    The balanced generic60-lifetime pilot independently reconciles14.639909s
    control versus14.606063s rays,0.231190% lower. Five medians decrease,
    profile05 increases, and all six sample ranges overlap. Symbols grow
    1817/1856 bytes and total text3656 bytes. This is insufficient evidence
    for PGO or adoption; preserve canonical8d source unchanged.

14. **Exact uncapped influence profile sums: own PGO measured and parked.**
    A private immutable256-byte table replaces only profile_sum arithmetic for
    all256 normalized byte inputs; public const API, relation cap tables, charge
    sites, state/layout and consumers remain unchanged. Native134 tests include
    the independent full-byte digit oracle. A strengthened10000-position own
    coordinate activity/influence oracle,54 strict replays and eight interruption
    fixtures also pass. Generic09d7e067 contains one complete table payload.
    Its balanced60-lifetime pilot independently reconciles14.690910s control
    c946104a versus14.527878s lookup,1.109747% lower. Five medians improve,
    profile29 increases, and all six sample ranges overlap. This is a modest
    finite observation without a confidence/qualification claim. The separately
    trained own-PGO artifact f3562ff6 passes54 strict/eight-wire regression, but
    its matched60-lifetime pilot sums13.424908s baseline8d9dddc5 versus
    13.4303025s lookup,0.040183% higher. Four medians decrease and two increase;
    all six ranges overlap. Park without adoption or broader cost runs.
    See `evidence/profile-sum-cpu-pilot-20261018/` and
    `evidence/pgo-profile-sum-cpu-pilot-20261018/`.

15. **Exact activity pressure-mark values: measured and parked.**
    A different private immutable256-byte table replaces only pressure_value
    weighted-popcount arithmetic; all masked callers, marks, charge sites and
    profile_sum remain unchanged. The independent full-byte per-bit test, all135
    native tests,10000 strengthened coordinate placements,54 strict replays and
    eight interruption fixtures pass. Frozen41300b67 contains one complete table
    payload. Its balanced60-lifetime generic pilot independently reconciles
    14.6522095s controlc946104a versus14.6978770s lookup,0.311677% higher.
    Three medians decrease and three increase; all six sample ranges overlap.
    Park this candidate without PGO or integration. It neither inherits nor is
    combined with profile_sum results. See
    `evidence/pressure-value-cpu-pilot-20261018/`.

16. **Repeated capture material endpoints: measured and parked.**
    The frozen79 diagnostic derivative passes54 unchanged strict replays and
    independently reconciles163,583,266 segment material source demands.
    An invocation-local1+K model avoids32,274,602 demands (19.7298%) across
    Q and ordinary frontier. Q alone contributes27,771,603 (41.5391% of Q
    endpoints;16.9770% of segment material demand); ordinary contributes
    4,502,999 (2.7527% of segment demand) and has11,035,210 zero-call loops.
    Select a Q-only lazy pure endpoint trial before any persistent layout.
    First-use/zero-demand initialization, recursive frame pressure and emitted
    code remain costs to measure. Counts are source opportunities, not emitted
    calls or CPU savings. See
    `evidence/material-allowance-census-20261018/RESULTS.md`.

    The invocation-local Q-only candidate21daa966 then passes138 native tests,
    all54 strict replays and eight interruption fixtures/24 searches. Its frame
    grows96 bytes and Q code277 bytes. The balanced generic60-lifetime pilot
    independently reconciles14.683823s root79 control9709f8e9 versus14.682551s
    reuse in summed medians,0.008663% lower. Three medians improve and three
    increase; every observed range overlaps. Park A and its two bounded codegen
    variants without PGO or adoption. Source opportunities did not become a
    useful measured CPU gain. See
    `evidence/q-material-reuse-cpu-pilot-20261018/README.md`.

17. **Checked bounded reply order: generic and own PGO support adoption.**
    Two production consumers need only the saturated count, with exact complete
    zero/one replies reused by Q. A checked-only LIMIT2 trial preserves EP first,
    tries existing king evasions early and skips their duplicate final pass.
    Full generation order, legality predicates and work/state ownership stay
    unchanged. All144 native tests,54 strict replays and eight interruption
    fixtures pass. Main capped code shrinks but a helper is newly outlined;
    combined code and peak stack do not establish a win. The balanced generic
    60-lifetime pilot independently reconciles14.679567s control d38ff037 versus
    14.4964515s candidate61fdefb3 in summed medians,1.247418% lower. Five medians
    improve, one rises and four observed ranges are separated. New exact-source
    own-PGO profiles each pass54 strict replays/eight-wire and independent
    byte-identical profile remerging. Their matched60-lifetime pilot reconciles
    13.544937s controle4921975 versus13.340055s candidate52ec6b9e:1.512609%
    lower, all six medians lower, five ranges separated and profile29 overlapping.
    Adoption is complete after fresh147/54/eight-wire/6161 composition validation
    with current88; full generated order and exact zero/one replies stay complete.
    No old8d profile transfer or complete cost result is claimed. See
    `evidence/bounded-reply-king-first-cpu-pilot-20261018/README.md`.
    Exact own-PGO evidence is in
    `evidence/pgo-bounded-reply-cpu-pilot-20261018/README.md`.

18. **Ordered bitplane checker discovery: generic and own PGO support composition.**
    Phase1 reuses existing coherent Position planes for exact ordered first-two
    checker identities at full/capped generation. It preserves pawn/knight/ray
    order, adjacent-king interleaving, blockers and caps. Q's projected mailbox
    remains unchanged.143 native tests include independent mailbox identity
    comparisons over10000 broad placements/all targets/both colors;54 strict
    replays/eight-wire pass. Full/capped local frames shrink32 bytes, while
    whole text grows1408 bytes and Q outlining changes; no neutrality follows.
    The generic60-lifetime pilot independently reconciles14.696158s d38ff037
    versus14.496659s132ba135:1.357491% lower, all six medians lower, with
    profile01/02/29 ranges separated and04/05/35 overlapping. Candidate7b17c000
    then passes own54 training/profile remerge,54 strict/eight-wire with zero
    missing/stale warnings. Its matched own-PGO60-lifetime pilot independently
    reconciles13.5684265s controle4921975 versus13.4018985s candidate:1.227320%
    lower, all six medians lower,01/02/04/29 ranges separated and05/35 overlap.
    Whole-suite CPU15 has46 nonidle ticks despite own-pane client affinity
    correction; no pervariant interference or absolute idle claim follows.
    Adopted through105 after fresh composed validation and a distinct matched
    generic95-to-combined pilot. These trial timings do not transfer.
    See `evidence/ordered-bit-checkers-phase1-cpu-pilot-20261018/README.md`.
    Own-PGO result:
    `evidence/pgo-ordered-bit-checkers-phase1-cpu-pilot-20261018/README.md`.

19. **Ordinary known-check admission: generic signal, own PGO pending.**
    Reuse the reached ordinary node's existing immutable-position check fact
    in a shared runtime full generator. False skips only ordered discovery;
    pin construction and unknown/capped/checked-Q behavior remain. No field,
    Boolean prequery or child/null inheritance is added.147 native tests,
    54 strict replays/eight-wire and independent source review pass. One full
    body survives with the same0x128 frame; whole text grows16 bytes. Its
    generic60-lifetime pilot reconciles14.4919105s731aa0aa versus14.386390s
    682446e7:0.728134% lower, five medians lower and profile05 higher with
    separated ranges. Profile02/04/29 favor candidate in separate ranges;
    01/35 overlap. Keep experimental pending a matched own-source PGO test.
    See `evidence/known-check-generation-cpu-pilot-20261018/README.md`.

20. **One projected Q bit view: generic and own PGO support composition.**
    Phase2 replaces the Q projected mailbox and both consumers together. One
    existing 32-byte tag-plane projection serves exact ordered first-two route
    detection and final own-king safety. Optimistic updates, eligibility,
    reply/history chronology and all charges remain. Native 145, strict 54 and
    eight-wire/24-search validation pass, including broad pre-legality pseudo
    projections and fixed unsafe/special/order witnesses. Codegen confirms one
    shared view; Q text grows 434 bytes, its frame shrinks 16, and unchanged
    ordinary source grows 143 bytes through outlining. No neutrality follows.
    The independent 60-lifetime generic pilot sums 14.546593 s for phase1
    `132ba135` versus 14.341421 s for phase2 `3462a87a`: 1.410447% lower.
    All six medians are lower; profiles 01/05/29 have separated ranges and
    02/04/35 overlap. Whole-suite CPU15 has 16 nonidle ticks, without
    per-variant attribution. Own-source54-case training, independent identical
    profile remerge and strict54/eight-wire regression also pass. The matched
    own-PGO60-lifetime pilot independently reconciles13.393119s phase1 control
    `7b17c000` versus13.1219665s phase2 `737a0946`:2.024566% lower. All six
    medians are lower and all six observed ranges are separated. Whole-suite
    CPU15 has15 nonidle ticks without pervariant attribution. Adopted through105
    after fresh composed validation. The direct generic95-to-combined pilot
    separately sums14.4239440s versus14.0816565s:2.373051% lower, with all six
    observed ranges separated. Earlier trial timings do not transfer; full54/12
    cost/gameplay qualification remains open. See
    `evidence/ordered-q-bitview-phase2-cpu-pilot-20261018/README.md` and
    `evidence/pgo-ordered-q-bitview-phase2-cpu-pilot-20261018/README.md`.


21. **Stateless activity destination values: select for integration validation.**
    The isolated one-file change derives an immutable256-byte physical-square
    table from the original value constants and selects the same eligible-rook
    variant before target traversal. No persistent field/cache, ownership,
    arithmetic width, charge, traversal or mark semantics changes. Native178,
    strict54 and eight-wire24 pass with independent source/archive/raw closure.
    Generic7cf39800 versus exact11739cadc62 independently reconciles70 lifetimes
    on the fixed custom seven cases01/02/04/05/29/35/08:14.5346415s versus
    14.4387960s summed medians,0.659428% lower, all seven medians lower and
    ranges separated for05/35 only. This is a development set, not the released
    pilot/full54 acceptance schedule.

    Fresh own54 training and independent byte-identical profile remerge produce
    d5ee1f3f; its fresh54/eight-wire24 and independent raw reconciliation pass
    with zero missing/stale-profile warnings. Its separate fixed70-lifetime
    own-PGO comparison to6a5ce6e2 independently reconciles13.344343s versus
    13.1695895s,1.309570% lower. Six medians are lower; profile29 is0.4075%
    higher with overlapping ranges.04/05/35 favor candidate with separated
    ranges; the other four overlap. Both whole-suite observations show zero
    CPU15 nonidle ticks, without continuous exclusivity or per-variant attribution.
    The original predeclared advancement rules pass; no favorable-case reruns,
    outlier deletion, confidence claim or generic-to-PGO timing transfer occurs.

    Generic activity shrinks563bytes with unchanged frame; own-PGO shrinks393
    and its frame16bytes. Scoped caller sizes/frames/call boundaries show no
    new growth. These are static observations, not dynamic retired work or
    cache/spill-neutrality proof. Select for fresh full117 diagnostic validation
    before source promotion. Current root/native and full54/12 costs remain
    exact117/6a; final qualification stays open. The separate pawn-forward-scan
    fusion is prepared from the original117 basis and remains unbuilt.
    See `evidence/activity-value-inputs-pgo-cpu-reconciliation-20261018-01/README.md`
    and `evidence/pawn-forward-scan-fusion-parent-review-20261018/review.md`.


22. **Pawn forward-scan fusion: parked after fixed generic pilot.** The isolated
    one-file source shares the candidate path/protection traversal with raw
    progress, retaining the backward scan and public scalar domain. Independent
    verification binds178 native tests (including an old-scan/coordinate-path
    differential),54 original strict replays and eight-wire24. Actual generic
    lowering removes the duplicate loop and raw call, with candidates local
    frame+48B and combined emitted text-209B. There is no persistent state.
    The fixed seven-case70-lifetime pilot retains14 excluded warmups and56
    measured samples, summing14.5281365s control39cadc62 versus14.497491s
    trial541d324c:ratio0.9978906104 (0.210939% lower). Six medians decrease;
    profile05 increases0.274293%. Only02/08 ranges separate; the other five
    overlap. Whole-suite CPU15 has one nonidle tick and15703 idle ticks, without
    pervariant attribution. Independent original70/accounting/source checks pass.
    The common5-of7/no-ratio>1.02 gate passes, but aggregate misses<=0.995 and
    profile08ratio0.983282196 misses<=0.97. Both predeclared branches fail.
    Park without a favorable-case/normal-variability rerun, own-PGO or activity
    composition. Root remains adopted activity sourceed85b6dd. Exact evidence is
    in [the trial checkpoint](../../evidence/pawn-forward-scan-fusion-trial-checkpoint-20261018/README.md).
    This result does not establish neutrality, significance or full54/12 cost.

23. **Remembered group reciprocal: parked after the fixed generic pilot.**
    Replacing repeated unsigned remainder with a constructor-owned exact
    reciprocal passes179 native tests,54 strict replays and eight-wire24,
    with independent source/raw closure. The emitted query division disappears,
    but ownership reorders embedded search fields and grows the root frame32B.
    The single fixed70-lifetime generic comparison against full-byte948c sums
    14.375005s versus14.368978s:ratio0.9995807306 (0.041927% lower),4/7 lower
    medians, worst1.00276197 and all seven observed ranges overlapping. It fails
    aggregate<=0.995 AND>=5 lower AND worst<=1.02. Park without own-PGO, retry,
    enlargement or composition; production retains remainder. The complete
    [TT checkpoint](../../evidence/fullbyte-remembered-reciprocal-trial-checkpoint-20261018-01/README.md)
    preserves740 members, both images, original raw measurements and all
    consumed dependencies. Static division removal did not predict useful
    whole-engine CPU improvement.

24. **Placement transpositions: one bounded pure-component trial.**
    A logging-only derivative retains all real producers and passes the original
    strict54. Offline reconstruction reconciles37,094,875 full encounters,
    115,801,445 activity relation queries and108 epochs, with zero resident-key
    payload mismatches. A1024-slot direct-map model has4,819,294 exact-board hits
    (12.9918% of encounters), representing8.0924% of activity R. Profile35 hits
    only4.3017%; profile08 hits16.9337%. Larger models add hits but do not
    establish any CPU benefit. This is a different opportunity from item2's
    rejected same-produced-node cache. No influence construction, pawn effect
    or semantic relation charge can be removed by these hits.

    After a bounded independent architectural critique, select one1024-slot
    activity/shelter scalar cache prototype. Enforce production-influence
    provenance throughout Search's full and selector call graph, including
    observed paths; public selectors with prefilled custom maps remain uncached.
    Preserve one shared numerical composition, exact placement admission and
    existing new-search clearing, without Position/Node growth. Use one fixed
    seven-case70-lifetime generic pilot including adverse profile35, advancing
    only at aggregate<=0.995 AND>=5 lower AND worst<=1.02. Failure parks it
    without resizing, relaxing the rule or retrying normal variability.
    Generica9472bd0 then passes184 native tests, original strict54 and eight-wire24,
    independently reconciled against exact69 source/archive/compiler and raw
    outputs. Actual emitted full evaluation adds491 text bytes and112 bytes of
    main stack reservation; root reservation grows32 bytes. A new816-byte hit
    weighting helper and payload/weight copies survive. Exact32-byte key
    comparison, heap65536/alignment64, miss fills and both charge paths are
    supported by the captured code; recursive Q/ordinary frames remain unchanged.
    These observations do not establish CPU or copy neutrality.

    The one fixed70-lifetime generic pilot independently reconciles14 excluded
    warmups and56 measured samples:14.348167s control948c versus14.1165515s
    candidate, ratio0.9838574851 (1.614251% lower),7/7 lower medians and worst
    ratio0.991736828 (profile35).01/02/04/05/08 observed ranges separate;
    29/35 overlap. CPU15 whole-suite deltas show15430 idle,3 nonidle and1 iowait
    tick, without per-variant attribution. The frozen rule passes. Advance to
    fresh own-source PGO preparation; no cache is adopted. See
    [decision0014](../decisions/0014-pure-component-cache-trial.md).

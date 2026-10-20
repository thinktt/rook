# Rook2 architecture and performance assessment

2026-10-20 · imp2-lead · reviewed repository HEAD `c23d7650d3a1588135c0745487d85ec1f63437eb`

**Rook2 has a credible basis for a short, focused continuation, but the evidence does not yet establish a route to recover another four seconds. I would retain candidate62, resolve the comparison baseline, and investigate earlier construction of checked move destinations before considering a representation rewrite.** A transposition-table layout experiment is the next distinct architectural possibility, conditional on its access population. More caches, another ordinary Influence delta, and isolated copy removal are poor default uses of the remaining effort.

The implementation has made substantial progress. The recorded whole54 total fell from candidate25's 73.059178 seconds to62's 67.640360 seconds, with intermediate changes to Influence, tactical generation, pin discovery and compiler layout. Those are separate measurement windows, not a causal decomposition of the gain. The problem now is selecting work with enough remaining benefit, rather than a shortage of possible edits.

This assessment covers the current architecture, the cataloged R1–R25/E26–E67 history, representative original decisions and cost studies, the current source paths, and outstanding qualification work. It is a survey, not a fresh conformance audit or independent replay of every archived result. I inspected only Rook2, the released specification and approved handoff material. I used no subagents and performed no builds, tests, benchmarks, profiling or engine executions. New numerical work is limited to arithmetic over existing reports, retained in [survey-calculations.json](2026-10-20-survey-calculations.json). Engine source, retained artifacts and implementation ownership are unchanged.

**The first decision is what “finish” means.** The released [acceptance policy](../../../king-spec/performance/acceptance-policy.md) distinguishes the optimization target, matching or beating KingRE, from qualification limits: aggregate CPU ratios at most1.10 and every individual ratio at most1.25, separately for all54 searches and all12 game units. Exact behavior and valid measurement remain prerequisites.

| Existing observation | Rook2 candidate62 | Historical Rust-PGO reference | Raw ratio |
|---|---:|---:|---:|
| Whole54, sum of case CPU medians | 67.640360s | 63.431779s | 1.066348 |
| Whole12, sum of game CPU medians | 675.156653s | 644.222971s | 1.048017 |
| Largest individual ratio,54 /12 | — | — | 1.167576 /1.123680 |

These figures are numerically inside the published limits, but they are **not qualified passes**: hardware/windows and the remaining comparison procedure differ. Raw54 parity would require removing4.208581 seconds, or6.222% of current time. That arithmetic does not establish that4.208581 is the actual same-hardware gap. The [current status](../../STATUS.md), [whole54 report](../../evidence/exttsp-profiled-standard54-results-20261020-01/README.md) and [whole12 report](../../evidence/exttsp-profiled-games12-results-20261020-01/README.md) preserve this distinction.

The [fixed-executable calibration](../../evidence/opaque-calibration-cpu-reconciliation-20261018-01/README.md) found Vic faster for that program: aggregate local/reference ratio0.938863, with per-case ratios0.906–0.972. The historical same-artifact candidate25 Bee/Vic search totals also differed,75.770s versus72.630s, under their stated scope. Neither observation licenses scaling current62 or the KingRE reference. They do, however, argue against assuming the VM is simply making Rook2 appear slower than it is. Contemporary comparable measurements have higher decision value than treating four seconds as a precise engineering budget. The approved [calibration memo](../../../spec-issues/v2.5.0/2026-10-16-performance-handoff/hardware-calibration.md) explicitly limits transfer between programs.

**The architecture is coherent; its basic ownership choices are not shown to be the bottleneck.** The [initial design](../architecture.md) was provisional, and some proposed details never became production. The following describes current code, not that proposal:

| Owner | Current design and consequence |
|---|---|
| Placement and transitions | Position160 combines a mailbox, chronological typed lists, fingerprints, rule state and four maintained tag planes. Node176 adds retained evaluation. Children are copied and then updated. Chronology and all redundant placement views must stay coherent. |
| Geometric queries | The planes supply Boolean attacks, projected safety and ordered checkers. Legal move generation uses a per-call safety summary. Nonchecked tactical generation has a separate checking-destination mask producer. Evaluation Influence has different transparency semantics and cannot replace these attack queries. |
| Evaluation | Root context is bound once. FAST uses retained terms; FULL selects the semantic pawn cache and computes current pawn terms, Activity, shelter, central terms and finishing. Influence materializes only on demand. Activity pressure feeds shelter; Activity piece values also feed tempo. |
| Recursive state | Each produced child owns its retained terms. Scout retries reuse that child; siblings inherit the parent. Per-ply candidate/extension/PV storage is separate, while ordering scratch is shared because ordering finishes before recursion. |
| Shared memory | The TT uses four12-byte records per48-byte group, recent-first lookup and prescribed replacement behavior. Generation tags normally clear it logically. The128-group pawn cache has specified identity/collision semantics; it is not a conventional optional optimization. |
| Interfaces and observation | Production wire/session handling and diagnostic translation are separate boundaries. Static generic/const observation paths avoid requiring a dynamic observer in normal recursion. Shared numerical and scheduling owners limit semantic divergence. |

Relevant source: [position](../../src/position.rs), [attacks](../../src/attacks.rs), [movegen](../../src/movegen.rs), [tactical](../../src/tactical.rs), [engine](../../src/engine.rs), [ordinary](../../src/ordinary.rs), [quiescence](../../src/quiescence.rs), [evaluator](../../src/evaluator.rs), [remembered](../../src/remembered.rs), [pawn structure](../../src/pawn_structure.rs), and [timed sequence](../../src/timed_sequence.rs).

Three boundaries constrain useful redesign:

- Physical computation may disappear while required N/R charges, ordering, retained/cache effects and interruption behavior remain. A faster search with fewer prescribed visits is not this optimization task.
- Geometry coherence, native-map provenance and the lifetime of a root-bound context are separate facts. Public mutable Positions and supplied Influence maps prevent treating a plain reference, hash or `Some` as universal authority.
- A geometrically legal attack map, evaluation Influence and Activity's direct/additional destinations are different computations. Sharing their storage or traversal requires an actual equivalence proof, not the observation that all contain rays.

The existing split is defensible. I found no architectural reason to replace recursion, remove the public scalar paths, introduce a global derived-state cache, or switch all placement to make/unmake now.

**The experiment history contains useful negative evidence, but it does not rank every architecture.** The [brief catalog](../performance-experiments.md), [early catalog](../../../rook2-experiments/catalogs/rook2-performance-catalog-early-20261020.md), [late catalog](../../../rook2-experiments/catalogs/rook2-performance-catalog-late-20261020.md) and [diagnostic inventory](../../../rook2-experiments/catalogs/rook2-performance-diagnostics-catalog-20261020.md) provide the full navigation. Their identifiers include censuses and unimplemented proposals; “67” is not a count of67 optimization runs.

| Family | What was established | What I infer for further work |
|---|---|---|
| Shared geometry, typed Influence enumeration, relation tables, static Activity specialization | Multiple adopted changes with separate own-PGO evidence. Persistent planes beat the tested local-supply implementation using the same Boolean kernel. | Preserve these as measured baselines. Their success does not justify adding arbitrary persistent fields. |
| Generation summaries, projected Boolean checks, tactical checking masks, bitplane pins | Repeated accepted reductions in geometric work. Candidate51 constructs quiet checking targets directly;57 changes pin discovery. | This is the strongest demonstrated source-change family. Examine remaining construction before rejection. |
| Fresh Influence masks and accumulation,37/43 | Both adopted.43 replaces repeated output expansion with local bit-sliced accumulation and a transpose, retaining a scalar no-slider path. | Fresh construction is already optimized. A new delta must beat this complete producer and its integration costs. |
| Pure-component cache24 and root-bound cache33 | Generic gains shrank to own-PGO reductions of0.357% and0.375%, below their gates. Lookup, payload and compiler-factoring costs remained. | High placement reuse alone is insufficient. Do not start with another cache size or weighted payload. |
| Same-node FULL, Activity/category reuse and null-map censuses | Same-node and category repeats were small; current62 whole-Activity repeats were about0.111%/0.043% in observed cases. The narrow null-map opportunity was small. | These observations actively lower the priority of the corresponding caches. They do not prohibit all possible reuse. |
| Incremental Influence29/30/50 | Ordinary eligibility exceeded95%.30 saved2.60029% whole simulated Ir on35, yet its native pilot failed.50 added masks and same-weight cancellation and still failed its generic gate. | Ordinary parent-map delta has now had several materially different attempts. Another census of high coverage is not new economic evidence. |
| Activity masks/geometry35/42/52 | Local/global setup and geometry replacements failed;35 expanded the Activity frame456→952B and code7884→19432B. | A large source-level work reduction can lose to setup and code generation. A fourth frontend needs a new mechanism and demand accounting. |
| Ordering49/54/55 | Bounds simplification lost most of its gain under PGO; six-stream merging and small-entry work missed generic advancement. Exact gap6/gap1 tie behavior matters. | Sorting remains a possible cost, but not an untried “replace insertion sort” opportunity. |
| Copy/API changes28/44/47/48/66/67 | Some failed to remove transfers. Others did remove them:66 removed a main-child160B copy and67 a Q-entry160B snapshot, but own-PGO gains were0.287%/0.078%. | Do not equate an observed copy with a substantial time budget. These narrow results do not settle complete make/unmake. |
| Tables, arithmetic, pawn fusion and return shapes | Mixed small results; several attractive generic changes vanished or regressed under own-PGO.65 reduced relation-table payload262144→7936B but gained only0.101% in its screen. | Fewer bytes, branches or arithmetic instructions are mechanisms to measure, not adoption arguments. |
| Compiler layout |62's paired screen improved1.044%; fat LTO36 and machine splitting63 failed their own-PGO screens. | Compiler effects are material, but a general flag sweep is not a supported path. |

The old [copy/undo microexperiment](../research/position-layout.md) was a short repeated-input wall-time test of Position128, with an adverse undo sample retained. It did not evaluate current160/176 state, predecessor-map lifetimes, Q probes, retries or integrated search. “Copy-child is proven optimal” would be false. Equally, the modest results of actual copy removal give no reason to fund a broad undo rewrite before measuring a credible total transition/restoration opportunity.

An initially proposed detail also remains absent: [the design](../architecture.md) proposed carrying generator source-list indices, whereas current `MoveList` stores moves alone and `Position::locate` searches the typed list. That is a genuine proposal-to-code difference, not a discovered speedup. Extra metadata must survive ordering/IIO, fit parent lifetime, handle non-generator moves and repay its storage/transport. I would keep it below the leading investigations until transition cost warrants it.

**The profile evidence locates work more reliably than it prices removable native time.** Current62 has a partial one-case35 simulation with these attributed NAME shares:

| Attributed NAME group | Share of recorded summary Ir |
|---|---:|
| Activity compute | 20.742% |
| Main ordinary group | 20.432% |
| Coherent Influence build | 10.910% |
| Full legal generation | 8.059% |
| Shelter compute | 4.898% |
| Quiescence group | 4.178% |

These are calculated from the [existing report](../../evidence/current62-branch-cache-results-20261020-01/report.json). They are neither native CPU shares nor complete physical function owners. Inlining places other work inside ordinary; the full legal-generation row does not price every bounded-reply call. The original strict study failed on two unattributed instructions out of43,796,694,936. Preserve that failure and unknown bucket. Their tiny size does not make the original method pass, but further investigation of those two instructions is unlikely to change the architecture ranking. The much larger limits are simulated behavior, attribution, a hypothetical cache model, and coverage of one busy case.

Earlier35/08 profiles provide useful contrasting contexts but belong to older artifacts. They cannot be combined with current62's rows into a current corpus-wide CPU partition. The TT source/access review is particularly instructive: its inline probe occupies modest simulated instruction context but carries substantial modeled memory misses. Instruction share alone would be a poor way to dismiss or promote it.

An illustrative cost test makes the scale clear. If a component really consumed20% of native runtime, removing6.222% of total time from that component alone would require reducing its complete cost by about31%. A10% component would need roughly62%. The table above does not establish either native premise. It shows why small classifier edits are an unconvincing plan for the entire raw gap.

**The screening process should be refined prospectively, not relaxed to rescue old results.** The fixed70 screen uses01/02/04/05/29/35/08. From62's whole54 medians, those cases total11.865881s,17.54% of the full corpus.04 and35 contribute7.724442s:65.10% of that subset, but11.42% of full54. This is a calculation of workload weighting, not a new fixed70 observation.

That subset is useful for detecting several known regressions. It cannot be assumed representative of every new mechanism. The “at least5/7 lower” rule can also penalize a deliberately selective optimization: unaffected cases can fluctuate on either side of equality even when the affected population improves. The0.5% floor is a resource decision, not a statistical significance threshold.

There is another historical distinction to retain. Decision0034 described a limited prospective PGO-sensitive exception, but later65–67 already used fresh own-PGO-first paths. The [current62 method](../../evidence/current62-pgo-first-method-preparation-20261020-01/README.md) explicitly removes generic timing as their prerequisite. Recommending “finally test PGO directly” would overlook completed work. A future plan should state the actual governing lane in one place instead of relying on the older default-policy wording.

For a new consequential change, I recommend fixing its affected workload classes and controls before implementation, using the actual production recipe, and using a screen whose weighting matches the intended decision. Keep an aggregate benefit threshold and explicit regression protection; do not require an improvement count that contradicts a selective mechanism. Reserve full54 and12 for independent broad confirmation. No old sample should be deleted, reinterpreted as passing, or rerun until favorable. Nor should the small positive point estimates of parked variants be summed into a hypothetical combined gain.

The records are unusually thorough, but their volume has an engineering cost. Many trials have separate preparation, permission, source, backend, archive and reconciliation documents. For future work, one bounded experiment record can link automated immutable receipts and hold the question, mechanism, exact scope, cost ledger, decision rule and result. Human review should concentrate on changed semantics and material code-generation risks. I would preserve raw evidence while reducing repeated prose and manual stage narration. I have not measured historical token or labor consumption, so this is a process assessment, not a quantified savings claim.

**My ranked next investigations are the following.** These are recommendations, not implementation selection or execution authority.

| Priority | Investigation | Evidence supporting it | Decisive missing evidence / stop |
|---|---|---|---|
| 1, decision prerequisite | Establish a contemporary comparable candidate/reference baseline and finish the qualification plan | Raw totals are close; calibration differences are material; target and acceptance limits differ | Exact same-hardware comparison and frozen uncertainty/resource procedure. If qualification is the goal, this may change the need for further optimization. |
| 2, first source candidate | Construct checked nonking destinations through the existing evasion constraint | Millions of candidates reach an immediate off-mask rejection; accepted51 shows the value of constructing a narrower inventory | Complete enumeration/setup cost, exact ordering, bounded-call economics and actual own-PGO benefit. Stop if filtering moves later or setup overwhelms skipped traversal. |
| 3, conditional architecture candidate | TT layout chosen from actual probe/store populations | Current48B groups can require two distinct lines on paths reaching retained records; miss filters and payload paths differ | Recent cutoffs versus full misses/retained hits, actual alignment, footprint and store costs. Stop if no access population supports a concrete layout advantage. |
| 4, bounded lower-risk work | Propagate exact evaluation demand to pure subterms | Current FULL computes some terms whose later exact coefficient can be zero | Frequency and complete saved producer cost, preserving all semantic charges and public observations. Stop if only rare zero configurations benefit. |
| Deferred | Broader state/restoration or Activity redesign | Initial architecture remains provisional; major owners remain expensive | A quantified whole-path budget and a distinct algorithm, not another copy deletion or local mask frontend. |

**For checked generation, the opportunity is enumeration rather than the projections already avoided.** The [current census](../../evidence/current62-generation-safety-census-results-20261020-01/summary.json) observes6,696,660 off-mask rejections on04 and6,425,338 on35. `GenerationSafety::accepts` already rejects them before projection. The proposal is to intersect allowed destinations with movement geometry before constructing or walking rejected candidates, while preserving existing blocker and source-order semantics.

The necessary invariants are concrete:

- Retain EP's distinct changed-square behavior, castle admission and king projections. Do not use an ordinary two-square proof for them.
- Keep type/source chronology, direction/near-to-far ordering, promotion expansion and the single-check pawn prefix. A bit scan in square order is not a drop-in replacement.
- Preserve limit2 behavior: checked bounded calls try kings early, and a result below two supplies a complete reusable list. About92.8%/93.4% of observed checked limit2 calls return two witnesses; eager global construction can lose on those early exits.
- Keep final projection for on-mask candidates until a separate proof replaces it. Earlier destination filtering is not complete king safety.

The census has no ordinary/Q/root attribution. It establishes occurrence, not the cost of the residual walks. Unchecked pinned projections are only about3.03%/2.45% of all counted projections in04/35. That makes replacing those projections a lower-priority question than the large off-mask enumeration population, without claiming the percentages measure time.

This is a plausible incremental gain, not a four-second forecast. A narrowly scoped prototype against62, preserving current public/reference paths for differential ordered inventories, is the most defensible first source experiment if the owner resumes optimization.

**For the TT, choose between competing populations rather than “align to a cache line.”** The [opportunity review](../../evidence/current62-tt-layout-opportunity-20261020-01/review.md) and [actual access review](../../evidence/current62-tt-layout-access-review-20261020-01/review.md) already establish the important baseline: the emitted probe performs conditional1/2/4-byte field loads, not an eager48-byte group load. Under64-byte lines, those individual naturally aligned loads do not split a line. Multiple fields can nevertheless touch different lines.

A64-byte aligned/strided group can colocate all four records but increases slab payload by one third. It must keep the same semantic group count `largest_prime(floor(tts/48))`; substituting `tts/64` would alter behavior. A compact48-byte layout with a contiguous identity header could improve full-miss filtering without that expansion, but a recent hit may then need a separate payload line where today's record is together. Store displacement, generation checks, mate-depth writes and setup costs also matter.

The source and access analysis is sufficient to pose this tradeoff; another purely textual proof of the same spans has little value. What is missing is the dynamic path mix and a bounded comparison of the chosen complete layout. I would prefer the compact identity-header option if full misses dominate, or consider aligned64 if broader record touches dominate and resource limits permit it. Neither preference is an unconditional recommendation. Shared-library/public semantics and prescribed collisions remain unchanged.

**For evaluation, start with exact unused dependencies, not more reuse.** `shelter::compose` multiplies screen by middlegame and pattern/exposure by `max(opening/2 - endgame + middlegame, 0)`, yet `components` computes all of them first. A private composed path could avoid a pure subterm when its exact multiplier is zero. Likewise, if shelter's final contribution is provably unused, its sole demand for Activity pressure can potentially be removed, including corresponding pressure-mark work, while retaining Activity piece values for tempo and all required R charges.

This extends the cataloged zero-shelter idea into a dependency question; it is unimplemented and its occurrence is not measured here. It is not permission to skip Activity when mobility weight is zero: tempo and relation work still consume it. Public `Activity`/`Shelter` outputs and supplied-map behavior must retain complete semantics, and every intermediate rounding owner must remain exact. The existing pawn-progress zero-factor guard shows the architectural pattern already has a local precedent. New predicates, branching and specialization costs can outweigh it.

The potential benefit is probably narrower than the entire Activity/shelter owner. I would not fund another whole Activity rewrite on its20.7% simulated share.35/42/52 already paid to test variants of that idea. A fundamentally different kernel would need to explain how it avoids their eager setup, wide live state and code growth.

**Several directions should remain parked unless new evidence changes their premise.**

- Ordinary parent-map Influence delta, including same-weight cancellation, has been tested in29/30/50. The previously suggested signed-delta temporary bitplanes remain algebraically possible and untested, but do not outrank the current candidates merely by avoiding an inverse transpose.
- Exact-placement, root-weighted and same-node caches have weak observed economics or recurrence. Broadening their lifetime also increases provenance and invalidation obligations.
- Copy-only/API variations are not a strategy for the full gap. A future make/unmake design must account for simultaneous predecessor/current access, Q reply probes, history restoration and retained scout state; the old microexperiment cannot select it.
- More relation-table compression, local arithmetic substitutions, a sorting algorithm swap or generic compiler-flag sweep needs a new cost mechanism. Existing smaller tables, fewer branches and removed copies already failed to predict worthwhile native gains.
- An unexplained two-instruction simulation residual should stay documented; resolving it is not on the critical path to a performance decision.

**Qualification needs its own finite completion plan.** The implementation has substantial recorded finite coverage:195 native tests,209 diagnostic tests,7673 mandatory cases across117 operations/115 fixture files, plus exact main-artifact54/wire/regular12 checks. Candidate62 reuses unchanged-source tests and the exact diagnostic companion where stated. None of this should be described as freshly rerun by this survey.

The [qualification gaps](../qualification-gaps.md) still identify composed TT/window/IIO/stop behavior, hint admission, arithmetic/caller joins and command/publication behavior. The [uncertified-hint question](../research/uncertified-hint-completion.md) is concrete but conditional: no admitted public witness has established the concerning empty-source path. It should receive a reachable witness or exclusion argument, not a guessed fallback or a claim of a demonstrated defect.

I recommend classifying each remaining item as a demonstrated failure, a specific unresolved behavioral question, or a broader review obligation, then assigning a finite closure criterion. That avoids both treating green fixtures as universal proof and allowing undifferentiated proof work to consume an indefinite optimization campaign. The existing [uncertainty proposal](../../evidence/qualification-uncertainty-proposal-20261019-01/proposal.md) is explicitly unadopted; its substantial repetition schedule is a decision to make, not an automatic next run. The external3288-game gate remains a separate off-Vic responsibility.

**If asked to lead the next phase, I would use two checkpoints.** First, bind the actual finish criterion and comparable measurement profile, preserve62 as the control, and prepare one checked-generation design with a complete cost hypothesis and ordered-inventory proof obligations. Reuse the existing census; do not repeat it merely to produce familiar counts.

At the second checkpoint, review that candidate's actual production-build result and the TT population evidence, if collected under a separately bounded plan. Continue only if a mechanism gives a worthwhile whole-workload gain or the evidence establishes another specific opportunity. If both fail, retain62 and concentrate on qualification and delivery. Do not automatically spend the rest of a weekly allowance.

I am willing to lead that bounded phase, but would not justify a transfer of ownership by promising parity. The present evidence supports a disciplined attempt and a credible stopping point. It does not support either declaring the architecture exhausted or committing to an open-ended rewrite.

All historical dispositions remain unchanged. The only repository changes from this survey are this report, its small offline calculation record and a catalog link. No production candidate was selected, no parked optimization was adopted, and no reference implementation source was inspected.

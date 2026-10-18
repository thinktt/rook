# Candidate25 remembered-result production review

Read-only source/spec review, 2026-10-18. **No concrete score, depth or window mismatch established in this bounded trace.** A supported invariant is that every ordinary store preserves its node's original query, even after child returns change the running lower boundary. This is not a whole-engine conformance or reachability proof.

Scope: current `/home/legolas/rook2/src/`, released `/home/legolas/king-spec/spec/`, production-map, qualification-gaps and linked numerical reviews. Read-only byte comparison established current ordinary.rs, quiescence.rs, remembered.rs, ordinary_policy.rs, timed.rs and root_schedule.rs equal the corresponding frozen candidate25 files in `/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj` (actual f4ab7f/0). This is a six-file binding, not a new complete source/artifact inventory. No Imp1/private implementation material was used.

## Original query survives post-child evolution

Ordinary computes absolute target `P+D` at ordinary.rs702–703. It dispatches nonpositive depth/final ply/maximum-depth to Q **before** ordinary charge/table access (704–723), then performs draw admission (732–734). Its single Query (735–744) contains current derived group, secondary identity, P, that target, and unchanged request.lower/upper. Query is Copy and never reassigned. A usable probe returns its decoded score directly (748–752); it is not clamped or root-adjusted here. This follows ordinary-iterations.md156–182 and cached-admission.md17–30.

All actual store sites pass that original Query through store_ordinary650–664:

| Origin | Source | Score and markers |
| --- | --- | --- |
| Fast cutoff | ordinary.rs789 | trial; inherited hint/quiet marker; markDepth false |
| Shallow/static-or-null cutoff | 844 | trial; inherited hint/quiet marker; markDepth false |
| Successful checking probe reaching U | 919–922 | actual negated Q return; discovered move; both markers true; search continues |
| Normal list completion | 1075–1080 | best capped by saved effective upper; final preference/quiet marker; markDepth true |

These match ordinary-iterations.md432–441. Draw, evaluator-bound, empty-list and mate-lower-bound early returns do not acquire a normal store (ordinary.rs732,802,854,857).

The running `lower` starts from request.lower (937), rises only inside strict best improvement (1053–1066), and never enters the saved Query. Thus, for example, a final interior score equal to raised running lower still gets both permissions against the original open window; it does not become upper-only through an accidental equality against the raised boundary. Final clipping happens before normal-store permission calculation, as specified.

A scout retry constructs a **new invocation** with its retry bounds (1033–1043), so that invocation intentionally constructs its own Query. The caller's original Query remains unchanged. Tail IIO receives the original Request (1070–1072), not local lower; each pass uses original L/U and its own passBest (1103–1149). The node-entry exported bound/marked depth remain the actual probe observations (929–934,1070), not metadata from intervening stores. See ordinary-iterations.md289–323,392–409.

## Normalization and depth are owned once

remembered.rs72–85 calculates permissions from **raw stored score versus supplied original endpoints**, then normalizes inclusively at +/-9000 by +/-P and stores remaining depth `target-ply`. Query decoding119–133 uses the normalized threshold, adjusts by query P, and applies actual permitted cutoff comparisons. There is no interior-exact immediate return. A qualifying normalized mate bound bypasses depth sufficiency and raises stored depth after metadata observation109–127; ordinary callers do not pre-normalize or repeat this conversion. These are the literal remembered-results.md26–37,95–112 rules, including normalized-band rather than decoded-band mate recognition.

Selective adjustment does not change Query target or depth (ordinary.rs756–762). Main child D is D-1+fresh (960); null child D is D-3/4, with **no extra subtraction** (827–830); IIO child D is shallowTarget+fresh-P-1 (1143–1147). The child's own P+D reconstructs its intended target. Fresh depth extension remains separate from accumulated OR flags (954–960,1126–1148), as required by ordinary-iterations.md228–238,306–323,373–375. The table consumes actual original remaining depth, not iteration number, selective depth, accumulated flags or updated lower boundary.

Q has no Query/probe/store path. Ordinary-to-Q target is max(0,P+D) (704–718); Q recursion increments target only for checked parents (quiescence.rs433–440). Its returned score can feed an enclosing ordinary store through negation, but no Q target/depth is copied into the parent's Query. Its actual score/bound returns and completion clipping remain distinct (243–279,297–301,449–470), consistent with quiescence-tree.md83–115,189–192.

## Window premise and remaining gaps

For an **ordered incoming window**, reaching ordinary main/IIO after admission yields effectiveLower<U (otherwise the early bound return fires), while the mate-lower gate ensures U>P-9998>-10000. Main best starts below U and any qualifying best/lower improvement reaching U ends the loop; therefore its continued full/scout/retry windows remain ordered. IIO passBest starts -10000<U and a qualifying promotion reaching U ends that pass. Null's (-U,1-U) is always width one. In Q, passing stand-pat with an ordered incoming window leaves running lower<U; child cutoff stops further recursion. These are local conditional invariants, not a universal production L<U theorem.

**Do not infer universal open windows.** Root randomization explicitly allows transformed-window collapse and forbids automatic widening (root-randomization.md64–77). Current timed.rs193–205,617–625 independently transforms endpoints and adjusts the returned root score; remembered stores occur inside the child, before that root adjustment. Root scheduler retries preserve their original root-window ownership (root_schedule.rs122–156). The pure remembered diagnostic's strict-open +/-10000 admission (remembered-results.md134–150) is not a production-wide cap. The old store-origin numerical proof explicitly tolerates equal/inverted windows (store-origin review lines24–26,70–82); its capacity enclosure does not prove their reachability or full composed semantics. No arbitrary direct table injection or hypothetical extreme tuple is claimed production-reachable here.

The current numerical crosswalk flags production record-origin/decoded-band/window propagation for further proof (production-retained117 numerical review92–95); production-map.md82–97 also links a historical capacity proof. This review checks current call ownership and recurrence, not a new complete normalization-capacity induction or a blanket refresh of historical source identities. In particular, it does not resolve every window/band-crossing state by appealing to fixture success.

The **conditional empty-source remembered-hint ambiguity stays open** exactly as docs/research/uncertified-hint-completion.md15–55 describes. Hint endpoint truncation/metadata is intentionally uncertified (remembered.rs86,111; remembered-results.md35–37). No new skip, fallback, certification or source repair is proposed. General collision/hint reachability, full lifecycle/qualification and source-global arithmetic remain outside this bounded finding.

No builds, engines, tests, profiling, timing, Git operations, source edits, old-plan edits or oracle execution. All helpers used housekeeping CPUs0–5,8–13 and HOME TMPDIR. Only this new evidence directory was written.

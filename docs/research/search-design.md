# Ordinary search design from the released specification

Status: independent design research, 2026-10-17. Sources are the released
KingRE specification 2.5.0 and its performance companion under
`/home/legolas/king-spec`, plus the Imp2 mission. No existing Rook/Imp1 source,
architecture, private findings, or advisor consultation informed this note.

**Fact** below means required behavior in the linked specification, including
rules whose available fixtures cover a narrower domain. **Proposal** means an
Imp2 implementation choice to measure. A prototype milestone is explicitly a
bounded implementation claim, never a reduction of the eventual production
requirements.

## 1. Binding state ownership

The principal composition authorities are [ordinary recursive iterations],
[joined search], and [session lifecycle]. Component diagnostic limits do not
narrow their production semantics.

| Owner | Binding lifetime and effects |
| --- | --- |
| Session/game | Initial position, chronological played prefix and resulting states, personality, clock schedule and adjustment, mode/color, post selection, work-clock origin. Preserve up to 799 prior plies. Rewinds remove inactive branches from history. |
| Search-fixed context | Root side, root phase and material values, root-owned evaluation coefficients, draw preference, variation settings, one acquired seed. Ownership does not swap when a descendant changes side. Current phase remains a separate node property. |
| Search-shared mutable state | Remembered results, pawn-classification groups, history scores/total, killer pairs, cumulative work, root candidate work, adaptive limits and best-change history. These survive siblings, ordinary/quiescence calls where applicable, ordering passes, retries and depth iterations. |
| Branch-local state | Board/history continuation, retained positional subtotal, pawn-progress contribution and evaluation age. A child inherits its parent's retained pair, increments age modulo 256, and can replace its own pair by full evaluation. Returning restores the parent's pair and age. |
| Ordinary node | Incoming window, remaining depth, preceding move/extension, entry remembered observations, saved effective evaluation bounds, best/running lower, preferred move, PV, candidate order and accumulated extension flags. |
| Root iteration | Policy selected at entry, visitation order, completed ranking, current best/second/PV and fixed previous-iteration best. Numerical current best/second/PV start fresh each depth; only order/work and shared search state carry over. |
| Output capture | Best completed root's score, line, depth/status, SearchID and clock, copied together at capture. Later work cannot restamp it. |
| Stop/finish | Actual charged prefix totals and finish-clock input. These may be later than the retained output capture. An open descendant has no returned score or PV. |

**Fact.** Every ordinary search starts with empty remembered results and pawn
state, zero history/total and empty killers, even without `new`. Within one
search, root evaluation can populate pawn state before iteration one; depth
entry must preserve it. Root ranking/work, prior PV and prior score also do not
carry between independent searches. An abort leaves the played position
unchanged and the next search still begins fresh. Sources: [learned lifetime],
[pawn lifetime], [session lifecycle].

**Fact.** The branch-local pair contains subtotals, not the finished evaluation
score. A fast evaluation uses current material, square balance, identity,
phase/check/reversible count and the inherited pair to finish a new score; it
does not return a saved finished score. It adds no relation charge and does not
query/update pawn groups. Full evaluation replaces the pair and resets age.
Sources: [retained evaluation], [ordinary recursive iterations].

**Fact.** A scout followed by a full-window re-search reuses the same produced
child after the scout's branch-local evaluation changes. Rebuilding that child
from the parent's original pair is incorrect. The next distinct sibling does
inherit the unchanged parent. Shared learned/remembered/pawn changes from the
scout survive both retry and sibling return. Source: [ordinary recursive
iterations] under Candidate search and completion.

## 2. Ordinary recursive transition order

These are binding ordering dependencies, not proposed module boundaries.
Here P is search ply, D remaining depth, `(L,U)` the original incoming window,
and I the enclosing root iteration depth.

1. **Dispatch before charge.** If D <= 0, P = 63, or P reaches personality
   `md`, delegate to quiescence at target `max(0,P+D)` with the same window.
   Charge only its quiescence entry, not an ordinary entry plus a tactical
   entry. Preserve I; an IIO shallow target is not a new iteration depth.
2. Otherwise charge one search unit, including nodes that subsequently draw,
   hit remembered results, prune, or find no legal moves. Immediately service
   an eligible poll after crediting that unit, before inventing a return for
   the node.
3. Historical repetition precedes killer clearing and remembered lookup.
   A repetition draw returns zero with an empty PV and leaves killers alone.
   Otherwise clear both killers for P+1, then test endpoint reversal. Reversal
   returns zero only if U <= 0. Null descriptors never qualify as reversal,
   including two nulls; they still participate in historical repetition.
4. Query remembered results using the unmodified incoming window and target
   P+D. A usable bound-bearing score returns immediately. Retain the query's
   final bound kind, hint, marked depth and quiet-mate marker for later use.
5. Compute selective adjustment from I, `sel`, current endgame weight and
   target P+D. Perform the fast-evaluation request if [fast entry] admits it;
   the later cutoff's depth/check/score guards must not suppress an admitted
   request. A successful [fast cutoff] stores its adjusted score and returns.
6. Otherwise perform full evaluation and retain this node's refreshed pair.
   At P <= floor((P+D)/2), replace evaluator bounds with [-10000,10000].
   Save this effective pair for early bound tests, initial best and final
   clipping. Test lower >= U before upper <= L; return the bound itself.
7. If D <= selective adjustment, static score >= U and the node is not in
   check, attempt the specified shallow cutoff. At D <= 2, with predecessor
   not in check and no king-pressure guard, use material threat and subtract
   25 (D <= 1) or 40 (D = 2). Otherwise search a null transition at child ply
   P+1 and remaining depth D-3 for D < 6, or D-4 for D >= 6, window
   `(-U,1-U)`, previous extension zero. There is no further depth decrement on
   child entry. On success store and return the trial score.
8. Generate the complete legal candidate set. Empty returns P-10000 in check,
   else zero. For a nonempty set, return P-9998 when that reaches U, before
   ordering. These terminal returns do not perform normal-completion storage.
9. Apply exact ordinary ordering. Optionally perform the checking-mate probe,
   then initial IIO, main candidate search, and an eligible tail IIO phase.
10. Normal completion caps best at the saved effective upper bound, performs
    cutoff-memory update only if the result is strictly above incoming L,
    and stores with the original window, original target and specified hint/
    markers. It returns the retained PV independently of final clipping.

Sources: [ordinary recursive iterations], [draw boundary], [cached admission],
[fast entry], [fast cutoff], [selective depth]. Arithmetic in [selective depth]
has explicit signed-32-bit wrapping before division/comparison; use a dedicated
exact helper rather than algebraic simplification under mathematical integers.

**Fact: main loop.** Initialize best from the effective evaluation lower bound,
running lower from L, PV empty, preferred move from the remembered hint (or a
successful checking-mate probe). Derive each fresh extension and child depth
`D-1+freshExtension`. When that depth is nonpositive, an estimate <=
`max(best,runningLower)` is consumed without a child visit. Special/check moves
estimate 10000; other estimates are not universally clipped to 10000.

Use the full child window `(-U,-max(best,L))` for the first candidate, while
best has not exceeded L, and whenever both original endpoints are non-full.
Otherwise scout with `(-min(best+1,U),-best)` and re-search with `(-U,-best)`
when the negated scout result is >= best+1 and < U. The best/PV/lower updates
are nested strict comparisons: a score must strictly improve best before it
can update the preferred move or PV; the PV changes only when that improvement
also exceeds running lower and is below U. A tie preserves the earlier line.
Sources: [ordinary recursive iterations], [frontier estimate], [move extensions].

**Fact: checking-mate probe.** It can run only with the stated quiet marker,
check, path-half, target-margin and encoded-material guards. It scans ordered
ordinary non-promotions that give check, searches quiescence at target P+1
and child window [-9000,-8999], and stops at the first negated score >= 9000.
A found score reaching U updates cutoff memory and stores a marked, quiet-
checked result, **then ordinary main search continues**. Replacing this with a
terminal mate return changes required behavior. Source: [ordinary recursive
iterations] under Legal moves, ordering and mate probe.

## 3. Internal iterative ordering is real shared search

**Fact.** Initial IIO runs for D >= 4 when node-entry marked depth is absent
or < D-2. Tail IIO runs after exactly the first main child completes without
ending main processing, for D >= 5 and node-entry final exported bound kind
exactly `lower`, and only with an unconsumed suffix. An `exact` record with
lower permission is not a `lower` observation. A store later in the node must
not replace the retained entry condition.

Targets are P+D-20, P+D-18, ... P+D-2 after removing targets below P+2; execute
every remaining target. Every pass starts pass best -10000, uses original L/U,
and begins with the preceding pass's order. For each candidate produce a fresh
extension from the parent/predecessor/previous extension and complete candidate
sequence as it stands for the pass. OR extension flags into that candidate's
accumulated flags. Search at remaining depth
`shallowTarget+freshExtension-P-1`, supplying accumulated flags as the child's
previous extension, with window `(-U,-max(passBest,L))`.

Only strict improvement over both prior pass best and L promotes to the front.
Stable removal/front insertion preserves other candidates; already visited
entries are not revisited. Only that qualifying promotion reaching U closes a
pass early, and later shallow targets still run. Tail phases can reorder only
the unconsumed suffix. Main search derives a fresh extension for its depth;
accumulated flags affect the child's extension context, not that depth.

All ordering children are ordinary recursive searches: work, TT, learned
ordering, pawn groups and search history have their normal chronological
effects. Only candidate ordering and extension flags, rather than a fabricated
parent score/PV, emerge as the ordering result. An interrupted ordering pass
has no fabricated completed order. Source: [ordinary recursive iterations]
under Internal iterative ordering. The fixed-iteration diagnostic qualifies
only initial/single-target/zero-extension IIO; complete ordinary search still
requires the broader rules above.

## 4. Quiescence order and work cannot be approximated by legal captures

**Fact.** Quiescence always charges one entry unit and starts with an empty PV.
Perform the same ordered repetition/clearing/reversal stage. At P=63, return
the fast static score after that stage. In check, skip ordinary static
evaluation and generate legal evasions. Outside check, choose evaluation:

- Immediate full evaluation if both colors' normalized material measure
  `(N+B+R+Q+floor((N+R)/16)) mod 16` is <= 1.
- Otherwise fast evaluation, followed by full refresh if
  `L-250 < fastScore < U+250` or the preceding move meets capture exception.
  Classify the move from its parent board; an empty en-passant destination
  does not become an occupied-destination exception.
- Test lower-bound return, upper-bound return, then stand pat, in that order.
  Save evaluator upper bound for list completion. In-check initial best is
  -10000 and saved upper bound is 10000.

**Fact.** Non-check production is deliberately pseudo-legal: captures, en
passant, quiet queen promotions, and allowed quiet direct checks. It excludes
underpromotions, castling, quiet king moves, quiet pawn double pushes and quiet
discovered-only checks. Do not remove self-check moves yet. In-check production
uses the ordinary complete legal evasion inventory, including all promotion
choices, but ranks it with the **shared quiescence preference rule**, including
history for ordinary quiet/king evasions. Quiescence reads shared history but
does not learn new priorities. Sources: [quiescence tree], [quiescence
candidates], [candidate production].

Non-check candidate processing is ordered:

1. Exclude nonmaterial nonchecks; exclude nonrecaptures only when
   `P > target+I`. Preserve the enclosing I through all descendants.
2. Promotions/en passant become forced. Ordinary captures compute the capture
   allowance from actual material change and the selected signed retained
   contribution, then run capture policy. For policy threshold
   T=max(best,runningLower), destination support is consulted exactly when
   `P >= target+floor((I-1)/2)`, E > T, and E-V <= T. An unforced estimate can
   raise optimistic best without raising lower or changing PV.
3. Unforced candidates must check. A single checking route that is not a
   recapture requires <= 1 legal reply or a positive produced-child repetition
   count. Simultaneous direct+discovered checks bypass this reply restriction.
4. **Only now reject self-check.** Keep any prior optimistic best update.

For policy, an ordinary king capture uses attacker value **50**, not its
ordering value 1500, and has no king exemption. Non-king policy values use
fixed root material values without ordering's low-value adjustment. Capture
support uses evaluation influence, not legal attackers, and has zero direct
relation charge. Sources: [quiescence tree], [capture policy], [capture
allowance], [capture defense].

Recurse with negated `(-U,-runningLower)`; increment target only when the
parent was in check. A strict best improvement changes PV only strictly
inside the current window. An empty non-check tactical list returns standing
best without later clipping; an empty evasion list returns P-10000; a nonempty
evasion list can return P-9998 before ordering. Exhausting an entered nonempty
list returns min(best,savedUpper), preserving its PV independently. Rejected
candidates add no child unit, and production/ordering/support have no direct
search/relation charge. Source: [quiescence tree].

## 5. Exact shared memories

**Remembered results — facts.** [Remembered results] is not a conventional
single-entry exact/lower/upper transposition table:

- G is the largest prime <= floor(`tts`/48). Group is the nonnegative 32-bit
  `primary XOR ((E*256) OR (F*65536))` modulo G; E is zero or 10*EP-rank+EP-file
  using zero-based rank/one-based file; F includes White-to-move 16 and rights
  WQ/WK/BQ/BK = 1/2/4/8. Identity within group is `secondary`.
- Each group has three depth-retained priorities and one recent/displaced
  result. Priority slots retain tie precedence across replacement. Equal-depth
  new identities displace the first least-depth priority. Existing retained
  identity + shallower depth writes recent only; equal/deeper replaces retained
  without clearing an older recent duplicate.
- Query matching recent first, then matching retained only if no usable recent
  score. Metadata can combine: non-null hint overwrites, quiet marker ORs,
  marked depth takes maximum. Final exported bound kind comes from the **last
  considered matching record**, not a permission union.
- A stored score has lower permission iff S>L and upper permission iff S<U.
  An exact interior result with sufficient depth supplies **no score**; only
  a permitted window cutoff is usable. A hint keeps source/destination only;
  it loses promotion and kind, unlike killers.
- Mate scores normalize at inclusive +/-9000 using store/query ply. A mate
  cutoff can bypass insufficient depth and increase stored depth. The query's
  marked-depth observation precedes that increase. Query is therefore mutable.
- Stores and queries have zero direct behavioral work charges. Early draw
  prevents both lookup and mate-depth mutation. Fast/shallow cutoffs, mate
  probes and normal completion have distinct store/marker rules; several early
  returns store nothing.

Source for board-derived keys and store callers: [ordinary recursive
iterations]; record semantics: [remembered results].

**Learned ordering — facts.** History has 768 color/type/destination keys and
a separately retained total. An eligible update requires an empty destination
before moving, so en passant, castling and quiet promotions qualify; occupied
promotion captures do not. Increment by `8*(remainingDepth+1)`, using the
prepromotion pawn type. When total becomes >10000, ceil-half each entry and
recompute total. Killers are full descriptors keyed only by ply. A new move
usually replaces second, repeat-second promotes to first, and repeat-first
still increments history. Nonrepetition entry clears P+1; current and P-2
killers feed ordinary ordering. Sources: [cutoff memory], [repetition admission].

**Pawn groups — facts.** There are exactly 128 retained groups, each initially
identity zero and empty structure. Equality of full pawn identity reuses the
record, including its original descriptor order, even for distinct colliding
pawn placements. Pawnless zero identity therefore reuses the initially empty
record; an initially-invalid flag would change this. A miss replaces only the
selected group, computing structural descriptors with doubled-pawn
coefficients 1024; current penalties/activity/candidates remain downstream
work, not cached final pawn scores. Source: [retained pawn structure].

**Ordering — facts.** Preserve piece chronology and exact legal/tactical
generation order. Ordinary priority categories and unsigned wrap are specified
first-applicable rules. Preferred priority >1 entries start in reverse
generation order; priority 0/1 entries remain deferred in original order.
Preferred sorting is not a generic stable sort: [priority sequence] first
stably sorts the six index-modulo-six classes, places each class back into its
positions, then stably sorts the combined sequence. Equal priorities can
therefore permute in mixed lists longer than six. Root score ranking instead
uses stable descending insertion with visit-order ties. Sources: [candidate
order], [candidate production], [quiescence candidates].

## 6. Root flow, polls and output ownership

**Fact: root flow.** Generate every legal root in natural production order;
initial root generation is not ordinary non-root ranking. Empty root means
fatal exit 1, with no successful post/move/result and no accepted search seed.
For a nonempty root acquire one seed per search, including rnd=0. Randomization
is a deterministic seed+descriptor function; retries do not advance a stream.
It transforms each root window before child search and the negated child
return before ranking, preserving mate/sentinel values and ordinary clamping.
Sources: [joined search], [root outcome], [root randomization].

At each iteration start freeze unrestricted/restricted policy from cumulative
SearchID <25000 / >=25000. Reset current numerical best/second/PV/ranking.
Unrestricted roots use second-ranked completed score (or -10000) as lower,
10000 as upper; first two therefore use full windows. Later results do not
reorder unvisited roots in the same iteration. Restricted first root is full
window; after it completes, pin it and stably sort remaining roots by retained
prior work descending. Later roots use exact [root aspiration], including
ordinary-score addition near mate boundaries, one retry on equality/exceeding
initial U, and the returned-versus-ranking two-point rule. Both attempts add
work; unused retry contributes none. Complete score ranking, with carried work
attached to each candidate, supplies next depth's incoming order. Sources:
[root work schedule], [unrestricted roots], [restricted roots].

**Fact: clock and event ordering.** N is charged search work; R is charged
unadjusted relation queries, not physical attack-map operations or a generic
node counter. An equivalent fused implementation must still charge the
specified logical events, including repeated required queries, and suppress
queries behind guards. Table/order/support arithmetic is zero direct charge.
The clock uses
`min(2147483647,floor((3806*K(N)+770*R)/30000000))`, with K(N)=N through
2147483647 and 2147483648 thereafter. Add retained origin modulo 2^32; observed
words have signed formatting. Reset carries **last observed** clock only,
clears segment counts and drops unobserved work/fractional remainder. Root
preparation is outside the new iterative work segment. Sources: [work clock],
[session lifecycle], [evaluation relations].

Immediately after a unit makes cumulative SearchID a positive multiple of
4096, perform a poll. Roots/retries/iterations do not restart the schedule;
relation queries advance time but not polls. Credit the unit first. A poll
stop preempts child completion even if it is the last otherwise-needed unit.
Maximum allowance governs natural poll stopping; adaptive root/iteration
limits are separate. Consume at most one available complete host line per
poll, in arrival order. Required ordinary commands include `?`, `force`, `.`,
post toggles, active `time`, inert `otim` and `easy` under the host scope.
Sources: [work-timed roots], [session lifecycle], [interrupted sessions].

For a restricted first completed root, score-drop adjustment runs before
best-change adjustment. On a new ranked best, apply best-change behavior,
capture the completed result and optionally publish, then root-time check.
A root-time stop includes that root and skips remaining roots/iteration
checks. After a fully completed unrestricted iteration whose total has reached
25000, easy-adjust current limits; restricted iterations do not apply it.
Then time/terminal completion checks use the specified order. Depth-one
root/iteration time checks do not read the clock, while maximum polls still
apply. Terminal rules include personality `md` and the independent D>61
ceiling; recorded `sd`/`st` do not replace ordinary limits. Use exact binary64
coefficients and rounding, not rational substitutes for 0.666/0.333. Sources:
[timed roots], [adaptive time], [iteration terminal stop].

**Fact: interruption.** Never return a fabricated score/PV, insert a completed
ranking entry, promote an incomplete IIO result, capture or learn from a
nonexistent return. Already charged work and already completed shared updates
survive. Unwind the open path to its current root; retain the last eligible
completed-root capture, which may be older than the latest completed root or
current iteration. Natural poll stop with no completed result has the precise
initialized first-root fallback: zero report fields, one-move first-generated
PV. It applies only with the required first-root owner and no prior capture;
diagnostic exhaustion, generic failure and abort do not use it. `force` plays
no move and publishes no new completion post. Live status renders current
exploration, including null, rather than retained best PV, and its complete
path does not use the post's byte truncation. Sources: [joined search],
[interrupted sessions], [session lifecycle].

**Fact: publication.** Capture copies metadata and PV together. Depths 1/2
defer, >=3 publish eligible captures immediately; do not deduplicate identical
events. Successful finish emits the deferred capture only if no capture was
already published, subject to post selection/lifecycle. Finish work must not
replace its SearchID/clock. Report normalization is separate from ranking:
ordinary score removes root draw preference and clamps to [-7900,7900],
mate/sentinels remain. Render notation from the root and captured coordinate
PV, applying each post's numeric-prefix-derived complete-token byte boundary;
display truncation cannot change selected coordinate move or captured line.
Sources: [post lifecycle], [output score], [PV notation].

## 7. Proposed efficient unified search state

The following is a proposal, not a claim about any existing implementation.

### A. One search owner with fixed context and reusable storage

Use one search owner containing immutable root context, canonical counters and
adaptive controller; small learned/pawn stores; reusable remembered-result
slab; root arrays; a 64-ply frame/scratch allocation; and separate retained
capture. Keep session/game history outside it. Start a new logical search by
resetting mutable search ownership and constructing root context once. Reuse
physical allocations across searches without reusing logical content.

Use packed full move descriptors throughout generation/search/PV/killers so
promotion and kind survive. Use a separate endpoint-only hint representation
for remembered moves. Avoid coordinate strings, maps and heap vectors per node;
format strings only at diagnostic/public observation boundaries. Retain exact
semantic piece chronology in the position representation chosen by the main
architecture, rather than deriving move traversal from arbitrary bit order.

### B. Split small frame control from board and scratch storage

Start with native recursion and explicit indexed per-ply storage, returning
`Complete(score,line)` or a distinct interrupted outcome. Do not implement an
explicit interpreter merely to get interruption: a typed outcome propagated
through all callers can unwind while retaining already committed shared state.
Ply is bounded; ordinary/quiescence handoff is a dispatch, not an extra frame
with another charge. An explicit frame machine remains a measured alternative
if recursion spills, duplication or status ownership become costly.

Keep small node control separate from large, colder buffers. A node frame
needs original window, depth/target/iteration context, retained evaluation
pair+age, saved bounds/static score, entry remembered metadata, best/running
lower/preferred move, candidate cursors, IIO phase/pass state and PV length.
Keep mutable retained evaluation state in the child position/frame, so the
same child can be re-entered for scout retry without resetting it.

Use either in-place board make/unmake with compact undo or a compact per-ply
board copy, according to the position architecture's measurements. Both can
satisfy the semantics. In either case, restore branch-local board/evaluation
state on all completed/interrupted paths; never roll back shared TT/history/
pawn memory. Preserve the current path in indexed move/history slots for
repetition and live status. Killer storage needs P+1=64 clearing even though
ordinary expansion ends earlier: allocate indices through 64 explicitly.

### C. Candidate buffers and PVs

Keep one reusable candidate segment per active ply, with packed moves,
unsigned ordering priority scratch and per-candidate accumulated extension
flags. A split layout avoids loading priority/flags in paths that do not use
them; a compact interleaved entry may win when IIO is active. Measure both.
Operate on ranges of the same segment for full-list/remaining-tail ordering;
metadata must move with identity. A cursor plus stable front insertion avoids
visited sets in an IIO pass: moving the current element to the front shifts
only the visited prefix, leaving the next unvisited position unchanged. Preserve
the complete inventory needed for extension decisions alongside the active
range; do not infer complete-node counts from a shortened tail accidentally.

The portable component maximum 230 is not by itself a new production maximum.
An inline capacity such as 256 is a proposal: establish a valid production
bound from position admission, or provide a cold growable overflow segment.
Never silently truncate. A 64-ply move/priority/flag allocation is on the order
of hundreds of KiB, so it should be allocated once, not copied wholesale at
node entry or embedded into hot control frames.

Use fixed-capacity per-ply PV slots and lengths; strict PV replacement copies
only the selected child's actual line. A triangular array can avoid storing
impossible long suffixes. Empty entry PV must be explicit even for early
returns. Root retained capture owns an independent line copy, so later scratch
reuse cannot mutate it. Diagnostic full traces should be opt-in observers
outside the default hot path; production must not materialize every diagnostic
evaluation/entry record merely to search.

### D. Memory layouts and reset cost

History is a flat 2*6*64 array plus total, and killers a flat array of descriptor
pairs. Both are small enough for straightforward clearing. Pawn groups can be
128 inline records with full identity, base structural scores and ordered
compact descriptors. A hit must preserve stale/colliding descriptor order;
downstream current-membership checks remain necessary. Do not add a generic
valid-bit rule that changes zero-identity reuse.

A candidate remembered-result layout is four 12-byte records per 48-byte
logical group: secondary identity, normalized signed score, signed depth,
endpoint hint and permission/marker/valid flags. Use sufficient signed depth
width for ordinary targets extended beyond a component transport's limit; do
not assume the diagnostic target<=64 bounds all production stored depths.
Three slots preserve fixed retained precedence and the fourth recent role.
Verify actual layout with compile-time size checks when implementing. Aligning
groups to 64 bytes is a measurable alternative with higher footprint, not a
behavioral requirement. G still derives from `tts/48` regardless of the
physical layout.

Avoid clearing a default-sized remembered slab eagerly for every short search
without measuring it. Logical generation tags in a side array or a touched-
group list can make reset proportional to used groups. First store in a fresh
group materializes empty retained slots and empty recent; first query observes
empty. Handle generation wrap with a real reset. Keep this mechanism distinct
from the pawn table's required zero-identity match. Profile full allocation/
reset/destruction cost as well as the inner loop; relocating setup is not a
performance saving under complete-lifetime accounting.

### E. Charge and poll at semantic boundaries

One tiny charged-entry operation increments SearchID and tests its low 12 bits,
calling a cold poll handler only on a positive boundary. A poll returns
continue/graceful stop/abort distinctly. Propagate stop before any completion
logic. Do not scatter an extra charge across cached/draw/mate branches or
charge generated moves. Relation accounting may batch a region only where
there is no intervening clock/trace observation; preserving physical helper
calls is unnecessary, preserving charged logical queries is mandatory.

Compute clock division only on required observations, not every relation or
entry. Keep N/R canonical and use wide enough intermediates for the ledger's
saturation and diagnostic integer domains. Separate current work from the last
observed snapshot, since reset and fine-work formatting consume the latter.
Do not maintain only an eagerly rounded elapsed counter. The uncommon poll/
command/output path can be cold; required adaptive/root/capture observations
remain explicit and ordered.

Root arrays should separate immutable candidate identity, carried work and
iteration score from visitation/ranking index lists. Stable insertion is
appropriate for small root prefixes and avoids sorting the unvisited suffix.
Snapshot candidate-start SearchID for carried-work deltas; retries add to the
same candidate owner. Keep root attempt, completed ranking and retained output
capture as different state objects so a poll cannot turn a partial attempt
into a completed result by mistake.

## 8. Early integrated measurement with bounded fidelity

The mission favors early complete pipelines. These milestones allow that
without disguising omitted semantics as conformance.

1. **Executable first iteration.** Integrate setup/history, chronology, complete
   natural roots, fixed root context/full root evaluation, actual quiescence,
   branch restoration, ranking/PV and canonical N/R. Run [first iteration] and
   [quiescence tree] fixtures rather than only a scalar best-move check. Permit
   a clearly labeled private prototype evaluator while integration is first
   being assembled, but never compare its different tree/work as equal-work
   KingRE performance. Replace it with the specified evaluator before claiming
   the released fixed-work benchmarks.
2. **Measured ordinary depth 2/3.** Add the complete ordinary entry/TT/evaluation/
   cutoff/main-loop/extension/learning path and strict sibling/retry ownership.
   Target the three released functional search units: selected-A start depth
   two, neutral start depth three, and neutral 15-ply opening depth three.
   Their projections include every final-iteration root result in visitation
   order, final score/PV and exact work. Keep full fixture output checks beside
   the smaller benchmark projection. At this stage say which IIO branches,
   clock modes and personalities are absent; do not infer them from depth
   three success.
3. **Broader fixed search.** Add initial IIO and prove the released depth-five
   cases, then full tail/multipass/extension-accumulation rules. Add focused
   tests for exact-interior TT nonreturn, recent/retained combined metadata,
   mate-depth mutation, quiescence self-check estimate effects and scout child
   retained-state reuse. These test semantics that ordinary chess tests miss.
4. **Timed/session closure.** Integrate actual work clock, all positive-4096
   polls, frozen late root policy, aspiration/randomization, adaptive/terminal
   stops and capture/publication. Validate open-child interruption, no-result
   fallback, force abort, status/null path and same-session fresh-search resets.
   Then run the released 54 production profiles, persistent selected-game
   route and continuous switching controls as applicable. A component or
   projected benchmark pass is not production qualification.

For every measured search, retain exact source/build/executable identities,
input and output-check status, wall and user/system CPU boundaries, N/R at
their true owned boundary and PMU availability. Retired instructions diagnose
work, cycles and CPI diagnose execution, CPU time decides whole-engine cost.
Report inner search and complete fresh-search lifetime separately; allocation,
preparation, reset, observation and destruction remain visible. Do not infer
terminal N/R from a final post, sum overlapping component costs, or average 23
unlike functional units into a headline engine result. Sources: [functional
workloads], [functional metrics], [performance acceptance].

The companion's whole-engine target is KingRE, with separate 54-search and
12-game collections, aggregate CPU-cost limits 1.10 and individual guardrails
1.25; its optimization target remains <=1.00. A frozen valid uncertainty/
measurement profile is required before calling a result qualified. Hardware
calibration and early mismatched-fidelity prototypes remain diagnostic, not
substitutes for matched behavior or final acceptance.

## 9. Initial architecture critique: choose the smallest ownership mechanism

This section refines the proposals above. It does not prescribe the main
architect's board/evaluator representation or claim measured speed.

### Recommended first version

Use native recursion, one reusable position slot and one invocation-control
slot per ply, packed in-place candidate rows per ply, fixed PV rows, and a
single shared ordering workspace. Preserve the distinction between position
state and invocation state even if they occupy adjacent fields in one physical
frame. Avoid an explicit resumable interpreter, linked candidate lists,
immutable position trees and per-return owned PV vectors in the first version:
their extra mechanisms have no demonstrated benefit for this bounded search.

The fundamental child sequence is:

1. Produce child position/history and inherited evaluation pair once.
2. Initialize its invocation control and empty returned-PV length; run scout.
3. On completion, keep the child's evaluation pair/age and board state while
   resetting invocation control/PV for an eligible full-window retry.
4. On candidate completion or interruption, restore parent branch-local state.
   Leave shared memories and charged counters alone.

For IIO, a later ordering pass is a new candidate visit, not that scout retry:
produce its child from the unchanged parent again, carrying shared-state
history and the candidate's accumulated extension flags. Main visitation does
the same. Do not retain one descendant evaluation pair per candidate across
all IIO passes: only the same-child scout/re-search case requires its special
reuse lifetime. The retained entry TT observation and accumulated flags already
provide the additional state that IIO requires.

The recursive return can contain only status plus score; its PV lives in the
child's indexed row. Copy that row into the parent's row on the specified
strict improvement. An interrupted status makes the score and row unavailable
to completion logic. A distinct tagged result is easier to audit than a
sentinel integer that could accidentally enter negation, comparison or TT store.
Polling needs no continuation after a graceful stop: ordinary thinking ends.
After unwind, retain only the selected output capture or initialized fallback.

### Shared priority scratch is sufficient

The numeric priorities and permutation workspace are needed while ordering the
current node, before any child recursion. Once its candidate row has been
permuted, ordinary main search and IIO use the row order/flags, not the original
priority vector. Quiescence likewise consumes its completed order without
needing those priorities again. A child can therefore overwrite the same
workspace. Initial/tail IIO use actual child returns and in-place promotions;
they do not require retaining ordinary priority scratch across a recursive call.
The checking-mate scan also begins after ordinary ordering is materialized.

This removes the reason to keep a full priority array in every frame. The
workspace must not be borrowed by a deferred iterator across recursion. Helpers
that temporarily generate legal replies for tactical eligibility must use an
explicit temporary range/workspace, rather than overwrite the current node's
retained candidate row. If helper nesting exceeds one scratch lifetime, give
that helper a second small workspace; do not restore a large per-ply priority
allocation by default.

### Concrete storage budget

These are proposed capacities and arithmetic, not production admission limits
or measured compiler layouts. They exclude positions/undo, evaluator maps,
pawn descriptors, session history and the remembered slab.

| Storage | Simple proposed representation | Bytes |
| --- | --- | ---: |
| Per-ply candidates | 64 rows * 256 entries * 4-byte packed candidate | 65,536 |
| Ordering workspace | 256 u32 priorities + 256 u16 indices + 256 u32 reorder temporary | 2,560 |
| Full fixed PV rows | 64 rows * 64 moves * 4 bytes + 64 byte lengths | 16,448 |
| Invocation controls | 64 slots at a target 96–128 bytes each | 6,144–8,192 |
| History and total | 768 u32 scores + u32 total | 3,076 |
| Killers | 65 pairs of 4-byte descriptors | 520 |
| Current path | 64 full descriptors | 256 |
| Retained output line | 63 full descriptors, excluding metadata | 252 |
| **Listed total** | With full PV rows and 96–128-byte controls | **94,792–96,840** |

A descriptor needs 6 source bits + 6 destination bits + promotion/kind bits;
three accumulated IIO extension bits can fit in a 32-bit candidate entry
without changing semantic move identity. Mask candidate-only metadata when
comparing moves or copying into killers/PV. This avoids an 8-byte padded
`move+flags` entry, which would double the candidate rows. Do not conflate a
queen promotion with an endpoint-only remembered hint.

A triangular PV allocation with capacities 63,62,...,0 has 2,016 moves, or
8,064 bytes plus 64 lengths, saving 8,320 bytes versus the simple full rows.
Its indexing and line-copy bounds are more complex. Start with full rows unless
an early whole-search measurement shows this footprint matters; both avoid
per-node allocation, and neither entails copying unused capacity on entry.
Candidate rows and frame controls are touched only at active plies, not scanned
in their entirety on every node.

A control-slot target around 96 bytes is plausible: eight 32-bit numeric
working values consume 32 bytes; entry TT observations, preferred/current move,
depth/target/extension context, range cursors and IIO phase/pass state fit in
the remaining budget with explicit alignment. Treat this as a size target to
verify, not a reason to compress arithmetic unsafely. Native recursion may keep
some values in registers or its own stack; writing every field eagerly into an
indexed frame as well can duplicate work. Only fields needed after a child,
for status, or for exact ownership should have persistent storage.

### Main pitfalls to test before freezing this design

- A blanket frame reset at each search call destroys scout-produced retained
  evaluation state. Conversely, retaining best/window/PV across retry reuses
  invocation state that must start fresh.
- One global candidate row fails under recursion; one global ordering scratch
  can be safe after materializing each node's order. Keep those different.
- One returned-PV slot shared across all plies lets a later child overwrite the
  parent's retained best. Per-ply rows plus a separate root capture prevent it.
- Array front promotion must move accumulated flags with the move, preserve
  the unvisited suffix, and restrict tail promotion to its range. Never restart
  a pass at the front after a promotion.
- Recomputing an extension for main depth must not substitute accumulated OR
  flags as the numeric depth extension. Preserve fresh and accumulated values
  separately at the call boundary.
- A mutable-board implementation must restore placement, chronology, rights,
  EP, counters and parent retained evaluation on every exit, while preserving
  search-shared changes. A full search snapshot/rollback would undo too much.
- Full-line memcpy on every child return, eagerly clearing every PV row, or
  serializing trace objects in default search wastes work; length reset and
  conditional line copying are sufficient.
- Candidate capacity and stored depth widths need production bounds. A
  convenient diagnostic limit cannot silently become a search truncation.

The first useful experiment is a fixed-completion depth-three search with
exact final root results/PV/N/R, comparing these simple rows/native recursion
against any proposed alternative under identical builds and complete setup
cost. Change one storage/dispatch choice at a time. Until that integrated
baseline exists, the extra complexity of a frame interpreter or arena of
individually owned nodes has no evidence supporting it.

[ordinary recursive iterations]: ../../../king-spec/spec/ordinary-iterations.md
[joined search]: ../../../king-spec/spec/ordinary-joined-search.md
[session lifecycle]: ../../../king-spec/spec/ordinary-session-lifecycle.md
[learned lifetime]: ../../../king-spec/spec/learned-state-lifetime.md
[pawn lifetime]: ../../../king-spec/spec/search-pawn-lifetime.md
[retained evaluation]: ../../../king-spec/spec/retained-evaluation.md
[draw boundary]: ../../../king-spec/spec/draw-boundary.md
[cached admission]: ../../../king-spec/spec/cached-admission.md
[fast entry]: ../../../king-spec/spec/fast-entry.md
[fast cutoff]: ../../../king-spec/spec/fast-cutoff.md
[selective depth]: ../../../king-spec/spec/selective-depth.md
[frontier estimate]: ../../../king-spec/spec/frontier-estimate.md
[move extensions]: ../../../king-spec/spec/move-extensions.md
[quiescence tree]: ../../../king-spec/spec/quiescence-tree.md
[quiescence candidates]: ../../../king-spec/spec/quiescence-candidates.md
[candidate production]: ../../../king-spec/spec/search-candidate-production.md
[capture policy]: ../../../king-spec/spec/quiescence-capture-policy.md
[capture allowance]: ../../../king-spec/spec/quiescence-capture-allowance.md
[capture defense]: ../../../king-spec/spec/quiescence-capture-defense.md
[remembered results]: ../../../king-spec/spec/remembered-results.md
[cutoff memory]: ../../../king-spec/spec/cutoff-memory.md
[repetition admission]: ../../../king-spec/spec/repetition-admission.md
[retained pawn structure]: ../../../king-spec/spec/retained-pawn-structure.md
[priority sequence]: ../../../king-spec/spec/tactical-capture-order.md#order-priority-sequence
[candidate order]: ../../../king-spec/spec/search-candidate-order.md
[root outcome]: ../../../king-spec/spec/root-go-outcome.md
[root randomization]: ../../../king-spec/spec/root-randomization.md
[root aspiration]: ../../../king-spec/spec/root-aspiration.md
[root work schedule]: ../../../king-spec/spec/root-work-schedule.md
[unrestricted roots]: ../../../king-spec/spec/unrestricted-root-sequence.md
[restricted roots]: ../../../king-spec/spec/restricted-root-sequence.md
[work clock]: ../../../king-spec/spec/work-clock.md
[evaluation relations]: ../../../king-spec/spec/evaluation-relations.md
[work-timed roots]: ../../../king-spec/spec/work-timed-root-sequence.md
[interrupted sessions]: ../../../king-spec/spec/interrupted-sessions.md
[timed roots]: ../../../king-spec/spec/timed-root-sequence.md
[adaptive time]: ../../../king-spec/spec/adaptive-time.md
[iteration terminal stop]: ../../../king-spec/spec/iteration-terminal-stop.md
[post lifecycle]: ../../../king-spec/spec/post-lifecycle.md
[output score]: ../../../king-spec/spec/output-score.md
[PV notation]: ../../../king-spec/spec/pv-notation.md
[first iteration]: ../../../king-spec/spec/first-iteration.md
[functional workloads]: ../../../king-spec/performance/functional-workloads.md
[functional metrics]: ../../../king-spec/performance/functional-metrics.md
[performance acceptance]: ../../../king-spec/performance/acceptance-policy.md

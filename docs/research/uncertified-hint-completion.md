# Uncertified endpoint hint at ordinary completion

Status: unresolved conditional composition/admission gap,2026-10-18. This is not
a demonstrated reachable engine defect or an admitted direct diagnostic case.
The exact released-contract and own-source review hashes plus specification-only
consultation are in `evidence/spec-empty-source-hint-20261018/`.

SEARCH-ORDINARY-ITERATIONS initializes best from the saved effective lower
bound and preferred from the remembered endpoint hint. A strict child best
improvement above running lower replaces preferred. Normal completion caps
best by the effective upper bound, then invokes SEARCH-CUTOFF-MEMORY when the
result exceeds incoming L, using the final preferred move. This control flow
is represented in `ordinary.rs`.

A conditional state worth resolving has L < effectiveLower < U, no usable
cached score, a non-null uncertified hint, no replacing quiet-mate preference,
and no main candidate score strictly above the initial best. If completion
still has capped best > L, the existing hint can reach the learned-state
consumer without having matched a generated legal move. A hash identity/group
collision is one possible concern; no public reachable witness establishing
all these premises together has been produced.

A later source proof narrows this condition. If effectiveLower <= L, any
completion learned update with final best > L must first have crossed L through
a strict improvement by a generated candidate, replacing the inherited hint.
A preceding quiet-mate replacement is also generated. Thus the empty-source
inherited hint is excluded in that region. In first-half nodes the effective
lower is -10000, so this exclusion applies conditional on incoming L >= -10000;
the wider normalized-score bound alone does not prove that caller-window premise.
In second-half nodes the quiet-mate probe is automatically disabled. The open
branch therefore requires effectiveLower > L and every consumed candidate score
<= effectiveLower, along with an actually reachable uncertified empty-source
hint and the earlier admission gates. Recent/retained metadata can carry a
nonnull hint without a usable score even at sufficient marked depth; metadata
does not supply a provenance proof. See the [bounded reduction](../../evidence/uncertified-hint117-reduction-review-20261018-score-context/review.md).

SEARCH-REMEMBERED-RESULTS explicitly does not certify hint legality.
SEARCH-CUTOFF-MEMORY states that a non-null move with empty destination updates
killers/history, with history keyed by the moving piece's color/type. It gives
no moving-piece interpretation for an empty source. Its direct diagnostic
inherits SEARCH-CANDIDATE-ORDER's candidate source occupancy/side condition;
remembered hash/killer descriptors can fail that condition. Therefore an
empty-source cutoff event is outside the direct cutoffMemory diagnostic domain,
and creating such a component test would not resolve composed-call admission.

The current native empty-source guard prevents indexing an absent piece. It
is not evidence that skipping every update is the specified composed behavior.
No pawn/color fallback, legality certification, suppressed update or other new
rule was inferred or adopted in this review. Imp1's consultation used only the
released contracts and public domains, with no implementation/source findings
or engine runs; it confirmed this interpretation gap without proving reachability.

Closure requires either a public reachable input producing the composed state
and authority clarification of its behavior, or a justified proof that this
state is excluded by the full production contract/invariants. Keep the
production review obligation open. Existing finite replay success and direct
component eligibility tests do not close it.

## 2026-10-20: smaller conditional completion certificate

A source/spec review, independently checked by the lead, discharges the
candidate-score premise for one sparse family. It does **not** establish a
reachable collision, close this gap or change the guard's behavioral authority.
No engine execution or implementation accompanies this result.

Let P have exactly a king and one minor of each color, no other pieces. Require
P unchecked, at least two legal moves, no legal move giving check, arrival by a
noncapture and no entry repetition return. At ply2, remaining depth1, take an
incoming window `L<0<U`, an admitted depth limit and no interruption. Suppose
actual lookup supplies H without a score.

Both insufficient-material endpoint assignments apply. The current phase is
endgame256, so FULL returns score/lower/upper all zero, independently of root
variation. Capturing either minor preserves the zero endpoints. Ordinary's
fast gate fails for these inventories; shallow cutoff fails because0<U.
Effective bounds remain0/0 in this second-half node. Quiet-mate and IIO gates
are disabled at this ply/depth. These facts follow from
[endgame adjustment](../../src/endgame.rs), [evaluation selection](../../src/evaluator.rs)
and the [ordinary policy](../../src/ordinary_policy.rs).

Fresh extensions are zero: the position is neither checked nor sole, the
combined two-minor inventory is not the single-piece sparse class, the preceding
move was noncapturing and there are no pawns. Searched children enter noncheck
Q at depth0 with upper boundary0. Sparse evaluation is FULL and its lower
bound0 returns immediately. A consumed frontier estimate is at most current
best0 by its admission test. Thus all consumed main scores are at most0;
best stays0 and never replaces H. Completion caps to0, exceeds L and invokes
learning with H. Requiring both H endpoints empty in P gives the unresolved
consumer condition.

One possible certificate to seek is iteration3 of one admitted, fresh,
fixed-iteration four-piece search. Its first root move a reaches Q at ply1/depth2
and must finish at zero with a generated H. Its second root move b reaches B at ply1/depth2; B's first
ordered reply c reaches a P satisfying the conditions above. The first two
root children have the full window; B is first-half, so its first reply also
gets that window. This route needs no extreme randomization or separately
supplied TT contents.

Q and P must actually have the same secondary identity and the same selected
conflict group, including side/rights/EP in group selection. Q's interior exact
zero record can export H without a usable score even at sufficient depth.
Q's completion store is immediately before B; B makes no store before its first
reply on the proposed sparse/full-window route. Matching recent/retained
selection still needs verification.

What remains is a complete admitted root/history, actual root/reply ordering,
legal a/b/c, Q's zero completion and H, the two numerical identity equalities,
P's empty endpoints, and all enclosing admission/entry gates. The released
permission for collisions does not prove that such a tightly constrained pair
exists. Use the chosen operation's actual table size and lifecycle; a synthetic
one-group table or a record preloaded by a separate search is insufficient.

This is a local sufficient-condition proof and a shorter search recipe.
Universal first-half caller-window exclusion remains conditional as above.
No public witness, newly specified fallback or final production closure follows.

## 2026-10-20: noncapturing sibling route excluded

One bounded, engine-independent enumeration completed for the subroute where
a, b and c are all ordinary noncaptures. It found **zero secondary-key
equalities**, across all eight profiles (root color × own N/B × opposing N/B)
and 1,526,240 index probes. All profiles completed; actual exit0, empty stderr,
no retry and unchanged helper/README hashes were independently checked by the
lead. This excludes the represented subroute before primary-group equality,
legal placement, ordering or hint selection need consideration.

For a/b moving the same piece from r to x/y, cancellation reduces secondary
equality to `S(own,x) XOR S(own,y) = delta(opponent,u,v)`. Every ordered x/y
with a common geometric predecessor is represented. For different root pieces,
enumerate each directed king edge and minor edge and match the XOR of their
deltas to an opponent king/minor edge; preserve both a/b assignments.
Both opponent directions and duplicate deltas remain in the index. K/N/B
directed empty-board edge counts are 420/336/560. Blockers, stationary-piece
placement and check constraints are relaxed, so a completed zero in this
superset is a valid exclusion. The implementation translates the published
key generator directly; no random-key or collision-probability assumption
is used.

The original recipe did not forbid **a capturing the opposing minor**. That
branch is outside this enumeration; the separate completed capture check below
addresses it. Other
inventories, earlier-iteration hints and different branch shapes also remain
outside the exclusion. The conditional score lemma and general composition
gap remain unchanged.

Exact frozen supports are in
`/home/legolas/agent-memos/rook2-hint-collision-feasibility-20261020/`:

- `collision_feasibility.py`: SHA256
  `2ef9e2053e980f77ff6aaf74b81b4d31146063283e7aedc63055ba3dfadc15f6`;
- `README.md`, the pre-run coverage/resource proof: SHA256
  `fc35a3c1daaa2d3f2211b0a3ddf6f4a9d5b282627012d27a64737570e7072dfe`;
- `result.json`: SHA256
  `75c70eb65e23905ca1f88f4d10ea293d7ebc4f0e58a2fcaac3b06e78a528f4a2`;
- `exit-code.txt`, `run.stderr` and identical before/after source hashes.

The pre-run source and README retain their original unexecuted wording.
The result and actual terminal establish execution. The one run used
housekeeping CPUs after the TT census quiet window closed, with 45-second wall,
28/30-second CPU, 128MiB address-space and 8,000,000 joined-edge limits.
It invoked no engine or fixture evaluator and changed no production behavior.

## 2026-10-20: direct ordinary root children are excluded

The lower-window premise can be discharged for actual direct root children
without proving a global score range or strict windows. This is a source
composition result for normal fixed/seeded/timed search, not for arbitrary
supplied Request values or controlled child-answer providers.

In fixed search, the ply1 request has lower=-10000. Seeded fixed search uses
`-A(10000,-adjustment)`, also exactly -10000, because ordinary-score addition A
preserves the mate/sentinel band. See
[fixed/seeded root execution](../../src/ordinary.rs#L591).

Timed root execution uses `child.lower=-A(requestedUpper,-adjustment)`.
The unrestricted and retry requested upper is 10000. Restricted aspiration uses
`A(min(10000,max(best,previous)+1),2)`, which is at most 10000. For any supplied
value at most 10000, A preserves that upper enclosure: ordinary-band values
are clamped to 8999 and other values are unchanged. Therefore every actual
timed root child has lower>=-10000, independently of whether the requested
window is strict, collapsed or inverted, and without assuming returned scores
are genuine mates or bounded by 10000. The previously accepted arithmetic
capacity premises still apply. See [score addition](../../src/timed.rs#L193),
[root scheduling](../../src/root_schedule.rs#L121) and
[actual child execution](../../src/timed.rs#L620).

A direct root child has ply1 and target equal to the root iteration. If it
does not immediately hand off to Q, remaining depth is positive, hence target
is at least 2 and it is in the first-half region. Its effective lower is thus
-10000<=incoming L. The earlier strict-improvement lemma excludes inherited,
unreplaced H at any normal completion that invokes learning. A preceding
quiet-mate replacement is also a generated move. Root retries preserve these
facts. This closes the empty-source inherited-hint route at these ply1
ordinary completions; it does not certify the legality of arbitrary remembered
hints at other consumers.

The fixed-root request, effective-bound substitution and strict-improvement
rules also appear directly in SEARCH-ORDINARY-ITERATIONS at lines121–130,
208–219 and378–429. Timed composition follows SEARCH-ROOT-ASPIRATION and
SEARCH-ROOT-RANDOMIZATION; no widened-window rule was introduced.

The proof does not propagate merely by negamax. A deeper full child receives
lower=-parent.upper, and the accepted 10063 capacity enclosure does not impose
parent.upper<=10000. The post-FULL guard supplies parent.upper>-10000, which
is the opposite side of the required enclosure. Main/scout/null/IIO joins
and deeper first-half nodes therefore retain their stated premises. No global
strict-window, genuine-mate or universal first-half exclusion is claimed.
No source behavior, test, engine run or helper execution changed.

## 2026-10-20: capturing sibling route also excluded

One separately bounded pure-key calculation completed after the compact48
native lane closed. It covers a capturing the opposing minor, with b/c
noncapturing and H generated at Q. All eight color/own-minor/opposing-minor
profiles completed: **3,031,520 index probes, zero algebraic matches and zero
candidates**. Actual helper exit0, empty stderr, complete JSON, unchanged
source hashes and profile/cardinality totals were checked independently by the
lead. There was one run, with no retry or engine invocation.

After a captures the opposing minor, Q's only moving-side piece is the opposing
king at u. Generated nonnull H must therefore start at u. Noncapturing b cannot
move that king; for H.source to be empty in P, c must move it u→v.
The inventory has no pawn or rook, so promotion, EP and castling add no omitted
geometry, including admitted joined setups. This inference requires H to be
generated at Q; merely receiving an inherited H would not suffice.

For a/b moving the same own piece A from r to z/y, the necessary equality is
`S(A,z) XOR S(A,y) XOR S(opposingMinor,z) = delta(opposingKing,u,v)`.
The captured-piece term appears once. All common geometric predecessors r
are represented. For different own movers K/M, enumerate both directed edges
and both a/b assignments; the removed minor's coefficient is selected at a's
destination. The opponent index preserves both king directions and duplicate
deltas. Blockers, king safety, H.destination and search ordering remain relaxed,
so a completed zero excludes the stricter represented branch.

The calculation visits1,505,280 different-piece edge pairs with two capture
assignments each, and64,512 same-piece destination pairs. Common-predecessor
filtering leaves20,960 same-piece index probes, giving3,031,520 total.
K/N/B geometry counts are420/336/560 directed edges. Published coefficient
checkpoints0/959/960/1919 are respectively12911fa0/84a7bc59/6e28fa04/06646f9f.
The frozen helper uses the released generator directly and imports no engine.

Together with the earlier noncapturing result, this excludes the proposed
four-piece sibling recipe **with a generated H at Q**. In that recipe P retains
all four pieces, forcing b/c to be noncaptures; a either captures the opposing
minor or is noncapturing. Other inventories, inherited-H routes and different
branch shapes remain outside these calculations. The conditional zero-score
lemma survives, but this particular recipe cannot realize its collision.
Stop this witness construction; no larger enumeration is selected.

Frozen supports are in
`/home/legolas/agent-memos/rook2-hint-capture-feasibility-20261020/`:

- `capture_feasibility.py`: SHA256
  `b3fd5312d6e21b3712cc109204ec904d23771676ab868d13bc5b9e1ada89376c`;
- `README.md`, the pre-run algebra/coverage/resource proof: SHA256
  `8f38a4aed56ec7d10eddd5b2e7aa699931d6f6d4d1205eed0d14286a9b758d1c`;
- `result.json`: SHA256
  `4ed7f945f927a12e84ed7a716a21d2735b8ea1decd1f77890bd3828f35412d51`;
- `exit-code.txt`, empty `run.stderr` and identical before/after source hashes.

The source/README preserve their pre-run wording. The actual result and helper
exit establish execution. The housekeeping-CPU run had45-second wall,
28/30-second CPU,128MiB address-space,8,000,000 joined-edge and1MiB combined
output ceilings. No production behavior or behavioral authority changed.

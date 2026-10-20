# SEARCH-ORDINARY-ITERATIONS — deterministic completed root iterations

This runnable diagnostic composes the already specified
position, evaluation, tactical and ordinary-search rules into complete
unrestricted root iterations. It returns every root result rather than only
the selected move.

## Request and fixed boundary

`search.ordinaryIterations` accepts version 1 with exactly this input:

```
{fen, moves, personalityParameters, completedIterations, controls}
```

`fen` and `moves` have the same setup domain and history-preservation meaning
as SEARCH-FIRST-ITERATION. The complete `personalityParameters` object
has exactly the 30 integer fields listed in the
[version-1 vector data](ordinary-iterations-personality-vectors-v1.json).
It must equal either the `neutral` vector or one complete member of
`selectedTwoIteration`; field order has no meaning and partial vectors,
profile names and fallback defaults are not accepted. The neutral vector
allows `completedIterations` from 2 through 6. A selected vector requires
exactly 2. Neutral requests that encounter internal iterative ordering are
further restricted by the produced-search boundary below. Every admitted
vector has `rnd:0`. `controls` is exactly:

```
{completion:"fixed-iterations",
 learnedState:"fresh-ordinary-search",
 pondering:false,
 workOrigin:"after-root-preparation"}
```

The root reached after `moves` must have at least one legal move. Preserve the
full move history and piece chronology; a final FEN alone is not a substitute.
Start with empty ordinary-search history and killer preferences, empty
remembered search results, and the root evaluation context derived from this
position. These states persist between depth iterations as described below.

The operation completes every requested iteration before returning. A host
poll, interruption, malformed state, a 4096th charged search unit, principal
variation longer than 63 moves, or an ordinary-search state outside the
qualified rules is an error. It must not return a prefix or a last-complete-
iteration result in those cases.

This requested completion boundary is distinct from an XBoard `sd` command.
A normal public search may stop before the nominal depth because of timing,
terminal-score or session rules. Such an incomplete public search is not an
expectation for this diagnostic. Conversely, this diagnostic does not promise
that public timed search naturally completes the same number of iterations.
The enclosing ordinary caller applies
[SEARCH-ITERATION-TERMINAL-STOP](iteration-terminal-stop.md) after a completed
iteration. Its ordinary depth limit comes from personality `md`, including the
default 999 value subject to the independent iteration-61 ceiling; recorded
`sd` is not that limit. This fixed-iteration diagnostic intentionally bypasses
that terminal consumer after each requested iteration.
Root preparation is performed, but its work is outside the response; all work
counters begin at zero immediately before iteration one.

## Personality binding and lifetime

After applying the complete move history, the side to move is the root side
for the whole request. Bind every `my` percentage to that color and every `op`
percentage to the other color. The suffixes `p`, `n`, `b`, `r`, `q`, `cc`,
`mob`, `ks`, `pp` and `pw` mean pawn, knight, bishop, rook, queen, central
influence, mobility, king safety, pawn progress and pawn structure,
respectively. Produce effective color-owned coefficients with
EVAL-PERSONALITY-WEIGHTS. Do not exchange these owners when the current side
changes at a descendant. The root phase and these color bindings remain fixed
through every descendant, root candidate and completed iteration.

Produce the root phase from the reached root placement with EVAL-PHASE. From
that fixed phase and `cfd`, produce the root-relative draw preference using
EVAL-SCORE-CONTEXT:

`floor(((4 * opening + 2 * middlegame + endgame) * cfd + 512) / 1024)`.

Its White-relative contribution is that value for a White root and its
negation for a Black root. This signed contribution is fixed for the search
and is consumed by descendant evaluations before their endgame rules, score
finishing, current-side orientation and bound decisions. Likewise, `sop`
produces the position-dependent variation range under EVAL-SCORE-CONTEXT and
is consumed inside each evaluation using the position identity required by
that contract. Neither value is recomputed from a descendant phase, rebound
to the current side or applied once as an adjustment to the returned root
result.

The other personality fields retain their referenced component meanings:
`avd` enters the material and pawn evaluation contracts, `sel` enters
SEARCH-SELECTIVE-DEPTH, `md` bounds ordinary depth, `ana` enters repetition
admission, and `tts` selects remembered-result capacity. The admitted vectors'
remaining fields are consumed by the evaluation contracts named below. These
rules describe composed search behavior, not a requirement to store a profile
object or use any particular initialization layout.

Scores in this response are the internal ranking scores produced and consumed
by the fixed search. A public analysis post can apply its separately specified
reported-score adjustment; that reporting transformation is outside this
diagnostic and must not be applied to these results.

## Iterative root schedule

Generate the complete legal root sequence using
SEARCH-ORDINARY-CANDIDATE-PRODUCTION. The first iteration visits that sequence
without learned, cached or previous-iteration reordering.

For each iteration D, visit every root candidate exactly once in the current
sequence. Rank completed candidates by descending returned score. Equal scores
retain their visitation order. The complete ranking from iteration D is the
root sequence for iteration D+1; no unvisited candidate is moved by results
obtained earlier in its own iteration.

At the start of every iteration, create a new empty completed-root ranking,
set root best score to -10000 and set the root PV to empty. Do not carry the
prior iteration's numerical best, second score or PV into these values. Carry
only its ranked move sequence and the search-wide learned, remembered-result
and pawn-classification states. The fixed root evaluation context is also
retained; it is not rebuilt from a descendant or from the prior iteration's PV.

Within one iteration, let R be the stable ranking of roots already completed.
The incoming root window has upper boundary 10000. Its lower boundary is the
second score in R, or -10000 until R has at least two entries. Equal scores
occupy separate ranked places, so two equal leading scores make that common
score the lower boundary for the third root.

Apply the root move and search its child at search ply one with remaining depth
`D-1`, previous-extension value zero, lower boundary -10000 and upper boundary
equal to the negation of the root lower boundary. Negate the returned child
score to obtain the root score. Consume the returned value as a bound-bearing
search result; do not replace it with a hypothetical full-window result.

After each root result, update R by stable insertion. The iteration's best and
second scores are the first two entries of R, with second score -10000 when R
has only one entry. Replace the root principal variation only on a strictly
higher best score. Its new value is the root move followed by that child's
returned PV. A tie retains the earlier PV. The iteration result is the final
best score and retained PV after all root candidates complete.

Every occurrence remains an ordered list entry. A move and a numerical window
may recur in later iterations; consumers must not collapse visits into a map
keyed by move or window.

## Ordinary recursive search

The following is a semantic state machine. It does not require a call stack,
table layout, branch decomposition or source organization.

An ordinary node is identified for these rules by current position/history,
search ply P, remaining depth D, incoming open window `(L,U)`, preceding move,
preceding extension, retained evaluation state, and the search-wide learned,
remembered-result and pawn-classification states.

### Entry and tactical boundary

If D is nonpositive, P is 63, or P has reached the personality maximum depth,
continue with SEARCH-QUIESCENCE-TREE from the produced node and the same
window. Its target ply is the greater of zero and `P+D`. Its returned score,
PV and work are the ordinary node's result. Otherwise charge one search unit
for this ordinary node before later admission decisions.

Pass the enclosing root iteration depth to the reusable quiescence rules,
including every checking probe below. This is not the node's remaining depth
or an IIO shallow target; it stays unchanged through ordinary and quiescence
descendants. Only the standalone selected-subtree diagnostic fixes it to one.
In particular, quiescence excludes a non-recapture only beyond its target plus
this enclosing iteration depth. In the depth-three opening fixture, the
`e2e4 d7d5 d2d3` prefix reaches tactical target three; a non-recapture at ply
five is within the limit of six. This admits `d8d1` to the remaining tactical
tests and permits its `e1d1` reply in the recorded child PV.

Apply [SEARCH-DRAW-BOUNDARY](draw-boundary.md#ordered-decisions) before
remembered results. A repetition draw returns zero with an empty PV before
clearing killers. Otherwise clear the next-ply killer preferences, then test
SEARCH-MOVE-REVERSAL: a true predicate returns zero with an empty PV only when
the incoming upper bound U is at most zero. With U positive, reversal alone
does not stop search. The separately specified mate-leaf consumer is unchanged.

Query SEARCH-REMEMBERED-RESULTS with P, target `P+D`, and the unchanged window.
A usable score returns immediately. Retain its move hint, marked depth and
quiet-mate-check marker when no score is usable; those observations affect the
later ordering and probe rules.

The remembered-result context begins empty for this operation and persists
through all roots and iterations. Its capacity is selected from the fixed
`tts` value: let G be the largest prime not greater than `floor(tts/48)`.
For a position, take `primary` and `secondary` from POSITION-IDENTITY. Let E be
zero when there is no en-passant target; otherwise E is ten times the target's
zero-based rank plus its one-based file. Let F be the sum of 16 for White to
move and 1, 2, 4 and 8 respectively for White queen-side, White king-side,
Black queen-side and Black king-side castling availability. The conflict group
is the least nonnegative 32-bit value of
`primary XOR ((E × 256) OR (F × 65536))`, modulo G. `secondary` is the identity
within that group. This is observable conflict behavior derived from the
request's position; an implementation is not required to expose these values,
accept them as inputs, or use a physical table with this organization. They do
not appear in the response.

### Static bounds and shallow cutoff

Obtain the node adjustment from SEARCH-SELECTIVE-DEPTH using the current
iteration number, fixed selectivity, current endgame weight and target `P+D`.
Apply SEARCH-FAST-ENTRY's admission rule to the preceding move and current
material. If admitted, calculate its fast score and consume
SEARCH-FAST-CUTOFF. A successful fast cutoff is stored as a remembered result
and returned immediately.

Otherwise perform the full evaluation, update this branch's retained
evaluation state, and charge its actual relation work. For nodes in the first
half of their path, inclusive, use static bounds [-10000,10000]. At later
nodes use the evaluator's produced lower and upper bounds. More precisely, the
full bounds apply when `P <= floor((P+D)/2)`; otherwise use the produced bounds.
These are the effective bounds saved for this node's remaining processing,
not a temporary pair used only for the early comparisons. Use the same pair
for initial best and final completion clipping below. Replacement changes only
the bounds, not the evaluator's static score or other produced evaluation
terms; do not retain the original endpoints as hidden later limits.
A lower bound at least U returns that lower bound. Failing that, an upper bound
at most L returns that upper bound.

When D is at most the selective node adjustment, the full score is at least U,
and the side to move is not in check, attempt a shallow cutoff:

- For D at most two, when the parent was not in check and the move did not
  create the SEARCH-KING-PRESSURE guard, calculate [EVAL-MATERIAL-THREAT](material-threat.md). The trial
  score is `staticScore - materialThreat - 25` for D at most one, otherwise
  `staticScore - materialThreat - 40`.
- Otherwise search the same side-to-move position after a null transition. Use
  depth `D-3` when D is below six and `D-4` when D is at least six, reset the
  preceding-extension value to zero, and use the negated window
  `(-U, 1-U)`. Negate that result for the trial score.

The stated depth is the null child's remaining depth at ply `P+1`; do not
subtract a further ply on entry. For a parent at `P=1, D=1`, the below-six
rule enters the child at `P=2, D=-2`, so its tactical target is
`max(0, 2-2) = 0`. In the selected depth-two opening fixture, the `f6g4`
root step follows this path and retains score 441. That fixture does not
require a child depth of `D-2`.

If the trial score reaches U, store it and return it. Otherwise continue.

The null transition has the state behavior of EVAL-MOVE-SEQUENCE: keep
placement, piece chronology, castling rights, phase, placement fingerprints,
square contribution and retained positional/pawn terms; exchange the side to
move; clear en passant; and increase the halfmove count and evaluation age
modulo 256. The child has no preceding move. The null state participates in the
subsequent search path, but is not appended to the public played-move history;
its null descriptor is consumed by SEARCH-MOVE-REVERSAL and cannot qualify as
an endpoint-reversing move, even against another null descriptor. This does
not bypass historical repetition or later remembered-result/evaluation rules.
The parent state is unchanged when the null child returns.

### Legal moves, ordering and mate probe

Generate all legal candidates. No candidates returns `P-10000` when in check,
otherwise zero. Before ordering a nonempty list, return `P-9998` if that value
reaches U.

Order the candidates through SEARCH-CANDIDATE-ORDER using current material and
root-phase positional values, the remembered move hint, the current and
two-plies-earlier killers, and the search-wide history scores. SEARCH-CUTOFF-
MEMORY updates these learned preferences as stated below. Pawn classifications
and retained evaluation state follow their existing search-lifetime contracts;
returning from a child restores its parent's retained evaluation state, while
shared learned and pawn-classification histories retain their chronological
effects.

The remembered quiet-mate marker can suppress this node's checking probe. If
it is false, the node is not in check, and `P` is no greater than both
`floor((P+D)/2)` and `P+D-3`, perform the probe when the side's encoded material
is at least 4112. That material number is
`pawns + 16*knights + 256*bishops + 4096*rooks + 65536*queens`.

Visit ordered ordinary, non-promotion moves that give check. Search each
resulting child through SEARCH-QUIESCENCE-TREE with target `P+1` and window
[-9000,-8999]. Stop this scan at the first negated score at least 9000 and use
that move as the remembered move preference. Mark the node as checked even if
no such move exists. A found score which reaches U causes the corresponding
cutoff-memory and remembered-result updates, but does not itself return from
this ordinary node; normal candidate search continues. This continuation is
required by the successful-mate fixture.

### Internal iterative ordering

Internal iterative ordering is an ordinary recursive search of shallower
children whose returned scores reorder the main candidate sequence. It does
not directly replace the node's best score or principal variation.

After ordinary candidate ordering and before the first main candidate, perform
an initial ordering phase exactly when D is at least four and the node-entry
remembered marked depth is absent or is less than `D-2`. Independently, after
exactly the first main candidate completes **without ending main-candidate
processing**, perform a tail phase exactly when D is at least five and the
node-entry remembered-result query's final exported bound kind is exactly
`lower`. `exact`, `upper` and `none` do not qualify, including an `exact`
observation that has lower permission but supplies no score. This condition
uses the retained entry query, not a later store or the first main result. A
first-main result which reaches U ends candidate processing immediately, so an
otherwise depth/bound-eligible tail is not entered and normal node completion
follows. If processing continues but no unconsumed suffix remains, there is no
tail work to perform. The tail phase receives only the still-unconsumed suffix;
the completed first candidate remains fixed at the front. Both phases use the
node's original incoming L and U. In particular, a tail phase does not replace
L with the lower boundary raised by the first main result.

Let P be the node ply and T be `P+D`. The shallow targets, in order, are
`T-20`, `T-18`, and so on through `T-2`, after discarding each target below
`P+2`. Execute every remaining target. Each target begins a new pass with best
score -10000 and the candidate sequence left by the preceding pass.

For each visited candidate in a pass:

1. Produce a fresh extension through SEARCH-MOVE-EXTENSIONS from the parent
   position, predecessor, incoming previous extension, and the complete
   candidate sequence as it stands for this pass.
2. Extension values 0 through 7 denote three independent extension flags.
   Retain, per candidate, the flagwise union of every fresh extension produced
   for it by earlier ordering passes and the current pass. Equivalently, the
   accumulated value is the integer bitwise OR of those values.
3. Search the actual produced child at remaining depth
   `shallowTarget + freshExtension - P - 1`. Supply the accumulated extension,
   not only the fresh extension, as that child's previous-extension input. The
   child window is `(-U, -max(passBest,L))`.
4. Negate the child return for the candidate score. Replace pass best only on a
   strict improvement.
5. Move the candidate to the front only when its score is strictly greater
   than both the previous pass best and L. A tie, or a score above L but not
   above the previous best, does not promote. Stable removal and front
   insertion preserve the relative order of every other candidate. Candidates
   already visited in this pass are not revisited after a promotion.
6. Close this pass early only when that same qualifying promotion reaches U.
   A pass cutoff is an ordering-pass result: it neither returns from the node
   nor suppresses any later shallow target.

On normal exhaustion, close the pass after every candidate in its current
visitation sequence has returned. Carry the resulting complete sequence and
the per-candidate accumulated extensions into the next shallow pass. After the
last pass, an initial phase supplies its whole resulting order to the main
loop. If that node later enters a tail phase, each suffix candidate retains any
extension flags accumulated by the initial phase. A tail phase replaces only
the unconsumed suffix and cannot disturb the completed prefix.

When the main loop later consumes a candidate, produce its extension afresh
through SEARCH-MOVE-EXTENSIONS. Its main child depth is `D-1+freshExtension`.
Supply the flagwise union of that fresh value and the candidate's retained
ordering extensions as the main child's previous-extension input. Thus an
accumulated ordering extension affects descendant extension context but does
not by itself increase the current main child depth.

Ordering children are ordinary recursive searches. Their cumulative search
and relation work, learned ordering state, remembered results, pawn
classification and position history remain in the search lifetime and are
visible to later ordering passes and main candidates. Returning from each
child restores the parent's retained evaluation state under the ordinary child
rule. The ordering result itself contributes no direct parent best score or
PV; only the reordered sequence, accumulated extensions and shared retained
effects cross into main consumption.

The currently published `search.ordinaryIterations` route remains narrower:
it admits only initial phases with exactly one shallow target and zero fresh
and accumulated ordering extensions. A required tail phase, a second target or
a nonzero ordering extension still makes that public request fail without a
partial response. Those are route limits, not unspecified search behavior; the
complete rules above define the broader ordinary-search composition pending a
separate route review.

This is a behavioral rule. An implementation using an unrelated internal
optimization is not rejected merely because it gives that mechanism the same
name.

### Candidate search and completion

For each ordered move, derive its fresh extension with SEARCH-MOVE-EXTENSIONS
and set child depth to `D-1+freshExtension`. Supply the extension accumulated
for this candidate as described above as the child's preceding-extension input;
without an ordering phase, that accumulated value is just the fresh extension.

Before visiting the main list, initialize node best to the saved effective
lower bound (−10000 in the first-half region), running lower to incoming L,
PV to empty, and preferred best move
to the remembered move hint or null. A successful checking-mate probe replaces
that preferred move. These are semantic initial values even when the
implementation represents them without mutable variables.

At child depth zero or below, derive SEARCH-FRONTIER-ESTIMATE from current
material, actual capture/check facts, static score and retained pawn/positional
terms. Let T be the greater of current best and running lower. If the estimate
is at most T, consume it as this move's score without searching a child. This
is not an “at most both” test: with best 30, running lower 10 and estimate 20,
the child is skipped because 20 is at most 30.

Otherwise choose one of these window behaviors:

1. Search the first candidate, any candidate while best has not exceeded L,
   and every candidate when both original endpoints are non-full with the full
   child window `(-U, -max(best,L))`.
2. For other candidates first use the scout child window
   `(-min(best+1,U), -best)`. If its negated result is at least `best+1` and
   below U, search the same produced child state again with
   `(-U,-best)` and use the second result.

Create one child state for a candidate. A scout and its full-window re-search
reuse that child after the scout's branch-local retained evaluation changes;
the retry does not rebuild the child from its initial inheritance. Once the
candidate finishes, the parent retains its own evaluation state. The next
sibling is produced from that unchanged parent, not from the prior sibling.
Search-wide learned ordering, remembered results and pawn-classification
history are different: their chronological effects survive child return and
are visible to the retry and later siblings.

For an ordinary move, produce placement, turn, rights, en-passant, halfmove
count and piece chronology with POSITION-MOVE-SEQUENCE. The child inherits the
parent's positional subtotal and pawn-progress value unchanged and increments
evaluation age modulo 256. A later full child evaluation may replace that
child's retained terms, but does not replace the parent's terms. Root children
and recursive children use the same inheritance rule.

Negate a searched child result for the candidate score. A score strictly above
best replaces best. If it is also strictly above the running lower boundary,
remember this move as the cutoff preference; when it is strictly below U,
replace the node PV with this move followed by the returned child PV. Only
inside that strict best improvement, raise the running lower boundary when the
score also exceeds it. Stop visiting candidates when it reaches U.

On list completion, cap best at the saved effective upper bound (10000 in the
first-half region). If the result
is strictly greater than the node's incoming L, update SEARCH-CUTOFF-MEMORY
using the remembered best move. Store the final score, move hint, marked-depth
state and quiet-mate marker through SEARCH-REMEMBERED-RESULTS, then return the
score and retained PV.

Every remembered-result store uses this node's derived conflict group and
identity, P, target `P+D`, and original `(L,U)` window; bound permissions then
follow SEARCH-REMEMBERED-RESULTS. A fast or shallow cutoff stores its cutoff
score, any previously returned cache hint, `markDepth:false`, and the inherited
quiet-check marker. A successful checking-mate score which reaches U first
updates cutoff memory and stores that score with its discovered move,
`markDepth:true` and quiet marker true, then continues normal candidate search.
Normal list completion stores capped best, the final preferred move or null,
`markDepth:true`, and the marker after any local probe. Early draw, evaluator-
bound, terminal-list and mate-lower-bound returns do not perform this normal
completion store.

## Output schema and closure

The response is exactly:

```
{initialCandidates, iterations, result}
```

`initialCandidates` is the first iteration's complete generated sequence.
`iterations` has exactly `completedIterations` entries, with depths 1 through
that number. Each entry is exactly:

```
{depth, candidates, steps, score, principalVariation, work}
```

`candidates` is that iteration's visitation sequence. `steps` has the same
length and order. Each step is exactly:

```
{move, window:{lower,upper}, score, bestScore, secondScore,
 childPrincipalVariation, principalVariation, work}
```

Moves and PVs use the SEARCH-QUIESCENCE-TREE `{move,kind}` descriptor. Scores
and window endpoints are integers from -10000 through 10000. PVs contain at
most 63 moves. `childPrincipalVariation` is the actual final child return,
including an empty PV for a bound or early return. `principalVariation` is the
root PV retained after consuming that step.

Every work value is exactly:

```
{searchCounterDelta, chargedSearchUnits, chargedRelationQueries}
```

The first two values are equal in this single-lane diagnostic. Step work is
cumulative from the zero origin, never decreases, and is below 4096 search
units. Iteration work equals its final step work. The next iteration starts
from that same cumulative work. `result` has exactly `{score,
principalVariation,work}` and equals the final iteration's three corresponding
fields.

Each step's cumulative work includes every ordinary and quiescence descendant
actually visited while calculating that root step, including null probes and
branches absent from its final PV. A descendant's charge is incorporated when
visited; do not add it again to the step's recorded cumulative work. A returned
score or PV does not reveal all branches whose work has already been charged.
The quiet-rook worked accounting in the [conformance guide](../conformance/README.md#quiet-rook-work-accounting)
shows this distinction at a null descendant of an ordinary root.

For a neutral request, the first iteration's candidates, steps, score, PV and
work are byte-for-byte the semantic response defined by
SEARCH-FIRST-ITERATION after renaming that contract's top-level `candidates`
to this iteration's `candidates`. Selected vectors use the same first-root
scheduling and response rules here, but SEARCH-FIRST-ITERATION does not admit
them. Later iterations extend rather than redefine the scheduling contract.

## Dependencies and held boundaries

This contract composes POSITION-SETUP, POSITION-MOVE-SEQUENCE,
POSITION-IDENTITY, EVAL-SEARCH-PAWN-SEQUENCE, the root evaluation contracts,
SEARCH-ORDINARY-CANDIDATE-PRODUCTION, SEARCH-CANDIDATE-ORDER,
SEARCH-SELECTIVE-DEPTH, SEARCH-CACHED-ADMISSION, SEARCH-REMEMBERED-RESULTS,
SEARCH-FAST-ENTRY, [EVAL-MATERIAL-THREAT](material-threat.md), SEARCH-KING-PRESSURE,
SEARCH-MOVE-EXTENSIONS, SEARCH-FRONTIER-ESTIMATE, SEARCH-CUTOFF-MEMORY and
SEARCH-QUIESCENCE-TREE. The root schedule, board-derived remembered-result key,
ordinary node transitions, scout/re-search rule and successful mate-probe
continuation are specified here because no earlier portable contract completed
those connections.

The version-1 diagnostic admits only the initial, single-pass,
zero-ordering-extension subset of internal iterative ordering. It does not cover a tail phase, multiple
shallow passes, or nonzero extension accumulation across ordering and main
consumption; arbitrary or modified personality vectors; natural roster
randomness; analysis, pondering or randomized search;
adaptive clocks and terminal-score stopping; persistent-session profile,
remembered-result or cache lifetimes; late root scheduling; interrupted
output; or general gameplay strength. The selected vectors deliberately
replace their roster randomness with `rnd:0`; they test deterministic
parameter composition, not natural play, clock calibration or strength. The
available grouped counterexamples distinguish combined percentage,
preference, and depth-control rule groups but do not establish that every
field in a group independently changes an output.

The currently published fixtures establish nine original-derived deterministic
contexts: four earlier neutral contexts, two neutral depth-five IIO contexts,
and one context for each selected vector. The four earlier neutral and three
selected fixtures remain byte-for-byte unchanged by the IIO expansion. One new
depth-five context observes two entered initial phases with no promotion; the
other observes two entered initial phases with two strict promotions. The
fixture responses contain only public semantic results derived from pinned
original observations; native and model results are corroboration, not their
expectation source. These fixtures do not imply equivalence for every admitted
position. Tail, multipass and nonzero-extension behavior is specified under
Internal iterative ordering above and used by complete ordinary search; its exclusion
here is a diagnostic admission and qualification limit, not a missing rule or
an implementation freedom.

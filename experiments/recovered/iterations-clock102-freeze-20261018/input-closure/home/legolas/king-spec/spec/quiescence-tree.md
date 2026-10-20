# SEARCH-QUIESCENCE-TREE — composed deterministic tactical search

This working contract joins position/history, evaluation, candidate production,
candidate decisions and recursive result consumption. It describes a bounded
diagnostic subtree, not an entire game, root move choice, strength calibration,
or complete engine conformance. The adapter must compute the search; it must
not recognize fixture positions or return recorded answers.

## Input and diagnostic boundary

`search.quiescenceTree` accepts exactly `fen`, `moves`,
`personalityParameters`, `rootMove` and `controls`.

- `fen` is a six-field FEN under POSITION-SETUP normalization. The halfmove
  count is 0..255 and fullmove number 1..1000000. The side not to move must not
  already be in check. A retained en-passant target must have the proper rank
  for the moving side and the opposing pawn behind it.
- `moves` contains 0..255 legal coordinate moves, with a lowercase promotion
  suffix where needed. Preserve the resulting history and piece chronology;
  do not rebuild an equivalent placement with different chronology.
- `rootMove` is exactly `{move, kind}`. Its coordinate move is legal from the
  position reached after `moves`. `kind` is `ordinary`, `castle` or `enPassant`
  and must agree with that move. Promotions retain kind `ordinary` and include
  their suffix. The resulting selected child must not be in check.
- `personalityParameters` is the complete fixed diagnostic vector below.
- `controls` is exactly `{iterationDepth:1, rootPass:"first-unrestricted",
  learnedState:"fresh-ordinary-search", pondering:false}`.

The parameter names with value 100 are:
`myp`, `myn`, `myb`, `myr`, `myq`, `mycc`, `mymob`, `myks`, `mypp`, `mypw`,
`opp`, `opn`, `opb`, `opr`, `opq`, `opcc`, `opmob`, `opks`, `oppp`, `oppw`,
and `sop`. The names with value zero are `ana`, `avd`, `cfd`, `myk`, `opk`,
and `rnd`. The remaining values are `md:99`, `sel:14`, `tts:67108864`.
No additional parameter or diagnostic input is accepted in this version.
The `opk` parameter does not reintroduce an authentication requirement.

Establish the ordinary fresh-search state at the position after public history.
Use its fixed root evaluation context and fully evaluate the root before
applying the selected root move. Observe only that move's quiescence subtree;
do not search other root alternatives first. Start at search ply 1, target ply
1 and window [-10000,10000]. Random score perturbation and pondering are off.

The currently qualified diagnostic requires that this first child reaches a
nonempty tactical list and ordering. Requests whose first child returns earlier
are outside this diagnostic's current observation boundary, although such
returns remain part of the recursive rules below. The qualified run must finish
before a host poll, interruption, 4096th visited node, or PV longer than 63 moves.
Out-of-domain or resource-limited execution is an error, not a partial match.
These are diagnostic limits, not new limits on ordinary engine gameplay.

## Position, history and evaluation state

Use the produced root context throughout the subtree. Child positions use the
ordinary move/history rules, including captures, promotions, castling rights,
en-passant state, reversible counts and piece ordering.

Each child inherits its parent's retained `positionalSubtotal` and
`pawnProgress`; its `evaluationAge` is the parent's age plus one modulo 256.
Full evaluation replaces that child's pair and sets its age to zero. Fast
evaluation consumes and preserves the pair and age. A child's final score is
never substituted for a retained subtotal. Returning from a child preserves the
parent's own pair and age, so a later sibling inherits the parent, not the
earlier child's final state.

Full evaluations use the retained pawn classifications described by
EVAL-SEARCH-PAWN-SEQUENCE in their actual chronological order. Fast evaluations
do not select or update those classifications. Branch-local score restoration
does not imply that the shared pawn information is rolled back.

## Admission and static result

At entry, charge one search unit and initialize this node's PV to empty. Apply
SEARCH-REPETITION-ADMISSION and SEARCH-MOVE-REVERSAL to the produced history.
A repetition draw returns zero. A qualifying endpoint reversal returns zero
when the incoming upper bound is at most zero. These returns precede terminal
static evaluation. The next-ply killer clearing rule is unchanged.

For this predicate, null transitions are not endpoint-reversing moves: if
either compared move is null, reversal is false, including two nulls. An
ordinary null trial delegated to quiescence uses this same rule; delegation
does not create a synthetic played move or an extra ordinary entry charge.

At ply 63, return the fast static score. Otherwise:

- In check, do not perform the ordinary static evaluation before replies.
- Not in check, compose EVAL-QUIESCENCE-ENTRY: select full or fast from current
  material; when fast is selected, refresh with full evaluation if its score
  lies strictly between lower minus 250 and upper plus 250, or if the preceding
  move satisfies SEARCH-CAPTURE-EXCEPTION.
- Consume the selected score/bounds as EVAL-QUIESCENCE-DISPOSITION. Test the
  evaluator's lower-bound return before its upper-bound return, then stand pat.
  A lower bound at least the incoming upper bound returns that lower bound; an
  upper bound at most the incoming lower bound returns that upper bound.
  Otherwise initialize best and standing score from the static score. Return
  immediately if best reaches the upper window; otherwise raise the running
  lower window to best when necessary.

Keep the evaluator's upper bound for final candidate-list completion. In-check
nodes begin with best -10000 and an evaluator upper bound of 10000.

## Candidate production and early mate boundary

Not in check, use SEARCH-QUIESCENCE-CANDIDATES. Its list is intentionally
pseudo-legal: do not discard king-exposing candidates before their estimate
and other specified effects. In check, produce ordinary legal evasions with
the position/history candidate-generation ordering rules. Apply the quiescence
shared [quiescence preference rule](quiescence-candidates.md#quiescence-preference-value)
to either list, including ordinary quiet evasions absent from the non-check
tactical producer. Fresh ordinary-search learned priorities are
initially zero; these quiescence visits do not learn new priorities.

An empty non-check tactical list returns the standing best directly, without
the later list-completion clipping. No legal evasion returns `ply - 10000`.
If evasions exist and `ply - 9998` reaches the current upper window, return
`ply - 9998` before ordering or searching a child. These early returns have
empty PVs. Candidate availability need not entail recomputing a previously
available reply set; no physical caching representation is required.

## Ordered candidate decisions

The reusable tactical rule consumes the enclosing root iteration depth I.
The standalone `search.quiescenceTree` diagnostic binds I to its required
`controls.iterationDepth:1`; an ordinary-search caller supplies its current
root iteration depth instead. Preserve I through all tactical recursion,
including check-evasion target increments. It is not current ply, remaining
ordinary depth, target ply, or an internal-ordering shallow depth.

Visit candidates in their produced priority order, preserving effects on best
even when a candidate is later rejected. A recapture has the same destination
as the previous move.

For a non-check node:

1. Exclude a candidate that is neither material-changing nor checking. Exclude
   a non-recapture when the current ply is greater than `target + I`, where I
   is the enclosing root iteration depth. The standalone diagnostic fixes I
   to one, giving `target + 1` only for that diagnostic. This late exclusion
   precedes special move admission as well as ordinary capture estimates.
2. Promotions and en-passant moves are forced candidates at this stage.
   For an ordinary capture, add SEARCH-QUIESCENCE-CAPTURE-ALLOWANCE to the
   standing score, deriving material and retained terms from this node.
3. Only the ordinary captures estimated in step 2 enter
   SEARCH-QUIESCENCE-CAPTURE-POLICY. Promotions and en-passant retain their
   forced status without an estimate-policy call; quiet checks have no capture
   estimate and proceed unforced to step 4. Use actual ply, target, enclosing
   iteration depth I and running best/lower window. For a non-king attacker,
   use its color's fixed root material value from
   [EVAL-MATERIAL-VALUES](root-material-context.md), without the ordering
   rule's low-value adjustment or captured-piece square term.
   If its conditions request destination support, use the placement-derived
   SEARCH-QUIESCENCE-CAPTURE-DEFENSE predicate. Preserve the policy's optimistic best
   update even when the candidate is not forced or later proves king-unsafe.
4. A candidate not forced must give check. A single checking route which is
   not a recapture is retained only when there is at most one legal reply, or
   the produced child has a positive repetition count. A simultaneous direct
   and discovered check bypasses this reply restriction. Only the greater-
   than-one reply predicate matters here, not a particular enumeration count.

Finally reject a move that leaves the moving side's king attacked. King safety
does not undo a previously made optimistic best update. In-check evasions do
not use the non-check estimate/check screens above.

An ordinary king capture uses the same estimate and destination-support policy
as an ordinary non-king capture: its moving-piece value for that policy is
exactly 50, for either color and every root phase. King personality fields do
not scale that value. There is no king exemption. The ordering-only attacker
value 1500 does not enter the deduction. The ordinary king-safety rejection
still applies after the estimate's specified effects.

## Recursion, PV and completion

For an admitted child, increment ply. Increment the target by one if the parent
was in check; otherwise preserve it. Search with the negated window
[-upper,-runningLower]. Negate the returned child score for the parent.

A strict improvement over best replaces best. Only when that improvement is
also strictly inside the current window does the PV become this move followed
by the child's returned PV. A tie, fail-low or fail-high does not perform that
PV replacement. Raise the running lower window on a strict score improvement
over that lower window. Once it reaches the upper window, do not visit the
remaining ordered candidates.

The mate-ending fixture demonstrates the tie rule: `g6h7` establishes score
9998 and that one-move PV; a later `g6e8` child also has parent-relative score
9998 (its child return is -9998). The later
equal result leaves the earlier PV intact. Matching only the final score and
work would not distinguish replacing this PV incorrectly.

Completion after entering a nonempty candidate list returns the lesser of best
and the saved evaluator upper bound. The earlier empty-list and mate returns
retain their separate rules. Preserve the resulting PV independently of final
score clipping.

## Result and work observations

Return exactly `nodes`, `score`, `principalVariation`, `work`, `trace` and
`evaluations`. Moves use the same `{move,kind}` shape as `rootMove`.
Work objects contain `searchCounterDelta`, `chargedSearchUnits` and
`chargedRelationQueries`, all nonnegative integers relative to entry into the
selected subtree. They exclude preparation/evaluation of its parent root.

Number visited nodes 1,2,... in entry order. `trace` records:

- Entry: `{event:"enter", node, parent, ply, target, window, move, position, work}`.
  `parent` is null only for node 1; `window` has `lower` and `upper`.
  `position` contains `placement`, `sideToMove`, `castling`, `enPassant`,
  `halfmoveClock` and Boolean `inCheck`. Sample work before this node's charge.
- Return: `{event:"leave", node, score, principalVariation, work}`. Sample work
  after the node and its completed descendants. Returns nest with entries.

`evaluations` has one entry per visited node in the same numbering order:
`{node,parent,arrival,parentRetained,stages,departure}`. Each retained value is
`{positionalSubtotal,pawnProgress,evaluationAge}`. A stage contains exactly
`{kind,before,after,score,lowerBound,upperBound,work}`, where kind is `full` or
`fast` and stage work is its own delta. Empty `stages` means that no evaluator
was called at that node, not that it produced a zero score.

Evaluation relation charges come from the composed evaluator's actual activity
and pawn consumers. Candidate ordering and destination-support classification
add no charged relation queries. A rejected move adds no child search unit.
The final node-1 return agrees with the aggregate score, PV and work.

## Qualification limits

The accompanying fixtures include openings/history, capture chains, promotions,
king-exposing candidates, pawn endings, en passant, empty evasions and pre-order
mate bounds. They do not establish every admission/overflow boundary, every
personality configuration, shared-state collision or clock interruption.
Full-search/root scheduling, general timing and complete personality acceptance
remain separate obligations.

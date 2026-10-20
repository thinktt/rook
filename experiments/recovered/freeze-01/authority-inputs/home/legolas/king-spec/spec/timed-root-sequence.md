# SEARCH-TIMED-ROOT-SEQUENCE — root scheduling through adaptive stopping

This contract connects ordinary root exploration, retries and retained work
with [adaptive allowances](adaptive-time.md) and selected-result capture.
The controlled child replies determine the adjustment events; those events
are no longer supplied separately. Root candidates are abstract identities,
and each completed child supplies a score, work amount and elapsed-time advance.
Real move generation, recursive child searches and work-to-time production
remain separate requirements.

## Fresh state and iteration policy

Begin with the given candidate order, zero cumulative SearchID, zero accumulated
work for every candidate, zero best-change history and newly initialized
allowances. Iterations run from depth one through the number supplied, unless
a stopping condition ends the sequence. This diagnostic starts fresh; it does
not establish which state an enclosing persistent session must reset.

At the beginning of each iteration, choose unrestricted exploration if cumulative
SearchID is below 25000, otherwise restricted exploration. Preserve that choice
throughout the iteration, even if a child crosses the threshold. The first
candidate always uses an unrestricted window. In a restricted iteration,
after completing the first candidate, sort the remaining candidates by their
accumulated prior work, greatest first and stable on ties. The first candidate
stays first. This is the [root work policy](root-work-schedule.md).

Within the iteration, rank completed candidates by score, greatest first,
preserving exploration order on equal ranking scores. The final ranked order
and accumulated work feed the next iteration. The previous iteration's best
score stays fixed as the previous-score reference throughout the current one.

## Windows, replies and work

Use the [unrestricted](unrestricted-root-sequence.md) and
[restricted](restricted-root-sequence.md) window/ranking rules. In this bounded
ordinary-score domain they mean:

- An unrestricted child's lower bound is the current second-ranked score,
  or -10000 before there are two completed candidates; its upper bound is 10000.
- A restricted child's lower bound is current best plus two. Its upper bound
  is max(current best, previous iteration best) plus three.
- If the restricted initial reply equals or exceeds its upper bound, retry
  that same candidate with the same lower bound and upper bound 10000.
- The last reply supplies the returned score. For a restricted candidate whose
  returned score is at most the lower bound, subtract two for ranking; otherwise
  ranking score equals returned score. No such subtraction applies to the first
  candidate or an unrestricted iteration.

Each executed reply adds its supplied work to cumulative SearchID and advances
elapsed centiseconds by its supplied amount. Both attempts contribute when a
retry occurs. Add all work spent on the candidate in this iteration to its
retained candidate work. Unused replies contribute nothing.

The time advance occurs at child completion. All subsequent observations see
that time until another child completes. This explicitly controlled diagnostic
does not insert polls inside a child or replace the production work-clock rules.

## Adjustment admission, capture and stopping

For the first completed candidate of a restricted iteration, apply the score-drop
adjustment using the fixed previous-iteration best and the new returned score.
This applies even if no increase ultimately qualifies. It does not apply merely
because work crossed 25000 during an unrestricted iteration.

Whenever a candidate becomes first in the current ranked order, record a best
change and apply its depth-dependent adjustment. If the same candidate admits
both score-drop and best-change adjustment, **score-drop runs first**. The latter
tests the resulting retained limits, not their prior values.

After those adjustments, capture a new best candidate's score, identity,
cumulative SearchID and current elapsed time together. At depths at least three,
publish that capture immediately. At depths one and two, retain it without an
immediate publication. Equal-ranked later candidates do not replace the earlier
best. Child PV is empty in this diagnostic, so the captured PV consists of the
single root identity. The [post-lifecycle](post-lifecycle.md) contract separately
describes successful finish-time publication of deferred captures.

Then perform the root-completion clock check. If it stops, retain that root's
completed work and any newly captured result, and do not search the remaining
candidates or perform an iteration-completion check. Thus the selected capture
can precede the final work/time observation when a later non-best root stops.

After every candidate completes without a root stop:

- If the iteration began unrestricted and cumulative SearchID is now at least
  25000, apply easy adjustment to the actual best and second-ranked scores.
  Do not apply it at completion of an iteration that began restricted.
- Perform the iteration-completion clock check with the resulting allowance.
- In this ordinary-score domain, the additional terminal case is a sole legal
  candidate: when average allowance is nonzero and depth exceeds one, the
  missing second candidate has score -10000 and ends the search. With zero
  average this particular condition does not stop it. The complete ordinary
  iteration boundary, including terminal scores, personality depth and the
  selective mate margin, is specified by
  [SEARCH-ITERATION-TERMINAL-STOP](iteration-terminal-stop.md). This controlled
  operation exercises only the sole-candidate member of that rule.

The other terminal conditions are outside this diagnostic's score/depth range
and controls. A sequence that
simply exhausts its supplied iteration list has `stopped: false`. No host command
or pondering conversion is involved.

## Controlled diagnostic

`search.timedRootSequence` accepts exactly `{queries: [...]}` with 1..16 queries.
Each query contains exactly:

- `average`, `maximum`: integer centiseconds in 0..1000000, maximum ≥ average;
- `start`: initial clock observation, integer 0..4294967295;
- `inCheck`: boolean root condition, fixed throughout the query;
- `labels`: 1..8 unique candidate identities in initial exploration order, each
  containing 1..24 ASCII letters, digits, underscores or hyphens;
- `iterations`: 1..8 entries, one for each successive depth.

Each iteration has one entry per label, in the **initial label order**, regardless
of later exploration order. Each candidate entry contains exactly two replies:
initial and retry. Each reply contains exactly `score` (integer -2000..2000),
`work` (integer 0..50000), and `elapsed` (integer centiseconds 0..1000000).
The retry is ignored unless the actual window comparison admits it. All supplied
replies must be valid, including those never executed because of stopping.

Output is `{sequences: [...]}`. Each result contains:

- `limits`: final iteration, root and maximum limits, in seconds;
- `changes`: final current, previous and older best-change counts;
- `depth`, `stopped`, `selected`, `score`: last executed depth, stopping status,
  retained selected label and its ranking score;
- `searchId`: all work actually executed;
- `selectedSearchId`, `selectedElapsed`: work/time captured with the selected
  result, not values overwritten at the end of later work;
- `passes`: ordered executed child calls;
- `posts`: ordered immediate publications, excluding deferred finish output;
- `clockChecks`: ordered observations made by initialization and adaptive checks.

Each pass contains exactly `depth`, `candidate`, `attempt` (`initial` or `retry`),
`lowerBound`, `upperBound`, `score`, `searchId`, and `elapsed`. Work/time values
are cumulative after that reply. Each post contains exactly `depth`, `candidate`,
`score`, `searchId`, and `elapsed` captured at publication.

Each clock check contains exactly `stage`, `depth`, `index`, and `elapsed`.
Stage is `initialization`, `adjustment`, `root-completion`, or
`iteration-completion`. Initialization has depth/index zero. Other indices are
zero-based exploration indices; iteration completion uses the candidate count.
Two adjustments can therefore produce two consecutive observations at the same
depth/index. Depth-one root/iteration checks and depth-at-most-three best changes
consume no observation. These follow the adaptive-time contract.

`clockChecks` intentionally omits seed acquisition and report metadata reads;
it is an adaptive-controller trace, not a claim about every engine clock read.
Those omitted reads do not advance the supplied diagnostic time. Depth suffix,
notation and complete PV formatting are not part of this output.

Queries are independent. Reordering/repeating queries or shifting the starting
clock preserves their corresponding results. Renaming labels consistently
changes only label-valued outputs. Changing unused replies does not change an
observation. Unknown/extra fields, malformed labels and values outside the
declared domain are errors.

## Evidence and remaining scope

The [portable fixtures](../conformance/fixtures/timed-root-sequence-v1.json)
include threshold crossings within and between iterations, upper-bound retry
equality, stable ties and work ordering, coupled score-drop/best-change updates,
sole-candidate stopping, short/deep capture lifetime, partial iteration stops,
GM18100 allowances, clock wraps and bounded maximum request shapes.

The diagnostic supplies child replies and controls iteration advancement;
policy, ordering, retry and adjustment decisions are produced by the stated
rules. Its immediate-publication result composes capture eligibility with the
separately specified depth rule; it does not itself exercise final text output.

Legal candidates, recursive child results, charged work, polls, terminal/depth
stopping and final public output are connected by [complete ordinary search](ordinary-joined-search.md);
retained sessions use [ordinary session lifecycle](ordinary-session-lifecycle.md). Those
requirements are not qualified by this supplied-reply diagnostic alone.
Pondering remains outside the ordinary target; complete gameplay fidelity is
not established by these component fixtures.

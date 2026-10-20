# SEARCH-WORK-TIMED-ROOT-SEQUENCE — counted activity through search interruption

This contract connects [root scheduling](timed-root-sequence.md), the
[KingRE work clock](work-clock.md), [adaptive allowances](adaptive-time.md)
and interrupted-result ownership. Child scores and activity counts are supplied;
elapsed time is **not** supplied. The clock and stopping decisions must follow
from the executed activity. This diagnostic is not a complete recursive search.

## Activity and clock

Start with fresh candidate order, zero cumulative SearchID, zero relation-query
count, and the given clock origin. Retain cumulative counts across candidates,
retries and iterations within the query. Separate queries start fresh.

Each attempted child has a supplied score, a number of unadjusted relation
queries, and a number of search work units. Its activity order is explicit:
perform all its relation queries first, followed by its search units one at a
time. This order is a diagnostic control, not a requirement that normal
evaluation groups its work this way. Each unadjusted relation query contributes
one relation unit. Each search unit contributes one to SearchID. Work belonging
to an unattempted reply contributes nothing.

Within this bounded diagnostic, elapsed centiseconds are

`floor((3806 × SearchID + 770 × relationQueries) / 30000000)`.

Do not round each child separately: fractions accumulate across activity in
the entire query. Observations do not themselves add work. The starting clock
word translates all clock observations, with unsigned 32-bit wrap, but does
not change elapsed time or any search decision in this domain. The general
ledger's saturation and reset semantics remain defined in WC-LEDGER.

## Polls within a child

Immediately after each search unit that brings cumulative SearchID to a
positive multiple of 4096, perform an ordinary poll. There is no poll at zero.
Relation queries advance virtual time but do not advance this poll schedule.
Neither a new candidate, a retry, nor a new iteration restarts the schedule.

The poll reads the clock **after** crediting that unit and all preceding
activity. With no host command and ordinary, non-pondering KingRE policy, stop
if elapsed seconds are at least the retained maximum allowance. Use the
maximum allowance, not the adaptive root or iteration allowance. Average zero
does not disable a nonzero maximum. The two-zero-allowance behavior follows
TIME-ADAPTIVE-SEQUENCE.

A poll stop interrupts the attempt immediately, including when the poll
coincides with its final supplied unit. Count the work already performed, but
do not produce the supplied score. Do not perform its remaining units, a retry,
ranking, a best-change or score-drop adjustment, a new capture, or subsequent
root/iteration checks. Later candidates and iterations do not run.

Without a poll stop, finish the attempt normally. Its score then enters the
window/retry/ranking rules of SEARCH-TIMED-ROOT-SEQUENCE. Those rules also
govern adjustment admission, capture and the separate root/iteration stopping
checks, using the work-derived clock. Depth-one root/iteration checks do not
enforce the ordinary adaptive time limits; polls still enforce the maximum.
Thus crossing the maximum during relation-only work does not itself stop a
depth-one child before the next eligible stopping boundary.

## Result and report ownership

An interrupted attempt is not eligible to become the selected result. Preserve
the most recent best-result capture from completed candidates. It may belong
to the current iteration or an earlier one. Its score, identity, depth,
SearchID and elapsed time remain the captured values, even though total search
work and the latest elapsed time can be larger.

If no candidate has completed and been captured, the outcome has no selected
candidate and no score; captured depth, SearchID and elapsed time are zero.
This is a diagnostic outcome, not a specification of the public protocol's
fallback move or finish behavior. Already published captures remain unchanged.
The diagnostic does not add a finish-time post.

## Diagnostic interface

Operation `search.workTimedRootSequence` accepts `input: {queries}` with one
through four independent queries. Each query has exactly the fields and
bounded settings of `search.timedRootSequence`: `average`, `maximum`, `start`,
`inCheck`, `labels`, and `iterations`. Each child reply instead has exactly
`{score, work, relations}`. Score is an integer from -2000 through 2000;
both activity counts are integers from zero through 50000. There are one
through eight iterations and one through eight candidates, with exactly two
replies for each candidate in each iteration. Unused replies are ignored.
The reduced query-count bound keeps maximum-shaped responses within the
portable runner's one-mebibyte per-case limit.

The response has `output: {sequences}`. Sequence fields follow
SEARCH-TIMED-ROOT-SEQUENCE with these additions and differences:

- `selected` and `score` are null when no result has been captured; `depth` is
  the selected capture's depth, or zero when absent.
- Each pass has `completed`. An interrupted pass has `completed: false` and
  `score: null`; its SearchID and elapsed time include the interrupting unit.
- Clock checks may have stage `poll`. Every check also reports the observed
  `searchId` and `relationQueries`. Its index is the zero-based candidate
  exploration index, including for a retry of that candidate.
- Sequence-level `relationQueries` is the executed query count; `lastElapsed`
  is the final observed elapsed time. `selectedSearchId` and `selectedElapsed`
  continue to describe the retained capture, not the final work totals.

Clock-check rows cover initialization and adaptive/poll control observations.
They are not a log of every clock read used for captured metadata or diagnostic
reporting. No clock value, child score or activity after interruption may be
invented to complete the supplied schedule. Reject malformed requests rather
than coercing values or returning partial successful output.

## Remaining enclosing requirements

This composition removes supplied elapsed time and indivisible child work from
the earlier root diagnostic. Real child generation, score computation and the
chronological production of relation/search activity remain to be specified
and connected. Cross-search reset lifetimes, host stop/abort, pondering,
public fallback/finish and the known long-PV/overlong-clock research boundaries
are not closed by these controlled child tests.

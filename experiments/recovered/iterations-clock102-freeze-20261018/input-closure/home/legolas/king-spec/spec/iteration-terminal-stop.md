# SEARCH-ITERATION-TERMINAL-STOP — ordinary iteration-complete stopping

After an ordinary root iteration has completed every legal root candidate,
apply this decision after the easy-time adjustment and before starting the next
iteration. The decision consumes the completed iteration's best score, second
score and the immediately preceding iteration's best score. If there was only
one legal root candidate, its second score is -10000. Stopping retains the
completed ranking, selected result, principal variation and all charged work.
The search's terminal work totals are the totals after the complete iteration.
They are separate from the SearchID and elapsed time stored with the selected
best-result capture. That capture keeps the values from the instant the result
was selected; this stop does not restamp it with the later iteration totals.

This rule does not run after an interrupted child or a root-completion time
stop. It is separate from work polls and root-completion checks. The elapsed
test below uses the iteration allowance current after all adjustments at this
boundary.

## Functional decision

Let D be the completed iteration depth. Derive the fixed root endgame weight
from the root placement using EVAL-PHASE. Derive M, the root mate margin, from
D, the personality `sel` value and that endgame weight using
SEARCH-SELECTIVE-DEPTH. Test these conditions in order and stop at the first
one that holds:

1. D is greater than one and the signed 32-bit centisecond difference between
   current clock and search-start clock, multiplied by 0.01, is at least the
   current iteration allowance in seconds.
2. Average allowance is nonzero, D is greater than one, and both current and
   previous best scores are at least 9000.
3. Average allowance is nonzero, D is greater than one, and current best score
   is at most -9000.
4. Average allowance is nonzero, D is greater than one, the second score is at
   most -9000, and personality `ana` is zero.
5. D is greater than 61.
6. D is at least personality `md`.
7. Current best score is at least `10000-M`.
8. Current best score is at most `-10000+M`.

If none holds, continue to the next iteration. Conditions 2–4 are disabled
when average allowance is zero and do not apply at depth one. The mate-bound
conditions are not subject to either gate.

The ordinary public `go` path uses personality `md`; a recorded XBoard `sd`
command does not replace it. The value 999 is the ordinary default and is
valid, but the independent D>61 condition prevents an ordinary search from
executing hundreds of iterations. Explicit-depth search modes are outside this
contract.

## Clock arithmetic

Treat each clock as an unsigned 32-bit word. Subtract start from current modulo
2^32 and interpret the result as signed 32-bit centiseconds. The comparison is
the binary64 expression `elapsedCentiseconds * 0.01 >= allowanceSeconds`.
This preserves both wraparound and the original comparison boundary; it is not
an instruction to wait for host time.

## Runnable scalar diagnostic

`search.iterationTerminalStop` accepts `{queries:[...]}`. Each query contains
exactly:

```
{rootPlacement, iterationDepth, selectivity, maximumDepth, analysisMode,
 averageCentiseconds, bestScore, secondBestScore, previousBestScore,
 startClock, currentClock, iterationLimitSeconds}
```

`rootPlacement` is the placement field of the root FEN. Depth is 1..64,
`maximumDepth` is 1..999, `selectivity` is signed 32-bit, clocks are unsigned
32-bit words, scores are integers -10000..10000, `analysisMode` and average
centiseconds are integers 0..2147483647, and the iteration allowance is a
finite nonnegative number of seconds. Those last three values are supplied
caller state. The output per query is
`{stop,reason,elapsedCentiseconds,rootEndgameWeight,mateMargin}`.

The complete response is `{version:1,output:{results:[...]}}`, with exactly
one result per query in input order and no additional fields. `stop` is Boolean;
`elapsedCentiseconds` is the signed integer difference defined above;
`rootEndgameWeight` is the integer EVAL-PHASE endgame weight (0..256), and
`mateMargin` is the integer M derived above. `reason` identifies the first
true decision row, using exactly these strings:

| Functional decision row | `reason` |
| --- | --- |
| 1: elapsed iteration allowance | `"elapsed52"` |
| 2: current and previous winning score | `"confirmedWinningScore"` |
| 3: losing best score | `"losingBestScore"` |
| 4: losing alternative score | `"losingAlternativeScore"` |
| 5: iteration ceiling | `"iterationCeiling"` |
| 6: personality depth | `"personalityDepth"` |
| 7: winning mate bound | `"winningMateBound"` |
| 8: losing mate bound | `"losingMateBound"` |

If no row holds, `stop` is false and `reason` is null. Otherwise `stop` is
true. The label `elapsed52` is a diagnostic spelling, not a replacement for
the current iteration limit or an instruction to use a fixed multiplier.

The diagnostic supplies completed ranking scores to isolate this consumer.
Those scores are outputs of the enclosing root iteration, not additional
engine settings. It deliberately has no supplied mate margin, explicit depth
cap, anticipating flag or `sd` field: phase and M are produced by referenced
contracts, while this ordinary boundary fixes anticipating false and the
explicit-depth mode disabled.

## Evidence and boundary

Observed ordinary searches demonstrate the depth-two `losingAlternativeScore`
stop and a nearby continuing search. Component cases additionally distinguish
the score threshold, previous-best, average-allowance and analysis gates. Clock ordering,
personality-depth, global ceiling and mate-bound cases are composed from their
independently qualified producer and consumer rules; they are not claimed as
new natural original-search witnesses.

Pondering/anticipating conversion, analysis-mode search lifetime, explicit
depth modes, root production and public final output remain in their separate
contracts.

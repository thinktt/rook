# EVAL-QUIESCENCE-DISPOSITION — static returns before tactical continuation

This connects [quiescence evaluation selection](quiescence-entry.md) to its
immediate search decision. The evaluation is produced from setup and move
history; its score and bounds are not diagnostic inputs.

## Request and result

`evaluation.quiescenceDisposition` accepts exactly the same input as
`evaluation.quiescenceEntry`, with all its domains and state-lifetime limits.
Establish and evaluate the history, apply the final ordinary move, and select
its evaluation as specified there. The current position is not in check;
earlier draw, cycle and terminal-ply admission are outside this operation.

Return the same `{results: [...]}` sequence, adding `disposition` only to the
last result. Let L and U be that result's lower and upper evaluation bounds,
S its selected score, and alpha and beta the requested search window.

| First satisfied condition, in this order | `action` | `reason` | `score` |
| --- | --- | --- | --- |
| L >= beta | `return` | `lower-bound` | L |
| U <= alpha | `return` | `upper-bound` | U |
| S >= beta | `return` | `stand-pat` | S |
| None | `tactical` | `null` | `null` |

`disposition` has exactly these three fields. All comparisons include
equality. Return the indicated value without clipping it to the window and
without replacing an evaluation bound by S. Bounds are tested before the
score; a bound return remains the reason even when the score also satisfies
the stand-pat condition. The ordinary final result's `score` remains S and
can differ from `disposition.score`.

This decision performs no further evaluation or relation work and does not
alter the selected result's retained state. Each request is independent.

## Meaning of tactical continuation

`tactical` means that these static checks did not return and tactical move
production is the next stage. It does not assert that a tactical move exists,
that any candidate is legal or eligible, or that a child is searched. It is
not a completed quiescence result. This operation stops before tactical move
generation, candidate filtering/ranking, recursive children, final upper-bound
limiting, and result/PV publication.

The contract composes an admitted evaluation and its immediate consumer, not
an entire recursive call. The declared history domain does not claim natural
search reachability for every diagnostic sequence. Whole-search admission,
retained-state lifetimes across siblings, and downstream continuation remain
separate requirements for full engine conformance.

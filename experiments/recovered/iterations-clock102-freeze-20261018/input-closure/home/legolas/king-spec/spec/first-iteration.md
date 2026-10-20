# SEARCH-FIRST-ITERATION — complete deterministic first root iteration

This diagnostic composes position/history, generated legal moves, recursive
quiescence search, root ranking, principal variation and charged work. It
computes every child result. No candidate list, search window, child score,
evaluation result, work amount or selected move is supplied as an input.

## Request and scope

`search.firstIteration` accepts exactly `fen`, `moves`,
`personalityParameters` and `controls`.

Use the FEN normalization, coherent en-passant, turn-legality, history length
and complete fixed parameter vector specified by
[SEARCH-QUIESCENCE-TREE](quiescence-tree.md). The controls are exactly
`{iterationDepth:1, rootPass:"first-unrestricted",
learnedState:"fresh-ordinary-search", pondering:false}`. There is no
`rootMove` input and no requirement to select a non-checking root child.
Preserve history and piece chronology instead of rebuilding only the final
placement. Start with fresh ordinary-search learned state, randomness zero,
and the root evaluation context produced from that position.

The root must have at least one legal move. All of its legal moves participate,
including moves giving check and those whose child returns before producing a
tactical list. The entire iteration must finish before a host poll,
interruption, the 4096th charged search visit or a principal variation longer
than 63 moves. A resource/domain failure is an error, never a partial result.
These diagnostic bounds do not restrict ordinary engine gameplay.

Stop at completion of this first iteration. This is a requested diagnostic
boundary, not an assertion about where adaptive timing would stop. Root
preparation establishes context but its work is excluded from this response.
Charge counters start at zero after that preparation.

## Generated roots and child search

Derive the full legal root candidate sequence using the position/history
generation order in [SEARCH-ORDINARY-CANDIDATE-PRODUCTION](search-candidate-production.md).
Use that contract's legal-generation order, not its subsequent non-root ranking.
No prior-root preferences or learned priorities reorder this initial sequence.
Visit each candidate once in that sequence; ranking completed candidates does
not reorder candidates still awaiting their visit.

Each child is searched at ply one and target ply one. Compose the recursive
rules in SEARCH-QUIESCENCE-TREE, without that diagnostic's selected-child
non-check/nonempty-list admission restriction. Check evasions, static returns,
empty lists and repetition returns follow the same recursive rules. Use actual
move-produced state and preserve the root's evaluation context throughout.

For the first two roots, the incoming root window is [-10000,10000]. For each
subsequent root, its lower boundary is the second-highest score among completed
roots; its upper boundary remains 10000. Equal scores occupy separate ranked
positions. There is no random score adjustment in this diagnostic.

Search the child with the negated window: child lower is -10000 and child upper
is the negation of the incoming root lower. Negate the returned child score to
obtain this root's score. A returned bound is consumed as returned; do not
substitute an exact full-window score or perform a best-window re-search.

## Ranking, PV and retained state

Rank completed roots by descending returned score, preserving visit order for
equal scores. `bestScore` is the first ranked score; `secondScore` is the second
ranked score, or -10000 until two roots have completed.

Replace the best principal variation only for a strictly higher root score.
The replacement consists of that root move followed by its returned child PV.
A later equal score preserves the earlier best PV. Child PVs may be empty even
when their results affect ranking. The completed iteration's score and PV are
the final best score and PV, not necessarily the last root's result.

Each child inherits the root's retained evaluation state. Returning restores
that root state before another child begins; an earlier child's final subtotal
or evaluation age must not become the next child's inherited value. Shared pawn
classification history follows EVAL-SEARCH-PAWN-SEQUENCE across full evaluations
in actual visitation order. It is not reset between root candidates. An
implementation may represent this behavior differently; no storage layout is
required by this contract.

## Response

The output is exactly `{candidates, steps, score, principalVariation, work}`.

`candidates` is the complete initial ordered list. `steps` has one entry per
candidate, in that same order. Each entry is exactly:

```
{move, window:{lower,upper}, score, bestScore, secondScore,
 childPrincipalVariation, principalVariation, work}
```

Moves use `{move,kind}` descriptors as in SEARCH-QUIESCENCE-TREE. PVs are ordered
arrays of these descriptors. All scores and window endpoints are integer
values in [-10000,10000]. `childPrincipalVariation` is the actual returned
child PV; `principalVariation` is the retained best root PV after that result
has been consumed.

Every `work` is exactly
`{searchCounterDelta, chargedSearchUnits, chargedRelationQueries}`. Step work
is cumulative through that child's completed result. Search-counter and charged
search deltas agree in this single-lane diagnostic, are positive and below 4096,
and strictly increase between roots. Relation charges are nonnegative integers
and never decrease. Final work equals the final step's work. Root preparation
and any activity after the diagnostic boundary are excluded.

These fixtures qualify composition within this diagnostic. They do not define
later iterations, arbitrary personalities/settings, real-time command arrival,
adaptive work-clock stopping, persistent sessions, or full game conformance.

# SEARCH-FAST-ENTRY — fast evaluation, cutoff and retained result

This contract starts after an ordinary non-root search has passed its early
draw checks and found no usable remembered score. It specifies whether the
fast evaluation is requested, how its result enters the shallow-cutoff decision,
and what a successful cutoff retains for later searches.

## Admission and consumption

Use the current node's endgame weight, current iteration depth and personality
selectivity in [SEARCH-SELECTIVE-DEPTH](selective-depth.md). Let A be its node
adjustment and d the target ply minus current search ply.

For each color's **current** material counts, define

`H = (N + B + R + Q + floor((N + R) / 16)) mod 16`.

The fast evaluation is requested exactly when all of these hold:

- the preceding move is ordinary, not castling or en passant;
- it is not a promotion;
- its destination was empty before that move;
- at least one color has H at least two;
- d is at most A.

Pawns do not contribute to H. Neither the previous position's material counts
nor the moving color alone decides the material condition. With at most
fifteen non-pawns per color, H is the ordinary non-pawn count. Normalization
also applies to the larger independently supplied diagnostic counts.

If admitted, request the fast static score and pass it to
[SEARCH-FAST-CUTOFF](fast-cutoff.md). Its score/check/depth and pressure guards
still apply. Admission does not itself require being out of check, a sufficiently
high score, or d at most two. For example, d=3 can cause a fast-evaluation
request even though the resulting fast-cutoff attempt must reject that depth.
Likewise a check guard can reject the cutoff after fast evaluation was requested.
This ordering cannot be replaced with early suppression of that request.

If admission fails, neither fast evaluation, pressure nor threatened material
is requested through this path. If admission succeeds but the cutoff fails,
ordinary evaluation is the next continuation. A successful cutoff returns its
adjusted score and stores a remembered result before returning.

At this entry, promotion and nonempty-destination cases have already been
excluded. Therefore the capture-exception guard inside SEARCH-FAST-CUTOFF
cannot be true for an admitted query. Its broader direct diagnostic cases
remain useful component tests, but are not reachable combinations through
this entry contract.

## Retained result

Use [SEARCH-REMEMBERED-RESULTS](remembered-results.md) to store the cutoff
score with this search's current ply, target ply, lower and upper window bounds.
The lower window bound is the original input bound. With an initially empty
result context there is no move hint, quiet-mate marker or marked-depth marker.
The returned score is at least the upper bound, so the retained permission
is lower-only, including equality. Zero and negative cutoff scores are stored
as well as positive scores.

Later queries follow the remembered-results contract, including required depth,
mate-distance score normalization and successful mate-query depth effects.
The original cutoff score need not be returned by every later query: a deeper
ordinary query or a different window may have no usable score even though a
lower-bound record remains present.

If this fast path does not produce a cutoff, it stores nothing. This statement
ends before ordinary evaluation; later search work may store other results.

## Diagnostic

The opt-in operation `search.fastEntry` accepts an ordered `queries` array
of 1..4096 objects. Each object has exactly:

- `cutoff`: one complete query from `search.fastCutoff`;
- `iterationDepth`, `selectivity`, `endgameWeight`: the corresponding inputs
  and domains from `search.selectiveDepth`;
- `moveKind`: `ordinary`, `enPassant` or `castling`; a non-ordinary kind requires
  null `cutoff.capture.promotion`;
- `currentMaterial`: White/Black named counts with the same domain as
  `search.captureException` material, distinct from the previous material
  supplied inside `cutoff.capture`;
- `lowerBound`: integer −10000 through one less than `cutoff.upperBound`;
- `followups`: 1..4 objects containing `searchPly` (0..63), `targetPly` (0..64),
  `lowerBound` and `upperBound` (integers −10000..10000, strictly ordered).

Each query starts with an empty remembered-result context. Its follow-ups
query the same position identity and conflict group, in their supplied order.
State from one query does not carry into the next query. Follow-up target ply
may be below its search ply, as allowed by SEARCH-REMEMBERED-RESULTS.

Output is `results`, one object per query, containing:

- `cutoffScore`, `pressureChecked`, `materialThreatQueried`: as in the cutoff
  contract, all absent/false if the attempt was not admitted;
- `fastEvaluationQueried`: boolean observation of the fast-score request;
- `resultStored`: boolean observation of a retained-result write;
- `remembered`: ordered follow-up observations with the fields and meanings
  from SEARCH-REMEMBERED-RESULTS.

`cutoff.staticScore` and `cutoff.materialThreat` are controlled responses,
used only if requested. They are not assertions about what a full evaluator
would produce for the supplied context. The diagnostic accepts independently
supplied move, material, phase, check and pressure facts; it does not certify
a reachable board. It imposes no internal representation or production command.

## Remaining composition

These tests qualify actual entry, cutoff, storage and query composition with
controlled evaluator responses and an empty initial result context. They do
not establish fast-score generation, threatened-material generation and its
charged work, full board/history-derived identity, existing cache hints or
markers, the preceding draw/cache decisions or continuation through ordinary
evaluation. Query observations are not complete SearchID or work-clock charges.

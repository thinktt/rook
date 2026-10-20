# EVAL-QUIESCENCE-ENTRY — selecting evaluation from move-produced state

Working composition contract. A non-check position admitted to ordinary
quiescence evaluation chooses between the full and fast evaluations defined
by [EVAL-RETAINED-SEQUENCE](retained-evaluation.md). The choice depends on
current material, the produced fast score, the search window, and the
preceding move in its parent position. This contract connects those inputs
to actual setup and forward moves; it does not accept a supplied static score.

## Diagnostic request

`evaluation.quiescenceEntry` accepts exactly `fen`, `percentages`,
`averageDepth`, `cfd`, `sop`, `history`, `move`, `alpha`, and `beta`.

Initial setup and personality settings have the domains and fixed-root
semantics of [EVAL-MOVE-SEQUENCE](evaluation-moves.md). `history` contains
0..255 of that contract's `{move, kind}` transitions. Establish the initial
full evaluation, then perform this history with its selected full/fast
evaluations, preserving chronological state and pawn retention.

`move` is one additional legal coordinate move, with a required promotion
suffix when applicable. It cannot be a diagnostic null move. Its resulting
side to move must not be in check. `alpha` and `beta` are integers satisfying
`-10000 <= alpha < beta <= 10000`. They describe the window for this final
position, not the root position.

Apply the final move as in EVAL-MOVE-SEQUENCE, but choose its evaluation using
the rules below. No final evaluation kind, inherited value, material count,
capture classification, phase, fingerprint, pawn order, or fast score is
supplied. Missing, extra, malformed, and out-of-domain inputs are errors.

This diagnostic starts at admitted non-check evaluation, below the terminal
search-ply limit. It does not run prior repetition/cycle checks. History
length is a forward-state diagnostic bound, not the active recursive ply.
Neither repetition nor the reversible counter automatically stops this
diagnostic. It also does not establish that every admitted diagnostic
history would occur under a complete search's selection policy.

## Initial selection

For each color in the current position, let N, B, R, Q be its knight, bishop,
rook, and queen counts. Define the normalized material measure as

`(N + B + R + Q + floor((N + R) / 16)) modulo 16`.

If **both** colors have a measure at most one, perform full evaluation
immediately. There is no preliminary fast score in this case.

Otherwise perform fast evaluation using the inherited positional subtotal
and pawn-progress value, current position and fixed root context. Let F be
its final, side-to-move-oriented score, including the specified preference,
variation, endgame adjustment, and score scaling. Use F, not the unadjusted
base or a root-oriented score, for the following decision.

## Refresh after fast evaluation

Perform a full evaluation after the fast evaluation if either:

- `alpha - 250 < F < beta + 250`; or
- the preceding move satisfies [SEARCH-CAPTURE-EXCEPTION](capture-exception.md).

The window comparisons are strict. Equality at either endpoint does not
meet the window condition, but the capture exception can still require a
refresh. Classify the preceding move using its **parent position**, before
the move: promotion qualifies; an empty destination does not; otherwise the
captured color's material and pawn count determine the exception under the
linked contract. En passant does not acquire this exception merely because
it removes a pawn from a different square.

If a refresh is required, its complete full-evaluation result replaces the
fast result. Otherwise retain the fast result. Full evaluation refreshes the
retained pair and resets its age; a fast-only choice preserves them. Full
evaluation consumes the existing pawn retention established by earlier
evaluations, rather than forcing a fresh pawn recomputation. Relation charges
are those actually required by the selected evaluation sequence; the fast
stage has no relation charge.

## Response and observation boundary

Return `{results: [...]}` with the initial evaluation, all history results,
and the final selected evaluation. Each has the EVAL-MOVE-SEQUENCE shape.
Only the final result additionally contains:

`selection: {initialKind, fastScore, refreshed}`

- `initialKind` is `full` for immediate full evaluation, otherwise `fast`.
- `fastScore` is JSON `null` for immediate full evaluation, otherwise F.
- `refreshed` is true only for fast evaluation followed by full evaluation.

The final result's ordinary `kind` describes its selected result: `full`
for either full path, and `fast` for the fast-only path. Its `inherited`
member is observed after the final move but before either evaluation stage.
Its `retained`, score, bounds and relation count are observed after selection.

Each request starts independently. Previous requests cannot affect it.

This ends before the search consumes the selected bounds/score for a cutoff,
updates its window, produces tactical candidates, or searches children. It
does not specify root evaluation, the terminal-ply fast leaf, check evasions,
draw admission, sibling/backtracking effects, or general recursive search.
Those connections remain required for complete engine conformance.

[Quiescence disposition](quiescence-disposition.md) extends this diagnostic
through the immediate bound/stand-pat checks, still before tactical generation.

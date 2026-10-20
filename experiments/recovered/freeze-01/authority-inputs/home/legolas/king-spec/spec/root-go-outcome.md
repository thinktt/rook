# SESSION-GO-OUTCOME — one fresh ordinary `go`

This bounded contract connects public command setup to either a completed
ordinary move or the engine-defined fatal outcome for a generated empty legal
root. It is a composable diagnostic, not the complete ordinary-search request interface.

## Request

`session.goOutcome` version 1 accepts exactly `{commands, remainingTimeCs}`.
Start one fresh engine session in force mode, enter XBoard mode, process the
ordered setup commands, synchronize both clocks to `remainingTimeCs`, and send
`go`. `remainingTimeCs` is the public protocol clock value; it is not a
precomputed search allowance.

The current evidence domain is a canonical six-field `setboard` position with
empty history, `post`, `easy`, the complete neutral parameter vector with
`md=1` and `rnd=0`, equal 60000-centisecond clocks, no pondering, and no `sd`
command. A nonempty root is admitted only when it is in check and the complete
first iteration finishes below the existing resource bounds. These are
diagnostic qualification limits, not claims that histories, other profiles,
ordinary non-check roots, or other clock values are invalid engine inputs.

The request does not supply check state, legal candidates, terminal class,
score, SearchID, principal variation, selected move, or expected outcome.
The textual halfmove and fullmove counters remain part of the exact public
command, but `setboard` establishes the engine-visible position with halfmove
counter zero and notation fullmove one. Candidate generation and search use
that normalized state.

## Outcome

Generate the complete legal root sequence from the reached position.

When it is nonempty, perform the normal first unrestricted iteration under the
existing position, evaluation, recursive-search, reporting and capture rules.
The complete iteration must finish before the first 4096-work host poll.
Derive every best-result capture, its cumulative charged-work clock, phase and
depth status, score normalization, and post-publication lifecycle. Do not infer
a single post or a zero elapsed clock merely from `md=1`.
Return exactly:

```text
{kind:"move", posts:[...], move:COORDINATE_MOVE}
```

Each semantic post contains exactly `depthToken`, `evaluation`, `searchId`,
`pv`, and `engineCentiseconds`, with the meanings already used by
`session.searches`. Derive `pv` using [PV-NOTATION](pv-notation.md), with
this post's numeric fields and complete-token byte limit.
`searchId` belongs to the captured best-result post; it is
not automatically the total work after every root has finished. `move` is the
first semantic move of the selected final PV. After observing the move, a
conformance adapter may send `quit` and require clean cleanup, but that cleanup
is not part of the `go` result.

When the generated legal root sequence is empty, do not construct a search
result or classify the position as checkmate or stalemate for this operation.
Publish no semantic search post, move, or terminal-result event and terminate
the engine process with status 1 and no signal. Return exactly:

```text
{kind:"fatalExit", exit:{code:1,signal:null}, posts:[], move:null}
```

This rule is selected by generated legal-root count, not by a supplied label,
native adjudication text, a generic search failure, timeout, resource error,
or arbitrary process exit 1. Adapter/process failures are conformance errors,
not this union arm.

## Evidence boundary

The checked fixture qualifies a complete public post, move and successful
process completion. Both zero-root fixtures establish fatal exit 1. The
stalemate case additionally qualifies literally empty post-`go` stdout and
stderr; complete literal streams are not qualified for the checkmate case.
Therefore this contract forbids semantic post, move, and game-result
events on both fatal paths but does not claim byte-for-byte empty checkmate
stdout or stderr. Incidental nonsemantic diagnostics are outside this version.

The request and response contain only the semantic fields defined above.

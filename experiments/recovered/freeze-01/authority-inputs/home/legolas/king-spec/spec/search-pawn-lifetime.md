# SEARCH-PAWN-LIFETIME — ordinary search boundaries

This contract connects [retained pawn behavior](retained-pawn-structure.md)
to ordinary searches. It does not impose a physical storage layout or require
an implementation to keep discarded search-local data in memory.

## Lifecycle rule

An ordinary search begins with cleared retained pawn state: every retained
group has identity zero, zero base scores and empty pawn descriptors. State
from an earlier completed search does not carry into this new search, even
when the same process, personality or position is reused without `new`.

Evaluation at the root can populate this initially cleared state before the
first iterative-deepening iteration. Do not clear it again merely because an
iteration starts. Retained selection, replacement, structural order and current
evaluation rules continue across evaluations and iterations of the same search.
Iteration setup preserves the existing retained state before root exploration.

This establishes the search boundary, not when an implementation must physically
release storage. It does not characterize idle commands' internal mutations,
interrupted/ponder/analysis/solve searches, or history-derived pawn ordering.
The [retained subtotal](retained-pawn-subtotals.md) diagnostic supplies effective
context; [fixed-root pawn sequences](search-pawn-sequence.md) additionally
produce it and retain pawn state across explicit evaluations. Neither is a
complete search, history-update or alternate-mode contract.

## Public session diagnostic

`session.searches` exercises an ordered sequence in one fresh engine session.
Input is `{searches: [...]}`, with 1..16 objects containing exactly:

- `commands`: 1..256 single-line setup commands, each at most 2000 characters;
- `allowanceCs`: integer 1..1000000, supplied as remaining centiseconds before
  this search.

The session uses XBoard command semantics and the target's reset-safe work
clock. Process each command list in order, supply `time allowanceCs`, and start
the search with `go`. Wait for the selected move before proceeding to the next
list. Preserve command/game/personality state between lists. Finish cleanly
after the last move. There are no asynchronous stop/ponder messages in this
diagnostic, and no implicit new game between searches.

The bounded setup vocabulary is `new`, `force`, `easy`, `post`, `undo`,
`level 0 5 0`, coordinate moves with optional lowercase promotion, FEN
`setboard`, and `cm_parm` integer assignments with optional `default`.
In the ordinary explicit-settings domain, each list starts with `new` or
`force`, contains `force`, and explicitly
establishes `rnd=0` and `md` from 1 through 4. Nonzero randomness and other
depth limits are outside this diagnostic, not forbidden production behaviors.
The final parameter state after all `default` tokens must still satisfy those
limits. Setup must not trigger an automatic search; use `force` before moves.
Malformed structure, extra fields, multiline strings and `go`/`quit` inside
setup lists are rejected rather than interpreted as extra operations.

There is one additional, bounded inherited-settings domain:
[SESSION-SEARCHES-INHERITED-SETTINGS](persistent-ordinary-session.md#session-searches-inherited-settings--public-companion-and-limits).
It is the three-search, standard-start neutral-md3 A/B/A topology specified
there: the first list establishes the settings once, the second list is
`["force","undo",B]`, and the third is `["force","undo","undo"]`.
For this domain only, later lists must inherit `md=3` and `rnd=0` and must not
restate them. This exception overrides the per-list explicit-settings rule,
not the common response or transport rules. It does not admit arbitrary
inherited-setting action sequences.

Output is `{results: [...]}`, in input order. Each result contains:

- `move`: the selected coordinate move, including any promotion suffix;
- `posts`: the complete ordered semantic search reports before that move.

Each post has `depthToken`, `evaluation`, `searchId`, `pv`, and
`engineCentiseconds`. Preserve the reported depth token, integer evaluation,
integer SearchID, principal-variation text and work-clock elapsed centiseconds.
For this diagnostic, a search report has five fields: numeric depth token at
least 1000, signed integer evaluation, signed integer centiseconds, unsigned
integer SearchID, and nonempty PV text. Trim the PV's outer whitespace and
normalize digit `0` to letter `O` (the castling spelling convention); retain
other PV text and report order. The depth token is not reduced to nominal depth.
Do not reduce this to the final post or compare only the move. Ignore startup
banners, parameter echoes and transport carriage returns, not search reports.
Timeout, nonzero/signaled exit or forced termination is not a passing result.

## Evidence limits

Public fixtures cover eight-search persistence, repeated positions without
`new`, short/deeper transitions, personality/history changes, both root colors,
a sparse pawn position and return to the initial position. Fresh-process and
prefix repetitions check sequence independence where the input resets state.
Their 18100-centisecond allowance is a controlled lifecycle-test budget, not a
new calibration for the sampled personalities.

Additional component evidence distinguishes search-entry clearing from
cross-iteration retention. The public examples do not, by themselves,
completely qualify search or evaluation.

# SESSION-ORDINARY-ITERATIONS — bounded persistent ordinary searches

Status: original-backed bounded contract. The semantic example and its public
companion come from the same complete original session in which each following
action was sent only after the preceding selected move was received. The
contract is intentionally limited to the domain below.

## Request

Operation `session.ordinaryIterations`, version 1, has exactly this input:

```
{initial, personalityParameters, schedule, actions, controls}
```

`initial` is exactly the standard initial six-field FEN and an empty move
history. `personalityParameters` is the complete neutral 30-field vector of
SEARCH-ORDINARY-ITERATIONS with `md:3` and `rnd:0`. These effective settings
are established once and inherited by every search in the session; commands
must not be invented to restate them. `schedule` is exactly
`{levelCommand:"level 0 5 0", remainingTimeCs:18100}`.

`actions` is the ordered nine-action topology below. Every search object is
exactly `{kind:"search", completedIterations:3}`. The move object is exactly
`{kind:"move", move:B}`. Every `force` or `undo` object contains only `kind`.
`B` is any coordinate move legal from the restored initial position and must
differ from search A's selected move.

```
search, force, undo, move B, search, force, undo, undo, search
```

`controls` is exactly:

```
{arrival:"wait-for-each-move-v1", completion:"natural-md3",
 inheritedSettings:"session-global-md3-rnd0-v1", pondering:false,
 searchState:"fresh-each-go", workOrigin:"after-root-preparation"}
```

Wait for each search's selected move before sending the next action. There is
one fresh process, no implicit `new`, no pondering, no asynchronous stop, and
no supplied seed, clock sample, child answer, root answer or completion flag.
At each `go`, reset search-local ordinary state as required by the referenced
search contracts while retaining the protocol position, history, configured
personality and time-control settings. `force` changes play mode but does not
replace the position. `undo` removes exactly the latest played move.

Every reached root must be nonterminal, not in check, and have a nonempty
complete legal root-candidate set. The three-iteration limit does not require
internal iterative ordering, and every admitted search completes before the
first 4,096-work host-poll boundary. A request or observed answer outside these
bounds is a diagnostic-domain failure. It does not establish that the engine
would reject the same position, action, depth or work amount in normal play.

This contract admits only the standard-start neutral-md3 resource domain. Its
published example uses `B=d2d4`; the request rule admits any legal `B` within
the stated action topology and resource bounds.

## Response

A successful response is `{version:1, output:{initial,actions,searches,final}}`.
No fields may be omitted or added.

Every snapshot (`initial`, each action's `before` and `after`, every search's
`root` and `after`, and `final`) contains exactly:

```
{initialFen, currentFen, moves, sideToMove, mode}
```

`moves` is the complete coordinate history from `initialFen`. `mode` is
`force`, `play-white`, or `play-black`; the latter two identify the side the
engine was assigned by the preceding `go`. Snapshots reflect the action after
it has completed, including the selected engine move for a search. The fixture
snapshots are derived by applying the accepted commands and observed selected
moves under the position/move contracts; they are not additional engine output.

Each action records its zero-based `index`, `kind`, `before` and `after`.
Search actions also record `searchIndex`; the supplied move action also records
`move`. Each of the three search objects contains exactly:

```
{index, root, completedIterations, ordinary, selectedMove, after}
```

`ordinary` is the complete SEARCH-ORDINARY-ITERATIONS output: every initial
candidate, iteration order, root window, actual returned score, child PV,
retained score/PV and cumulative work. It is computed from the reached root
and fresh per-search state, not supplied by the session request. The selected
move is the first semantic move of the final result PV and is applied before
`after` is recorded. A2 must reproduce A1's root identity and complete ordinary
answer in this deterministic domain.

For every search, `initialCandidates` and every iteration candidate list must
contain exactly the complete legal move set of that search's `root`. Each root
move must be legal there and its move kind must match the transition. A child
PV is a legal continuation after its associated root move; retained, iteration
and result PVs are legal continuations from the root. Move kinds are exactly
`ordinary`, `castle`, and `enPassant`. A promotion is `ordinary` with a
lowercase promotion suffix in its coordinate move; `promotion` and
`en-passant` are not move-kind spellings.

Iteration score and PV close from the last root's retained best and PV. The
final search result is independently required to equal the last completed
iteration under SEARCH-ORDINARY-ITERATIONS. Search work is measured separately
from the stated origin for every `go`; it is not accumulated across searches.

## SESSION-SEARCHES-INHERITED-SETTINGS — public companion and limits

The public companion uses `session.searches` and preserves the
actual command grouping: its first list establishes `md=3` and `rnd=0`; the
second and third lists inherit those settings and do not repeat parameter
commands. Admission evaluates effective settings across the ordered session:
the first list must establish the admitted values, and later lists inherit them
unless an explicit command changes them. This companion requires effective
`md=3` and `rnd=0` for all three searches and rejects restatement or change in
the second and third lists.

The companion's expected values are the complete ordered public posts and
selected moves observed while waiting for each move, with successful session
completion. It is the bounded exception to the per-list explicit-settings
admission in [session.searches](search-pawn-lifetime.md#public-session-diagnostic),
not a general extension to arbitrary inherited-setting sequences.

The response contains only the fields defined above. This contract does not
cover nonstandard starts, nonempty initial history,
other personalities/depths/randomness/time controls, pondering, interruption,
game termination, more or fewer actions, or persistence after a failed search.

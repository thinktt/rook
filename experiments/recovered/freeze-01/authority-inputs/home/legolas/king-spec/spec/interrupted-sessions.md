# SESSION-INTERRUPTED-SEARCHES — ordinary search with queued host commands

An ordinary search can accept a host command while exploring a candidate.
Host commands are examined at search-work polls, every 4,096 counted search
units. A diagnostic queue makes their arrival reproducible: one pending
command is available at each successive poll, starting with the first.
Relation work contributes virtual time but does not advance that poll count.
This does not require any particular wall-clock delay or transport mechanism.

`?` requests a graceful search stop. With an available selected result, finish
the search and play that result. The result need not describe the branch being
explored when the command was received. Preserve already captured report
metadata and the ordinary deferred-publication rules; do not fabricate a new
completed result from an interrupted child.

`force` aborts ordinary thinking and returns to force mode without playing a
move. Reports already published remain visible; do not publish an additional
successful-completion report. The searched game position/history is not
advanced by the interrupted exploration. This is distinct from `?`, which
advances the game by the selected move.

`post` and `nopost` respectively enable and disable subsequent search-post
publication. These commands do not themselves stop the search. A `.` command
publishes a live status observation even when search-post output is disabled.

## Live status

A live status reports elapsed virtual centiseconds, cumulative SearchID,
the current depth token, remaining root candidates, total root candidates,
and the current exploration path. It is not a copy of the most recently
published best line. The remaining count excludes the current candidate.

The exploration path can contain a null-search step. Render it as the literal
word `null`, leave pieces and castling rights unchanged, remove any en-passant
opportunity and switch the side to move for interpreting subsequent path
moves. Continue displaying the path after this step. This is a diagnostic
search event, not an additional legal move in the played game or a command
that the user can submit as a game move.

## Controlled session diagnostic

`session.interruptedSearches` accepts exactly `{searches: [...]}` with 1..16
ordered searches in one persistent engine. Each contains exactly:

- `commands`: 1..256 setup command strings, each at most 2,000 characters;
- `allowanceCs`: integer 1..1000000, applied as `time` after setup;
- `queued`: zero to four diagnostic host commands.

Setup starts with `new` or `force`, contains `force` and `easy`, and explicitly
selects `post` or `nopost`. Its vocabulary is `new`, `force`, `easy`, `post`,
`nopost`, `undo`, `level 0 5 0`, coordinate moves (optional lowercase promotion),
six-field `setboard`, and `cm_parm` assignments or `default`. Setup positions,
moves and rewinds must be valid. Use the existing personality and position
contracts for their meaning; this diagnostic does not broaden accepted engine
parameter domains.

Every search explicitly sets `rnd=0`. All random-setting assignments in its
setup must be zero. It also explicitly sets `md` within 1..20 when queued
commands are present, or 1..4 otherwise. Defaults must not override these
final settings. The higher depth permits observation of host polls; it is not
a separate production default. Pondering remains disabled.

A nonempty queue ends in `?` or `force`; any preceding entries are `.`, `post`
or `nopost`. An empty queue runs to ordinary completion. The diagnostic
requires that search reaches each queued command's poll: an early natural
completion is not a passing execution of a later scheduled interruption.
After the search ends, apply the next search's setup in the same process.
There are no implied resets between searches or before `force`-only setups.

The result is `{results: [...]}`, one entry per search, each containing an
ordered `events` array. Retain interleaving and multiplicity:

- A post is `{type: "post", depthToken, evaluation, searchId, pv,
  engineCentiseconds}`.
- A status is `{type: "status", engineCentiseconds, searchId, depthToken,
  remaining, total, pv}`.
- A played move is `{type: "move", move}`, using coordinate notation.

Numbers are JSON numbers, not strings. `pv` uses space-separated move text;
castling is normalized to `O-O` or `O-O-O`. Preserve `null`. Setup echoes,
spacing, idle synchronization echoes and abort diagnostic wording are not
included in this semantic event stream. A stopped or ordinarily completed
search has exactly one final move event; an aborted search has none.
The process must exit cleanly after all searches. A timeout, forced kill,
malformed event or incomplete command schedule is failure, not parity.

## Composition evidence and limits

The [fixtures](../conformance/fixtures/interrupted-sessions-v1.json) pair each
interruption with a same-position follow-up search and a fresh reconstruction.
After a graceful stop, `undo` restores the played move before the follow-up;
after abort, no undo is needed. This tests publicly observable restoration and
subsequent search results, not equivalence of every hidden state quantity.

The examples cover first-poll stop, status before abort, successive status
polls, enabled/disabled/toggled posts, a live null-search path and retained
capture reports. They use explicit personalities and current calibrated
allowances, including GM18100, with randomness disabled. Original-side public
observations supply expected event streams. These are composition fixtures,
not a complete mathematical definition of recursive search.

The ordinary production host/timing scope, including full status-path output
and applied clock commands, is defined in
[session lifecycle](ordinary-session-lifecycle.md#ordinary-host-and-timing-scope).
That broader production rule does not expand this diagnostic's queued-command
vocabulary or its fixture coverage. First-root fallback is defined by joined
search; its absence from these fixtures does not establish unreachability.
Randomized interruption coverage remains separate; excluded host modes are
not made ordinary requirements by this diagnostic.

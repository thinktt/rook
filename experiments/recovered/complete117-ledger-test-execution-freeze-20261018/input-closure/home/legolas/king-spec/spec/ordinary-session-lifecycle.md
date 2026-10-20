# Ordinary-play in-process session and reset lifecycle

This is the ordinary, non-pondering session contract. A session can remain alive
across moves, searches, position changes and games. Restarting the process before
each move is not required. This versioned contract defines the required behavior;
its functional rules prescribe neither storage layout nor allocation.
Existing component diagnostics have narrower test domains, not narrower session
semantics. Pondering, analysis, hint, solve and interactive editing are not
required by this contract.

The production byte-stream interface, admitted command forms, numeric text
domains and exact replies are defined by
[KING-XBOARD-ORDINARY](ordinary-xboard-wire.md). The semantic transitions below
do not require a host to use only the fixed fresh-ingress command stream.

## State that persists

Keep the initial game position, the current chronological move prefix and its
resulting positions/reversible counts; effective personality parameters; time
schedule and accumulated game-clock adjustment; selected engine color and play
mode; post-output selection; and the reset-safe work-clock origin. A fresh
session has the initial conditions also used by the
[fresh ingress diagnostic](ordinary-play-ingress.md#fresh-startup-and-clock-state):
force mode, standard position, zero history/clock adjustment/work origin,
default parameters and the five-minute schedule. Posts and pondering are
initially disabled.

The current position and repetition history are not search caches. Reconstruct
search positions and the full active pre-root history using
[move sequence](move-sequence.md), [history admission](history-admission.md) and
[repetition admission](repetition-admission.md). Preserve up to 799 prior plies
for a subsequent search. The separately specified 800th-move protocol boundary
is not enlarged by retaining the process. Rewound or replaced branches are not
part of the active repetition history.

## Idle command transitions

The following rules concern valid ordinary commands between searches. Numeric
parameters retain their stated component domains; this section does not invent
a malformed-command grammar.

| Command | State change | State retained |
| --- | --- | --- |
| `new` | Restore standard position; clear active game history, reversible count, result and game-clock adjustment/measurement; select playing Black and the Black clock color | Personality, time schedule, post selection, configured clock policy and work-clock origin |
| `setboard FEN` | Establish the supplied placement, side, castling and EP as a new initial position; clear prior history, reversible count and game-clock adjustment/measurement; derive game result from the new position | Personality, time schedule, play mode, selected clock color, post selection and work-clock origin |
| `undo` / `remove` | Rewind one/two plies, saturating at the initial position; restore that position and reversible count, and recompute game result | Personality, schedule, play mode/color, accumulated clock adjustment and work-clock origin; no time refund |
| `force` | Disable automatic replies | Position/history, personality, schedule, clock adjustment and work-clock origin |
| `cm_parm ...` | Apply ordered parameter updates/queries under [PARAM-COMMAND](personality-configuration.md) | Position/history, schedule, game-clock adjustment and work-clock origin |
| `cm_parm default` | Restore parameter defaults except retained `opk` | Position/history, schedule, game-clock adjustment and work-clock origin |
| `level ...` | Replace the time schedule | Position/history, personality and the existing clock adjustment; do not retroactively recompute it |
| `time r` | Synchronize the game-clock adjustment from the then-current schedule, game-ply count and selected clock color | Position/history, personality, schedule and work-clock origin |
| `white` / `black` | Select Black/White respectively as both engine color and clock color, under the legacy command convention | Board side to move, play mode, history, personality and clock adjustment |
| `post` / `nopost` | Enable/disable search-post output | Position/history, search parameters and clocks |
| `easy` | Disable pondering and use the normal allowance branch | Ordinary position, personality and clock state |

`setboard` ignores supplied FEN halfmove/fullmove counters: its effective
reversible count starts at zero and notation fullmove at one. Replaying actual
moves then produces those values. It is therefore not interchangeable with
replaying a history that has repetition or reversible-count significance.

Recorded `sd` and `st` settings also survive game/position resets; `level`
clears the recorded `st` setting. Ordinary timed `go` uses the personality `md`
and allocated-time rules, not these recorded fields as replacement depth/time
caps. See [allocated search](allocated-timed-search.md).

After `new`, send `force` before replaying moves if no automatic search is
intended. In force mode a legal coordinate move advances history only. In normal
play it also causes an automatic search when the resulting side to move is the
assigned engine color and the protocol has not declared the game finished.
`go` explicitly selects the current side to move as the engine color and starts
the ordinary search. A selected move is applied before a following command acts
on the session. `quit` ends the process; a fatal empty-root exit likewise cannot
be reset into another search. See [root outcomes](root-go-outcome.md) and the
[joined outcome rules](ordinary-joined-search.md).

## Each ordinary search has fresh search-local state

Begin every search with empty remembered/transposition results, empty retained
pawn state, zero ordering-history scores/total and no killer preferences. Use
the current `tts` capacity and current parameter vector. Derive root evaluation,
legal candidate order, active contempt and all subsequent search values anew.
There is no cross-search reuse of a previous score, PV, best move, root ranking,
candidate-work ordering or interrupted child answer. Clearing is required at
the next search boundary, not at every idle command.

Within that one search, retain and update state across recursive calls and
iterative-deepening depths according to [ordinary search](ordinary-iterations.md),
[learned lifetime](learned-state-lifetime.md),
[pawn lifetime](search-pawn-lifetime.md) and remembered-result rules. A new depth
is not a new search. On completion, publish the result under
[joined search](ordinary-joined-search.md), apply its move and retain the resulting
game history. Do not carry the discarded search-local state into the next move.
After an abort without a selected move, the game position is unchanged; the
next search still starts with fresh search-local state. Graceful stopping and
first-root fallback remain distinct from abort.

## Clock and seed lifetimes

Game-clock adjustment and work-clock origin are different quantities. Idle
`new`/`setboard` clear the former, not the latter. `undo`/`remove` clear neither.
Use [TC-SESSION-SETUP](clock-session-setup.md) for schedule/synchronization and
[WC-LEDGER](work-clock.md) for charged time.

At ordinary search entry, read the current work clock for seed/allowance/time
origin as specified by the joined search. Start a new charged-work segment at
iterative search entry, carrying the last observed clock into its origin and
clearing segment counts. Preparation must not contribute hidden charge to the
new segment. Preserve the work-clock origin after the search and across idle
game-reset commands. Report elapsed differences, not absolute session uptime.

The game clock begins measurement at the search's start observation. If its
stored adjustment is A, the measurement began at clock C0 and the current clock
is C, the effective adjustment during measurement is the signed-32-bit wrapped
value of `A + (C - C0)`. Finishing stores that value and ends measurement, even
when the search stops without playing a move. An idle `time r` replaces the
effective adjustment with `B = 100 S(floor((p+b)/2)) - r`, using the schedule
and color definitions of TC-SESSION-SETUP. If received while measurement is
active, store the signed-32-bit wrapped value `B - (C - C0)` so that the current
effective value becomes B without restarting measurement.

For each nonfatal ordinary search acquire one new seed using
[RANDOM-SEED-LIFETIME](seed-lifetime.md): external seconds plus current work
clock, modulo 2^32. Retain it within the search; do not use a running PRNG stream
carried from the preceding search. Reusing a position or setting `rnd=0` does
not suppress this acquisition. Controlled seed injection is a separate optional
test capability: it substitutes the per-search seed, not a personality value
or a search answer. If exposed, document whether it is a constant override,
explicit next-search assignment or a stepped sequence; game reset must not be
silently assumed to restart that test sequence.
The required accepted-gate profile is the persistent constant override in
[GATE-SEED-COMMAND](gate-seed-command.md); the broader optional-control note
does not redefine its command, acknowledgment or consumed-seed observation.

## Meaning of reset and fresh-process equivalence

`new` is a game reset, not a complete startup reset. In particular, it does not
restore default parameters, restore the default time schedule, reset the work
clock to zero or restore every protocol option. `setboard` and rewind are even
narrower. There is no additional mandatory "factory reset" command.

A caller can keep the process alive, explicitly set the required parameters,
reconstruct the correct initial position/history, synchronize clocks and run
another fresh search. The same search-local inputs must yield the same search
behavior, but identical board and personality alone do not imply identical
answers: history, allowance, seed and clock observations must also agree.
Natural seeds can differ between a reused process and a fresh process because
the former retains a work-clock origin. This contract does not erase that
behavior to manufacture unconditional fresh-process equivalence.

## Qualification scope

Existing persistent-session, clock-setup, clock-seeded-session, pawn/learned
lifetime, interruption and joined-search fixtures exercise parts of this
composition. Their small depth/history/profile domains are diagnostic limits,
not restrictions on ordinary session use. The command/reset rules above do
not imply a separate observed witness for every row or every possible command
sequence.
The gameplay gate exercises in-process searches with explicitly matched seeds.
It does not compare naturally seeded fresh and continuous processes, and no
such universal equality is promised.

## Ordinary host and timing scope

The required operating profile has nonnegative elapsed intervals no greater
than 2,147,483,647 centiseconds per search. This limits elapsed differences,
not absolute session uptime, and does not require restarting between searches.
Longer search lifetimes and their overflow behavior are outside this handoff;
no rejection, wraparound stopping rule or graceful recovery for them is
promised. Existing adaptive and publication rules apply within this bound.

During search, complete newline-terminated named command lines are consumed in
arrival order, at most one available line at each 4,096-search-unit host poll.
The host may make a line available before a poll; wall-clock arrival does not
itself interrupt recursion. A line arriving after the last poll is not thereby
guaranteed to affect that search. The scope assumes complete lines fit the
ordinary command grammar; fragmentation, overlength input and timing within
transport assembly are not specified. Deterministic queued diagnostics supply
availability explicitly and retain their narrower command sets.

- `?` gracefully stops and publishes the retained result or specified fallback.
- `force` aborts without playing a move or publishing a new completion post;
  completion of that abort leaves the session in force mode. A subsequent
  legal move therefore updates history without an automatic reply.
- `.` publishes the current status and continues; `post`/`nopost` affect later
  post publication without stopping.
- `time r` applies the active-measurement synchronization rule at the command's
  consumption point. It changes the game-clock adjustment, not the already
  initialized search allowances/adaptive limits. `otim r` has no effect.
- `easy` keeps pondering disabled. Pondering, analysis, hint/solve and other
  unspecified commands during search are not required by this ordinary profile.

Live status renders the complete current search path (at most 64 entries),
including null steps under [interrupted sessions](interrupted-sessions.md).
It does not use the post-line 380-byte truncation rule, even when its rendered
path crosses that size. This is an output requirement, not a requirement to
store or export a particular internal representation. Constructed long-path
coverage does not establish a naturally reached long-status witness.

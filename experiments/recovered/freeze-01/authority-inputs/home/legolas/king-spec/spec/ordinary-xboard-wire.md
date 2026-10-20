# KING-XBOARD-ORDINARY — production wire profile, version 1

This is the required ordinary, non-pondering King XBoard-facing interface.
It is King's dialect, not general modern XBoard/CECP compliance. It is a
production byte-stream interface, separate from the JSON diagnostic adapter.
Use the existing search, personality, clock, position and session contracts
for semantics; this contract supplies the public forms and bounded admission.

## Process and records

Supply a documented executable launch command that starts this profile with
the specified token-independent, reset-safe KingRE work-clock behavior. No
particular executable name, programming language, launch-option spelling or
internal architecture is required. Do not substitute a host wall clock for
that work clock.
Diagnostic tracing and explicit seed overrides are off for normal production.
The accepted gameplay replay uses the separate opt-in
[gate seed command](gate-seed-command.md); it does not alter this default.
The separate opt-in [fine-work post formatter](work-clock-profiling.md) changes
the third search-post field's units/ownership for profiling only. All ordinary
commands, stopping and status output continue to use their existing rules.

The process reads commands from standard input and writes protocol output to
standard output. Startup is silent: no banner, prompt, feature negotiation or
automatic parameter dump. `xboard` is silent and does not reset session state.
One process can handle multiple games. Initial state and resets are defined in
[session lifecycle](ordinary-session-lifecycle.md); `new` is not a fresh process.

Commands use ASCII, case-sensitive tokens, separated by one or more spaces or
horizontal tabs. Leading/trailing spaces or tabs and blank lines are allowed.
Each command ends in LF or CRLF. Admit at most 40 tokens including the command
name, and at most 1023 bytes **including** the line terminator (thus at most
1022 payload bytes with LF or 1021 with CRLF). Input containing NUL, non-ASCII,
embedded carriage returns, overlength records, or an unterminated final record
is outside this profile. It need not reproduce permissive malformed parsing.

Every emitted record uses ASCII and LF, even for CRLF input. Make a completed
record available without waiting for another input line. Do not write prompts,
debug traces, log messages or diagnostic-adapter JSON to stdout. Successful
ordinary operation has empty stderr. Environmental/startup failures may use
stderr and a nonzero exit; those are not specified engine results.

Between searches, `quit` exits with code 0 and no farewell record. Clean stdin
EOF between commands also exits 0, silently. The host must not use EOF or
`quit` during search as a substitute for the specified search-time controls.
Fatal outcomes below terminate with code 1 and no signal; no later command is
processed. Host synchronization uses completed output or process termination,
not an invented ping/pong handshake.

## Admitted command forms

Unless explicitly shown, commands take no arguments. `INT` is an optional
`+` or `-` followed by one or more decimal digits, with mathematical value in
−2147483648..2147483647; leading zeroes are allowed. No suffix, exponent,
hexadecimal, saturation or overflowing spelling is admitted. Stored values
are returned in ordinary decimal without a redundant plus or leading zeroes.

| Form | Meaning and response |
| --- | --- |
| `xboard` | Enter XBoard mode; silent. |
| `new` | Standard position and normal Black-playing mode; resets/retentions follow session lifecycle. Silent. |
| `quit` | Idle clean exit. |
| `force` | Disable automatic replies; silent when idle. |
| `go` | Select the current side as engine color and start ordinary search. |
| `MOVE` | Apply a coordinate move, report any resulting game result, otherwise search automatically when it becomes the selected engine side's turn outside force mode. |
| `setboard FEN4` or `setboard FEN6` | Establish a new initial position; silent. |
| `undo`, `remove` | Rewind one/two plies, saturating at initial position; silent. |
| `white`, `black` | Select Black/White respectively as engine color and clock color; do not change board side to move or force/play mode. Silent. |
| `level STAGE [STAGE ...]` | Replace the schedule, retaining accumulated clock adjustment and clearing recorded `st`; silent. |
| `time INT` | Synchronize own remaining centiseconds; negative values are admitted. Silent. |
| `otim INT` | Ignore opponent-time value; no state change or output. |
| `sd [INT]`, `st [INT]` | Store depth/time setting, with omitted value zero; silent. These do not replace `md` or allocated-time stopping in ordinary timed search. |
| `post`, `nopost` | Enable/disable subsequent search posts; silent themselves. |
| `easy` | Disable pondering; silent. |
| `cm_parm [PARAM ...]` | Ordered updates/queries and one reply, defined below. |
| `random`, `draw`, `?`, `.`, `nop` | Idle no-ops, silent; `?` and `.` differ during search. |
| `result RESULT` or `result RESULT {COMMENT}` | Idle notification ignored; no state change or reply. |
| `bk` | Fixed no-book reply below. |

`MOVE` is two lowercase squares (`a1` through `h8`) followed, on promotion,
by lowercase `q`, `r`, `b` or `n`. No SAN input, `usermove` prefix or castling
token is required: castling is the king's coordinate move. An otherwise
well-formed coordinate token that is not accepted produces the illegal-move
line below and does not advance the game. Position/history legality includes
the expressly specified joined exceptional transitions, not an inferred
normal-chess restriction.

`FEN4` contains placement, side, castling and en-passant fields under
[POSITION-SETUP](position-setup.md). `FEN6` adds nonnegative decimal halfmove
and positive decimal fullmove fields within signed-32-bit range. Both forms
have the same effective setup: textual counters are ignored, reversible count
starts at zero and notation fullmove at one. Invalid setup parsing is outside
this valid-input profile; it is not permission to reject admitted setups.

`RESULT` is `1-0`, `0-1`, `1/2-1/2` or `*`. An optional braced ASCII comment
has no semantic effect and must fit the record/token bounds. No result
notification changes the engine's own board or adjudication.

### Clock grammar and numeric admission

A `STAGE` is `MOVES BASE INCREMENT`. Admit one through ten triples. `MOVES`
and `INCREMENT` are `INT`. Positive move counts are retained; a nonpositive
count means 999 moves and ends the effective stage list; later supplied
triples are ignored. Positive increments are retained in seconds; nonpositive
increments become zero.

`BASE` is `INT` minutes or `INT:INT` minutes and seconds. Convert exactly to
`60*minutes + seconds` (or `60*minutes`). If this total is positive and at
most 2147483647, retain it as base seconds; otherwise use zero. Seconds are
not restricted to 0..59: the total, not a civil-time interpretation, determines
the base. This normalization is silent. The last effective stage repeats; 999
is a finite stage length, not infinity. See
[TC-SCHEDULE](time-allowance.md#tc-schedule--accumulated-scheduled-time).

These lexical domains do not require extreme-duration arithmetic. For this
ordinary profile, every schedule/allowance value consumed by clock
synchronization or allowance calculation must be finite, and each resulting
centisecond integer conversion must lie within its specified signed-32-bit
domain. Apply the specified schedule and allowance arithmetic to determine
admission for the requested game/history; this is not a
restriction to particular witnessed schedules or the fresh diagnostic's fixed group clocks.
Elapsed-search lifetime has the separate bound in
[ordinary host/timing scope](ordinary-session-lifecycle.md#ordinary-host-and-timing-scope).
This is a composition-domain limit, not an extra parser rejection or fixed
aggregate schedule cap. Out-of-domain arithmetic and longer search intervals
remain outside this profile.

`time` uses [clock synchronization](clock-session-setup.md) and the active
measurement rule in session lifecycle. Neither `level` nor `time` implies a
reset of position, personality or the work-clock origin. Command storage
admission does not broaden the effective personality/search value domains.

### Parameters

`PARAM` is `default`, a name, or `name=INT`. Names contain ASCII letters,
digits and underscores, beginning with a letter; recognized names and aliases
are exactly those in [PARAM-COMMAND](personality-configuration.md).
Unknown names are admitted queries/assignments and return `name=?` without
changing known settings. Names are case-sensitive. `default` preserves `opk`.
Each token acts in order, including multiple updates on one line.

The reply is literal `cm_parm`, followed by one space and each token's reply
in input order, then LF. Token replies are `default`, `name=VALUE`, or
`name=?`. An empty query is exactly `cm_parm\n`. Accepted integer storage is
not a promise to execute searches outside the specified personality domain.
The stored `opk` value is exempt from such search-domain restrictions: it is
unconditionally inert under [PARAM-DEFAULTS](personality-configuration.md#param-defaults--default-values).

## Sequencing and commands during search

Process idle commands in arrival order. Send `force` after `new` before replay
when automatic replies are unwanted. A completed engine move is applied before
the next idle command. Persistent position, clock, parameter, seed and search
state lifetimes are owned by [session lifecycle](ordinary-session-lifecycle.md).

During an ordinary search, the only required command forms are `?`, `force`,
`.`, `time INT`, `otim INT`, `post`, `nopost`, and `easy`. Consume complete
available lines at the specified work polls, in order, at most one per poll.
`?` gracefully finishes with the retained result or specified first-root
fallback. `force` writes exactly `aborting search ...\n`, aborts without a
played move or new completion post, and leaves the session in force mode. Earlier posts remain
visible. `.` writes one live status and continues. The other admitted forms
apply their stated effects and continue; `time` does not recompute already
initialized search allowances. A line arriving after the last poll is handled
later as an idle command. See [interrupted sessions](interrupted-sessions.md).

## Exact output records

In the forms below, `\n` denotes one LF byte, not two printable characters.
There is no trailing space unless explicitly part of a literal reply.

**Move:** `move COORDINATE\n`, using the input coordinate/promotion alphabet.
No bare coordinate line or `usermove` record is emitted. An ensuing game result
is a separate following record.

**Post:** the four decimal numeric fields and their minimum widths/signs from
[PV-NOTATION](pv-notation.md#search-post-numeric-prefix), followed by each
displayed raw King PV token preceded by one space, then LF. There is no `post`
prefix. Preserve raw digit-zero castling, promotion without `=`, and mate-as-
check notation. The append-then-test 380-byte limit includes the numeric
prefix but excludes LF, retaining the crossing token. The final zero-depth
fallback uses its specified zero report fields; it is not filtered out.

**Status:** literal `stat01: ` followed by elapsed centiseconds (minimum width
6), one space, cumulative SearchID (minimum width 9), one space, depth token
(minimum width 5), one space, remaining root count (minimum width 3), one
space, total root count (minimum width 3). These are right-aligned decimal
integers, with a minus only for negative values and no redundant plus. Append
one space per raw King path token and then LF. Widths are minima, not clipping
limits. Use the current exploration path, including `null` as specified by
[live status](interrupted-sessions.md#live-status), not the saved best PV.
The remaining count excludes the current root. No post-line truncation applies.

**Result:** `RESULT {REASON}\n`. A White win uses `1-0`, Black win `0-1`, and
draw `1/2-1/2`. Exact reason text is `Checkmate`, `Stalemate`,
`Draw lack of wood`, `Draw 3 x position`, `Draw 50 moves`, or `Movelist full`,
selected with the existing [history/result rules](ordinary-play-ingress.md).
Do not print a result just because a diagnostic labels a position terminal;
apply the specified command's result-publication behavior.

**Illegal coordinate:** `Illegal move: TOKEN\n`, preserving the rejected
coordinate token's spelling, not the surrounding whitespace.

**Unknown idle command:** `Error (unknown command): TOKEN\n`, where `TOKEN`
is the first token. In particular, `protover`, `ping` and `pong` are unknown:
there is no `feature` or `pong` reply. Recognized but excluded modes such as
`analyze` are outside this profile, not required to produce an unknown error.

**Book query:** exactly
` This engine does not have a book.\n \n Okay?\n\n`.
The leading spaces, single-space second line and final empty line are retained.

**Fatal termination:** apply the empty-root rule in
[SESSION-GO-OUTCOME](root-go-outcome.md) and the separately established
[exceptional king-victim continuation](ordinary-play-ingress.md#exceptional-king-victim-continuation).
Neither emits a selected move, search post or invented game result. Fatal
exit is not a generic fallback for parser, environment or implementation errors.

## Coverage and exclusions

The rules above define the production profile; transcript examples do not
limit them to the tested positions or command values. Exact fixture events
remain semantic projections: for example their letter-O castling is not the
raw wire spelling. Protocol output has no required timestamp or seed echo.

Pondering/`hard`, full analysis/`exit`, hint/solve, interactive editing,
file-loading extensions, unsupported startup modes, malformed-input extremes,
and other commands/combinations during search are not required. This profile
neither implements modern CECP negotiation nor silently narrows ordinary
commands to the specific sequence used by one host.

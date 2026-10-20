# SEARCH-ORDINARY-JOINED-SEARCH — fresh ordinary search and public result

This runnable diagnostic operation joins fresh command ingress to one ordinary, profile-driven timed
search and its public result. It is a diagnostic operation, not an engine
protocol command.

For successive searches in one live process, use
[ordinary session/reset lifecycle](ordinary-session-lifecycle.md). This operation is its
fresh-ingress diagnostic, not a requirement to restart the engine between moves.
In-process searches retain command/game/clock state but start with fresh
search-local caches and learned ordering. The broader session contract does
not change this diagnostic's request or response envelope.

## Request and admission

The portable request envelope is exactly:

```text
{
  version:1,
  operation:"search.ordinaryJoinedSearch",
  input:{
    setup:SETUP,
    personalityParameters:PARAMETERS,
    clock:CLOCK,
    systemSeconds:UINT32,
    randomnessOverride:INTEGER,       // optional
    diagnosticCapacity:CAPACITY       // optional
  }
}
```

No other envelope or input fields are accepted. `SETUP`, `PARAMETERS`, `CLOCK`,
`UINT32`, the optional override and their exact nested fields and domains are
defined by [ordinary-play engine ingress](ordinary-play-ingress.md). The operation name is
exactly `search.ordinaryJoinedSearch`. It does not accept an allowance, acquired seed, evaluator/search
answer, retained cache, profile name, expected output, or fixture identifier.

The operation derives the command sequence, average and maximum allowance,
fresh acquired seed, and empty retained-state controls. It admits four kinds
of closed nonfatal search outcome:

- a completed root followed by a time stop;
- an entire completed iteration followed by a time or terminal stop; or
- a natural 4096-work poll before any root completes, using the initialized
  first-root fallback arm specified in the final interruption/fallback section;
  or
- a later natural 4096-work poll stop with a prior completed-root capture and
  an unfinished descendant belonging to the currently explored root. An unfinished IIO
  child contributes no fabricated return, score, PV, promotion, ranking update,
  capture, or answer; publication retains the earlier completed-root capture
  while terminal work belongs to the poll.

If initial root generation instead produces no legal candidates, ordinary
`go` terminates the engine with exit code 1 and no signal. This fatal outcome
is distinct from a completed search result and emits no portable post, move,
or terminal-work value. The response union is bound to that independently
generated root set: the fatal arm requires zero candidates, while the normal
post-and-move arm requires at least one.

The separately specified [exceptional king-victim continuation](ordinary-play-ingress.md#exceptional-king-victim-continuation)
is a production command-sequence requirement, not a zero-root result or a
successful search. Do not use this diagnostic's zero-root response to infer
its cause. Its fatal public behavior is specified by that ingress rule;
this bounded JSON diagnostic does not add a representation for the exceptional
sequence or for arbitrary missing-king continuations.

`CAPACITY` contains exactly the integer fields
`maximumEnteredIterations`, `maximumChargedSearchUnits`, and
`maximumResultBytes`. Their respective ranges are 1..9, 1..524288 and
1..16777216. The default is 3 iterations, 8192 charged search units, and 16
MiB. These are execution and result-storage limits only; changing them does
not describe engine behavior or reduce the intended search rules to those
ceilings.
After composition, the complete serialized JSON response must fit
`maximumResultBytes` or the diagnostic fails without returning a partial
response.

This operation's result-size admission is separate from the bundled runner's
1 MiB subprocess-output capture ceiling. Larger valid responses require a harness
with sufficient capacity; see [DIAG-TRANSPORT](diagnostic-interface.md).

## Authoritative composition

For a request in the admitted domain, execute these bindings in order. The
narrower admission limits of the referenced component diagnostics do not
replace this joined contract's inputs.

Use the joined-specific setup admission and en-passant transition rules in
[ordinary-play ingress](ordinary-play-ingress.md#joined-request-ingress), the exact numerical
interpretation in TC-ALLOWANCE, and the operating boundaries in
[session lifecycle](ordinary-session-lifecycle.md#ordinary-host-and-timing-scope).

1. Apply ordinary-play engine ingress. Its normalized initial position and all retained
   moves are the sole position/history source; its effective thirty-field
   vector is the sole personality source; its derived average/maximum
   allowances and accepted first-search seed are the timing and randomness
   sources. Start with empty learned ordering, pawn-classification and
   remembered-result state, and create fresh remembered/transposition capacity
   from effective `tts`. Do not import state from another request.
2. Produce every pre-root state with [POSITION-SETUP](position-setup.md) and
   [POSITION-MOVE-SEQUENCE](move-sequence.md), preserving chronology, rights,
   en-passant state, reversible count and identities. Carry all zero through
   799 prior states into [SEARCH-HISTORY-ADMISSION](history-admission.md) and
   [SEARCH-REPETITION-ADMISSION](repetition-admission.md); do not truncate the
   joined history to an older diagnostic's 255/256-move capacity. Generate the
   complete legal root sequence as required by SEARCH-ORDINARY-ITERATIONS,
   which reuses the legal-set and natural-order rules of
   [SEARCH-ORDINARY-CANDIDATE-PRODUCTION](search-candidate-production.md) at its
   root boundary, subject to joined ingress's explicit override of the
   standalone candidate domain. A final root meeting one of ingress's enumerated
   protocol-terminal conditions remains available to the outcome rule, while a
   prefix producing any such reason before another supplied move is not a valid
   history.
3. If the generated root sequence is empty, take the fatal arm below under
   [SESSION-GO-OUTCOME](root-go-outcome.md). Do not construct a seed-accepted
   search result merely because `systemSeconds` was present. Otherwise acquire
   the ingress seed once at the beginning of the first depth and retain it as
   required by [RANDOM-SEED-LIFETIME](seed-lifetime.md).
4. Execute the semantic ordinary node state machine in
   [SEARCH-ORDINARY-ITERATIONS](ordinary-iterations.md), including its referenced
   evaluation, extensions, pruning, remembered-result, repetition,
   quiescence, learned-state and pawn-state rules. Its personality-binding
   section fixes root-side ownership of all evaluation coefficients and the
   consumers of `avd`, `cfd`, `sop`, `sel`, `md`, `ana` and `tts`; `rnd` is
   consumed at the root boundary below. The joined path uses the complete IIO
   rules in that contract, including initial and tail phases, every admitted
   shallow target and accumulated extension flags. The restricted
   `search.ordinaryIterations` and zero-IIO `search.genericTimedSearch`
   transports are test interfaces and do not narrow this rule.
5. At every iteration entry, feed the score-ranked carryover order, each
   candidate's retained work and cumulative SearchID into
   [SEARCH-ROOT-WORK-SCHEDULE](root-work-schedule.md). SearchID below 25000 uses
   the unrestricted sequence; SearchID at least 25000 keeps the first candidate
   fixed, stably orders the tail by retained work, and uses
   [SEARCH-ROOT-ASPIRATION](root-aspiration.md) and
   [SEARCH-RESTRICTED-ROOT-SEQUENCE](restricted-root-sequence.md), including its
   retry and ranking-score rules. The unrestricted arm uses
   [SEARCH-UNRESTRICTED-ROOT-SEQUENCE](unrestricted-root-sequence.md). This late
   policy is selected at iteration entry and remains selected for that
   iteration even if later work crosses 25000.
6. For each actual root request, use the retained seed, effective `rnd`, move
   descriptor and pre-adjustment root window with
   [SEARCH-ROOT-RANDOMIZATION](root-randomization.md). Its transformed bounds
   govern the child search and its adjusted return governs root ranking,
   later windows, PV selection and result capture. A repeated move reuses the
   same seed rule; it does not acquire or advance a random stream.
7. Accumulate every search-unit and relation-query charge at the exact event
   owned by the recursive/evaluation contracts. Cumulative search units are
   SearchID for root scheduling and captured reports. Convert the two counters
   to KingRE observations with [WORK-CLOCK](work-clock.md); host elapsed time
   is not a substitute. Initialize adaptive limits from the ingress allowances
   and root check state, then apply [TIME-ADAPTIVE-SEQUENCE](adaptive-time.md)
   at best changes, completed roots, completed iterations and each nonzero
   4096-search-unit poll. After an iteration's time adjustment, also apply
   [SEARCH-ITERATION-TERMINAL-STOP](iteration-terminal-stop.md), including the
   personality depth, selectivity/mate-margin and score gates.
8. Root ordering, retry, best-change capture and stopping follow
   [SEARCH-TIMED-ROOT-SEQUENCE](timed-root-sequence.md) with actual recursive
   replies and work rather than supplied diagnostic replies. A completed-root
   stop includes that root; an iteration stop includes the whole iteration;
   an interrupted poll includes charged prefix work but no fabricated return
   for the open child. Publish the retained capture under
   [OUTPUT-POST-LIFECYCLE](post-lifecycle.md),
   [OUTPUT-SEARCH-SCORE](output-score.md), and the phase-adjusted selective
   depth. Finish-time work does not restamp the capture's score, SearchID, PV
   or elapsed value. Render the captured coordinate PV under
   [PV-NOTATION](pv-notation.md), including its numeric-prefix-derived byte
   limit and semantic projection. Display truncation does not change the
   captured line or selected coordinate move.

Project only the portable response fields below. Completed iterations,
recursive frames, candidate work and adaptive traces remain functional state;
their omission from this response does not permit an adapter to skip their
effects or obtain them from a fixture.

The complete semantic search keeps five owners separate:

- completed iterations contain only fully closed iterations;
- the retained result belongs to the best completed root captured for output,
  which need not be the chronologically latest completed root;
- its SearchID, score, and PV belong to the timing best-change capture;
- terminal total work and finish-clock input belong to the actual root,
  iteration, or poll stop; and
- posts and the final coordinate move belong to the public output lifecycle.

The portable response deliberately exposes the independently runnable subset:

```
{version:1, output:{ingress, terminalWork, events}}
```

`ingress` has exactly the nested fields, types, constants and array orders in
[Portable ingress output schema](ordinary-play-ingress.md#portable-ingress-output-schema).
`terminalWork` contains exactly nonnegative integer `searchWork` and
`relationWork` at the stop. `events` contains one or more ordered public posts
of exactly `{type:"post",depthToken,evaluation,searchId,pv,
engineCentiseconds}`, followed by exactly one
`{type:"move",move:COORDINATE_MOVE}`. Numeric post fields are safe integers;
`pv` is the semantic King move-text sequence defined below; the final move is lowercase
coordinate notation with an optional promotion suffix. The richer
completed-iteration and captured-root state remains
part of the functional search specification, but is not additional output for
this portable operation. An adapter must produce the requested behavior, not
substitute a stored answer.

### Public PV rendering

[PV-NOTATION](pv-notation.md) derives legal move tokens by replaying the
captured coordinate PV from the reached root. Use each post's actual numeric
fields to derive its prefix length, then apply the complete-token boundary
from [OUTPUT-PV-LINE](pv-line.md). The public semantic string normalizes raw
castling zeros to letter O only; promotion omits `=` and mate uses `+`.
Fixture strings are observed expectations, not a substitute algorithm or
permission to dispatch on a fixture. The initialized fallback uses the same
renderer with its zero report fields and one-move PV.

The mutually exclusive zero-root response is:

```
{version:1, output:{derivedIngress, fatal:{exit:{code:1,signal:null},events:[]}}}
```

`derivedIngress` uses that same exact schema with `seed` absent. It contains
position/history, personality, clock/allowance and controls. It omits seed acquisition:
request-derived seed inputs do not establish that the fatal path
accepted a seed. It also omits `terminalWork`; a zero-root fatal exit is not a
completed or interrupted search result. The empty `events` array states that
this portable outcome contains no post, move, or inferred checkmate/stalemate
announcement.

Post depth tokens use the phase-adjusted root margin from
[SEARCH-SELECTIVE-DEPTH](selective-depth.md). The applicable endgame weight is
derived from the root placement; root check state is not a substitute for that
phase input.

The observation-derived fixtures contain four fresh low-depth cases: P001 from the
standard start, P004 after `e2e4`, P004 in a checked position with legal roots,
and P004 in a zero-root fatal position. Qualification controls only the
externally observed seconds value. The derived allowance, accepted seed when
the path reaches acquisition, search result, stopping point, work totals, fatal
exit, and public output are observed rather than supplied. The fatal fixture
omits seed and terminal work and contains exit code 1 with no public events.
Conformance uses the same fresh command ingress and controlled external-seconds
boundary. The fixtures contain no profile
lookup key and do not authorize fixture dispatch.

Retained neutral and P054 root/poll cases qualify the stop/result/public
projection only. Their allowances were supplied to the older generic timed
operation, so they are not fresh-ingress closure evidence. They preserve
the important distinction between terminal work (for example 4096 or 8192 at
a poll) and an earlier published SearchID. Public output is not inferred from a
neighboring result: the retained public projection is separately observed and
must compare exactly.

Focused evidence additionally covers a P004 `md=2`
setboard root already in check and a P004 `md=2` checkmate root with zero legal
candidates. The checked case preserves all six generated evasions and produces
a normal post and move. The zero-root case establishes the fatal response arm;
its supplied-position checkmate classification is not an emitted terminal
reason. Standard history is exercised by `e2e4`; broader histories remain
pending joined qualification, not forbidden target behavior. Implementations
must fail closed when they hit an unsupported diagnostic boundary rather than
silently changing the position or history.

A graceful natural-time poll before any root completes uses the initialized
first generated root as a fallback only when the search state has all of the
following: no completed root or iteration, no retained result
or timing capture, a nonempty computed root list, and an active first-root owner
equal to candidate zero. It publishes one zero-depth, zero-score, zero-SearchID,
zero-elapsed post with that move as its one-move PV, followed by the move. The
terminal charged work and elapsed stopping state remain separately owned by the
poll. This fallback bypasses captured-score adjustment, including contempt;
host abort, diagnostic exhaustion, and generic failure publish no fallback.
Controlled interruption evidence establishes this finish rule, not its natural
reachability under an unmodified KingRE work clock.

For either poll arm, the unfinished child and every unfinished ancestor belong
to the current root's exploration. Unwind them without fabricating returned
scores, PVs, completed candidates, ranking updates or captures. Keep charges
already incurred and the last eligible completed-root capture, if any; an open
IIO pass contributes no fabricated completed ordering result. Already completed
children retain the shared-state effects specified by ordinary search; this
rule does not roll back their charged work or completed updates. These are semantic
conditions, not a requirement to export a trace, use ancestor frames, or
implement a particular validator or proof interface.

Still outside this boundary are retained sessions, pondering/analysis,
malformed host records, and arbitrary command modes. Open-IIO interruption with
an earlier result remains admitted by the semantic ownership rules above; no
natural stopping poll inside IIO is currently qualified. Constructed
interruption cases are not natural stopping witnesses. Those missing
witnesses do not make the stated unwind and fallback ownership rules
unknown. The bounded witnesses establish composition for their stated domains,
not every profile, clock, or position.

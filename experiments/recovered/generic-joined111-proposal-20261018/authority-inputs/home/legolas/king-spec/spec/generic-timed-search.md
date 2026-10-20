# SEARCH-GENERIC-TIMED-SEARCH — parameterized counted-time search

This runnable diagnostic operation
composes position history, a complete numeric personality vector, recursive
ordinary search, explicit-seed root variation, functional work accounting,
adaptive stopping, retained results and public search output.

It is an opt-in diagnostic contract, not an engine protocol command. Its
diagnostic admission and resource failures do not state which values or
positions the original engine accepts through its public command interface.

## Request

Version 1 operation `search.genericTimedSearch` accepts exactly:

```
{fen, moves, personalityParameters, seed, allowance, controls}
```

`fen` and the ordered coordinate `moves` select the reached position. The
history has at most 255 moves. The reached position must have a side to move
that is not in check and between one and 256 legal root candidates.

`personalityParameters` has exactly these thirty integer fields:

```
{myp,opp,myn,opn,myb,opb,myr,opr,myq,opq,myk,opk,mycc,opcc,
 mymob,opmob,myks,opks,mypp,oppp,mypw,oppw,avd,sop,rnd,sel,cfd,md,ana,tts}
```

No profile name, roster number, default alias or omitted field is accepted.
The diagnostic domain is:

- each of the twenty non-king `my` and `op` percentages: 0 through 1000;
- `avd`: -100 through 100;
- `cfd`: -10000 through 10000;
- `sop`: 0 through 100;
- `sel`: 0 through 64;
- `rnd`: 0 through 1000;
- `md`: 6 through 99;
- `tts`: 4194304 through 67108864; and
- `ana`, `myk`, and `opk`: zero.

`opk` is the inert compatibility parameter specified by
[PARAM-DEFAULTS](personality-configuration.md#param-defaults--default-values).
Its zero value here is a diagnostic binding, not a production search
restriction. The other ranges are conservative diagnostic coverage limits,
not claims about command parsing or clamps outside them.

`seed` is an unsigned 32-bit integer retained for the whole search.
`allowance` is exactly `{averageCs:1,maximumCs:1}`. It supplies the two timing
allowances directly; it does not specify how a game clock produces them.
`controls` is exactly:

```
{completion:"natural-work-clock", learnedState:"fresh-ordinary-search",
 pondering:false, analysis:false, seedSource:"explicit",
 workOrigin:"after-root-preparation"}
```

Object key order is irrelevant. A request within these ranges is admitted for
computation; admission does not select or contain an expected answer.

## Search state and work

Normalize the position, apply every history move, bind all thirty parameter
values and generate the legal root candidates in their natural order. Begin a
fresh ordinary search. Apply the recursive search, evaluation, ordering,
extension, transposition, repetition and retained-state rules specified by the
ordinary search and its component contracts whenever their admitted domains
are reached.

The runnable diagnostic observes entry to internal iterative ordering and
counts it for the whole search. A successful response requires the terminal
count to be zero. Entry to that currently unsupported rule exits through a
dedicated fail-closed diagnostic boundary and cannot return a partial response.
This is an execution-domain guard, not a claim that the original engine lacks
iterative ordering.

Apply the explicit seed and `rnd` value to each actual root return under
[SEARCH-SEEDED-ORDINARY-ITERATIONS](seeded-ordinary-iterations.md). The adjusted
score participates in ranking, later root windows, PV selection and result
capture. Stable descending ranking determines the next iteration's visitation
sequence; equal scores preserve their existing relative order.

Each new iteration resets its numerical ranking and PV. It retains the prior
iteration's ranked visitation sequence and all search-wide state whose
ordinary-search contract spans roots or iterations. It does not reset retained
evaluation or learned state between roots.

Start charged search units and charged relation queries at zero after root
preparation. Charge the work defined by [WORK-CLOCK](work-clock.md) across the
entire search. With cumulative values N and R, elapsed centiseconds are:

`floor((3806*N + 770*R) / 30000000)`.

This is functional search work, not host time, processor instructions,
completed depth or the most recently published SearchID.

## Clock decisions and stopping

Initialize and update the three adaptive limits from the supplied allowances
and actual search progress under [TIME-ADAPTIVE-SEQUENCE](adaptive-time.md).
Preserve its binary64 arithmetic and comparison order.

After each completed root at depths greater than one, perform the root check.
After each completed iteration at depths greater than one, perform the
iteration clock check, then apply
[SEARCH-ITERATION-TERMINAL-STOP](iteration-terminal-stop.md) using the completed
ranking and personality parameters. At every nonzero multiple of 4096 charged
search units, perform the work-poll check before continuing the active child.
Equality with a limit stops.

A root stop includes that completed root and all of its ranking, PV, capture
and work effects. A poll stop interrupts the active child: it excludes a child
return, root score, ranking change, PV change or result capture for that
incomplete child, while retaining the work already charged.

After the adaptive best-change update required by
[SEARCH-TIMED-ROOT-SEQUENCE](timed-root-sequence.md), an adjusted score that
strictly improves the **current iteration's** best replaces the captured
result. The comparison starts again from -10000 when the iteration begins; it
is not a comparison with the numeric score captured in a prior iteration. A
later iteration can therefore replace a numerically better earlier capture.
An equal score within the current iteration retains the earlier capture. The
captured depth, root visit index, score, PV, SearchID and elapsed value remain
those at capture time even if more work is charged before stopping. Root visit
indices are zero-based temporal positions within that iteration; they do not
describe storage. Apply update-before-capture and root-stop ordering exactly as
specified by SEARCH-TIMED-ROOT-SEQUENCE.

## Response and field origins

Success returns `{version:1,output}`. `output` has exactly:

```
{seed, initialCandidates, iterations, timeChecks, stop, result, events}
```

- `seed` is the explicit retained request seed.
- `initialCandidates` is the complete legal root sequence from the reached
  position. It is an array of the same exact `{move,kind}` semantic move
  objects defined below, including the promotion suffix convention.
- `iterations` contains the actual completed root visits, functional incoming
  windows and random adjustments, returned scores, retained rankings/PVs and
  cumulative charged work.
- `timeChecks` contains every functional root, iteration and work-poll clock
  decision in temporal order.
- `stop` identifies the natural root or poll boundary and total charged work.
- `result` is the latest root that strictly improved its current iteration's
  best, with that capture's values.
- `events` contains literal public search posts and exactly one final
  coordinate move under [OUTPUT-POST-LIFECYCLE](post-lifecycle.md).

The root/window/work records are diagnostic observations of functional state;
they are not lines printed by the original public protocol. Only `events`
represents literal public posts and move output.

Each iteration is `{depth,complete,steps}`. Every completed step is:

```
{move, window:{lower,upper}, adjustment, score, bestScore, secondScore,
 childPrincipalVariation, principalVariation,
 work:{chargedSearchUnits,chargedRelationQueries}}
```

`depth` is a consecutive integer from 1 through 6 and `complete` is boolean.
`move` and every PV entry are exactly `{move,kind}`. The coordinate string is
four lowercase square characters, followed for promotion by exactly one of
`n`, `b`, `r`, or `q`; a promotion has kind `ordinary`. `kind` is exactly
`ordinary`, `castle`, or `enPassant`. PVs contain zero through 63 moves.

Every window endpoint, `score`, `bestScore`, and `secondScore` is an integer
from -10000 through 10000. `window` is the root-oriented requested window
**before** the random adjustment. `adjustment` is the integer defined by
[SEARCH-ROOT-RANDOMIZATION](root-randomization.md) from the request seed, `rnd`,
semantic move and window. `score` is the adjusted root-oriented returned score;
it is not the child's opposite-oriented score or the public reported score.
`childPrincipalVariation` is the actual child's returned PV, and
`principalVariation` is the root PV retained after this step.

Every `work` object has exactly `chargedSearchUnits` and
`chargedRelationQueries`, both safe nonnegative integers. Charged search units
are at most 8192 in a successful response; charged relation queries are at most
9007199254740991. Work is cumulative and nondecreasing from the zero origin.

An iteration is complete only after all of its roots and its completion
boundary. The stopped iteration is present with `complete:false`.

Each time check is:

```
{point:"root"|"iteration"|"poll", depth, rootIndex,
 work:{chargedSearchUnits,chargedRelationQueries},
 elapsedCs, limitSeconds, stop}
```

`point` has exactly the shown values. `depth` is 1 through 6, `rootIndex` is
null or a nonnegative integer in that iteration, `elapsedCs` is a nonnegative
safe integer derived from work, `limitSeconds` is the binary64 limit produced
by the adaptive-time rules, and `stop` is boolean.

Iteration checks use `rootIndex:null`; root checks name the completed root;
polls name the active root. Do not invent depth-one root or iteration checks.

The stop and captured result are:

```
stop: {point:"root"|"poll", depth, rootIndex, work, elapsedCs, pendingRoot}
result: {depth, rootIndex, score, principalVariation, searchId, elapsedCs}
```

`pendingRoot` is null at a root stop. At a poll stop it contains only the
interrupted root `{move,window:{lower,upper},adjustment}`. It has no return
score or PV. The stop's `depth` is 1 through 6, `rootIndex` is a nonnegative
temporal index, `elapsedCs` is the work-derived nonnegative safe integer, and
its `work` has the exact work schema above. The result's `depth` is 1 through
6, `rootIndex`, `searchId`, and `elapsedCs` are nonnegative safe integers,
`score` is -10000 through 10000, and its PV has zero through 63 semantic moves.

Every public post event is exactly:

```
{type:"post", depthToken, evaluation, searchId, pv, engineCentiseconds}
```

`depthToken`, `evaluation`, `searchId`, and `engineCentiseconds` are safe
integers; `pv` is the semantic King move-text sequence from
[PV-NOTATION](pv-notation.md), including the numeric-prefix-derived whole-token
byte limit. The final event is exactly
`{type:"move",move}` with a lowercase coordinate move including the optional
promotion suffix. No other event type or field is admitted. Capture-time score
normalization, depth token, move text, SearchID/time retention, shallow deferral and
finish suppression follow OUTPUT-POST-LIFECYCLE and its referenced public
output contracts.

## Version-1 completion boundary

Success requires a natural root or poll stop within six entered iterations,
at most 8192 charged search units, PVs of at most 63 moves, and no actual
internal-iterative-ordering call. A partial observation, unsupported ordering,
different termination or resource overrun is a diagnostic failure with no
semantic response. It is not evidence that the original engine rejects the
request or behaves that way outside this bounded operation.

Still outside this version are production allowance allocation, automatic seed
acquisition, persistent sessions, repetition-sensitive history isolated from
placement, nonzero `ana`/`myk`/`opk`, root-in-check and terminal searches,
analysis, pondering, host poll commands, other stop modes and larger resource
lifetimes. The admitted numeric ranges define the diagnostic request domain;
the original-backed fixture evidence samples four requests rather than every
cross-product.

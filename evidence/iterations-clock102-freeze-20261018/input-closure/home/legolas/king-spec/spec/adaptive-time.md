# TIME-ADAPTIVE-SEQUENCE — retained allowances and ordinary stopping

The average allowance initializes two adaptive limits, used at root completion
and iteration completion. The maximum allowance is a separate limit checked
at work polls. Score deterioration and instability can increase the adaptive
limits; a clearly preferable move can reduce them. These changes persist for
the remainder of the search. They do not change the maximum limit.

This contract describes how **admitted events** change those limits and the
subsequent stopping decisions. It does not yet define how a full search produces
or admits every event. In particular, supplying an easy-adjustment event does
not prove that its scheduling conditions hold in a real search.

## Numerical conventions and initialization

Allowances and clock observations are in centiseconds. Limits below are in
seconds. Use binary64 values and round each stated floating multiplication to
nearest, ties to even. Decimal coefficients such as 0.666 and 0.333 denote their
nearest binary64 values, **not** the fractions two-thirds and one-third.
Integer divisions in score thresholds truncate toward zero.

Let A be average allowance multiplied by 0.01. For nonzero average, initialize:

| Root condition | Iteration limit I | Root limit R |
| --- | --- | --- |
| Not in check | A × 0.52 | A × 0.85 |
| In check | A × 0.29 | A × 0.47 |

For zero average, both adaptive limits are 999000000. For nonzero maximum,
the maximum limit M is maximum multiplied by 0.01; otherwise it is 999000000.
Initialization consumes one start-clock observation. Initialize all change
counts to zero. A new search starts a new independent allowance state.

For each event, elapsed seconds E are `(clock − start) mod 4294967296`,
multiplied by 0.01. The qualified diagnostic domain limits this nonnegative
interval to 2147483647 centiseconds. The ordinary-play profile uses
the same per-search elapsed bound; longer lifetimes are outside its required
scope, as stated in [session lifecycle](ordinary-session-lifecycle.md#ordinary-host-and-timing-scope).

## Iteration history and best changes

Retain best-change counts for the current, previous and older observed
iteration. On entry to a greater iteration depth, the current count becomes
previous, previous becomes older, and current becomes zero. Repeated events at
the same depth preserve the counts. A supplied depth jump advances history once,
not once for every missing depth; natural depth scheduling remains separate.

A `best-change` event first increments the current count. At depths one through
three it performs no allowance adjustment and consumes no clock observation.
At greater depth, consume one observation. An increase is eligible only when
E > I × 0.5 and R < A. Clamp each retained count to at most three **for computing
instability only**; do not truncate the retained counts themselves.

Instability is three times current, plus twice previous, plus older. Multiply
both I and R by two when instability exceeds 14, by 1.5 when it exceeds 10 but
not 14, and otherwise leave them unchanged. Use the currently retained limits
for eligibility, including earlier changes in the same iteration.

## Score deterioration

An admitted `score-drop` event consumes one clock observation. It changes
nothing unless E > I × 0.5. Let P be previous score and B the new score.
Define integer U as P divided by 100, truncated toward zero, and define
S = 100 + 8 × min(U², 100).

If P − B exceeds the truncated integer value of S × 30 / 100, double R.
If it additionally exceeds the truncated integer value of S × 130 / 100,
double R again and double I. Equalities do not qualify. Maximum limit M is
unchanged. A score-drop event does not itself count as a best change; when both
apply, their order must be represented in the event sequence.

## Easy adjustment followed by iteration completion

An `easy-iteration-check` first adjusts the limits, then performs the iteration
stop check described below. For zero average, skip the adjustment. Otherwise
let the margin be min(best score, 100) minus second score, with no lower cap on
best score. Select the factor from the strict threshold bands:

| Margin | Not in check | In check |
| --- | --- | --- |
| At most 70 | 1 | 1 |
| Greater than 70, at most 170 | 0.666 | 1 |
| Greater than 170, at most 400 | 0.5 | 0.666 |
| Greater than 400, at most 800 | 0.333 | 0.5 |
| Greater than 800 | 0.25 | 0.333 |

Multiply both I and R by that factor. The adjustment itself consumes no clock
observation. The same event's stop comparison uses the **adjusted** I.

## Stop checks

| Admitted event | Clock observations | Stop condition |
| --- | --- | --- |
| `root-check`, depth 1 | None | Continue |
| `root-check`, greater depth | One | E ≥ R |
| `iteration-check` or `easy-iteration-check`, depth 1 | None | Continue within this score/depth domain |
| Either iteration check, greater depth | One | E ≥ I |
| `poll-check`, any admitted depth | One | E ≥ M |

The ordinary `iteration-check` does not apply easy adjustment. These checks
assume no host stop/abort command and no pondering.
Terminal-score and depth-limit stops are outside this diagnostic's bounded
score/depth domain. Stop at the first true decision; do not process the remaining
events or let them change state or consume clock observations.

## Controlled diagnostic

`time.adaptiveSequence` accepts exactly `{queries: [...]}`, containing 1..256
independent sequences. Each sequence contains exactly:

- `average`, `maximum`: integers 0..1000000, with maximum ≥ average;
- `start`: clock observation, integer 0..4294967295;
- `inCheck`: boolean root condition, fixed through the sequence;
- `events`: 1..64 ordered admitted events.

The request may contain at most 4096 events in total, including unexecuted
suffixes. This is a batching limit; sequences can be split between requests.

Each event contains exactly `stage`, `clock`, `depth`, `previousScore`,
`bestScore`, and `secondScore`. Stage is one of the six event names above.
Clock is an integer 0..4294967295. Elapsed intervals must be nondecreasing
and within 0..2147483647. Depth is a nondecreasing integer in 1..30. Scores
are integers -7900..7900. Scores unused by a stage have no effect. All events,
including a suffix after a stopping event, must satisfy the input domain.

Output is `{sequences: [...]}`. Each entry contains `initial` and `afterEach`.
The latter has one observation for each executed event, ending at the first
stop or the end of the input. Each observation contains exactly:

- `limits`: `[I, R, M]` in seconds;
- `stop`: boolean, false for the initial observation;
- `clockReads`: cumulative count including the initial start observation;
- `changes`: current, previous and older best-change counts in that order.

Queries are independent and preserve input order. Repeating or reordering
queries cannot change their individual results. Shifting the start and every
event clock by the same amount modulo 4294967296 changes no observation.
Malformed/extra fields and values outside the stated domain are errors.

## Evidence and remaining composition

The [portable fixtures](../conformance/fixtures/adaptive-time-v1.json) cover
threshold neighbors, signed score truncation, retained change history,
adjustment order, first-stop ownership, zero allowances and clock-word wraps.
Expected observations come from the original target with admitted stages and
controlled clock readings. They include the resulting limits, history and
clock-consumption trail, not just the final decision.

Still required: actual event admission and ordering within root search; the
work-to-clock producer and poll schedule; terminal/depth stopping; pondering
conversion and host commands; complete selected-result/report ownership;
cross-search reset and overlong elapsed lifetimes. This component contract is
not a complete timed-search or full personality-fidelity claim.

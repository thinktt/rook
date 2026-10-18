# Time schedules and search allowances

Status: initial behavioral contract, with bounded fixtures. These rules choose
allowances; they do **not** define when a search stops or how work becomes time.
Those composition requirements are connected separately by
[complete ordinary search](ordinary-joined-search.md) and
[session lifecycle](ordinary-session-lifecycle.md); their remaining limitations do
not change this arithmetic contract.

## TC-SCHEDULE — accumulated scheduled time

Input is a nonempty ordered schedule of stages. A stage supplies a positive
move count, a base credit in seconds, and an increment in seconds per move.
The last stage repeats after its move count is exhausted. The queried move
index `n` is zero-based and nonnegative. Stage boundaries belong to the next
stage: at the first stage's move count, its full credit has been earned and
the next stage's base credit is already available.

Define `S(n)` as the sum of:

- Each completed stage's base credit plus its increment times its move count.
- The active stage's base credit plus its increment times the number of moves
  completed within that stage.

For one stage of 40 moves, 300 seconds and no increment, `S(0)=300`,
`S(39)=300`, `S(40)=600`, and `S(81)=900`. For stages `(40,300,0)` then
`(20,120,1)`, `S(40)=420`, `S(59)=439`, and `S(60)=560`.

This diagnostic contract receives the effective schedule. It does not yet
specify parsing of a user's time-control command. In particular, a stage with
999 moves is a finite repeating stage, not a mathematical infinity.

## TC-ALLOWANCE — average and maximum search time

Inputs are the effective schedule, the nonnegative game half-move count `p`,
a signed accumulated clock adjustment `a` in centiseconds, the personality's
search optimism `s`, and whether pondering is enabled. Positive adjustment
means less time is available; negative adjustment increases available time.
An external remaining-time message is **not** itself this adjustment.

Define `m = floor(p/2)` and `e = 0.01 a`. Define the planning length `L`:

- Without pondering: `L = 36 + 0.1(100-s)`.
- With pondering: `L = 27 + 0.15(100-s)`.

For each integer `j` from 1 through 99, define
`q(j) = 1 - 0.96 × 0.966667^j`. The planned target in seconds is

`T = min(999000000, min_j [(S(m+j-1)-e)/(q(j)L)])`.

The immediate budget in seconds is

`B = min(S(m)-e-1, 0.75(S(m+1)-e-1), 0.6(S(m+2)-e-1))`.

The average allowance is `A = max(T, 0.5)`. The maximum allowance is
`M = min(max(B, 1), 4A)`. Return `trunc(100A)` and `trunc(100M)` in
centiseconds, where `trunc` discards the fractional part toward zero.
The two outputs are independently truncated; maximum is not calculated from
an already truncated integer average. For example, an average output of 705
can coexist with a maximum output of 2821.

### Exact numerical interpretation

The equations above use binary64 values. Each decimal coefficient denotes its
nearest binary64 value. Round each arithmetic operation to nearest, ties to
even; do not fuse operations or retain additional precision across the stated
rounding boundaries. This specifies numerical results, not implementation
structure. An implementation may use any method that produces those results.

Scheduled credits within the stated domain are exact integers. Convert their
values to binary64 before the allowance arithmetic. Compute `e` by rounding
the product of `a` and the binary64 value of 0.01. In `L`, form the integer
difference `100-s`, round its product with the coefficient, then round the
addition of 36 or 27.

Let `b` be the nearest binary64 value to decimal 0.966667. For each `j=1..99`,
the power term is the single correctly rounded binary64 value of the exact
real number `b` raised to integer `j`. Repeated rounded multiplication, a
power of the exact decimal fraction, or a library approximation is acceptable
only if it gives that same value. To obtain `q(j)`, first round the product of
that power and binary64 0.96, then round its subtraction from 1.

For each slope, separately round `S(m+j-1)-e` and `q(j)*L`, then round their
quotient. Select the minimum of these values and 999000000. For each immediate
budget arm, round `S(m+k)-e`, then subtract 1 and round again; for the second
and third arms round the resulting product with 0.75 and 0.6 respectively.
Minimum/maximum select values without further arithmetic. Form the rounded
product `4*A` before selecting `M`. Finally round each independent product
`100*A` and `100*M`, then truncate it toward zero to obtain the two integers.
No comparison tolerance is allowed at an integer threshold.

The joined portable response compares the integer allowances, not explanatory
floating values T and B. Those explanatory values remain excluded; the
numerical interpretation above determines the required integer thresholds.

## Current domain and open work

The initial diagnostic domain is 1 or 2 stages, integer base seconds
from 0 through 3600, integer increment seconds from 0 through 60, integer
stage lengths from 1 through 10000, move indices/game half-move counts 0 through 10000,
signed clock adjustments from -100000000 through 100000000 centiseconds,
and optimism from 0 through 100. Fixtures cover a much smaller subset and do
not establish all cross-products. The transport rejects requests outside this
working test domain rather than inventing engine behavior for invalid inputs.
Future domain expansion requires additional characterization. This initial
two-stage limit is a test-interface scope limit, not a claim that the engine
accepts at most two time-control stages. The production `level`/`time` grammar
and numeric admission are specified by
[KING-XBOARD-ORDINARY](ordinary-xboard-wire.md#clock-grammar-and-numeric-admission).

Complete protocol parsing beyond the stated command subset is not supplied
by this arithmetic diagnostic. Active measurement and ordinary stopping are
connected by the ordinary session and joined-search contracts, subject to their explicit
operating scope. Focused threshold examples are not exhaustive range evidence.
[TC-SESSION-SETUP](clock-session-setup.md) covers the first idle command,
synchronization, reset and personality-input composition slice. Those sequence
fixtures, not the arithmetic fixtures alone, support that additional coverage.

Tests: `time-schedule-v1.json` and `time-allowance-v1.json` in the conformance
fixtures directory. Schedule examples are mathematical boundary examples;
allowance examples are sanitized original-side observations. These tests do not
establish complete engine conformance.

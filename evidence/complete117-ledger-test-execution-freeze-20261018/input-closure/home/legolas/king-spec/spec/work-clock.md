# Virtual work clock

Status: the ledger/observation contract is specified and tested. For ordinary
play, charged activity and consumer placement are connected by
[joined search](ordinary-joined-search.md), its ordinary-search/evaluation rules and
[session/reset lifecycle](ordinary-session-lifecycle.md). This scalar ledger
diagnostic alone does not establish complete clock conformance.

## WC-LEDGER — work converted to observed centiseconds

For a work segment, let `N` be its charged search units and `R` its charged
relation queries. Neither means host instructions, CPU time, wall time, every
generated move, or every attack-map operation. They are behavioral work counts
whose charging rules must be specified with search and evaluation.

Define the effective search count:

`K(N) = N` for `0 <= N <= 2147483647`; otherwise `K(N) = 2147483648`.

The segment's whole-centisecond contribution is

`T(N,R) = min(2147483647, floor((3806 K(N) + 770 R)/30000000))`.

This is an integer mathematical definition. It does not require any particular
width of intermediate accumulator or a floating-point implementation. In
particular, summing fractional times per activity and rounding each separately
would not implement this rule.

The clock retains an origin `E` and the last observed clock word `L`, both
initially zero. An observation returns

`L = (E + T(N,R)) mod 4294967296`.

For the diagnostic interface, report that word as a signed centisecond value:
words below 2147483648 retain their value; larger words are reported minus
4294967296. Repeated observations with unchanged work return the same value.
Merely waiting for a faster or slower machine does not create work credit.

A segment reset establishes `E = L` and clears `N` and `R`. It does not
recalculate `L` from work performed since the last observation. Consequently:

- Observed whole time carries into the new segment.
- Work not observed before reset does not add to the carried origin.
- A fractional segment remainder does not carry across reset.
- Repeated resets without new observations do not move the origin.

For example, 7882 search units and no relation queries remain below one
centisecond. Two relation queries added to those units cross the boundary.
If that one centisecond is observed, later unobserved work cannot increase the
origin used by a reset. Resetting two separate just-under-one-centisecond
segments does not combine their fractions into one centisecond.

## Diagnostic contract and evidence scope

`clock.workSequence` starts a fresh ledger and applies ordered events:

- `work`: supplies absolute `searchUnits` and `relationQueries` for the current
  segment. This is an explicit diagnostic input, not a production command or
  a requirement to store those values in a particular layout.
- `observe: true`: produces one signed clock observation.
- `reset: true`: performs the segment reset defined above.

Counts are nonnegative decimal strings to avoid loss of integer precision in
transport. The current diagnostic domain permits search units through
9007199254740992 and relation queries through 18446744073709551615, at most
256 events and 128 observations, with at least one observation. `work` may
replace counts with any values in this domain for boundary testing; it does
not claim actual search can naturally reach every supplied combination.

The fixtures in `work-clock-v1.json` cover rounding, combined work, repeated
reads, observed/unobserved reset behavior, search-count conversion, local
saturation, signed and unsigned clock boundaries, and repeated reset cycles.
These establish the ledger behavior at supplied work inputs. They do not prove
that an engine charges the correct events or places observations correctly.

The separate [fine-work post formatter](work-clock-profiling.md) exposes a
quantized most-recent-observation numerator in the production post's third
column when explicitly selected. It does not change this clock arithmetic,
its observations/resets or ordinary elapsed-time reporting by default.

## Composition dependencies and scope

The ordinary-play composition must use the following dependencies; the ledger
formula alone does not supply them:

1. Specify every charged search event, including quiescence, repetitions,
   cutoffs and terminal/ply-limit boundaries.
2. Specify which evaluation relation queries are charged and which modified
   relations are not; an implementer may not substitute a generic node count.
3. Specify observation/reset placement across search preparation, posts,
   polling, root/iteration boundaries, completed searches and reset.
4. Test consumer behavior when clock words cross signed/wrap boundaries.
   Ledger-word parity is not proof that all elapsed-time consumers agree.

The joined ordinary-search and session contracts connect these rules without
requiring solver or pondering modes. Component and joined tests have finite
coverage; they are not a proof of all reachable clock-wrap combinations.
The work formula does not establish strength calibration or netbook equivalence.

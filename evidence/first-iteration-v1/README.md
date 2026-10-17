# First unrestricted root iteration: partial evaluation

The native first-root loop visits each generated legal root exactly once in
natural order. The first two roots use the full root window; subsequent roots
use the second-ranked completed score as lower boundary. Equal scores occupy
separate places. Strict best improvement replaces the root PV, while ties
retain the earlier PV. Children inherit the root's retained state, and the
shared pawn cache follows actual full-evaluation visitation across roots.

The loop uses concrete recursive quiescence. Root preparation is outside the
search-work origin; all children share cumulative search/relation counts and
one execution budget. A stop unwinds to the public root history and returns an
error. No unfinished child or partial iteration becomes a completed result.

This remains a development interface with partial evaluation. Pawn progress/
races/endings, central influence, board patterns, nonneutral personality and
late-endgame adjustments are missing. Later ordinary iterations, remembered
results, host polling/timing and production protocol are also pending.
Conformance and qualified performance are not claimed.

Generic release executable SHA256:
`c784316bcd98e8d4b0d9e1d4c6199bcb2939bff2a8bb45a1b1d9ca70dd91f66b`.
The exact local executable is `rook2-dev-exact`. The neighboring build directory
contains the original build receipt and a verified archive of all pre-Cargo
source/tool bytes. The archive sidecar preserves the original receipt hash.

All ten released first-iteration requests were explored with three fresh
repetitions each. Initial candidate order matches every expected sequence.
A separate sorted-score consumer checked each actual returned window, best,
second, tie-preserved PV and cumulative work. Diagnostics on/off agree on
score, PV, candidate order and charged work. Existing selected-quiescence
outputs match all ten previously frozen outputs exactly after refactoring
their cumulative-sequence boundary. These checks are recorded in
`exploration.json`; they do not assert full expected steps or score parity.
Incomplete evaluation changes several root choices and trees.

Three cases were measured with5,000 fresh search preparations/iterations per
process, one excluded warmup and three measured fresh processes per variant:

| Case | Nodes | Full/fast | Pawn hits/replacements | CPU median, diagnostics on/off |
| --- | ---: | ---: | ---: | ---: |
| Initial position | 20 | 20/20 | 4/16 | 0.131767 / 0.128500 s |
| Opening history | 48 | 43/48 | 32/11 | 0.359972 / 0.349432 s |
| Promotion-sensitive | 98 | 82/45 | 82/0 | 0.421407 / 0.413148 s |

CPU includes root preparation and process startup/output; the displayed work
and evaluator counts exclude root preparation. Diagnostic root-step capture
allocates vectors at the root boundary; recursive tactical nodes do not
allocate. The non-diagnostic specialization omits those step captures.
One full and one fast call can occur at the same node. All outputs are
identical within each schedule. CPU range/median spans0.02–1.52%; three samples
are insufficient for a strong claim about small observer overhead.

Engines ran on CPU14 and orchestration on0–5,8–13. Aggregate guest CPU15
observations recorded766 idle ticks and zero other ticks across collection.
This does not verify continuous host-task exclusion. Instructions/cycles
remain unavailable. No cross-machine or KingRE performance ratio is inferred.
TT traffic is still absent; the production representation decision remains
provisional pending ordinary search and remembered-result integration.

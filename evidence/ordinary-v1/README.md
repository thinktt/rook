# Ordinary/tactical pipeline baseline with partial evaluation

This frozen development slice includes actual iterative ordinary recursion,
quiescence, shared pawn classification, learned history/killers, remembered
results, static/fast/null cutoffs, frontier estimates, extensions, mate probes,
scout retry and initial/tail internal ordering. One search-state owner shares
candidate buffers, ordering scratch, PV storage and counters across both modes.
Each candidate creates one child; a scout retry reuses that child's refreshed
retained state. IIO children preserve shared cache/learned effects while the
parent's retained state stays local.

The evaluator still omits pawn progress/races/endings, central influence,
bishop coordination/opening patterns, nonneutral personality and specialized
late-endgame adjustment/bounds. Root timing/work-clock scheduling, natural
host polls, production protocol and session/personality composition are absent.
The fixed development runner completes1–8 iterations or errors on its explicit
resource limit; it does not publish a partial result. It does not define the
eventual production depth limit or interruption publication policy.

Generic release SHA256:
`6bcff22e53bb6313908040ac67efd5583830f56478bbf1dacded122a663bbf5c`.
The exact executable is retained locally as `rook2-dev-exact`. The neighboring
build receipt and verified source archive preserve the exact pre-Cargo bytes,
compiler and settings. No PGO, reference ratio or qualification is claimed.

All six neutral ordinary-iteration fixture requests were explored with three
fresh logical repetitions and diagnostics both on/off. Initial candidates,
actual stable carryover, root windows/ranking, strict PV consumption and
cumulative result consistency were checked independently. Scores, PVs and
work still differ from released expectations because evaluation is incomplete;
these are not fixture passes. All20 earlier quiescence/first-root observations
remain exactly unchanged after moving shared state into `engine::Search`.

`exploration.json` and `workload-exploration.json` retain those observations.
The native suite separately tests interruption unwinding, diagnostics parity,
legal PVs, stable root carryover, real IIO/null/scout activity under collisions,
and a controlled lower-bound entry whose one-item tail retains extension flags
into the main loop. That controlled test is not a claim of natural reachability
from a fresh search of that exact root.

| Workload | Searches/process | Visits/search | Full/fast | Pawn hits/replacements | TT hits/stores | CPU median, diagnostics on/off |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Opening depth4 | 128 | 4189 | 2820/3617 | 2067/753 | 274/1134 | 0.821361/0.812400 s |
| Tactical depth3 | 128 | 5588 | 2970/4765 | 2169/801 | 57/595 | 1.218969/1.222708 s |
| Quiet rook depth4 | 128 | 1484 | 1234/1031 | 1234/0 | 24/383 | 0.201254/0.204105 s |
| IIO/collision depth6 | 16 | 50766 | 47495/0 | 47419/76 | 185/20224 | 0.560846/0.559637 s |

The first three use the specified64 MiB TT budget. The last deliberately uses
96 bytes/two groups as a separate collision/IIO stress workload; do not combine
it with the others as a typical engine aggregate. It enters816 initial and5
tail ordering phases, with1012 passes and2297 ordering children. Other cases
exercise actual fast cutoffs, mate probes, null trials and refreshed scout
retries. Full/fast counts can overlap at one node, and material-threat charges
also contribute to the reported relation total.

Each schedule has one excluded fresh-process warmup and three measured fresh
processes. All outputs agree within each schedule. Diagnostics on/off agree on
each completed iteration's order, score, PV and work, plus final consumption
witness. Counts are omitted rather than reported as genuine zeros when
development diagnostics are disabled. CPU range/median spans0.37–1.90%; the
samples do not establish a reliable small observer-overhead estimate.

CPU includes search preparation, initial table allocation, logical search clears,
all completed iterations and process startup/output. Charged counters exclude
root preparation and do not equate to machine instructions. Repeated searches
start fresh logical state while reusing allocated storage in one process.
Raw output, direct-child wait4 receipts, hashes and schedules are retained.

Engines requested CPU14; recorder and orchestration used0–5,8–13. Across the
collection, guest CPU15 recorded2294 idle ticks, one user tick and two system
ticks. Keep that interference observation: this was not proof of complete
exclusion. PMU instructions/cycles remain unavailable. These are development
CPU measurements, not final performance qualification or evidence of meeting
the KingRE reference target. Layout/restoration alternatives remain unselected.

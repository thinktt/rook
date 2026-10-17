# Fixed-root CPU baseline with composed evaluation

This version includes the evaluator formula families absent from earlier
baselines: central/pattern terms, pawn progress/endings/races, fortress bounds
and late-endgame finishing. Root-bound settings also work through the native
API. These four neutral fixed-iteration searches match the released expected
scores, PVs and cumulative N/R work. Their changed behavior/work makes earlier
partial-evaluation timings unsuitable as speedup denominators.

Generic x86-64 release SHA256:
`5528fb2329975697aee1318710303081713ddb43da227210268f90ecbe87d5ad`.
The exact executable is retained locally as `rook2-dev-exact`. The neighboring
`evaluation-v2-build-20261017` directory binds the successful stable build,
compiler/settings, verified pre-Cargo source archive and 114 passing native tests.
The external 1,352-case checker uses the same engine source bytes.

| Workload | Searches/process | N/search | R/search | Full/fast | Pawn hits/replacements | CPU median on/off |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Start depth3 | 512 | 507 | 3379 | 485/497 | 257/228 | 0.422765/0.418455 s |
| Opening history depth3 | 256 | 1811 | 8936 | 1515/1740 | 1251/264 | 0.837192/0.837676 s |
| Quiet rook depth4 | 256 | 1436 | 1508 | 1191/1045 | 1191/0 | 0.418364/0.416842 s |
| IIO empty depth5 | 128 | 2064 | 871 | 1727/156 | 1708/19 | 0.289306/0.287501 s |

The last case enters two internal-ordering phases and searches two ordering
children. All use the 64 MiB TT budget. Allocated search storage is reused in
each process, with fresh logical learned/pawn/TT state for every repetition;
TT generation wrap also performs its actual physical clear. Full/fast counts
may overlap at one node; semantic R includes specified material-threat queries.

Each schedule runs one excluded warmup and three measured fresh processes.
All four outputs agree byte-for-byte within each schedule. Every emitted root
step with diagnostics on matches expected windows/ranking/PVs/work. With
diagnostics off, per-step records are absent; all emitted iteration/final
fields still match, and results/work/consumption witnesses agree across modes.
The native checker separately verifies move kinds; this CLI emits coordinate
strings. CPU range/median spans 0.18–2.06%; these few samples do not establish a
small observer-overhead difference. `collect.py` records the complete schedule
and separately checks behavior after timing; `workloads.json` preserves inputs,
expected projections and fixture identities.

CPU is direct-child wait4 user+system: startup/preexec, initial allocation,
root preparation, all repetitions, logical clears and output are included.
N/R exclude root preparation. Recorder/helpers use 0–5,8–13 and the engine
requests CPU14. CPU15 recorded 1 user tick and 1632 idle ticks during collection;
this is not proof of absolute exclusion. PMU instructions/cycles are unavailable.

This is an F1 development CPU collection with selected exact native anchors.
It does not establish the complete F2 trace ladder, qualification workload
endpoints, calibration, PGO/reference ratios or performance acceptance. Timed
root scheduling, host polls and public personality/session/protocol remain
unimplemented. No final layout/restoration selection is made here.

Two collector preflights are retained locally and excluded from these results:
one used an incorrect output path and the next expected diagnostic records
from the specialization that omits them. The final eight schedules are fresh
and complete; no engine failure or abandoned sample is hidden in the aggregate.

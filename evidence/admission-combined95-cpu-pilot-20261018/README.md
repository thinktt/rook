# Shared search scalar boundaries — generic95 CPU pilot

Candidate6e7b2935 sums14.486596s in six case CPU medians versus14.461466s
control731aa0aa: ratio1.0017377215,0.173772% higher. Four medians are lower,
two higher, and all six observed ranges overlap. This finite comparison finds
no clear regression. It does not establish CPU neutrality, confidence bounds,
own-PGO behavior or final cost qualification.

| Case | Current88king median CPU s | Candidate95 median CPU s |
| --- | ---: | ---: |
| profile-01 |1.144045|1.146129|
| profile-02 |0.8083645|0.8081465|
| profile-04 |4.7582585|4.7902865|
| profile-05 |2.618208|2.6136735|
| profile-35 |4.856774|4.8537035|
| profile-29 |0.275816|0.274657|

The only native differences are ordinary.rs, ordinary_policy.rs and
quiescence.rs. They share the existing ordered draw/clear/reversal boundary,
handoff, terminal mate scalar and effective evaluation bounds/cutoff. The
candidate adds a separately bounded mate-leaf component and seven cold
diagnostic transports. No bitplane or known-check experiment is composed here.

Fresh candidate151 native tests,54 strict replays, eight-wire/24 searches,
149 adapter units and7393 cases/95 operations/89 complete files all pass.
The existing current88king147/54/eight-wire validation is exactly bound.
Both artifacts use the same generic compiler/settings. `regression-gate.json`
checks exact source closures, artifacts and retained functional dependencies.

All60 fresh native lifetimes pass the unchanged strict oracle:12 excluded
warmups and48 measurements, four per variant/case in alternating order. CPU is
whole native-process wait4 user+system time; engine affinity14 and helpers
0-5,8-13 are independently checked. No other owned native/build/test/training/
profiler/Git job overlapped; children performed small source/text work only.
Parent actually observed55883/ace2ea exit0, followed by independent original
receipt reconciliationc7bf06 exit0.

The bounded codegen review still records ordinary text+753bytes/local RSP+16
and Q text+23bytes with unchanged RSP. Static inlining/callsite changes are not
dynamic work counts. The absence of a clear finite CPU regression does not
remove those costs or qualify later profiles. Whole-suite CPU15 snapshots
contain19 nonidle ticks (13user/6system); other guest panes/system/host were
untouched. Those aggregate ticks cannot attribute engine/variant interference.
No absolute sibling idle, exclusive-host, PMU or reference claim follows.

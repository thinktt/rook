# Activity arithmetic widths: measured and parked

Baseline generic artifacte7168491 and isolated candidate73ad8177 use identical
43-file native sources except `src/activity.rs`. Both pass all54 strict replays.
The candidate also passes134 native tests and10,000 broad constructed placements
against our independent prior coordinate-based influence/activity oracle.
Builds, source archives and source-bound arithmetic review are retained in
the neighboring `activity-*-build`, `activity-widths-check`,
`activity-widths-oracle` and `activity-widths-preparation` directories.

The fixed whole-native pilot contains six declared public cases. Each has one
excluded warmup per variant, then four alternating forward/reverse measurement
rounds:60 lifetimes total,48 measured. Every lifetime exits normally and passes
the strict oracle. Engine affinity is CPU14 and helpers use0–5,8–13. No owned
build, native test, other collection or profiler overlaps the pilot.

Sum of case medians is14.947846s baseline versus14.9086955s candidate, ratio
0.997380860 (0.261914% lower). All six observed sample ranges overlap. Candidate
medians increase on profile01,02 and29, and decrease on04,05 and35. These finite
observations do not support adopting the change or spending a separate PGO
trial on it. The prototype remains isolated and canonical8c source is unchanged.

[analysis.json](analysis.json) independently reconciles all60 original native
wait4 receipts, strict comparator results, hashes, exact schedule, normal exits,
CPU/task observations, sample selection and aggregates. `driver-terminal.json`
and `tool-terminal.json` retain actual successful return observations.
All original attempts and sample bytes remain preserved. No PMU, confidence
interval, qualified reference comparison or full54/12 performance claim follows.

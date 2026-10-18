# Canonical persistent attack-plane PGO pilot

The canonical repository artifact
`915f83e4c93bbb1b378c9a7d4250f93981347a4a75760db1510330ee395277fd`
was compared with prior production `1dc996b2` on six unchanged public cases.
Each case has one excluded warmup per variant and four measured alternating
AB/BA rounds:60 fresh native lifetimes,12 warmups and48 measured. All pass the
unchanged strict comparator and exit normally. No failed/replaced samples or
dropped outliers occur.

Independent original-byte reconciliation checks all60 native wait4 receipts,
comparator outputs, schedules, hashes, input stability, CPU14/single-task
observations and housekeeping helper placement. The actual session96474 terminal
return was0(chunk e385de,04:32:41UTC); the precise tool result was recovered from
this agent's own persisted transcript after compaction and retained separately.

| Sum of six CPU medians | Seconds |
| --- | ---: |
| Prior production1dc996b2 |15.388885|
| Canonical persistent915f83e4 |14.907624|

The ratio is0.968726714, or3.127329% lower. All six case medians are lower, but
profile04 sample ranges overlap. `analysis.json` retains all per-case samples
and finite ranges; these do not establish a confidence interval, universal
improvement or a noise allowance. This result belongs to canonical915f, separate
from the earlier isolated f4a2f8bf trial.

Native wait4 includes startup/destruction and a small Python pre-exec prefix;
there is no protocol byte relay. Placement has a one-time post-exec observation,
without continuous descendant monitoring or an assertion of exclusive host
ownership. No owned builds/tests/other engines/profilers overlapped collection.
PMU, reference calibration, final resource/observer/uncertainty qualification,
complete54/12 cost and current-artifact gameplay obligations remain open.

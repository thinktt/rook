# Checked-slider generic screen — parked

The unchanged fixed70 gate failed. Summed case-median CPU is13.406918s control
and13.370616s candidate: ratio0.9972922934,0.27077% lower. Four of seven cases
are lower, worst ratio1.007133475. Required: ratio≤0.995, at least five lower,
worst≤1.02 and all validity checks. No retune, repeat, PGO rescue or adoption.

All70 fresh native lifetimes,14 excluded warmups/56 measured, pass original live
and independent offline replay checks. All70 native PIDs are unique. Four measured
samples per case/variant; no deletion. The exact frozen schedule and198 immutable
pins match after collection. Generic images remain0cde6b78 (candidate) and5d10b2fa
(control), separate from retained own-PGO62.

| Case | Control range / median CPU s | Candidate range / median CPU s | Ratio |
| --- | --- | --- | ---: |
| profile-01 | 1.003696–1.011722 / 1.008316 | 0.989237–0.999071 / 0.993662 | 0.985467346 |
| profile-02 | 0.709165–0.719513 / 0.715666 | 0.714801–0.723247 / 0.717315 | 1.002304146 |
| profile-04 | 4.299915–4.309890 / 4.307588 | 4.251857–4.297221 / 4.270359 | 0.991357459 |
| profile-05 | 2.364702–2.390185 / 2.373726 | 2.351462–2.373518 / 2.368746 | 0.997902033 |
| profile-29 | 0.238135–0.244658 / 0.242126 | 0.240554–0.241122 / 0.240851 | 0.994736212 |
| profile-35 | 4.369942–4.384348 / 4.375042 | 4.364553–4.420589 / 4.392485 | 1.003986934 |
| profile-08 | 0.384023–0.388931 / 0.384455 | 0.385126–0.390145 / 0.387197 | 1.007133475 |

Guest CPU15 interval tick deltas: `[0, 0, 0, 14585, 0, 0, 0, 0, 0, 0]`. These are point observations;
no owned15 workload, continuous sibling idleness or exclusive host claim is made.
No PMU, full54, regular12, production-PGO or qualification run occurred.

Raw: `/home/legolas/rook2-experiments/checked-enumeration-compiler-20261020-01`.
Actual collection `2d171d/0`, independent reconciliation `844d68/0`.
See `screen-closed-summary.json` for exact supports; compiler report remains frozen.

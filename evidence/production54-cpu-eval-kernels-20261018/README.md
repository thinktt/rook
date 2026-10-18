# Canonical evaluation-kernel whole-native CPU collection

Artifact `8c4619a7c3f33bed6eb17c396a7d9d8d223262dd1595c4f23812e5de17809953`
uses the integrated compact relation kernel and typed-list influence enumeration.
Its canonical build/profile and regression identities are recorded in
[build evidence](../production-eval-kernels-use-build-20261018/README.md).

The unchanged public54 corpus was collected in stored case order. Each case has
one excluded warmup and three measured fresh lifetimes:216 total,162 measured.
Every lifetime exits normally and passes the independent strict replay oracle.
The direct wait4 boundary includes native startup, setup, search and destruction.
Engine affinity is CPU14; helpers use0–5,8–13. No owned build, other engine or
profiler overlapped this collection. These observations do not establish
exclusive host execution.

The sum of54 case CPU medians is **81.828432s**. The published reference sum is
63.431779s, giving raw uncalibrated ratio1.290022656. Per-case raw reference
ratios range1.212027151–1.398729317. The maximum observed three-sample
range/median is1.751798%; this finite spread is not a confidence interval or an
acceptance allowance.

The previous915f83e4 collection totals88.486549s. All54 new case medians are
lower; the aggregate is7.524440% lower. Earlier3660fecf totals97.685122s.
These sequential historical comparisons include multiple implementation and
compiler-profile changes. The separate balanced pilots support the individual
engineering decisions; timing is never transferred between artifacts.

[verification.json](verification.json) independently reconciles every original
raw sample, oracle result, normal exit, native accounting receipt, affinity/task
observation, source/input/artifact identity and exact integer-microsecond
aggregate. [historical-comparison.json](historical-comparison.json) retains every
case comparison. The driver and reconciler are under
`../production54-eval-kernels-preparation-20261018/`, including the actual
successful terminal observation. Raw streams remain byte-preserved.

This is a complete local CPU collection with reported-only status. No PMU
instructions/cycles, calibration, qualified uncertainty profile, full12 costs,
focused gameplay or full gameplay qualification is established by it.

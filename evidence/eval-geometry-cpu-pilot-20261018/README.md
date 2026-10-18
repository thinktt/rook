# Shared evaluation-geometry whole-native CPU pilot

All60 complete lifetimes passed direct native accounting and the unchanged
strict oracle. Both variants are generic x86-64/non-PGO. The prospectively fixed
six cases include the earlier four anchors plus the completed54 collection's
largest absolute-cost and largest raw relative-gap cases. Each case uses one
excluded warmup/variant then four AB/BA/AB/BA measured rounds (12 warmups,
48 measured lifetimes). No owned builds, other engines or profilers ran during
measurement. Driver/recorder/checker/input/artifact hashes and before/after local
context are retained. CPU includes the whole native lifetime plus a small child
pre-exec prefix and excludes comparator/supervisor CPU, with no byte relay.

| Case | Baseline median CPU s | Shared tables median CPU s | Ratio |
| --- | ---: | ---: | ---: |
| profile-01 | 1.3556775 | 1.3289675 | 0.98030 |
| profile-02 | 1.0501020 | 1.0438365 | 0.99403 |
| profile-04 | 5.6070890 | 5.5155670 | 0.98368 |
| profile-05 | 3.1053480 | 3.0094840 | 0.96913 |
| profile-35 | 5.6990380 | 5.5400360 | 0.97210 |
| profile-29 | 0.3521230 | 0.3458350 | 0.98214 |
| Sum of case medians | 17.1693775 | 16.7837260 | 0.97754 |

Every median improves; the sparse case02 has overlapping ranges and is
individually inconclusive. Other cases and the weighted local total support
adopting the shared immutable tables without extra mutable node state. This is
a modest generic-build result; an independent PGO rebuild/comparison must check
the production profile. All54 strict replays,130 native tests and the10,000-
placement coordinate-oracle differential check precede this pilot. No complete
reference-performance, PMU or cross-host qualification is claimed.

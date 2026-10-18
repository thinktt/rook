# Shared geometry with matched compiler PGO procedures

The same six prospective cases used for the generic experiment compare two
independently trained PGO artifacts. Each source trained on one full unchanged
54-case ordinary replay, with retained raw profiles/merge/use receipts. Both
production artifacts passed all54 strict replays before timing. The fixed
schedule retained one excluded warmup/artifact/case and four measured alternating
forward/reverse rounds:60 normal strict-oracle/native-accounting lifetimes,
12 warmups and48 measured. All source/artifact/recorder/input hashes match.

| Case | Previous PGO median CPU s | Shared geometry PGO median CPU s | Ratio |
| --- | ---: | ---: | ---: |
| profile-01 | 1.2823120 | 1.2579365 | 0.98099 |
| profile-02 | 0.9635110 | 0.9469720 | 0.98283 |
| profile-04 | 5.1783790 | 5.0026620 | 0.96607 |
| profile-05 | 2.9046960 | 2.7821065 | 0.95780 |
| profile-35 | 5.3373825 | 5.1759115 | 0.96975 |
| profile-29 | 0.3351145 | 0.3250070 | 0.96984 |
| Sum of case medians | 16.0013950 | 15.4905955 | 0.96808 |

The sum is3.19% lower and every median improves. This supports keeping
shared immutable evaluation geometry under the PGO production profile. All
samples/paired differences, range/min/max data, local context, direct native
wait4 accounting and strict output records are retained. CPU includes the whole
native lifetime plus the small pre-exec child prefix and excludes comparator/
supervisor CPU; native streams have no relay. No owned build, other engine or
profiler ran during collection. Root source editing stayed in an isolated
uncompiled hypothesis; frozen measured artifacts did not change.

This remains a local six-case comparison. The earlier complete54 CPU collection
belongs to the previous PGO artifact; these pilot ratios do not replace a new
complete collection, calibration, uncertainty, game timings or final acceptance.

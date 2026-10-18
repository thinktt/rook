# Generic versus compiler PGO CPU pilot

The native source and release/target settings match. The sole optimization
change is use of the retained compiler profile; each artifact has its own
verified build receipt and source archive. Both passed all54 strict public
replays before this collection. Four anchor cases were fixed before launch,
with one excluded warmup/variant and four measured rounds in AB/BA/AB/BA order.
All40 native lifetimes passed direct accounting and the unchanged strict oracle
(eight warmups,32 measured). No owned builds, profilers or other engine runs
were active during collection.

| Case | Generic median CPU s | PGO median CPU s | PGO / generic |
| --- | ---: | ---: | ---: |
| profile-01 | 1.3637930 | 1.2982810 | 0.9520 |
| profile-02 | 1.0459355 | 0.9776320 | 0.9347 |
| profile-04 | 5.6148580 | 5.2234045 | 0.9303 |
| profile-05 | 3.1412035 | 2.9357120 | 0.9346 |
| Sum of case medians | 11.1657900 | 10.4350295 | 0.9346 |

This establishes a modest additional local improvement, not a full-corpus or
qualified cross-host performance result. `analysis.json` retains every sample,
range/spread and paired difference. The driver/case manifests and before/after
context bind schedule, artifacts, inputs, recorder and observed placement.
CPU includes native startup/setup/search/destruction plus the small child
pre-exec prefix, excludes comparator/supervisor CPU, and has no protocol relay.
PMU access, calibration, full54/12 collections and final uncertainty remain open.

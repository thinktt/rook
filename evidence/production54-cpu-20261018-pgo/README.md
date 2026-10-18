# Complete local54 whole-native CPU collection

Frozen ordinary PGO artifact
`3660fecfa0c4a681e6a7152009417199d91706fa9acf0508e073c76427e18438`
completed the stored54-case corpus order, with one excluded fresh-process warmup
then three measured fresh-process repetitions for each case:216 lifetimes,
54 warmups and162 measured. Every run passed the unchanged strict public oracle,
normal native exit, artifact/recorder identity and untruncated stream checks.
`verification.json` revalidates actual per-run receipts independently of the
collector's summary-complete flag.

The sum of54 case medians is97.685122 native user+system CPU seconds. Per-case
samples, medians, ranges and range/median spreads are retained; the maximum
observed three-sample range/median was2.443%. This spread is an observation, not
a frozen uncertainty interval or a tolerance for acceptance.

| Largest local costs | Median CPU seconds |
| --- | ---: |
| profile-35 | 5.351241 |
| profile-04 | 5.264343 |
| profile-43 | 4.765384 |
| profile-17 | 4.576844 |
| profile-07 | 3.955962 |
| profile-44 | 3.633689 |
| profile-52 | 3.630313 |
| profile-49 | 3.510522 |

This is a complete **local CPU collection**, not a qualified performance pass.
The published whole-life reference sum is63.431779s; the raw uncalibrated planning
ratio is1.5400. Hardware calibration, resource/observer compatibility and final
uncertainty remain open. `planning-analysis.json` binds the published input hash
and retains every raw ratio/gap for engineering prioritization; it makes no
threshold pass/fail decision and applies no hardware conversion.

Direct wait4 native CPU includes startup, all setup, search, output/destruction
and the small Python child pre-exec prefix; it excludes supervisor/comparator
CPU. Native stdout/stderr descriptors are inherited directly, with no byte relay.
The strict checker retains complete native output strings in each raw comparator
report; commands/inputs are bound to unchanged public workload/checker hashes.
One post-exec task/affinity observation plus source-audited single-process engine
ownership is used; continuous descendant monitoring is not claimed. Engine CPU14
and housekeeping helper placement are observed. Before/after local resource and
CPU snapshots do not establish exclusive host ownership. Other owned activity
was limited to document inspection and cold adapter editing, with no builds or
other engine/profiler runs during measurement. PMU I/C/IPC are unavailable.

The manifest freezes960s/run,3600s aggregate, stream/receipt/aggregate byte guards
and outer10s cleanup. Those are development safety bounds, not chess time inputs.
No run failed, was replaced, or was silently retried. Complete12-game timing,
full gameplay and mandatory diagnostic/production review remain required.

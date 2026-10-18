# Matched baseline, lookup and combined PGO comparison

Frozen variants915f83e4/1e5d075d/b17776fb each pass54 strict public replays and
eight interruption fixtures. The two prototypes have their own independently
verified54-case compiler profiles. No trial profile or timing is reassigned
to canonical source integration.

For each of six unchanged cases: one warmup per variant, then four measured
forward/reverse rounds. All90 lifetimes reconcile independently:18 excluded
warmups and72 measured. Every original native/comparator hash, strict pass,
normal exit, schedule, artifact/input identity and one-time CPU14/single-task/
housekeeping observation matches. No sample failed, was dropped, replaced or
rerun. Session71231 actually returned0(chunk87a01d).

Sum of six CPU medians:14.7940530s baseline,14.3190285s lookup,13.7237695s
combined. Combined/base0.927654477(7.234552% lower); combined/lookup0.958428814
(4.157119% lower). Every combined observed maximum is below both respective
control minima. `analysis.json` retains all samples and comparisons. These are
finite ranges, without confidence intervals, universal improvement or acceptance
allowances. Three-variant ordering uses four alternating forward/reverse rounds;
it does not rotate the middle variant through all schedule positions.

No owned build/test/other engine/profiler overlapped collection. Native wait4
includes startup/destruction and a small Python pre-exec prefix, with no protocol
relay. The source is adopted under decision0006; canonical training/build and
cost evidence follow separately. Final PMU/resource/observer/uncertainty/
calibration, full54/12 and gameplay obligations remain open.

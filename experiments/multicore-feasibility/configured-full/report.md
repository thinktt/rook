# Practical own-PGO FULL mode: retain for behavioral qualification

**The usable two-thread mode retains the measured acceleration.** Original54
search wall is64.369022s versus69.056196s accepted serial:6.79% lower, at1.863x
total CPU. It is0.15% above the previous positive two-thread PGO image. The
single-CPU configuration defect is addressed; scaling beyond2 remains unresolved.
Recommend retain this option for exact-image behavioral qualification, with no
further tuning selected here. This is research evidence, not local adoption.

## Frozen source and artifacts

Source `66f35e440b2180d4d22c2bcd0e5a8c99c0f1185d` adds only configuration-time
affinity policy to the practical integration. Above-one requests query the
configuring thread's permitted Linux mask before mutation; exactly one allowed
CPU configures1 while retaining requested budget. Larger masks permit at most2,
without claiming physical cores/capacity. Requested1 skips querying. Query
failure is explicit/unchanged configuration; unsupported non-Linux multi-thread
policy errors. No engine affinity setter or reactive change after external
placement is introduced. The shared numerical body/worker protocol is unchanged.

Own-PGO ordinary image,7,536,152 bytes:
`/home/legolas/rook2-experiments/configured-full-20261024-01/production/rook2-pgo`
SHA256 `8f26d39fd1a69bc8a3aa6da2c364b6ddb4b065bc585a27c7420ae994566f8b1b`.
Own profile `production/training/merged.profdata` in that experiment root:
SHA256 `b7bd8ca21e8b9f64426af124be95bfc14feadd9b01bb94fb14bbefc7c550c6be`.
Preserved controls are accepted serial5cf01208 and previous positivea977bb00;
main, their bytes and the previousf9ee profile remain unchanged.

[Plan](plan.md), [configuration proof](verification-proof.json),
[results](results.json), [closure bindings](proof.json),
[complete54 timings](full54-timings.csv). Raw source/build/profile/stream receipts:
`/home/legolas/rook2-experiments/configured-full-20261024-01/`.

## Production-build result

| Original54 single-observation sum | Accepted serial5cf | Previous2 a977 | Cleaned1 | Cleaned2 |
|---|---:|---:|---:|---:|
|Search wall seconds|69.056196|64.270245|69.831350|64.369022|
|Whole native CPU seconds|69.137609|128.593350|69.912544|128.778462|
|Whole lifetime wall seconds|69.479642|64.758741|70.250667|64.852088|
|Maximum observed RSS KiB|68676|68936|68664|68960|

Cleaned2 saves6.7875% search wall versus accepted serial and7.8222% versus its
inline mode. CPU ratios are1.86264x/1.84199x. Whole-lifetime wall saves6.66%
versus serial. Cleaned1 is1.1225% above accepted serial; source/profile/code-layout
costs are combined, not isolated to a guard or affinity query. Cleaned2 is0.1537%
above a977 in the same window; that descriptive difference is not a significance
claim. This is not a new current KingWCR/KingRE comparison.

Cleaned2 improves46/54 cases versus accepted serial,22/54 versus a977. Eight
serial regressions sum0.233468s; largest absolute loss is43,+0.121712s (+4.11%).
Worst relative case15 loses6.72%; best relative46 saves11.90%. The43 loss occurs
in a substantial search, so a startup-only explanation or short-search selector
is unsupported. All rows are retained. One observation/configuration/case has
no per-case uncertainty estimate.

The preceding repeated small study gives four-case median sums
11.036039/10.487385/11.150617/10.545647s for serial/previous2/cleaned1/cleaned2.
New2 saves4.4436% versus accepted serial, costs0.5555% versus previous2, with
1.91046x serial CPU. Its ranges lie below serial in35/08/04 and above in43
(+4.66%). Summed worker maxima10.564711s stay below summed serial minima
11.018807s: a descriptive envelope, not a confidence interval or fixed numerical
gate. This evidence selected the already-authorized unchanged-image extension;
the saved decision binds the small audit and exact artifact.

## Execution and accounting

One fresh instrumented source build trains original54 once per mode1/2:
108 native PID-bound profiles, one equal-weight merge, one use build. Compiler
recipe matches both controls: Debian Rust1.85.1/LLVM19.1.7, GNU generic x86-64,
O3/ThinLTO/one CGU/panic-abort/debug1 and profiled-only ExtTSP. Source, flags,
tool/profile identities and missing/stale-profile warnings are checked. Merge
record/raw hashes are independently audited; LLVM was not independently remerged.

108 training lives/1248 posts,64 small lives/864 posts (16 excluded warmups,
48 retained) plus4 idle probes, then216 descriptive54 lives/2496 posts all pass.
Total388 replay lives/4608 posts; every native/driver stage exits0, with no retry,
replacement, repeated training, new variant or retune. Separate read-only auditors
verify original projected streams, placement, native exits, schedules and metrics.

Native startup allows14/6 before configuration. External placement verifies
coordinator14/helper6 before releasing the first setup input; original pipes and
tap/comparator stay unchanged. This ordering matters: configuring after narrowing
the coordinator to14 would deliberately select one thread. Helpers/builds use
0–5,8–13, owned15/7 unused. Point masks/guest tick records do not prove isolation.

Search wall spans original go-write→move-data. Direct wait4 CPU/RSS/lifetime
includes all native threads, configuration, active helper, parking, joined quit
and a small Python pre-exec prefix. Four startup250ms idle probes register0 ticks
at10ms resolution, not literally zero cost or every idle period. Active search
can still spin during blocked Host callbacks. Captured stdin excludes end(data)
cleanup; pinned runner and complete output/exit retain that boundary. No PMU.

## Configuration evidence and next decision

12 focused unit checks and13 native CLI controls pass, including invalid/query
failure with unchanged configuration/cache. The failure is injected through the
setter's narrow query seam, not induced in the OS. Exactly two original08 lives,
requested1/2 with only CPU14 permitted, each observe one native task and pass10
posts. Lifetimes0.3892s/0.3874s replace pathological sharing; the old55.61s result
is preserved and was not rerun. Poll/boundary task observations are finite.

These native configuration checks use the generic22c60b44 image; the production
8f26d39f image has the same frozen source and its separate training/replay evidence.
The unchanged worker source reuses the prior practical-integration protocol and
11s controlled-barrier evidence. Production panic-abort does not imply unwind
recovery; default-off archived features were not requalified.

Proceed next with a selected exact-image behavioral qualification scope, including
the configured policy, before calling this adopted. No broad mandatory or gameplay
suite, production adoption, external delivery/release, final performance
qualification or scaling beyond2 follows from this study.

# FULL split: parked lifecycle and own-PGO survey

**Retain this positive research option.** The own-PGO two-thread image completes
the descriptive54 in63.946851s search wall versus68.237305s production control:
**6.29% less elapsed time**, costing **1.873x total CPU**. It now parks between
searches. This is not adoption, qualification or evidence of scaling beyond2.

## Frozen identities and method

Source `5612b55f395a31874ef9bc77611792155d5e920b`;
[design/finite plan](plan.md), [lifetime review](lifetime-review.md),
[results](results.json), [proof](proof.json), [54-case table](full54-timings.csv).
Raw images, profiles, source/build archives and all observations:
`/home/legolas/rook2-experiments/full-split-production-20261024-01/`.

Use image `rook2-pgo`,7,511,128 bytes, SHA256
`a977bb0031b1beeb6fb50f8c391968f6e2d959ae86d648727442bdf027c88763`.
One binary supports inline/default budget1 and worker budget2. Merged own-source
profile SHA256
`f9eefbd025c74a3247449c10fa0074fc5f178bcc49f1d623bed36cd9dcbdcadc`.
Exact accepted dynamic serial control remains `5cf01208…`,7,118,416 bytes;
its compiler executables/versions and production recipe match this build.

Debian Rust1.85.1/LLVM19.1.7, generic x86-64 GNU, O3/ThinLTO/one-CGU/panic-abort/
debug1. One fresh instrumented image executes original54 once per mode,108
PID-bound profiles merged once with equal weights; then one use build with
profiled-only ExtTSP. No missing/stale-profile warnings admitted. The training
adaptation covers actual worker execution and joined shutdown, retaining native
profiles and strict replay instead of relying on an unexecuted serial-only worker
path. Recorded merge/raw/hash verification is **not an independent remerge**.

All108 training,36 small comparison and162 full54 replay lives pass:306 lives,
3624 ordered posts. Small comparison excludes9 warmups, retaining3 observations
per case/configuration. Its predetermined sufficient automatic extension trigger
passes; it is not a universal gain/rejection threshold. The54 extension has **one
observation per case/configuration**, rotated order, no replacement or repeated
training. No full mandatory suite, gameplay gate, external delivery or release.

## Elapsed, CPU and serial cost

| Original54 single-observation sum | Production control | Candidate budget1 | Candidate budget2 |
|---|---:|---:|---:|
|Search wall seconds|68.237305|69.171315|63.946851|
|Whole native CPU seconds|68.307437|69.241398|127.931937|
|Whole lifetime wall seconds|68.516236|69.450678|64.234730|
|Maximum native RSS KiB|68656|68860|68912|

Worker wall reduction is6.29% versus production control and7.55% versus candidate
inline; CPU ratios1.873x/1.848x. Candidate inline costs1.37% more search wall than
production control. That measured difference includes source/profile/code-layout
changes; it does not isolate the lifecycle guard. Default budget1 starts no helper.

Worker improves47/54 cases versus production control,49/54 versus candidate inline.
Worst relative control regression is profile22,+5.81%. The seven control losses
sum0.240366s; largest absolute loss is profile43,2.886502→3.005729s (+0.119227s).
Regressions cannot all be dismissed as tiny searches or startup. Best relative
improvement is profile46,13.03%; no case selector or tuning was tried.

Small three-case median search-wall sums are8.090458/8.204298/7.482624s for
control/inline/worker. Worker improves7.51% versus control and8.80% versus inline;
35/04 ranges separate from both controls, while08 is close to production control
with overlap. All retained samples/ranges and full CPU/RSS are recorded.

Search wall spans original go write to move callback. Direct native wait4 CPU/RSS
and lifetime wall include startup/setup, worker startup, search, parking, joined
shutdown and a small Python pre-exec prefix; all worker CPU is included. Thus the
higher CPU cost is visible rather than hidden in main-thread samples. No PMU
instructions/cycles were collected. Historical separate-window KingWCR timings
supply no current comparative qualification.

Coordinator14, helper6, harness/build0–5/8–13; owned siblings15/7 unused. Point
native thread-affinity and search-endpoint observations pass, with guest proc
context preserved. This does not establish exclusive guest/host isolation.

## Lifetime behavior and focused checks

The helper starts parked; outer lexical ordinary/timed/first-iteration/public-Q
guards retain active spinning across FULL calls. Nested scopes preserve the outer
owner. Final release drains/discards pending output and waits for empty slots plus
PARKED acknowledgment; direct standalone FULL owns a one-call scope. Root weights
and all packet inputs remain owned snapshots. No worker crosses a search lifetime
with stale work, and switching budget1/dropping the owner joins it.

Eleven actual focused tests pass:4 worker protocol,2 native owner/error and5 prior
numerical/search tests. They cover normal completion, node stop, live finish/
abort/host error, capacity error, repeated roots, nested ownership, abandoned
requests and test-profile unwind. An initial wrong worker-test filter ran0 tests;
its receipt is preserved and only the correct group was added. A first idle check
failed before native launch because the old image path omitted its target triple;
that setup failure is retained, with3 actual final idle processes afterward.

In one250ms startup-idle interval, old generic budget2 consumed0.25 CPU seconds;
new generic budget1/2 each registered0 ticks at10ms resolution. The three own-PGO
idle probes likewise each register0 ticks. PGO startup handshake is29.55–30.48ms
and quit-through-supervisor exit15.42–15.91ms; these include harness boundaries,
not isolated helper-start/kernel times. Guard-state tests establish parking after
actual search exits; the CPU probes sample startup idle, not every idle period.

Limits remain explicit: active searches can spin while Host callbacks block;
production panic=abort skips lexical destructors (unwind tests cover test-build
behavior only); CPU6 and the10s wall-abort policy remain research-specific. Timed
search still uses logical N/R and prescribed polls, not measured helper CPU/wall.
Finite replay and selected host tests are not exhaustive live-host fidelity.
Input tap captures write() setup/query/search bytes; cleanup via end(data) remains
outside the tap, with pinned runner plus complete output/exit checks retained.

## Recommendation

Keep the parked, own-PGO FULL split as the measured two-thread baseline and retain
the negative queue checkpoints unchanged. The net54 gain is useful, serial cost
and extra CPU are material, and scaling beyond2 remains unresolved. No further
native variant or adoption is selected in this closure; return the next larger
pure-work opportunity as a bounded source recommendation before implementation.

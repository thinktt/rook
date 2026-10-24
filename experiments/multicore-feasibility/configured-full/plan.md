# Configuration cap and one practical own-PGO comparison

Selected memo:
`/home/legolas/agent-memos/imp2-lead-to-imp2-configured-full-pgo-20261024.md`.
Preserve main, the frozen5cf accepted serial and a977/f9ee positive research
artifacts, and the usable-full55.61s single-CPU result unchanged.

Configuration takes the calling thread's current Linux `sched_getaffinity`
snapshot before mutation for requests above1. Exactly one allowed CPU caps
configured execution at1 while preserving the positive requested budget;
otherwise configure at most2. Default/requested1 requires no query. Invalid
requests and query errors leave prior configuration intact. The query never
sets/widens affinity and does not infer physical cores, cgroup capacity or
exclusive ownership. A later external mask change does not reactively reconfigure
an already-created helper. Non-Linux multi-thread policy reports unsupported
until an authoritative implementation exists; default1 remains query-free.

First run focused actual-budget/cache/root/Host/lifecycle checks and the CLI parser.
A narrow query seam exercises failure/no mutation; it is not an OS fault probe.
Native inspection checks requested/configured under one-CPU and14/6 masks, and
original08 runs once each with requested1/2 under CPU14, with exactly one task
and original projected replay verified in both. Do not rerun the old two-thread
one-CPU image. Generic compilation here supports verification, not a timing study.
Checkpoint/freeze passing source before profile training.

Then one generic-x86-64 GNU instrumented image, original54 once per mode1/2,
108 PID-bound native profiles and one equal-weight merge. Own-source use build
uses the established Rust1.85.1/LLVM19.1.7 O3/ThinLTO/one-CGU/panic-abort/debug1
recipe with profiled-only ExtTSP. No stale profile, repeated training, retune or
variant. Record/hash verification of the merge is not an independent remerge.

Small comparison:35/08/04/43; accepted5cf serial, previousa977 current2 and new
cleaned1/2. One excluded warmup plus three rotated retained observations yields
64 lives,48 measured/16 warmups, plus4 separate250ms idle probes. External native
startup permits14/6; configure before supervisor pins/verifies main14/helper6,
then release the first protocol write. Original pipes/comparator remain unchanged.
All helpers/builds0–5,8–13, owned15/7 idle. Point observations are not isolation
proof. Search wall is original go-write→move-data; native wait4 CPU/RSS/lifetime
includes all helper CPU, startup, configuration, parking and joined shutdown.

If the new two-thread result remains clearly useful versus accepted serial in
the observed ranges, one descriptive original54 extension is authorized: one
rotated observation per configuration/case,216 lives, no repeats. Parent makes
that evidence judgment after small closure; no fixed numerical rejection gate
or automatic rescue. Otherwise close the small result and stop.

Use existing180s/life,1800s measurement-stream and2400s training caps with finite
supervision/owned cleanup. Preserve all native failures; no native retry. Keep
configuration verification, instrumented training and production timings distinct.
Independent raw/schedule/hash/placement reconciliation precedes closure. No broad
mandatory/gameplay suite, adoption, performance qualification, delivery or release.

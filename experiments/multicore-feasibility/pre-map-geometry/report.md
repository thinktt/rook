# Pre-map geometry result

Park unchanged. Staging is **0.6747% slower** than matching unstaged3 and
**1.5563% slower** than preservedd71 over the three-case sum of search medians.
The08 matched gain does not overcome35/43 losses. No PGO, retune or rescue.
c242/profile1a81 remains the provisional research leader; main/release untouched.

| Configuration | Search median sum, s | Whole-process CPU median sum, s |
|---|---:|---:|
| preserved1 | 8.469164 | 8.474204 |
| preserved3 | 7.345385 | 22.035551 |
| inline1 | 8.536931 | 8.541218 |
| unstaged3 | 7.409705 | 22.229743 |
| staged3 | 7.459699 | 22.378954 |

These are sums of three case medians, not one full54 run. Search covers the
original go-write through move-data callback; CPU is native wait4 including all
joined threads and the Python pre-exec prefix. Original35/08/43 each has one
excluded warmup and three interleaved measured observations/configuration.

| Case | Preserved3 median [range], s | Unstaged3 median [range], s | Staged3 median [range], s | Staged/off |
|---|---:|---:|---:|---:|
| profile-35 | 3.757338 [3.710459, 3.763802] | 3.762988 [3.753755, 3.781306] | 3.814557 [3.772224, 3.818555] | +1.3704% |
| profile-08 | 0.370990 [0.366005, 0.374099] | 0.378880 [0.373907, 0.379235] | 0.371018 [0.370299, 0.373848] | -2.0751% |
| profile-43 | 3.217057 [3.210132, 3.247899] | 3.267836 [3.249182, 3.271305] | 3.274124 [3.273602, 3.282948] | +0.1924% |

35 overlaps its matched sibling but is entirely above preserved3.08 is entirely
below its matched sibling but overlaps preserved3.43 is entirely above both.
Newinline1 costs0.8002% versus oldinline1; newunstaged3 costs0.8756% versus
preserved3. Staged CPU/off is1.006712x; staged CPU/retained is1.015584x.
Inline/common drift is not a causal subtraction from the feature result.
All45 samples and per-case CPU/wall/RSS medians are in [timing.csv](timing.csv).

All99 focused identities passed once.20 CLI controls, two dormant1/2 original08
affinity replays, one actual3 staged08 witness and one cold production layout
passed.60 replay lives reproduced700 ordered posts; all65 replay/idle native
receipts, placement, joined CPU, raw hashes and actual terminal chains reconcile.
All five250ms idle probes observed0 CPU ticks at100Hz; this is resolution-limited.
No semantic/native discrepancy detected in this finite scope; no broad
conformance/gameplay/performance qualification follows.

The first compile exited101 before running any unit: the new cfgtest helper
used unavailable serde_json. Only that test file parser changed; no dependency
or production bytes changed. [Repair binding](closure.json) preserves original
source/tools/pipeline/empty stdout/two E0433 diagnostics. The original clock
includes the repair gap: pipeline915.653s, terminal raw
audit932.693s of3600s.99 executions/99 passes/0 unit
failures, one separate failed compile; no successful control/request repeat,
deadline reset or repeated timing sample. All15 subsequent stage exits are0.

Actual production Shared1024/align64 is192B larger than preserved832; request,
PacketRegion320 and output/done offsets remain unchanged. Map payload128 at512,
ready at640; lifecycle704, latch768, wait832, Control896. Raw Packet312,
SideGeometry128/color; owner state6368/align16 and Flight80 are observed.
No actual allocator extent or compiled helper stack-frame size was measured.
New image7984136B versus7932032B; .text grows
14768B and .rodata1088B. This is whole variant/code/storage cost,
not evidence that a particular cache line or phase caused the result.

Every staged replay has a positive real final mapReady epoch:35=1574501,
08=361835,43=2523136. Unstaged3 and new three-thread idle remain0; disabled
inline/default/capped and old missing fields remain null. No hot census added.
Original4096spin/512sampling and Release done/SC completion exchange remain.

Sampled publication/kernel intervals now include optional geometry/map waiting;
they cannot be compared as the old isolated Activity interval. Residual join
starts after the inventory hook. Both winning readiness-conditional inventory
hooks remain: earlier completion may suppress early generation and move demand
later. Materialization/replay, map copy/acquisition, code/storage and changed
inventory execution are priced together. No min(map,geometry) saving bound,
additive prior inventory gain, isolated copy/cache/notification cause or universal
negative about pre-map work follows.

Ownership/cancellation and common numerical-consumer review are in
[ownership-proof.md](ownership-proof.md) and [source-review.md](source-review.md).
Helpers end all initial/map borrows before done or owned Abandoned; missing-map
abandonment reaches actual Control-checked park. Positive-depth restore is not
retirement; fixed callers must publish/join or unwind to saved zero before reuse.
Some/custom/public/FRESH/observed and modes1/2 preserve authority. Interleaving
tests support, rather than replace, the source weak-memory argument. Native
abort is distinct from test-build unwind cleanup.

Build: Debian rustc/cargo1.85.1, LLVM19.1.7, x86_64-unknown-linux-gnu generic
target-cpu=x86-64; settings/tool binaries exactly match preservedd71. Owner14,
helpers6/4, housekeeping0-3,8-13; siblings15/7/5unassigned. Guest placement
receipts are not host-exclusive scheduling or physical cache proof. No PMU run.

Exact artifacts/source/profile controls,41 preserved identities and1481 full
audit input pins are bound by [closure.json](closure.json) to the external raw
audit. Full raw path:
`/home/legolas/rook2-experiments/pre-map-geometry-20261029-01`.
New image SHA256: `e2fbdad54643e9577e8475fa12e7a7b153d7aaf4e460042c2b1923c6ffb9fdaa`.
Preparation/source patch are reproducible experimental setup, not a promoted
binary. Recommendation: retain the existing leader and park this variant.

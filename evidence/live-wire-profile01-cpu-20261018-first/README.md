# First ordinary profile-01 CPU pilot

This is a reported-only local development measurement, not whole-lifetime
acceptance or a reference-hardware comparison. The frozen first artifact is
`893448ddee8730364d239a1d2b8288acbe12cb94249733bbf1e3d52f8711a873`;
its [source/build evidence](../live-wire-build-20261018-first/receipt.json)
and separate 54-case correctness replay are retained.

The released `conformance/profiling/benchmark.mjs` ran unchanged on Vic with
its driver on housekeeping CPUs and the engine's verified affinity CPU14.
The workload is the complete unchanged `profile-01`, natural acquisition,
rnd=0, fine-work posts, one fresh-process warm-up and three measured fresh
processes. All four runs completed with identical posts and selected move.

| Quantity | Measured observations |
| --- | --- |
| Selected-move CPU seconds | 1.760, 1.760, 1.750; median 1.760 |
| Selected-move wall seconds | 1.763342, 1.761346, 1.752906; median 1.761346 |
| Last-post work field | 3,659,038 (1.219679333 virtual work seconds) |
| Last-post work / CPU second | 0.938215, 0.931053, 0.938215 |
| CPU accounting resolution | 10 ms |

The last-post rates use that post's own sampled CPU interval. They do not use
the later selected-move denominator. CPU fields are main-process user+system
samples around the host's go write request and output receipts. Startup, setup,
destruction, absolute CPU boundaries and go write completion are not measured
by this driver. These endpoints are distinct from primary whole-lifetime cost.

[Raw benchmark](benchmark.json) retains complete records and individual sample
boundaries. [Context](context.json) binds binary/build/tool/workload identities,
affinity/resource view and broader before/after guest CPU snapshots. That broad
window includes the launch-review delay: CPU15 accumulated seven user and ten
system ticks, so exclusive sibling idleness is not claimed. Host scheduling,
firmware, guest housekeeping and physical frequencies were not observed.
PMU access remains unavailable; no instruction/cycle count is inferred.

The first external launch review timed out without starting a measurement.
The sandbox fallback failed at `getconf` with EPERM. One permitted review retry
then ran the released benchmark successfully; the failed fallback is retained.
No system-wide affinity, isolation or measurement permissions were changed.

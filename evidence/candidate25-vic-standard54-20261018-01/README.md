# Candidate25: Vic standard54 timing

Exact candidate25 (`51529ceb…`), unchanged from the Bee delivery, passes all 54 cases on Vic. One excluded warmup and three measured fresh lifetimes per case:216 lifetimes, 54 warmups, 162 measured samples, 2496 matching semantic posts. No retries or sample deletion.

| Engine | Machine | Sum of 54 median search CPU (s) |
|---|---|---:|
| KingWCR, historical supplied benchmark | Bee | 64.140 |
| KingRE Rust v1.1.1 generic PGO, released reference | Bee reference host | 63.277733 |
| Rook2 candidate25, audited returned benchmark | Bee | 75.770 |
| Rook2 candidate25, this collection | Vic | 72.630 |

All entries sum the54 per-case medians rather than the elapsed duration of a complete benchmark batch. KingWCR's historical window, the released Rust reference, the Bee candidate25 window and this Vic window differ. Rust SEARCH native-leaf CPU and the benchmark process tick observations have different accounting mechanisms; these are informational comparisons, not a qualification decision. The earlier 63.431779s Rust number includes the whole process; 63.277733s is its search CPU total.

Candidate25 takes 72.630s search CPU on Vic versus 75.770s on Bee. Bee/Vic aggregate ratio is 1.043232824: Bee took 4.323% longer. Per-case ratios range from 1.000000 to1.071429; 10ms CPU quantization especially affects the short cases. This measures the observed difference for this exact candidate and workload, not isolated virtualization overhead or a universal machine conversion.

Vic summed median whole-native CPU is 73.059178s. Summed median search receipt wall is72.987961969s. Summing each case's observed search CPU minimum/maximum gives 72.320s to72.870s; this envelope is not a confidence interval.

The collection ran 2026-10-18T23:03:04.386610+00:00 through2026-10-18T23:08:33.605576+00:00. Engine affinity CPU14 was verified through native execution; helpers used 0–5,8–13. Sibling15 had 32920 idle ticks and 1 system tick over the batch, with no owned sibling workload. Finite observations and guest affinity do not establish exclusive host ownership. Cgroup/resource snapshots are retained; no host/global security or isolation settings changed. A previously owner-approved user-owned Herdr bridge affinity restriction was applied before the run and recorded in plan.json.

The existing controller tap records immediately before the GO write request through the received selected-move chunk, with native /proc user+system ticks (10ms resolution). Whole-native CPU uses the unchanged account_native.py direct-child wait4 measurement, including a small Python pre-exec prefix. The released strict comparator owns behavioral assertions. The unchanged tap captures stdin.write records; cleanup sent through stdin.end is absent from its stdin capture. Clean exits and the released comparator validate completion.

Independent verification recomputes all 216 native/tap records, identities, input hashes and 54 medians. Offline released checkReplay rechecks both the comparator record and independently captured native output for every lifetime: 432 checks. No additional engine runs occurred during verification. No PMU, full conformance, full gameplay gate or performance qualification is claimed.

Inputs:released king-spec commit 1c89c21a4645ec85adf28285616d822b3cd91f73;Rook2 source checkpoint a7d274950f43059dc594c79aa2cb9883c2907267. Exact build record, executable identity, schedule, recorder adaptation and helper placement are pinned in plan.json and collection/manifest.json. Full recorded evidence is in closed-collection.tar.gz, bound by archive-manifest.json. Per-case timing summaries are in timings.csv and independent-reconciliation.json.

Bee result: /home/legolas/spec-issues/v2.5.0/2026-10-18-imp2-candidate25-benchmark-results/

Rust reference: /home/legolas/king-spec/performance/statistics.md and reference54.json

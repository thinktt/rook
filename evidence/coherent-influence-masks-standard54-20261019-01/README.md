# Candidate37: Vic standard54 timing

Exact own-PGO37 image54be6552…c023f/source72 graph568e8737…c8c2f completes all54 cases:216fresh lifetimes,54excluded warmups,162measured samples,2496matching semantic posts. No retry or sample deletion. Independent receipt/accounting reconciliation and432 offline original checkReplay assertions pass; no further engine runs occur in verification.

| Engine/window | Search CPU summed medians(s) | Whole-process/native CPU summed medians(s) |
|---|---:|---:|
| Rust KingRE v1.1.1 genericPGO, released Bee reference |63.277733|63.431779|
| Rook2 candidate25, earlier Vic window |72.630|73.059178|
| Rook2 candidate37, this Vic window |71.050|71.424373|

These sum54 per-case medians, not elapsed benchmark-batch time. Current37 is2.175410%lower in search CPU and2.237645%lower in whole-native CPU than the earlier25 collection. Those separate Vic windows provide descriptive comparison, not a paired full54 causal speedup. The independently paired own-PGO70 screen measures2.147243%lower whole-native CPU at5/7lower under its predeclared rule.

Whole-native medians are lower in51cases and higher in3, with worst historical ratio1.008201(profile21). Search medians are lower in42, equal in11 and higher in1:profile39 rises0.14→0.15s at10ms tick resolution. Preserve all per-case samples/ranges in timings.csv and independent-reconciliation.json; no ranges are confidence intervals.

Current local37 totals are12.282784% above historical Rust search CPU and12.600299% above historical Rust whole-process CPU. Host/window/accounting differences remain; this is not final performance qualification or a measured Bee37 result. The audited Bee25 search total75.770 belongs to25 only; no universal Bee/Vic conversion is applied. Full12 cost qualification, comparison/repetition policy and production-domain review remain open.

Collection12:16:22.423716→12:21:45.348473UTC on2026-10-19. Native children useCPU14, helpers0-5,8-13; every receipt/PID/argv and finite task/affinity observation reconciles. CPU15 accumulated32292idle ticks and0nonidle ticks; no owned sibling workload.194selected user-owned Herdr/Codex threads were already on housekeeping;0affinity changes. Other idle actors may retain permission. No absolute guest/host/firmware exclusion or PMU claim.

Search boundary is the existing controller pre-GO-write→received move chunk using/proc10ms CPU ticks. Whole-native uses unchanged direct-child wait4 user+system including a small Python preexec prefix. The tap captures stdin.write; cleanup through stdin.end is absent from captured stdin. Original strict comparator/clean exits validate completion. Parent pins all77 launch inputs before/after both verifiers, including exact historical25 proofa093b0ba; native/source/build/profile/runtime/helper identities remain stable.

Original methods:accepted candidate25 collector/account_native/tap_wire and released1c89c21 replay assertions. Candidate37 collector differs only in descriptive labels; verifier changes only historical comparison data/labels. Actual outer collector terminald5a8b9/0, independenta2372e/0, offline original487824/0.

# First integrated development baseline

This is a local cost baseline of `material-square-activity-alpha-beta-v1`, not
a KingRE search-performance comparison. The artifact SHA256 is
`54ee2ff1149da5622f0edcc447ae99452834cfa862c62b7e56319a118be2e7a0`.
Its exact source/config/build identity is in
`../build-integrated-smoke-20261017-01/receipt.json`.

The frozen [workloads](workloads.json) use depth4 and eight deterministic
searches per fresh process. Each case has one excluded complete warmup and
three measured fresh processes, serially. Root setup and search arena creation
are inside each lifetime; the eight searches reuse arena allocation and reset
their invocation counters/PV. No TT, learned or pawn state is used in this
artifact. Scores, PVs and diagnostic occurrence counts agree across all four
lifetimes for each case.

| Case | Median complete-lifetime CPU seconds | (max-min)/median |
| --- | ---: | ---: |
| Quiet opening after six plies | 0.098104 | 4.23% |
| Tactical position with castling | 0.581026 | 1.65% |
| Sparse rook ending | 0.022789 | 0.82% |

CPU is direct-child kernel wait4 user+system, including the small Python child
pre-exec prelude. Wall spans the recorder's fork request through reaping and
has collection/polling overhead; it is separate from internal search latency.
Raw samples, wall costs, warmups and outputs are retained in each case directory;
[results.json](results.json) summarizes all samples and occurrence counts.

The recorder places engine execution on CPU14 and itself on helpers0-5,8-13.
The outer orchestration script waited between child collections and did not
have its own explicit affinity restriction; it is outside engine CPU. Guest
affinity does not prove exclusion of all other guest or host activity. No
compilation or external native correctness checks ran during collection. This
is a development profile, not final isolated/counter qualification.

Missing score terms include pawns, shelter, central influence, patterns and
endgame/final finishing. Search is plain fixed-depth alpha-beta with natural
legal order; quiescence, full/fast selection, TT/repetition, KingRE root windows,
extensions/pruning/IIO, clocks and production output are absent. The artifact
reports no KingRE semantic N/R; its activity relation-query counter is only
that implemented component's work. Partial-tree cost cannot establish the
approved whole-engine target or select the final representation by itself.

Instructions/cycles/IPC are unavailable. The core projection check is separate
behavior evidence, not a qualified complete search oracle. No timing outlier
was dropped, no follow-up run selected, and no reference ratio is calculated.

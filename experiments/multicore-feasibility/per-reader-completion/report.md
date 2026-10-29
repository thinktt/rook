# Per-reader completion registration: fixed generic result

**Park unchanged**, per imp2-lead. Separating completion flags did not improve
this fixed comparison. Preserve provisional PGO leaderc242/profile1a81 and generic
controld71. No retune, PGO, adoption or qualification follows.

[All ranges](case-ranges.csv), [results](results.json), [concise closure](closure.json),
[actual layout](production-layout.json), [source proof](ownership-proof.md).

| Configuration | Sum of search medians, s | Joined whole CPU medians, s | Lifetime wall medians, s |
|---|---:|---:|---:|
| Preserved d71 inline1 | 8.430636 | 8.435134 | 8.454378 |
| Preserved d71 mode3 | 7.352079 | 22.054324 | 7.379842 |
| New5152 inline1 | 8.503982 | 8.508725 | 8.527395 |
| New5152 mode3 | 7.388668 | 22.166591 | 7.417460 |

New3 loses0.4977% wall and0.5090% CPU to preserved3; inline loses0.8700% wall.
The new mode3/inline ratio remains0.868848 wall and2.605160 CPU, describing the
existing parallel option rather than a benefit of this change. These are sums
of three case medians, not full54 totals or paired per-run speedups.

| Case | d71 mode3 median [min,max], ms | New mode3 median [min,max], ms | New/old change |
|---|---:|---:|---:|
| 35 | 3758.463 [3752.717,3773.986] | 3779.760 [3779.114,3790.704] | +0.5666% |
| 08 | 368.698 [366.085,372.009] | 372.485 [367.101,374.807] | +1.0272% |
| 43 | 3224.918 [3224.393,3231.752] | 3236.423 [3233.446,3238.244] | +0.3568% |

All three mode3 medians lose;35/43 ranges are separated negatively and08 overlaps.
Losses are21.297/3.787/11.505ms respectively,36.589ms in total. Inline35/08/43
changes are+0.6394/+0.2200/+1.2362%;35/08 ranges overlap,43 is separated. Common
inline drift is not a causal subtraction, rescue or estimate of synchronization
benefit. Three repetitions describe this window, not statistical significance.

Only colors_worker.rs changes in the69-file isolated derivative. The original
numeric/input/activation/retirement bodies, eight selected types,68 other source
files and sole concrete Cells Sync are source-checked unchanged; dispatch's one
exhaustion signal statement is explicitly normalized for this comparison. Normal
reader i retains one unconditional SC false exchange after actual done; a true
consumer always notifies under Sleep without rechecking. The sole waiter registers
both flags before every cold predicate, clears both on resolved exit and keeps
4096 spins. Side terminal/startup/join-error signals use their own flag; owner
shutdown/exhaustion execute both exchanges separately before OR. Stop never
acknowledges peer retirement. Owned inputs, original observations, both owner
inventory hooks and every numerical/body boundary remain fixed.

All27 existing worker controls plus seven new tests pass:34 exact identities,
34 executions, no failure or repeat. The seven contain23 fixed subcases covering
both-reader publication/terminal before/between/after registration, stale true
notifiers across generations, two pending notifiers, spurious re-registration,
owner terminal and non-short-circuited second exchange.43 unaffected controls and
numeric evidence are reused, including the historical single-owner70-pass/71-
execution fixture-only failure/repair history. There is no new broad suite.
Test unwind controls do not certify production panic=abort recovery.

The one generic production build passes14 CLI/two actual original08 affinity
fallbacks. Rust1.85.1/LLVM19.1.7 and the GNU generic x86-64 opt3/ThinLTO/oneCGU/
debug1/panicabort recipe match d71; no PGO. Before timing, the cold production
instance confirms Shared896B/
align64/address phase0, OwnerState6368B/align16 and exact prefixes. Request/packet/
white/black/lifecycle/latch0/latch1/Wait/Control offsets are0/64/384/448/512/576/
640/704/768. Output56+done8 slots remain64B, done at440/504. Query is off during
timings. Compared with d71, Shared grows64B and Wait/Control move64B. More cold
registration/clear/signal operations and a larger line footprint belong to the
complete cost; no allocator extent, cache traffic or isolated RMW cost is measured.

- Candidate SHA256 `515207502cb3d4a4a86bbd21139f9b3654e8cf4f7956de89bddb6ffd79f8f77d`,7935496 bytes.
- Control SHA256 `d71c4f9fa662af73c81d891f16c2b56ded2d2ccfbe982ed5ae81829a14fd573d`,7932032 bytes.
- Candidate worker SHA256 `77e7edd25bb737b18b40e8a90bd1026b5f321b2694b406bef509dbdd7c211c40`.
- Setupd87e0b61; frozen preparation SHA256 `0c55f15b06ba6505e15e11de2901d39a02ae0f47347ff2de139f9c57bd9cd625`.

Original35/08/43 use one excluded warmup plus three fixed interleaved observations
per cell:48 replay lives/36 measured/12 warmups, followed by four250ms idle probes.
Both hooks are requested in every mode and dormant in1. All560 ordered posts
and original logical-work projections pass independent saved-raw replay. All52
comparison/idle native receipts plus separate cold layout process are terminal;
the full external audit binds1205 paths. Six stages exit0 first attempt, original
pipeline200.252s/terminal audit210.410s within3600; collection145.357s within1800,
life180s. No source repair, engine request repeat, clock reset or profile generation.
One pre-native patch-context whitespace check was resolved using a zero-context
patch; the old preparation/patch/freeze script are preserved externally. Engine
source was unchanged by that metadata cleanup.

All four idle probes record0ticks/250ms at100Hz: below resolution, not literal
zero work. Measured per-process peak RSS ranges are old1 19300–19584KiB, old3
19348–19848KiB, new1 19300–19608KiB, new3 19404–19616KiB. Separate peaks must not
be summed as simultaneous allocation requirements.

Owner14/helpers6,4;H0-3,8-13;siblings15/7/5 unassigned. Actual pre-input thread
placement passes and housekeeping is restored; guest affinity is not host
exclusivity. Search wall uses original go-write→move tap; wait4CPU/lifetime/RSS
include setup and joined shutdown. Existing residual-join samples exclude eager
generation. No PMU/cache-cause claim or performance/mandatory/12-game/external
qualification follows. Raw builds/runs are preserved at
`/home/legolas/rook2-experiments/per-reader-completion-20261029-01`.
Quiet hold is released and native work is stopped at the decision point.

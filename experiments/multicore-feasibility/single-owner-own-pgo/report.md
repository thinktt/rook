# Single-owner activation: unchanged own-PGO/full54

Retain exact **c242f0e4 / profile1a81bdac** as the provisional research leader,
per imp2-lead's review. Preserve a4ec and all predecessors. This descriptive
comparison does not qualify or adopt the engine.

[All54 rows](full54.csv), [machine results](results.json),
[concise terminal closure](closure.json), [actual layout](production-layout.json).
These are direct sums of one observation per case/configuration, with no
warmups or repeated cells; they are not medians or confidence intervals.

| Configuration | Search wall, s | Joined native CPU, s | Lifetime wall, s | Mean / maximum lifetime peak RSS, KiB |
|---|---:|---:|---:|---:|
| Accepted serial5cf | 69.640657 | 69.723556 | 70.071645 | 22194.5 / 68696 |
| Retained a4ec inline1 | 70.327902 | 70.413184 | 70.753595 | 22240.0 / 68744 |
| Retained a4ec mode3 | 58.934958 | 176.819294 | 59.430524 | 22328.2 / 68892 |
| New inline1 | 70.539314 | 70.630608 | 70.972331 | 22214.6 / 68816 |
| New owner3 | 58.692377 | 176.093198 | 59.189951 | 22350.1 / 68816 |

| Comparison | Search-wall change | Whole CPU ratio | Faster / slower cases |
|---|---:|---:|---:|
| owner3 / retained3 | -0.4116% | 0.995894 | 39 / 15 |
| inline1 / retained1 | +0.3006% | 1.003088 | 16 / 38 |
| retained1 / serial1 | +0.9868% | 1.009891 | 6 / 48 |
| inline1 / serial1 | +1.2904% | 1.013009 | 2 / 52 |
| owner3 / serial1 | -15.7211% | 2.525591 | 54 / 0 |
| owner3 / inline1 | -16.7948% | 2.493157 | 54 / 0 |
| retained3 / retained1 | -16.1997% | 2.511167 | 54 / 0 |

New3 saves242.581ms in total against retained3. The15 losses sum55.409ms.
Largest absolute gain is35:48.170ms (-1.4324%). Largest absolute loss is43:
17.175ms (+0.6299%), reversing its generic gain. Best relative case is01
(-2.3668%); worst is22 (+1.3204%,6.785ms). All loss rows and four outliers per
comparison are retained in results; the CSV contains every case, wall/CPU/
lifetime/non-search/RSS observation and all seven wall ratios.

The new inline image is0.3006% slower than retained inline and1.2904% slower
than accepted serial. Its largest absolute loss against retained inline is42,
42.498ms (+2.1421%); best absolute gain is17,20.455ms (-0.5930%). These
controls price common source/profile/build changes. Do not subtract inline
drift to isolate lock savings. The generic0.5223% gain had overlapping ranges;
this separate profile/workload gives no per-case significance or causal cache,
mutex or allocation conclusion. Mode2 is trained, not measured here.

The69 source inputs are unchanged from the closed generic experiment, including
its test-only Q fixture permission repair.70 unique passing controls are reused:
71 actual executions included one original fixture failure, retained outside
Git with its first build/source/receipts. No unit control or source was rerun or
repaired in this lane. Normal owner dispatch/completion/readiness avoid Control
locks; owned input, narrow cell ownership, original SC-RMW, observations,
numerical bodies and public standalone pre-observer parking stay fixed. Saved
depth restoration remains subordinate to terminal/drained state.

Training matches the retained joint mixture: original54 once each in inline1,
current2 (both hooks requested/dormant), ordinary-on/Q-off3 and ordinary-on/Q-on3.
216 unique native PID-bound profiles reproduce2496 ordered posts. Equal raw
inclusion feeds one canonical LLVM19 merge and one ACTUAL independent supervised
remerge into fresh output. They are byte-identical; only the canonical profile
feeds the single use build. Training is not performance evidence. Rust1.85.1/
LLVM19.1.7, GNU generic x86-64, opt3/ThinLTO/oneCGU/debug1/panicabort and use-only
ExtTSP match the retained recipe. No training, profile or source retune.

- New use image SHA256 `c242f0e498ceeddb9aa2532cbace46730ffebcb6a0e756274179b3297c1b40da`,7902552 bytes.
- Canonical profile SHA256 `1a81bdacaeee3ac4b949cb495f8a99f0d68c96579cca4e7b807f83a501169910`,127648 bytes.
- Retained image SHA256 `a4ecf096d2144a79608b0ff4f3dc827bc8e5119730f2c43b29f46d1f7ffe62b5`; accepted serial `5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a`.
- Source checkpoint19a1c1b8; this lane's setup2dee84db. All37 protected artifacts remain unchanged.

Fresh14 CLI/two original08 affinity fallbacks and one cold actual-production
layout admission pass. Shared832B/align64/address phase0 plus OwnerState6368B/
align16 match the closed generic projection. Request/packet/white/black/
lifecycle/latch/wait/Control offsets remain0/64/384/448/512/576/640/704. The old
Shared was7168B; moving state to owned Box also changes indirection, placement
and startup. No allocator-header extent or cache traffic was measured. Layout
query is off throughout training/comparison.

Original54 case order rotates five configurations modulo5. Slot counts are
serial[11,10,11,11,11], retained1[11,11,10,11,11], retained3[11,11,11,10,11],
inline1[11,11,11,11,10], owner3[10,11,11,11,11]:10/11, not perfect balance.
270 comparison lives reproduce3120 ordered posts; five idle probes each record
zero ticks over250ms at100Hz, meaning below resolution rather than zero work.
491 training/comparison/idle native rows plus the separate cold layout process
are terminal. The full terminal audit binds1932 paths and2941 row-file checks;
the concise closure pins that external audit instead of duplicating its bulk.

All eight native stages exit0 first attempt. Original pipeline1216.045s is
within3600s; training592.269s within2400 and comparison503.363s within1800;
life bound180s. One post-pipeline metadata invocation used unsupported `--raw`
and exited2 at argparse, before the closer body. Corrected `--root` passes;
the exact error record is bound in closure. No tool/source change, merge repeat,
engine request repeat, profile regeneration or clock reset accompanied it.

Owner14/helpers6,4 (training mode2 helper6), housekeeping0-3,8-13, siblings15/7/5
unassigned. Actual pre-input placement passes and housekeeping is restored;
guest pinning does not establish exclusive host execution. Search wall is the
original go-write to move tap; joined wait4 CPU/lifetime/RSS include startup,
setup and teardown. RSS peaks are per process with case-specific TT sizes, not
simultaneous allocations. Original sampled residual join excludes eager
generation; active helpers may spin through blocking Host callbacks. These
finite replay/controls are not mandatory/regular12/full3288 qualification or a
matched Bee/KingRE comparison.

Raw builds/profiles/receipts are preserved at
`/home/legolas/rook2-experiments/single-owner-own-pgo-20261028-01`.
Native work is stopped. The separately selected per-reader completion design
is source-only; it changes none of these frozen bytes.

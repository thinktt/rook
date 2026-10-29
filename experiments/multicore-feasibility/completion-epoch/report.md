# Strong completion epoch: fixed generic result

**Park unchanged**, per imp2-lead. All three mode3 medians are slower despite a
small inline improvement; no demonstrated net gain warrants PGO or retuning.
Preserve provisional leaderc242/profile1a81, genericd71 and every predecessor.

[All ranges](case-ranges.csv), [results](results.json), [concise closure](closure.json),
[actual geometry](production-layout.json), [lowering](lowering.json),
[source/wake proof](ownership-proof.md).

| Configuration | Sum of search medians, s | Joined whole CPU medians, s | Lifetime wall medians, s |
|---|---:|---:|---:|
| Preserved d71 inline1 | 8.459844 | 8.463833 | 8.482418 |
| Preserved d71 mode3 | 7.342935 | 22.029017 | 7.369485 |
| New9853 inline1 | 8.444726 | 8.448893 | 8.469748 |
| New9853 mode3 | 7.365883 | 22.098191 | 7.393414 |

New3 loses0.3125% search wall and0.3140% whole CPU to preserved3. Inline gains
0.1787%, with all three inline ranges overlapping. No causal subtraction can
turn this into a notification gain. New3/inline wall0.872247 and CPU2.615513
describe the existing parallel option, not benefit from this change. These are
three-case sums of medians, not full54 totals, per-pair speedups or significance.

| Case | d71 mode3 median [min,max], ms | New mode3 median [min,max], ms | New/old change |
|---|---:|---:|---:|
| 35 | 3743.577 [3732.660,3756.676] | 3752.711 [3750.560,3765.077] | +0.2440% |
| 08 | 371.511 [371.159,371.698] | 372.117 [371.531,372.355] | +0.1631% |
| 43 | 3227.847 [3227.582,3231.044] | 3241.055 [3235.301,3243.209] | +0.4092% |

35/08 ranges overlap;43 is separated negatively. Losses9.134/0.606/13.208ms
sum22.948ms. Inline35/08/43 changes are-0.0501/+0.0898/-0.3711%. The CSV
retains all12 cells and every wall/CPU/lifetime/non-search/RSS range.

Only colors_worker.rs changes in the exact69-source derivative. Normal done
becomes SC, then the normal publisher reads the single flag SC and unconditionally
owes Sleep/notification on true without clearing/rechecking. Only the cold
predicate after SC registration uses SC done equality. Hot4096-spin/readiness/
output consumption remain Acquire. Every old cold terminal SC exchange/helper/
caller,21 production declarations, all27 old test bodies, selected ownership/
numeric bodies,68 other source files and the sole Cells Sync are source-checked
unchanged. Observations, both inventory hooks, input/retirement/reverse edges and
terminal-depth cleanup remain fixed. Native interleavings support but do not
replace the reviewed local SC/coherence and mixed terminal proof.

All27 base worker tests plus five targeted tests pass once:32 exact identities,
no failure/ignore/repeat. The targets cover before/around registration for either
reader, saved true loads across exit/new generation, both true loaders, spurious
re-registration and terminal exchange while a normal wake is owed. Real delayed
peer drain, partial startup and nested exhaustion remain covered.43 unaffected
controls/numerical evidence are reused, including the historical70-pass/71-
execution fixture-only failure/repair record. No broad suite or feature gate.
Test unwind is distinct from production panicabort behavior.

One matched generic build uses Rust1.85.1/LLVM19.1.7, GNU generic x86-64,
opt3/ThinLTO/oneCGU/debug1/panicabort and no profile.14 CLI/two actual original08
affinity fallback checks pass. Before data, actual non-test Shared832/align64/
address phase0 and OwnerState6368/align16 match d71. Single latch576, Wait640,
Control704 and all payload prefixes/done440/504 remain unchanged; query is off
during timings. No allocator/header extent or cache geometry was inferred.

The two saved objdump inspections pass before collection, followed by the parent
instruction read on the original clock. [Lowering summary](lowering.json) binds
the complete dumps, source-correlated sites and surrounding instructions:

- Old normal done at18c24 is `mov %rbp,(%rax)`, then18c2a calls helper467e0. Its flag exchange is `xchg %al,0x240(%rdi)` at467ea.
- New done at18caa is `xchg %rax,(%rcx)` after a generation copy/pointer reload;18cad reads the flag with `movzbl 0x280(%r14),%eax`. Test/branch18cb5/18cc1 selects the inline notification path.
- New cold terminal helper retains flag `xchg %al,0x240(%rdi)` at4698a. No normal flag RMW or explicit fence appears at the designated normal publication sites. The true notification branch still contains mutex/Condvar atomics.
- The normal notification body is now inline rather than the old helper call. The containing entry18420 reserves328B instead of312B, with changed spill slots/register work. Whole .text grows576635→577051B (+416). These are observed code differences, not an isolated xchg-location cost or an allocation/cache explanation.

Register bases differ between sites; the source mapping and actual instructions
bind them without assuming an Arc-header displacement. Matching the intended
mechanism was a pre-data admission, not a performance claim or compiler proof.
The cold SC predicate uses ordinary memory loads at44131/4413d on this target;
its source ordering and unchanged hot Acquire scope remain explicitly admitted.

- Candidate SHA256 `98538a3892888e99505cebe420f64269fb2fb486d6a6b92d9637d2d5ccdfbbb5`,7934496 bytes.
- Control SHA256 `d71c4f9fa662af73c81d891f16c2b56ded2d2ccfbe982ed5ae81829a14fd573d`,7932032 bytes.
- Worker SHA256 `d5e8da29ce545b22a780efd3b4a59e952f7579b6d52dfdafdb3b5aec989ef01d`.
- Setupe3622510; frozen preparation SHA256 `33f1f942433521193e3f874bf2bc3d3c620f207518fcd6a64aded0ccb16f9fb1`. All40 protected artifacts remain unchanged.

Fixed original35/08/43 use one excluded warmup plus three interleaved observations
per cell:48 lives/36 measured/12 warmups, then four250ms idle probes. Both hooks
are requested and dormant in1. All560 ordered posts/logical-work projections pass
independent saved-raw replay. All52 comparison/idle native receipts plus separate
cold layout are terminal; full external audit binds1229 paths. Seven stages exit0
first attempt, original pipeline310.436s/terminal343.026s within3600, including
the pre-data instruction-inspection gap. Collection147.340s within1800, life180s.
No source repair, repeated completed request/control, clock reset or PGO.

All four idle probes record0ticks/250ms at100Hz, meaning below resolution. Measured
per-process RSS ranges are old1 19248–19676KiB, old3 19368–19732KiB, new1
19248–19592KiB, new3 19340–19704KiB; separate peaks are not simultaneous memory
requirements. Owner14/helpers6,4;H0-3,8-13;siblings15/7/5unassigned. Pre-input
placement passes and housekeeping is restored; guest affinity is not exclusive
host isolation. Original go-write→move tap bounds search; wait4CPU/lifetime/RSS
include setup and joined shutdown. Existing sampled residual join excludes eager
generation. No PMU/cause, mandatory/regular12/external/performance qualification
claim follows. Raw evidence:
`/home/legolas/rook2-experiments/completion-epoch-20261029-01`.
Quiet hold is released and native execution is stopped at the decision point.

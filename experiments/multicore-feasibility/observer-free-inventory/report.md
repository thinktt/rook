# Observer-free inventory: both matching modes regress

**Park this exact variant.** Removing research observations does not improve the selected three-case run. Lean3 is 6.95% above retained3; lean4 is 6.52% above sibling lean3, 13.92% above retained3 and 12.42% above old4. Preserve the stronger own-PGO 67d/profile948747 and all previous artifacts. No native rescue or follow-on is selected.

[Timings/ranges](timings.csv), [results](results.json), [closure](closure.json), [plan](plan.md), [source review](source-review.md), [preserved setup repair](preparation-repair.md).

One original 35/08/43 stream, four frozen configurations, one excluded warmup plus three rotations each: 48 strict replay lives /560 ordered posts, 36 measured/12 warmup, then four idle probes. Independent saved-raw reconciliation passes. These are sums of case medians, not full54 totals.

| Case | Preserved3 | Old4 | Lean3 | Lean4 | Lean4 / sibling3 | Lean4 / retained3 |
|---|---:|---:|---:|---:|---:|---:|
|35|3.847451s|3.791272s|4.006152s|4.156835s|+3.76%|+8.04%|
|08|0.385448s|0.396447s|0.430759s|0.477241s|+10.79%|+23.81%|
|43|3.455570s|3.602744s|3.785626s|4.124332s|+8.95%|+19.35%|
|Median sum|7.688469s|7.790463s|8.222537s|8.758407s|+6.52%|+13.92%|
|Whole CPU median sum|23.067305s|31.162349s|24.669376s|35.033480s|1.420x|1.519x|
|Lifetime wall median sum|7.717574s|7.820419s|8.252441s|8.788603s|—|—|

All lean4 retained samples exceed all sibling lean3 samples in each case; all lean3 samples exceed retained3, and all lean4 samples exceed old4. Full ranges and all three samples per cell are preserved in results. The lean4/sibling3 changes are +3.76%/+10.79%/+8.95% for 35/08/43. Lean3/retained3 changes are +4.12%/+11.76%/+9.55%. The net negative is consistent across these cases; three observations do not qualify other workloads.

Old4 remains mixed versus retained3: −1.46%/+2.85%/+4.26%, aggregate +1.33% at 1.351x CPU. Lean4/old4 adds 12.42% wall and 1.124x CPU. Shared cleanup and the fourth-reader increment are separate: even sibling lean3 regresses, and the fourth reader adds another 535.870ms over it. No serial configuration is included, so no serial-cost conclusion follows.

Median cell peak RSS spans 19496–19732KiB. All four 250ms idle probes observe 0 ticks at 100Hz (10ms resolution), rather than establishing literally zero CPU. Complete native CPU/lifetime includes startup/setup, all threads, joined shutdown/reporting and a small Python pre-exec prefix. Search wall retains the original go-write→move-data callback boundary. Disabled versus historical report formatting also differs outside that search interval.

The clocks, histograms, producer atomic counts, owner-ready sample and late demand/discard Control locks are absent from BOTH lean modes. This deletion changes packet/output/control layout and compiler/code placement as well as instructions. The measured result prices that complete variant; no particular cache-line, pickup, compiler or scheduling cause has been established. `.text` old4/lean is 580971/562475B; `.rodata` 325524/323836B. Retained3 `.text` 562459B has a distinct hash despite near-equal size. This is net matched-mode evidence, not an isolated cost for an atomic instruction or a lower bound on every possible lean design.

## Fidelity and exact identity

- The 65-file source derives from frozen inventory65 (23ff9d69/7074456e), with only colors_worker.rs, evaluator.rs, ordinary.rs and the existing inventory owner test module changed. Activity/Shelter, generation/admission, thread cap, numerical kernels, whole-helper transport and other source remain unchanged. The source patch applies to that bound inventory base, not the later whole-helper source.
- Private installed receipt is a zero-sized marker with no epoch key/destructor/transport lease. Some appears only after the used slice and length are installed; None keeps native fallback. Early returns drop the marker locally. Original ordering/generated/N/R/supplied-map authority and null-descendant row ownership stay at their demand points.
- Request/done, Published/Joined/Discarding, actual third-reader retirement, reverse output edge, active scopes, single-waiter unconditional SC handshake and 4096 spins remain. Public/FRESH scope close points are preserved. Source review found no removed observation field with admission or lifetime authority; 14 key protocol bodies are identical.
- 40 distinct focused controls pass: 29 worker, 8 actual owner and 3 scope; 8 unchanged evaluator numerical/cache tests and earlier 17 math controls retain historical evidence. The actual test path contains no cfg(test) restoration of removed statistics. Disabled report is exactly {"enabled":false}. Test-only snapshots read existing synchronization state.
- 15 exact-image CLI/cap controls and two original 08 requested4→configured1/2 fallback searches pass. Actual main14/color6/4/inventory2 placement is gated before first input. All 48 benchmark raw streams match original score/move/posts/work and native exits; finite checks are not broad mandatory/gameplay qualification. No new helper-work counts or demand/readiness census is claimed; policy continuity is supported by source and focused tests.
- New same-image lean3/4 SHA256 `6da55696941e4197edd1c82499eb233d2da520630868722776da06492221e6c7`, 7,794,440B. Controls are immutable7ac72f mode3 and36c40a mode4; full identities/ELF hashes are in results. Generic Rust 1.85.1/LLVM19.1.7, x86-64 GNU,O3/ThinLTO/oneCGU/debug1/panic-abort, no PGO. Both preserved control recipes/source maps are independently admitted.

## Failed setup receipts and original clock

Initial setup b7465ceb compiled; worker29 passed. The owner group passed 7/8, then a new assertion confused inventory_request (an epoch) with a request count: public root preparation used epoch1, ordinary inventory used epoch2. Score/generated assertions had passed. The sole source repair is test-only: public root must leave private request 0, and the ordinary request must equal the next actual colors epoch. Production source did not change after the initial attempt. The failed native test exit101, old65 source, 37 original inputs and original failed pipeline remain preserved.

Repair commit 4d37d64d retains that failure. A subsequent preflight rejected late helper-file writes before directory creation/native work; the bounded reuse audit added a housekeeping hash check and moved output validation before mkdir. Commit 9a2f1fe9 refreshes their bindings after all writes stop. That helper invocation has no native exit receipt because no engine/test/build ran. It is preserved in continuation-preflight-failure-02.json; no failed record is rewritten as a clean first attempt.

The successful continuation reuses worker29 once with its original target-dir/argv/log hashes; only the failed owner group is rerun, repeating its seven already-passing tests, followed by the unstarted scope/build/CLI stages. Source/input copies and reuse checks prove only the owner test changed. Both benchmark collection and independent reconciliation pass first attempt, with no completed benchmark-life repeat or source/tool change during data.

One persisted 3600-second clock closes at 681.560s including all failures, repairs and gaps. Collection is 149.209s within 1800s; per-life 180s. Continuation stage exits are all 0; the original owner101 remains explicitly separate.

Main14, colors6/4, inventory2, H0–1,8–13 in every configuration; owned siblings15/7/5/3 unassigned. Housekeeping restoration is audited. Guest sibling tick deltas include small CPU3 housekeeping and CPU15 iowait, and CPU2 softirq activity. Placement is observed guest affinity, not host exclusivity or PMU attribution. No historical hardware conversion, matched KingWCR claim or qualification follows.

All 17 protected image/profile bindings remain unchanged, including strongest full54 candidate 67d011/profile948747. Preserve this exact failed-economics variant and the original instrumented record. No PGO, retune, new graph, broad qualification, adoption, external delivery or automatic rescue. Native work is stopped. Raw evidence: `/home/legolas/rook2-experiments/observer-free-inventory-20261026-01`, successful continuation in `continuation-01`.

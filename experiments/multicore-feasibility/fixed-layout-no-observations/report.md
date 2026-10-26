# Original layout recovers the lean regression; four remains mixed

**Preserve this counterfactual without promotion or another native lane.** Fixed3 is 5.18% below lean3 in the same window, 0.51% below observed3 and 1.31% above retained3. Fixed4 is 1.22% below its matching3 but 0.07% above retained3 at 1.334x whole CPU. The restored representation materially changes the result; a net four-thread gain over the strongest generic reference is not established. Preserve strongest full54 candidate67d/profile948747.

[Timings/ranges](timings.csv), [results](results.json), [closure](closure.json), [plan](plan.md), [source review](source-review.md), [compiled-layout reference](layout-reference.json).

Original 35/08/43, six configurations, one excluded warmup and three frozen rotations per cell: 72 replay lives /840 ordered posts, 54 measured/18 warmup, plus six idle probes. These 54 measured observations cover three cases, not the full54-case suite. All native stages and independent saved-raw reconciliation pass first attempt; one pre-data manual-admission helper token correction is disclosed below.

| Case | Retained3 | Observed3 | Observed4 | Lean3 | Fixed3 | Fixed4 |
|---|---:|---:|---:|---:|---:|---:|
|35|3.862940s|3.859535s|3.802244s|4.019977s|3.878029s|3.784615s|
|08|0.386971s|0.396391s|0.397761s|0.432319s|0.392402s|0.381971s|
|43|3.466202s|3.601045s|3.599530s|3.791662s|3.546833s|3.555085s|
|Median sum|7.716113s|7.856971s|7.799535s|8.243957s|7.817264s|7.721670s|
|Whole CPU median sum|23.149680s|23.572701s|31.197748s|24.733447s|23.453220s|30.886603s|
|Lifetime wall median sum|7.745963s|7.889240s|7.829158s|8.275110s|7.845046s|7.752418s|

| Comparison | Search-wall change | Whole CPU ratio |
|---|---:|---:|
|fixed3 / observed3|-0.505%|0.994931x|
|fixed3 / lean3|-5.176%|0.948239x|
|fixed3 / retained3|+1.311%|1.013112x|
|fixed4 / fixed3|-1.223%|1.316945x|
|fixed4 / retained3|+0.072%|1.334213x|
|fixed4 / observed4|-0.998%|0.990027x|

All three fixed3 ranges are below lean3 ranges. Lean3 again loses to retained3 by 6.84%, so the prior common regression is reobserved rather than borrowed from another window. Fixed3 versus observed3 is mixed: +0.48%/−1.01%/−1.51% on 35/08/43; 35/43 ranges overlap, 08 separates favorably. The aggregate 0.51% reduction is descriptive evidence, not an established universal saving. Fixed3 still loses all three case medians to retained3.

Fixed4/sibling3 changes are −2.41%/−2.66%/+0.23%; 35/08 ranges separate favorably, 43 overlaps. Against retained3, 35/08 improve 2.03%/1.29% with separated ranges, but 43 loses 2.56% with separated ranges. Their absolute changes are −78.325/−5.001/+88.883ms: the aggregate +5.557ms (+0.072%) conceals a real workload mix and does not establish parity. Fixed4 adds 31.69% whole CPU over matching3, 33.42% over retained3. Its 0.998% gain over observed4 is also kept distinct. No workload selector or serial-cost conclusion is implied.

The three-case medians/ranges and every retained sample are in results/CSV; three observations do not predict all 54/12 behavior or provide confidence intervals. Median peak RSS cells span19704–19876KiB. Summing lifetime RSS peaks is not simultaneous memory use. All six 250ms idle probes observe 0 ticks at 100Hz, a 10ms-resolution observation rather than literal zero CPU.

## Source and compiled representation

Setup `1d4884732be82b4d5a9e117b3b3b43e2a5da30ed` freezes 65 source inputs. Only colors_worker.rs changes from lean65; the other 64 inputs, zero-sized installed marker, repaired fixtures and lean callers remain exact. Twelve concrete struct bodies match original inventory65, including Metric.u128, histogram arrays and atomic storage. All fields initialize safely; unused None/zero stores and startup defaults are actual costs. No hot clocks, histogram/counter record methods, production accounting RMWs or late demand/discard locks return. Numerical kernels, admission, thread cap, original semantic N/R/generated demand, supplied-map authority, used-slice transfer, sparse participants and scope-close/SC-wake protocol remain unchanged.

Before timing, manual compiled-layout admission passes all six exact-source/image checks. Arc allocation 15584/alignment16, Cells1488, Packet312, color output56, inventory output1064, Reader24, Mutex<Control>13904 and Control13888 match the old image. Every reference hot B-offset—input/output, request/readers, Control and waiting cluster—matches. The two constructors contain 1172 equal address/RIP/comment/hash-normalized instructions while preserving memory operands/immediates; named producer/consumer uses independently confirm the map. This is manual reconstruction from saved narrow disassembly, not a private DWARF type dump or fresh independent machine-code re-extraction by the raw checker.

The pre-data helper initially expected a request-publication operand based on r12; actual compiled publication uses rcx as the same Arc base. Its assertion stopped before any timing. The failed helper snapshot/record and corrected receipt are preserved under raw/layout-evidence. Actual offsets matched throughout: no source/type discrepancy, source change, alternate layout, benchmark repeat or clock reset. Native tests/build/CLI/collection/audit stages all exit 0.

Representation restoration recovers 427ms from lean3 in this screen, but also changes instruction offsets/code layout and stores. `.text` observed/lean/fixed is 580971/562475/564683B; `.rodata` 325524/323836/323892B. HeapBmod64 and coherence traffic are unknown. No measured cache-miss cause, isolated atomic cost or synchronization nanoseconds follows. Request/done compactness and the excluded Flight/waiting explanation remain as documented.

## Validation, artifacts and boundaries

40 existing affected controls pass (worker29, actual-owner8, scopes3); historical unchanged numerical/cache/generation evidence is retained. Tests exercise the observation-free path without cfg(test) statistics. 15 CLI/cap checks and two original08 requested4→configured1/2 fallback searches pass. Actual pre-input task names/counts/masks and all 72 original strict score/move/posts/work streams, joined exits and raw identities pass independent saved-raw audit. No new helper-work census or broad mandatory/gameplay qualification is claimed.

One new generic image serves both fixed modes: SHA256 `81d33161df3c5147f56d0e878f11d5d486c9360d1255c954def101d2294e61b2`, 7,795,472B. Controls retain exact7ac mode3,36c mode3/4 and6da mode3 bytes. Rust 1.85.1/LLVM19.1.7, generic x86-64 GNU,O3/ThinLTO/oneCGU/debug1/panic-abort, no PGO. All original build recipes/source/tool identities are admitted and 18 protected image/profile bindings remain unchanged.

One persisted 3600-second clock closes at 819.882s, including manual inspection/gaps; collection 223.426s within 1800s, per-life 180s. No source/tool changes during data, completed-life repeats, retrain or second variant.

Main14, colors6/4, inventory2 when configured, H0–1,8–13 consistently; owned siblings15/7/5/3 unassigned. Housekeeping restoration and guest tick deltas are saved; small sibling/kernel/IRQ activity remains, including CPU2 softirq. Guest affinity is not exclusive host isolation. Search wall uses original go-write→move callback endpoints; wait4 CPU/lifetime/RSS includes all threads, startup/setup, joined shutdown/reporting and a small Python pre-exec prefix. Historical and disabled report work outside search also differs. No PMU, hardware conversion or matched KingWCR performance claim.

Close this one counterfactual and preserve the exact source/image and all prior records. The old representation is the better observed form of this graph, but fixed4 offers no aggregate gain over retained3 here. Keep 67d/profile948747 as the primary full54 option. No automatic padding/layout variant, tuning, PGO, qualification, adoption or external action follows. Native work is stopped. Raw: `/home/legolas/rook2-experiments/fixed-layout-no-observations-20261026-01`.

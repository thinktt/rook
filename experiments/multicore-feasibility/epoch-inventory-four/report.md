# Conditional inventory4: useful generation, no net win over retained3

**Park this fixed variant; preserve the positive epoch3 image/profile/source.** Search-wall median sum 7.777120s is 0.81% above preserved epoch3 at 1.344x whole CPU. It is 0.52% below the slower same-image3 control, at 1.326x CPU. Case 35 gains, 08/43 regress against the preserved image. All selected controls and replay/audit checks pass first attempt; this is an economics negative, with no post-freeze source/tool/native repair or completed-life repeat.

[Timings/ranges](timings.csv), [concise results](results.json), [closure](closure.json), [plan](plan.md), [domain proof](generation-domain.md), [bounded source challenge](source-review.md). No retune, PGO, qualification/adoption or follow-on execution.

## Complete generic result

Original35/08/43; one excluded warmup and three fixed rotated observations per configuration: 60 successful replay lives, 45 measured/15 warmups, 700 ordered posts, plus five separate 250ms idle probes. Median sums describe these selected cases and are not complete54 totals.

| Case | Preserved3 | New inline1 | New current2 | New epoch3 | Inventory4 | Four vs preserved3 | Four vs sibling3 |
|---|---:|---:|---:|---:|---:|---:|---:|
|35|3.840123s|4.422963s|4.026317s|3.860003s|3.786943s|-1.38%|-1.89%|
|08|0.387354s|0.388983s|0.381331s|0.399233s|0.398003s|+2.75%|-0.31%|
|43|3.487301s|3.447417s|3.570848s|3.558301s|3.592174s|+3.01%|+0.95%|
|Median sum|7.714777s|8.259364s|7.978495s|7.817537s|7.777120s|+0.81%|−0.52%|
|Whole CPU median sum|23.144303s|8.265688s|15.950952s|23.453537s|31.108190s|1.344x|1.326x|
|Lifetime wall median sum|7.743783s|8.285349s|8.008466s|7.847659s|7.807930s|—|—|

In 35 every inventory4 sample (3.784181–3.807598s) is below every preserved3 sample (3.809864–3.860089s), with only a 2.266ms gap between ranges. In 08 and 43 all inventory4 samples exceed all preserved3 samples:0.397459–0.398581 vs0.386646–0.390090s, and3.581243–3.604462 vs3.446811–3.494352s. Against same-image3, 35 improves with separated ranges, 08 overlaps and 43 loses with separated ranges. Three observations do not define confidence intervals or predict all54/12 behavior.

New sibling3 itself costs 1.33% aggregate over preserved3 (+0.52%/3.07%/2.04% by case). Therefore a small gain against sibling3 does not recover the complete integration cost. Code/frame/layout/routing and larger state remain part of the comparison; do not attribute a specific case regression to one compiler or synchronization cause.

Four is 2.52% below current2 and 5.84% below inline, at 1.950x and 3.764x whole CPU respectively. These do not supersede the stronger preserved3 baseline. Median lifetime peak RSS spans 19304–19776KiB across these case/configuration cells; each detailed range is retained in results. All five 250ms idle probes show 0 ticks at 100Hz, a 10ms-resolution observation rather than literally zero CPU.

## What was actually prepared and used

Counts below sum the three retained inventory4 lives per case; each individual life has identical demand counts.

| Case | Requested/generated/installed | Color-only FULL (no inventory request) | Original demand | Discarded | Parent demand after later epochs | Parent discard after later epochs |
|---|---:|---:|---:|---:|---:|---:|
|35|2914443|1809063|2224608|689835|64155|59379|
|08|667440|418065|656808|10632|0|0|
|43|3199020|4370388|2462979|736041|30111|239271|

Every requested job completes, generates and installs its used slice; domain-unavailable, failed, unsettled-discarded and pending-receipt counts are 0. Requested=installed=demanded+discarded closes, with original demand 76.33%/98.41%/76.99% on 35/08/43, matching the earlier census. Color-only calls receive no fabricated inventory acknowledgment. Later-epoch counters directly observe activation-local parent receipts surviving descendant FULL work;08 has no null interposition. Installed results on early exits are still physical waste, without generated/N/R/ordering charges.

The source retains the two positive side consumers and the original coordinator pawn/cache/rounding path. Confirmed ordinary FULL alone requests the sparse third reader after Influence demand. Colors join into Joined; original numerical FULL completes; inventory settles and copies only its used slice+length into row[p] before bounds/null handling. The local receipt selects original demand versus discard after arbitrary descendant epochs; it never requires pool-latest equality. No per-call Arc/key/null Box or whole 512-slot copy. Public/root/Q/FRESH/supplied-map authority and original logical consumers remain unchanged.

Before the single native source freeze, source review removed the redundant opposite-king in_check: the unchanged pure bounded generator creates no child, excludes king victims and is total on coherent ancestry plus king-indexing checks. An opposite-king-attacked position is now an exact native-list control; forced unavailable is explicitly test-only. Unused preliminary preparatory bindings are preserved outside Git under `/home/legolas/rook2-experiments/epoch-inventory-four-predata-guard-review-20261026-01`; no native execution preceded that decision and it was not a timed variant.

## Paired observations and their cost limits

Stride 512 follows colors epochs; these are weighted pooled means over retained sampled inventory jobs, not per-case medians.

| Sampled mean ns / fraction |35|08|43|
|---|---:|---:|---:|
|Guard/generator interval|343.44|228.33|256.48|
|Producer end after publication|511.97|415.38|424.99|
|Numerical FULL complete|877.55|679.09|757.06|
|FULL complete→inventory acquired|40.82|43.05|39.65|
|Acquired→used row installed|40.13|37.36|43.27|
|Demand after installation|236.26|116.31|159.75|
|Discard after installation|668.40|118.06|1093.28|
|Producer end at/before FULL complete|5736/5748 (99.79%)|1250/1254 (99.68%)|6299/6312 (99.79%)|

Producer end precedes the per-job completed/generated/generatedMoves atomic RMWs, output done Release and completion latch; it is not owner-visible readiness. The guard/generator interval excludes those later costs. FULL→acquired includes predicate/ownership checks, clocks and any wait; acquired→installed includes copy and clocks. Neither isolates pure waiting or memcpy. Each late demand/discard timestamp precedes its extra owner Control acquisition/counter update: the reported interval excludes that final accounting work, while complete search timing pays it. These counters/locks are observer costs as well as actual timed costs, not an inherent lower bound on lean delivery.

The producer/FULL differences are paired within each sampled request; final demand/discard follows its own receipt. Saved fixed histograms do not retain individual request rows or stratify producer/FULL differences by eventual demand versus discard. Consequently the readiness fractions above describe all settled jobs; they are not conditional useful-work fractions or latency predictions. After-install demand/discard intervals can include null descendants, which are not extra overlap because the shared lease was already released. Periodic aliasing, timestamps and observer perturbation remain unestimated.

High readiness is thus not the missing criterion: all consumed lists are installed, but guard/generation, third input-reader cache traffic, completion/installation/late-accounting locks, discarded generation and an actively spinning fourth core remain paid. The study does not isolate their individual critical-path shares or prove the leanest possible delivery would lose. No observer-removal rescue run was performed.

## Validation, exact identity and scope

- Source/setup checkpoint `23ff9d69ca69254376df947ebac824be3d2acf92`: 65 files, five changed existing paths and one new test module against frozen epoch64. Canonical engine source/main/release are untouched. The committed zero-context source patch reproduces this isolated delta from its bound base.
- 50 focused passes first attempt: 21 affected existing worker controls plus 10 new worker controls, 8 existing composed-Evaluator controls, 3 existing scope controls and 8 new actual-owner/cap controls. Earlier unchanged mathematical evidence is retained; no broad suite. New controls cover sparse epochs, delayed third-reader/Joined/cold-wakeup/reverse-edge/close/failure/overflow, exact special/checked lists, unavailable fallback, public/FRESH observer parking, actual null continue/cutoff with descendant FULLs, stop cleanup and truthful 1/2/3/4 configuration.
- 15 exact-image CLI checks and two actual original08 fallback searches pass, request 4→configured 1/2 on restricted permission. Four-thread task placement and source/image/raw bindings pass independent audit in the frozen benchmark. Original strict score/move/posts/work replay and complete joined exits pass all 60 lives. Exact N/R/state comparisons belong to focused controls; this is not broader behavioral qualification.
- Candidate `36c40aee75f8a93c773bc450f440ac14a2a94d8faa1057549805659ea4092e5f`, 7,882,384B; preserved generic3 `7ac72fc63cf4086944b3abfd71f45eb1f0347796f2520bb97aa87fc8de3fb65c`, 7,798,776B. New modes1/2/3/4 use one identical image.
- ELF `.text` 562,459→580,971B and `.rodata` 324,300→325,524B have distinct hashes in results. Rust 1.85.1/LLVM 19.1.7, generic x86-64 GNU,O3/ThinLTO/oneCGU/debug1/panic-abort, no PGO, identical numerical kernels and matched compiler/recipe. Source/layout/observer drift is not an isolated transport or kernel measurement.
- Preserved own-PGO 67d011/profile948747 and all 12 protected artifacts/profile bindings remain unchanged. Raw/build/source/wire/housekeeping receipts: `/home/legolas/rook2-experiments/epoch-inventory-four-20261026-01`.

All eight stage exits are 0. The persisted clock reaches the final stage end at 294.297s; its final deadline check passes within 3600s. Collection takes 182.086s within 1800s, with 180s per life. Source/tool/input bytes stay frozen throughout; no native/setup failure, completed-life repeat, clock reset or post-data source change.

Main 14, colors 6/4, inventory 2; all five configurations use H0–1,8–13. Before first protocol input the supervisor checks actual thread count/names/masks; wait4 includes all threads, startup/setup/joined shutdown/reporting and a small pre-exec Python prefix. Search wall uses original go-write→move callback endpoints. Selected housekeeping is restored; guest ticks on unassigned siblings and additional CPU 2 kernel/softirq activity are recorded, without host exclusivity or PMU attribution. This generic screen cannot establish matched KingWCR, full mandatory/regular12/full3288 acceptance, production adoption or a portable speed conversion.

## Strongest next distinct direction (recommendation only)

| Direction | Evidence now | Remaining price / judgment |
|---|---|---|
| Whole-FULL one-helper epoch transport | Positive epoch3 transport result; existing mode2 still takes/copies under Slots and locks publication/output. All actual FULL calls are demanded. | Strongest small next discriminator: keep the whole numerical kernel, test direct ownership with one reader and compare retained2/3. Single-reader contention differs; publication/cache/lifecycle costs remain and no win is forecast. |
| Whole-FULL+inventory3 | Distinct CPU/balance graph, existing scratch settlement proof and real demand. | Larger FULL window is not the main evidence gap: four already has nearly all producer ends before FULL. Delivery/discard/observer costs remain, while giving up color-parallel arithmetic; not the strongest next step. |
| Fresh-map/side-FULL fusion | Adds genuinely new overlap in currently serial Influence construction. | Peer-map barrier and delayed owner pawn start remain unpriced; supplied maps require fallback. More ownership change than transport generalization; credible reserve, no prediction from these inventories. |
| Observer-free conditional delivery | Production RMWs and owner accounting lock are concrete avoidable observation work. | No isolated critical-path cost establishes that removing them reverses the net result. A lean consumer is a distinct unpriced hypothesis, not a lower-bound impossibility or an authorized rescue. |

Preserve this mixed/negative record and the positive epoch3 candidate. No source cleanup, removal, further prototype, measurement, PGO or qualification is selected by this closure.

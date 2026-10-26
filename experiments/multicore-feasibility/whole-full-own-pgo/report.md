# Whole-FULL own-PGO: a small two-thread gain, retained3 still fastest

**Keep prior67d as the primary three-thread candidate; preserve a8dd as a measured two-thread research option.** New2 totals 64.004516s versus 64.208272s prior2: 0.3173% lower, with 0.99687x whole CPU. The generic 2.62% gain does not reproduce at that magnitude in this broader own-PGO comparison. New3 is 0.2065% above retained3; new1 is 0.7448% above accepted serial. These single observations do not establish repeatability or justify automatic replacement.

[All54 rows](full54.csv), [concise results](results.json), [closure](closure.json), [frozen plan](plan.md). All stages in this lane pass first attempt; no source change, repair, retraining, profile weighting change, completed-life repeat or clock reset. The earlier generic idle-wrapper failure is retained as reused evidence; it is not rewritten as a clean first pass.

## Complete matched full54

Six configurations, one fresh observation per original case,324 comparison lives /3744 ordered posts, no warmups. Original case order and configuration rotations were frozen before data, balanced nine occurrences per start position. These are direct sums, not sums of medians or per-case significance estimates.

| Configuration | Search wall sum | Native CPU sum | Lifetime wall sum | Outside-search wall sum | Mean / max peak RSS KiB |
|---|---:|---:|---:|---:|---:|
|Accepted serial5cf|68.293755s|68.379441s|68.718770s|0.425016s|22186.6 / 68776|
|Prior67d mode2|64.208272s|128.458887s|64.700128s|0.491856s|22359.0 / 68748|
|Prior67d mode3|60.721374s|182.181755s|61.218856s|0.497482s|22370.3 / 68756|
|New inline1|68.802407s|68.888725s|69.238265s|0.435858s|22221.4 / 68808|
|New whole-epoch2|64.004516s|128.056830s|64.502942s|0.498425s|22373.0 / 68780|
|New color-epoch3|60.846776s|182.552547s|61.349414s|0.502637s|22352.7 / 68776|

| Comparison | Search-wall change | Whole CPU ratio | Faster / slower cases |
|---|---:|---:|---:|
|wholeepoch2 / prior2|-0.3173%|0.996870x|41 / 13|
|wholeepoch2 / prior3|+5.4069%|0.702907x|10 / 44|
|wholeepoch2 / colorepoch3|+5.1897%|0.701479x|12 / 42|
|colorepoch3 / prior3|+0.2065%|1.002035x|22 / 32|
|wholeepoch2 / serial1|-6.2806%|1.872739x|49 / 5|
|colorepoch3 / serial1|-10.9043%|2.669699x|45 / 9|
|inline1 / serial1|+0.7448%|1.007448x|6 / 48|

New2 improves 41/54 cases versus prior2, but saves only 203.755ms in the complete sum. Largest absolute saving is 43 (28.194ms); largest loss is 04 (12.384ms). Relative extrema are 18 (−3.016%) and 01 (+1.389%). Directional breadth is useful evidence, not a variance estimate or isolation of the transport mechanism.

Retained3 stays 3.283143s ahead of new2 overall; new2 trades 5.41% more elapsed time for 29.71% less CPU, and beats prior3 in 10/54 cases. Prior2 already offers a similar lower-CPU choice. New3 is 125.402ms above prior3, improving 22 cases/losing 32; largest absolute loss 44 adds 24.290ms. New1 loses 48/54 cases to accepted serial, adding 508.652ms overall. The table includes every per-case row; there is no selected workload-based thread policy.

New2 is 6.28% below accepted serial with 1.873x CPU; new3 is 10.90% below serial with 2.670x CPU. Those are gains over our preserved image, not matched KingWCR/KingRE performance. New2 versus sibling3 and accepted serial, and new3/one-thread versus their required controls, remain distinct comparisons.

All six 250ms idle probes observe 0 CPU ticks at 100Hz (10ms resolution), not literally zero CPU. Peak RSS ranges and per-life means are retained in results; summed lifetime peaks do not describe simultaneous memory use. Active helpers may still spin while the coordinator is blocked in Host callbacks.

## Exact source, training and build

- Exact unchanged 64-file source from generic setup `99a42049` /closure `1c68dd32d5f323e09faf784ff4fc50a5b5fca47d`; this lane setup `880d883527b7e3a65ab56df6440de8e34214bbf4`. Only evaluator_worker.rs differs from prior67d source; 63 other files and the ActivityShelter/numerical compute block are unchanged.
- Fresh joint1/2/3 training: 54 original cases per mode, 162 strict native lives /1872 ordered posts /162 unique PID-bound raw profiles. Equal inclusion, one canonical LLVM19 merge and one separately recorded actual independent remerge to a distinct file; bytes match. Training time is not performance evidence.
- Own profile `1e954c1692f221c470fb8959d000674604a25172b61dd8f79790d1f5c134bcfe`, 124,592B. New use image `a8dd1476e05934d166e8526498e36a658bfcdc93cf3240ed65b987aaf1a3f4e6`, 7,758,688B; new1/2/3 use these same bytes.
- Prior2/3 both use `67d011083f37f42904423247f5cf0ece2a1e36f0a4129da94fe7561d1f922ea7` and its preserved joint profile `9487473e31dfc30ae515cdce18e3f15ec3a653bfd1c5bd665a8f76d235e30311`. Serial is exact `5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a`; no thread flag. 8f stays protected, without becoming a seventh configuration.
- Same Rust 1.85.1/LLVM19.1.7, generic x86_64-unknown-linux-gnu/target-cpu=x86-64,O3/ThinLTO/oneCGU/debug1/panic-abort. One use-only ExtTSP-profiled build, same established recipe; no PGO sweep, source cleanup or observer removal.

Prior/new `.text` 591,979→591,643B and `.rodata` 324,220→324,596B have distinct hashes in results. Profiles are different fresh own-source products, so this comparison includes profile/code-layout effects; it is not a lock-only saving. Even the unchanged color path shifts slightly. Source changes against accepted serial are broader (17 existing files changed/12 added), and prior67d mode1 is not a cell in this six-config schedule: the new1/serial difference cannot alone isolate the helper change’s serial cost.

The three-case generic trial and this full54 have different populations, profiles, repetition counts and windows. Their 2.62% and 0.32% gains cannot establish how much PGO alone changed the mechanism. No new per-call instrumentation localizes this difference; new2 intentionally has no timing/readiness observer. Color mode3 keeps its original 512th-epoch observations, with exact matching FULL dispatch counts in all 54 prior/new case pairs.

## Fidelity, provenance and limits

Reuse 29 generic controls and their explicit retained numerical/color partition; no unit matrix repeated. Fresh use-image 13 CLI checks and two original08 request3→effective1/2 controls pass. Actual native thread counts/names/masks before first input, original strict replay, score/move/post/work streams, joined exits, source/build/profile/raw identities and all 324 comparison records pass independent saved-record audit. Finite focused state/N/R evidence is not broad mandatory/gameplay qualification.

The generic source proof remains applicable: private initialized cells, one coordinator/one reader, checked epochs and matched request/done ownership; every input reference ends before done and output reads before the next request’s reverse edge. Final close drains actual park/exit; the unconditional SC latch/Sleep handshake and 4096 spins are unchanged. Public/FRESH/standalone scope close remains at its original pre-composition point; production panic-abort is not unwind recovery. No per-call allocation, numerical kernel, caller state/cache/learning/poll owner or runtime selector changed.

The prior generic collector failed on a lazy idle import before input, preserving a missing native-exit receipt and cancelled supervisor. This lane explicitly exports the frozen check_task_masks helper before all runs, reuses the completed60+5 audit and keeps original failure bytes. It does not rerun or rewrite them. No new failure occurs here.

One persisted clock closes at 1129.100s within 3600s. Training 430.026s, comparison 610.622s and independent comparison audit 5.779s stay within their selected bounds; per-life 180s. No clock reset or hidden second profile/build/measurement stream.

Main 14, helper 6/color second 4; H0–3,8–13 consistently, siblings 15/7/5 unassigned. Housekeeping is restored and guest tick deltas recorded. Guest placement does not prove host exclusivity. Search wall uses original go-write→move callback endpoints; direct wait4 CPU/lifetime/RSS includes all threads, startup/setup, joined shutdown/reporting and a small pre-exec Python prefix. No PMU, host conversion or historical-reference-window qualification follows.

All 15 protected images/profile bindings, including 67d/948747, 8f/5cf, 7ac/a30 and parked inventory4, remain unchanged. Raw source/build/profile/wire/audit evidence is outside Git at `/home/legolas/rook2-experiments/whole-full-own-pgo-20261026-01`.

Recommend keeping both research artifacts and prior67d as the primary three-thread candidate. The new two-thread path has a small favorable descriptive result, while its same-image serial and three-thread observations do not establish an overall replacement advantage. Do not retune, retrain, repeat, adopt or qualify automatically; those are separate lead decisions. Native work is stopped.

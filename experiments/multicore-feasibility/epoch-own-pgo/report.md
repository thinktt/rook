# Exact epoch own-PGO: descriptive full54

**Retain the opt-in three-thread result; recommend bounded exact-image behavioral qualification next.** The complete search-wall sum is 60.763786s, 5.19% below preserved practical2 and5.28% below same-image2. It is 10.61% below accepted serial, at 1.422x practical2 /2.679x serial whole CPU. No further lane, adoption or external qualification is selected by this record.

[All54 rows](full54.csv), [concise machine results](results.json), [closure](closure.json), [frozen plan](plan.md). Every stage passes on its first attempt; no failed native life, repair, repeat, source change or parameter/profile sweep.

## Matched complete result

Each original case runs once per configuration: 270 fresh comparison lives, 3120 ordered posts, no warmups. The released case order rotates configuration order by case index modulo5. These are direct sums of single observations, **not per-case medians or significance estimates**.

| Configuration | Search wall sum | Native CPU sum | Lifetime wall sum | Outside-search wall sum | Mean / max peak RSS KiB |
|---|---:|---:|---:|---:|---:|
|Accepted serial5cf|67.973988s|68.059510s|68.402857s|0.428870s|22205.0 / 68620|
|Practical2 8f|64.092876s|128.229345s|64.581562s|0.488687s|22398.8 / 68948|
|New inline1|68.076222s|68.161880s|68.506248s|0.430026s|22251.2 / 68892|
|New current2|64.147690s|128.339177s|64.648232s|0.500542s|22391.9 / 68904|
|New epoch3|60.763786s|182.297940s|61.265485s|0.501699s|22379.3 / 68872|

| Comparison | Search wall change | Whole CPU ratio | Cases faster / slower / tied |
|---|---:|---:|---:|
|epoch3 / practical2|-5.1942%|1.421655x|48 / 6 / 0|
|epoch3 / current2|-5.2752%|1.420439x|47 / 7 / 0|
|epoch3 / serial1|-10.6073%|2.678508x|45 / 9 / 0|
|inline1 / serial1|+0.1504%|1.001504x|17 / 37 / 0|
|current2 / practical2|+0.0855%|1.000857x|24 / 30 / 0|
|epoch3 / inline1|-10.7415%|2.674485x|47 / 7 / 0|
|inline1 / practical2|+6.2150%|0.531562x|6 / 48 / 0|

New inline1 totals 68.076222s, only 0.1504% above accepted serial in this observation; its 17 wins/37 losses are listed in the CSV. New2 totals 64.147690s, 0.0855% above 8f with 24 wins/30 losses. These small differences remain unresolved noise/layout/profile effects. No claim that the default serial path is faster.

Epoch3 gains in 48/54 cases versus practical2 and 47/54 versus new2, so the result extends beyond the three-case generic screen. Against practical2, profile04 gives the largest absolute saving 262.050ms; 41 the largest relative saving 10.45%. Six losses are 02/08/25/39/48/51; 51 is the largest absolute loss 13.929ms, 02 the largest relative loss 1.19%. Against new2, the largest loss is 51 (+17.993ms); 02 has the largest relative loss 2.16%. Against serial, epoch3 improves 45 cases and loses 9; 35 saves 565.722ms, while 43 loses 130.285ms (+4.56%). The 43 regression remains material; it is not a startup-only effect. These per-case observations have no measured repeatability interval.

Five separate 250ms idle probes each show 0 process CPU ticks at 100Hz (10ms resolution), not literally zero CPU. Lifetime peak-RSS ranges are retained in results; summing peaks is a catalog statistic, not simultaneous memory consumption.

## Exact source, profile and artifact

- Frozen source/tool setup: `8f252731012f1efb6bc752762c01d4d4bf488644`; unchanged 64-file source from generic closure `5b36ff590e7aa0f15b7611c81d9a4aa945638561`.
- Own joint1/2/3 training: 54 original cases per mode, 162 native lives /1872 posts /162 PID-bound raw profiles. Equal inclusion, one canonical LLVM19 merge plus one separately recorded independent remerge; both files are byte-identical. Training time is not a performance observation.
- Use image: `67d011083f37f42904423247f5cf0ece2a1e36f0a4129da94fe7561d1f922ea7`, 7,756,888B. Modes1/2/3 use these same bytes.
- Canonical profile: `9487473e31dfc30ae515cdce18e3f15ec3a653bfd1c5bd665a8f76d235e30311`, 124,864B.
- Rust 1.85.1/LLVM 19.1.7; generic x86_64-unknown-linux-gnu / target-cpu=x86-64 /O3/ThinLTO/oneCGU/debug1/panic-abort. The single use build enables ExtTSP only with profile (`-enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false`); the missing-function warning option remains enabled.
- Raw evidence: `/home/legolas/rook2-experiments/epoch-own-pgo-20261026-01`. Exact paths/hashes/ELF sections, old profiles, source deltas, receipts and audit bindings are in results/closure.

New `.text` is 591,979B versus 562,667B practical2 and 540,811B serial; `.rodata` 324,220B versus 321,980B /320,472B. New source changes 8 existing files/adds 3 against practical2, and changes 17/adds 12 against serial; exact paths are recorded. Generic epoch source changes zero files in this continuation. Old images keep their distinct own-source profiles; new modes share a joint profile. Consequently matched speed differences include source/code layout/profile effects. The earlier isolated generic transport evidence supports net transport benefit, not a mutex-only saving or a portable CPU conversion.

## Fidelity, lifecycle and measurement boundaries

Fresh exact-use admission passes 13 CLI checks and two original08 controls: request 3 with one permitted CPU configures 1, and with two configures 2, with actual native task masks inspected. Reuse 32 generic protocol/lifetime/Evaluator/scope controls on unchanged source, with the explicit earlier 38-baseline partition. No new broad suite. Original comparison replay, score/move/posts/work and complete joined exits pass independent saved-record audit; source/image/profile and raw/PID bindings match.

Default 1, capped requested budgets and permitted-affinity fallback stay unchanged. Active search scopes own worker activation/parking; all packet references retire before matching done, outputs retire before overwrite, and cold waits use the reviewed single-waiter predicate/latch protocol. Production panic=abort does not provide unwind recovery; active helpers may spin while Host callbacks block. This study does not newly establish live-command/partial-stop fidelity or broad mandatory/gameplay acceptance for the exact PGO image.

Coordinator 14, helpers 6/4, selected housekeeping 0–3,8–13; actual pre-input native thread placement is checked. Unassigned siblings 15/7/5 still show guest kernel/idle/I/O ticks. Housekeeping restoration is recorded; guest placement does not prove host exclusivity. Original go-write→move callback wall endpoints exclude startup/setup; wait4 CPU/lifetime/RSS include all threads, startup/setup, joined shutdown, reporting and a small pre-exec Python prefix. Neither endpoint is a direct Bee or KingWCR qualification comparison.

One persisted pipeline clock closes at 1021.212s within 3600s, including gaps, builds, merge/remerge and audits. Collection stage 488.717s remains within 1800s. All seven stage exits are 0; no new native lane follows closure.

## Sparse readiness and interpretation

At stride 512 the 54 epoch lives dispatch 37,094,875 FULL packets and complete 72,426 sampled pairs, with no failed/discarded/missing-owner samples. Sides finish after owner in 66,345 samples (91.60%). Aggregate sample means: owner-ready 306.87ns, white-ready 446.78ns, black-ready 440.63ns, complete-entry→outputs-acquired 273.18ns. These are weighted sparse sample means, not per-case means or subtractable causal costs.

Publication follows coordinator snapshot/metadata preparation; side-ready clocks precede output/done release. The legacy copy interval covered lock/copy, whereas epoch measures direct-borrow/access setup; direct cache reads belong inside kernel time. Histograms/merge after observed join remain paid by whole-search timing. Fixed periodic sampling, observer perturbation, cache locality and ELF/PGO drift prevent a lock-only or pure arithmetic attribution. No PMU claim.

The full result supports retaining this option and qualifying its exact bytes before adoption. It does not establish full mandatory/regular12/full3288 acceptance, matched KingWCR performance, release promotion or scalability beyond three threads. Further architectural expansion and qualification are separately selected lead decisions.

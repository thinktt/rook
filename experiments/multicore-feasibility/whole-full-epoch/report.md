# Whole-FULL epoch: a faster two-thread option

**Retain this transport for unchanged-source own-PGO/full54.** New2 search-wall
median sum is 7.846632s versus 8.057632s preserved2: 2.62% lower, with 0.97382x whole
CPU. Retained3 remains 2.31% faster overall; new2 uses 0.68213x its CPU. This improves
the selectable two-thread option without establishing that color parallelism is
unnecessary. No tuning, adoption or qualification follows from this generic result.

[Timings/ranges](timings.csv), [concise results](results.json), [closure](closure.json),
[plan](plan.md), [ownership proof](ownership-proof.md),
[bounded source review](finalsource-review.md). All 60 benchmark lives are preserved
unchanged. One idle-wrapper import failure occurred before input; only the five
unstarted idle probes were subsequently run. The composed saved-raw audit passes.

## Complete matched screen

Original35/08/43; one excluded warmup and three fixed rotations per configuration:
60 replay lives (45 measured/15 warmups), 700 ordered posts and five separate idle
probes. Table values are per-case medians and sums of those medians, not full54
totals or confidence intervals.

| Case | Preserved2 | Preserved3 | New inline1 | New whole2 | New color3 | New2 vs old2 |
|---|---:|---:|---:|---:|---:|---:|
|35|4.081757s|3.836690s|4.450459s|4.004381s|3.841881s|-1.90%|
|08|0.381729s|0.387665s|0.391987s|0.372203s|0.390715s|-2.50%|
|43|3.594146s|3.444947s|3.473514s|3.470048s|3.511111s|-3.45%|
|Median sum|8.057632s|7.669302s|8.315960s|7.846632s|7.743707s|−2.62%|
|Whole CPU median sum|16.116567s|23.008390s|8.320448s|15.694640s|23.230228s|0.97382x|
|Lifetime wall median sum|8.085583s|7.696240s|8.341088s|7.874103s|7.770155s|—|

Every new2 observation beats every old2 observation in each case: 35 ranges
3.991842–4.048361 vs 4.077765–4.087085s; 08 0.370078–0.374618 vs 0.381020–0.384913s;
43 3.467714–3.478334 vs 3.548015–3.683118s. These separated finite ranges support
the local gain; three observations do not establish repeatability elsewhere.

Against preserved3, new2 loses 4.37% in35 with separated ranges, wins 3.99% in08
with separated ranges, and loses 0.73% by median in43 with overlapping ranges.
Against new color3, new2 is slower 4.23% in35 but faster 4.74%/1.17% in08/43, with
separated ranges in all three. Aggregate ratios follow:

| New2 denominator | Search-wall change | Whole CPU ratio |
|---|---:|---:|
|preserved2|-2.6186%|0.973820x|
|preserved3|+2.3122%|0.682127x|
|colorepoch3|+1.3291%|0.675613x|
|inline1|-5.6437%|1.886273x|

New color3 is 0.97% above preserved3 overall (+0.14%/0.79%/1.92% by case), despite
identical color/caller source. This is a useful drift control, not a diagnosis of
one layout cause. New inline1 is measured; this schedule has no preserved inline1
cell, so it cannot isolate old-to-new serial cost. Both are reasons to measure
accepted serial and two/three-thread options again under the own-PGO recipe.

All five 250ms idle probes record 0 CPU ticks at 100Hz (10ms resolution), rather
than literally zero CPU. Median lifetime peak RSS ranges 19336–19712KiB across
the 15 case/configuration cells; complete ranges are in results. Active helper
spinning during search/blocked callbacks remains a cost of both transports.

## Source and mechanism

Only `src/evaluator_worker.rs` differs in the 64-file corpus; 63 other files,
`ActivityShelter` declaration and the complete numerical `compute` block remain
byte-identical. Shared numerical-block SHA256 is
`c1e83ee2b14590a228b9f8070e6ac72df223676bfb053729b91a010798ad6d57`.
The ten crate-visible signatures and original pre-composition standalone/public
scope-close point stay unchanged. Inline1, color3, supplied-map authority,
FRESH, root/cache/retained/R/poll ownership and all kernel rounding stay in place.
Inventory65 code is absent.

Initialized private input/output cells replace the old Slots transport. Control
serializes one coordinator's publication, output consumption and final close;
request Release/Acquire publishes the actual complete input. The helper directly
calls the unchanged whole Activity/Shelter kernel and ends every Packet reference
before output/done release. Matching done acquisition permits scalar output
consumption; those reads end before the next request supplies the reverse edge.
Final close owns Discarding until actual helper park/exit, not a timeout. The
single-waiter Sleep/SC-RMW registration handshake and 4096-spin policy remain.
All remaining Control/RMW/cache traffic is paid; no new per-call observer, clock,
readiness/copy counter or heap allocation was added. Source/code-layout/cache
effects accompany the net transport change; four removed Slots acquisitions do
not constitute an isolated mutex-time measurement.

29 focused controls pass: 16 one-helper controls (eight prior active controls
adapted plus eight epoch controls),eight actual whole-Evaluator controls,three
root/scope controls and two affected color/config transitions. Of the previous 32
generic color controls, 30 unchanged controls are retained and two rerun. The old
11-second delay test remains separately ignored/unselected. New controls cover
input/output retirement, final-close races, cold registration/spurious/terminal
wake, failed startup, unpublished failure and nonwrapping epoch exhaustion.
13 changed-image CLI checks and two original08 request3→effective1/2 searches also
pass. All selected controls/build/admission pass first attempt. Test-build unwind
coverage does not imply production panic-abort recovery or exhaustive concurrency
verification.

## Preserved failure and bounded completion

After all 60 benchmark lives, the reused idle ready_record tried a lazy import of
`check_task_masks`, absent from the new common exports. First idle process was
cancelled before any input: stdin/stdout/stderr are empty and no input gate exists.
Supervisor exit−9 is recorded; that failed startup has **no native wait4 exit
receipt**. Its ready IDs are no longer live. This is a disclosed setup failure,
not proof of a normal native exit or an engine semantic failure.

Original failed pipeline/collection/result bytes remain untouched. The small
`finish_idle.py` continuation exports the exact frozen helper in memory and runs
only five previously unstarted idle probes in a separate directory. It changes
no engine, original source/tool input, binary, schedule or successful benchmark
life. `repair_reconcile.py` reparses all 60 original raw streams plus five new idle
streams, actual placement, native receipts, source/hash/code identities,
housekeeping and both original clocks. Its supervised saved-raw audit exits 0.
The collection has 65 successful native processes plus the one failed pre-input process;
no completed request is repeated and no clock is reset. The original reconciler
was not started after its collector failed; the bounded composed audit replaces
that terminal check without converting the failed stage to success.

Pipeline through repair audit is 1196.452s within3600s; original collection start through repair audit is 1071.839s within1800s. Repair audit itself is 1.267s. All successful native lifetimes remain within 180s.

## Identity, boundaries and recommendation

- Source/setup: `99a42049d9da541aec6aa7ebd39f80c92fb7f5df`.
- New image: `a30daa460780bd238c97b3c440b026975eceef13cb0cc498c4851df14ccc3e45`, 7,801,200B. New1/2/3 share these exact bytes.
- Preserved modes2/3: `7ac72fc63cf4086944b3abfd71f45eb1f0347796f2520bb97aa87fc8de3fb65c`, 7,798,776B.
- `.text` 562,459→563,355B; `.rodata` 324,300→324,612B. Section hashes are retained in results.
- Same Rust 1.85.1/LLVM 19.1.7, x86_64-unknown-linux-gnu/target-cpu=x86-64,O3/ThinLTO/oneCGU/debug1/panic-abort, no PGO.
- Raw/build/original failure: `/home/legolas/rook2-experiments/whole-full-epoch-20261026-01`; composed audit and idle completion: `idle-completion-01/` beneath it.

Main 14, helper 6 and color second 4; consistent H0–3,8–13, siblings 15/7/5 unassigned.
Actual native threads are checked before first protocol input. Original go-write→
move callback defines search wall; direct wait4 CPU/RSS/lifetime includes all
threads, startup/setup, joined shutdown/reporting and a small pre-exec Python
prefix. Both housekeeping segments are restored; guest ticks are recorded, without
host-exclusivity or PMU attribution. Original strict moves/scores/posts/work replay
passes all 60 lives; exact internal state/N/R evidence is finite focused coverage,
not full mandatory/gameplay qualification or a matched KingWCR result.

Retain the new two-thread transport and the stronger retained3 option. The next
useful discriminator is unchanged-source joint1/2/3 own-PGO/full54, comparing both
options and accepted serial with original endpoints. Do not tune this transport,
reinterpret this screen as full54 seconds, remove observations from another
variant, adopt/release or run broad qualification from this record. The separately
selected next lane has its own frozen source/profile/schedule; it starts only after
this closure commit.

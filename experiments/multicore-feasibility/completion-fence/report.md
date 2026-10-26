# Two-fence completion: park unchanged

Park the exact two-fence variant unchanged. The small mode3 improvement is smaller than inline drift and all mode3 ranges overlap; no notification-specific benefit is established. Preserve f8b829/profilebbb858 as research leader; no retune, PGO or adoption.

[Complete ranges](case-ranges.csv), [results](results.json), [closure](closure.json), [proof](ownership-proof.md), [independent challenge](independent-challenge.md), [plan](plan.md).

| Configuration | Summed search-wall medians, s | Summed joined native CPU medians, s | Summed lifetime-wall medians, s |
|---|---:|---:|---:|
| preserved1 | 8.375731432 | 8.379914 | 8.399930048 |
| preserved3 | 7.490874129 | 22.472156 | 7.517930939 |
| inline1 | 8.344495941 | 8.348960 | 8.367358477 |
| fence3 | 7.470673597 | 22.412236 | 7.498986688 |

New3/old3 is -0.269669% wall,0.997334x CPU; inline1/old1 is -0.372929% wall,0.996306x CPU. The complete mode3 change has a smaller net improvement than the inactive-path change. This does not establish a synchronization-specific benefit, and subtracting inline drift would not isolate one. No compiler/cache explanation is assigned.

| Case | New3 / old3 median change | Observed mode3 ranges |
|---|---:|---|
| profile-35 | +0.1730% | overlap |
| profile-08 | -1.1827% | overlap |
| profile-43 | -0.6741% | overlap |

All per-case search/CPU ranges below use measured observations only; CSV/JSON also preserve all samples, lifetime/nonsearch ranges and per-process RSS. One excluded warmup plus three rotating observations per cell; ranges are not confidence intervals.

| Case / config | Search wall median [min,max], s | Native CPU median [min,max], s | Per-process peak RSS [min,max], KiB |
|---|---:|---:|---:|
| profile-35 / preserved1 | 4.477951 [4.450266,4.505649] | 4.478842 [4.451215,4.506773] | [19380,19552] |
| profile-35 / preserved3 | 3.807722 [3.801237,3.852918] | 11.422476 [11.403136,11.558215] | [19500,19720] |
| profile-35 / inline1 | 4.463309 [4.456663,4.475759] | 4.464316 [4.457766,4.477218] | [19432,19524] |
| profile-35 / fence3 | 3.814311 [3.802331,3.821188] | 11.442405 [11.405108,11.462983] | [19520,19592] |
| profile-08 / preserved1 | 0.396123 [0.395961,0.396349] | 0.398118 [0.397787,0.398556] | [19372,19600] |
| profile-08 / preserved3 | 0.385282 [0.382238,0.388963] | 1.156557 [1.147708,1.167740] | [19524,19628] |
| profile-08 / inline1 | 0.395728 [0.393186,0.399786] | 0.397819 [0.394709,0.401617] | [19476,19532] |
| profile-08 / fence3 | 0.380725 [0.375600,0.382871] | 1.142860 [1.127658,1.149645] | [19600,19788] |
| profile-43 / preserved1 | 3.501657 [3.484582,3.542960] | 3.502954 [3.486274,3.544235] | [19464,19564] |
| profile-43 / preserved3 | 3.297870 [3.281645,3.310311] | 9.893123 [9.844874,9.929453] | [19516,19620] |
| profile-43 / inline1 | 3.485459 [3.480613,3.519644] | 3.486825 [3.481883,3.520705] | [19364,19604] |
| profile-43 / fence3 | 3.275638 [3.274095,3.315004] | 9.826971 [9.822202,9.944906] | [19604,19660] |

Per-process RSS is a lifetime peak, not an allocation/layout measurement; summing separate process peaks does not yield simultaneous memory requirements. All four 250ms idle probes observe 0 ticks at 100Hz (10ms resolution), not literally zero work. New3/new1 uses 2.684434x CPU and 0.895282x wall on this finite population. Both old/new1 request both owner hooks but keep them dormant. All old/new3 calls enable both hooks.

The publisher-only fence form is UNSOUND and was never built. The selected form has an unconditional publisher SC fence then SC waiting load; true always takes Sleep/notifies without recheck, and publishers never clear waiting. Every cold registration has its own explicit SC fence before predicates, including spurious loops. The source-mapped proof covers normal done, terminal handler, shutdown and epoch exhaustion, all after Control release. Actual matching done loads and original request/output reverse edges still control ownership; notifications never retire readers or authorize outputs.

The 25 worker controls include 24 retained cases and one new pause after BOTH true-load publishers, across first-waiter exit and next-epoch registration. Registration/spurious, terminal, prior-epoch delay, close/drain, startup and exhaustion controls pass. These gated controls support the proof but cannot demonstrate exclusion of the abstract one-fence memory-model counterexample. 35 unaffected Q/ordinary/arithmetic controls are reused; no broad qualification suite ran. Production panic remains abort; test unwind evidence is not production panic recovery.

One generic build and 14 CLI/two original 08 affinity fallbacks pass first attempt. Source 68 differs only in colors_worker.rs protocol/comments/test hooks; 67 other files are exact. Numerical body, owned packet/Flight/lifetimes, request/done, 4096 spins, 512 samples, layout declarations and observation policy remain unchanged. No alignment change, weakening, extra protocol flag, census, workload selector or tuning.

The single saved-image lowering check inspects each old/new image once with objdump/readelf, retaining full raw output. Actual publisher lowering is old `xchg %al,0x1b29(%rdi)` versus new `mfence; movzbl 0x1b29(%rdi),%eax`; Sleep access remains 0x1b18. Actual cold registration is `xchg` followed by `mfence` before predicate loads. Selected source-correlated blocks contain 0→2 mfence instructions and 8→7 xchg instructions, including neighboring work; those counts are not per-call cost or a cache attribution. No instruction-driven tuning followed.

Every production worker struct/enum declaration, including attributes, is byte-identical. These debug1 images emit no attributable Shared/Cells/Reader/Control/Flight type DIEs: full compiled sizes, alignments and offsets remain UNKNOWN. Matching direct waiting/Sleep displacements provide only partial relative-offset evidence, not complete layout/heap alignment equality. No assertion requiring redundant machine fences was imposed.

- New generic image `51e5ce59d6513eb98a7d7de75c363e73d6a80bcb29eed7befb6aa769f5741cd1`, 7881856 bytes, shared by new1/new3.
- Preserved Q generic `d2dd0ade6a96c0006663f08a7e3b7e7c5d87101e84a977315a232d69d7fce806`, 7881640 bytes, shared by old1/old3; never rebuilt.
- Latest PGO leader f8b829/profilebbb858 remains byte-identical; all 32 protected artifacts/profiles are preserved. Full identities and source maps are bound by closure.json/preparation.json.

All six pipeline stages exit 0 first attempt; 48 replay lives reproduce 560 ordered posts, four idle processes and 52 unique direct native terminal receipts pass saved-raw reconciliation. Pipeline 220.325s is within the original 3600s ceiling; collection 144.907s within 1800s, life 180s. No failure, repeat or clock reset. Final closure reparses the original bytes and binds 987 paths, including lowering output and both outer housekeeping restoration receipts.

Main 14/helpers 6,4; H 0-3,8-13; siblings 15/7/5 unassigned. Actual pre-input TIDs/affinities are gated and selected user-owned housekeeping is restored. This is guest placement, not host exclusivity. Search wall is original go-write→move callback; wait4 CPU/lifetime/RSS includes startup/setup/joined shutdown and the Python pre-exec prefix. Original readiness partition timings are not isolated synchronization costs; residual join excludes eager inventory work. Active helpers can spin while Host callbacks block.

Raw runs/build/lowering: `/home/legolas/rook2-experiments/completion-fence-20261026-01`. Setup fa7227ec; proof, source patch and exact source maps are versioned. Native work is stopped; park this exact variant without rescue/PGO/adoption. The separately selected writer-region question is source-only and adds no execution to this record.

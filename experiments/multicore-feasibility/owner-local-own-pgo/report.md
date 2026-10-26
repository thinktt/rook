# Owner-local own-PGO/full54: retain the new research leader

**Retain exact 3d914c/profilebf909c as the new research performance leader**, preserving 67d and accepted serial. Hook-on totals 60.049404s versus 61.587882s matching off (−2.4980%,52/54 faster) and 61.047211s retained3 (−1.6345%,44/54 faster). Whole CPU also falls. This is descriptive full54 evidence, not qualification or canonical adoption.

[All54 rows](full54.csv), [results](results.json), [closure](closure.json), [plan](plan.md), [policy](policy.json). Direct sums follow one observation per case/configuration; there are no warmups or repeated cells. Do not interpret these as medians, confidence intervals or matched KingWCR/KingRE qualification.

| Configuration | Search wall sum, s | Joined native CPU sum, s | Lifetime wall sum, s | Mean / max per-process peak RSS, KiB |
|---|---:|---:|---:|---:|
| Accepted serial5cf | 68.282114 | 68.366492 | 68.706466 | 22167.9 / 68680 |
| Retained67d mode3 | 61.047211 | 183.151691 | 61.544648 | 22343.7 / 68856 |
| New inline1 | 68.838654 | 68.920165 | 69.263801 | 22241.1 / 68744 |
| New mode3 off | 61.587882 | 184.777041 | 62.087058 | 22339.9 / 68748 |
| New mode3 on | 60.049404 | 180.163710 | 60.544173 | 22329.6 / 68800 |

| Comparison | Search-wall change | Whole CPU ratio | Faster / slower cases |
|---|---:|---:|---:|
| hook-on3 / hook-off3 | -2.4980% | 0.975033 | 52 / 2 |
| hook-on3 / retained3 | -1.6345% | 0.983686 | 44 / 10 |
| hook-on3 / serial1 | -12.0569% | 2.635263 | 52 / 2 |
| inline1 / serial1 | +0.8151% | 1.008099 | 4 / 50 |
| hook-off3 / retained3 | +0.8857% | 1.008874 | 7 / 47 |

On saves 1.538479s against matching off and 0.997807s against retained3. Matching on/off gains are broad:52/54; case43 is the largest absolute gain 159.197ms but only 10.35% of the full54 saving, versus dominating the earlier three-case screen. Relative best is 15 (−10.028%); the two losing cases and all rows remain in results/CSV. Largest matching loss is 53 (+10.129ms,+0.819%). Against retained3, largest saving 43 is 130.980ms; largest absolute loss 52 is 19.036ms, and relative worst 06 is+0.993%. Single observations do not establish per-case significance.

The new inline path costs+0.8151% versus accepted serial (50/54 slower), and off3 costs+0.8857% versus retained3 (47/54 slower). The positive on/off result more than offsets this measured common drift in the three-thread configuration; it does not eliminate the serial cost. The four-path profile/source/build differ from the old three-mode profile, so no individual refactor, profile, layout or readiness load is assigned that drift. Preserve the serial artifact independently. On is 12.0569% below serial wall while using 2.6353x CPU; elapsed improvement does not imply reduced total CPU versus one thread.

All five 250ms idle probes observe 0 CPU ticks at 100Hz (10ms resolution), not literally zero execution. Per-process RSS minima/maxima/means are in results; sums of lifetime peaks are not simultaneous memory requirements. Standard cases have different TT sizes, so the larger peaks are preserved rather than normalized away.

The earlier generic 2.757% matched gain remains directionally consistent with this 2.498% full54 result, but populations, images, profiles, windows and repetition policies differ. This is not a causal measure of what PGO changed or a basis for workload selectors. Original 512 sampling remains: owner_ready is before eager generation; residual join starts after it and excludes generation. A shorter join is not saved work, and no hot census was added.

Exact source 66 and 47 passed generic controls are reused unchanged from ce3d1524. Joint training runs original 54 once each in inline1/current2/3off/3on:216 strict lives, 2496posts and 216 unique PID-bound raw profiles. The mode/flag pair is recorded explicitly, including off/on sharing budget3. Equal raw inclusion, one canonical LLVM19.1.7 merge and one separately recorded ACTUAL independent remerge to a fresh output produce byte-identical profiles; only canonical output feeds use build. Training is not timing evidence.

- New use image `3d914cddf415cfb109bdabaf6eaf5b2384c3ca537a37a2f37a691c28ac5e91cc`, 7789192bytes, shared by new1/off3/on3.
- Own profile `bf909cd4b9a489f3de23e1b0b2d5bb45c0069f690354d76510636c8fed54cd1f`, 125560bytes.
- Retained3 is exact `67d011083f37f42904423247f5cf0ece2a1e36f0a4129da94fe7561d1f922ea7`, old profile `9487473e31dfc30ae515cdce18e3f15ec3a653bfd1c5bd665a8f76d235e30311`.
- Serial is exact `5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a`, original arguments. Generic7ac/4b40 and all 25 protected artifacts/profiles remain unchanged.

Compiler/recipe/provenance admissions match both controls: Rust 1.85.1/LLVM19.1.7, GNU x86-64/target-cpu=x86-64, opt3/thinLTO/CGU1/debug1/panicabort, use-only ExtTSP. No source cleanup, second profile/use build, observer removal, tuning or extra small screen. Exact use-image 14CLI/two original08 requested3→effective1/2 fallback controls pass; the requested owner flag is explicitly recorded even when dormant under a cap.

All 270 original full54 lives reproduce 3120posts; all five idle probes and actual pre-input TID placements pass independent raw audit. Source/image/profile/raw identities, all 491 training/comparison/idle direct native terminal chains and 2941 row hashes close. Existing color dispatch counts match across retained/off/on for all 54 cases. Logical work and finite controls support the mechanism, without broad mandatory/regular12/full3288 qualification.

Five configurations rotate through released 54 order. Exact slot counts are 10/11, not perfectly balanced: serial1 [11,10,11,11,11], retained3 [11,11,10,11,11], inline1 [11,11,11,10,11], off3 [11,11,11,11,10], on3 [10,11,11,11,11]. No warmup, life repeat or gain gate is applied.

All seven native pipeline stages exit 0 first attempt; pipeline 1167.545s within3600s, training 596.860s within2400, comparison 492.680s within1800 and life 180s. The old generic test-only compile failure/clock is retained as reused evidence, not rewritten. This PGO lane has no build, training, replay, semantic or comparison failure.

The extra final metadata closer initially treated common.prepared_run's three-element tuple as a dictionary. Its observed exit 1 and cause are saved in closure-attempt-01.json. A separate [adapter](close_adapter.py) unwraps that validated tuple and runs EVERY original closer check; frozen closer/source/profile/native bytes remain unchanged and no engine/build/benchmark is rerun. Terminal metadata closure passes at 1268.524s on the same ceiling. This tool repair is separate from the all-pass native pipeline.

Main 14/helpers6,4; H0-3,8-13; siblings15/7/5 unassigned. Actual native masks are gated before setup input and reversible user-owned housekeeping is restored. Guest placement is not exclusive host isolation. Search wall is original go-write→move callback; direct wait4 all-thread CPU/lifetime/RSS includes startup/setup/joined shutdown and the small Python pre-exec prefix. No PMU/historical-host conversion claim. Active helpers may spin during a blocked Host callback; no new production lifecycle claim is made.

Setup c0f8705b98026f6674a60a086116eb6fdc74a94d; raw/build/profile/failed-metadata receipts remain outside Git at `/home/legolas/rook2-experiments/owner-local-own-pgo-20261026-01`. Closure binds1126 paths and all 25 protected artifacts. Native work is stopped. Retain 3d914c as the new research leader, keep 67d/serial, and leave qualification, adoption or further work to separate selection.

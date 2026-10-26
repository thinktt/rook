# Writer-region unchanged own-PGO/full54

Retain exact a4ecf096/profile6cb9dcaa as the research performance leader after full54 review; preserve f8 and every predecessor. No source/profile/layout retune, qualification, canonical adoption or further native lane follows automatically.

[All 54 rows](full54.csv), [results](results.json), [closure](closure.json), [actual layout](production-layout.json), [plan](plan.md). Direct sums use one observation per case/configuration, no warmups or repeated cells. These are descriptive artifact comparisons, not medians, confidence intervals or matched KingWCR/KingRE qualification.

| Configuration | Search wall sum, s | Joined native CPU sum, s | Lifetime wall sum, s | Mean / max process peak RSS, KiB |
|---|---:|---:|---:|---:|
| Accepted serial 5cf | 68.279043 | 68.358829 | 68.696860 | 22176.0 / 68620 |
| Retained f8 inline1 | 69.467164 | 69.552959 | 69.892529 | 22270.1 / 68800 |
| Retained f8 mode3 | 59.909994 | 179.740984 | 60.403182 | 22348.4 / 68796 |
| New layout inline1 | 69.115223 | 69.203216 | 69.533405 | 22235.6 / 68840 |
| New layout mode3 | 59.317384 | 177.967157 | 59.808279 | 22343.5 / 68924 |

| Comparison | Search-wall change | Whole CPU ratio | Faster / slower cases |
|---|---:|---:|---:|
| regions3 / retained3 | -0.9892% | 0.990131 | 48 / 6 |
| inline1 / retained1 | -0.5066% | 0.994972 | 44 / 10 |
| retained1 / serial1 | +1.7401% | 1.017469 | 0 / 54 |
| inline1 / serial1 | +1.2247% | 1.012352 | 1 / 53 |
| regions3 / serial1 | -13.1251% | 2.603426 | 54 / 0 |
| regions3 / inline1 | -14.1761% | 2.571660 | 54 / 0 |
| retained3 / retained1 | -13.7578% | 2.584232 | 54 / 0 |

New mode3 saves 0.592609s against retained f8 over all 54 cases. Case 43 supplies 66.457ms (11.21% of net saving); the gain is spread beyond the generic three-case population. The six mode3 losses sum 24.323ms and remain individually listed. These counts and sums do not establish per-case significance.

All loss rows remain in results/CSV. Largest absolute and relative changes:

- regions3/retained3: absolute best profile-43 -66.457ms; worst profile-13 +9.392ms. Relative best profile-18 -3.924%; worst profile-12 +1.754%.
- inline1/retained1: absolute best profile-04 -40.910ms; worst profile-20 +4.438ms. Relative best profile-39 -2.531%; worst profile-12 +2.673%.
- retained1/serial1: absolute best profile-12 +0.116ms; worst profile-04 +88.882ms. Relative best profile-28 +0.195%; worst profile-39 +4.167%.
- inline1/serial1: absolute best profile-28 -0.380ms; worst profile-44 +64.347ms. Relative best profile-28 -0.043%; worst profile-12 +3.130%.
- regions3/serial1: absolute best profile-04 -674.915ms; worst profile-12 -1.451ms. Relative best profile-41 -20.349%; worst profile-51 -1.426%.
- regions3/inline1: absolute best profile-04 -722.888ms; worst profile-12 -2.269ms. Relative best profile-41 -21.314%; worst profile-51 -3.153%.
- retained3/retained1: absolute best profile-04 -737.173ms; worst profile-12 -1.993ms. Relative best profile-41 -21.207%; worst profile-08 -0.750%.

Old/new inline comparisons price common source/profile/build drift; both are also compared directly with accepted serial. No causal subtraction isolates layout or cache effects. Mode2 participates in training only; there is no two-thread performance result. The original three-case generic 0.6643% gain had overlapping ranges and predicted no full54 magnitude. Per-case single observations do not establish repeatability or significance.

Joint training composition matches retained f8 exactly: original 54 once each in inline1/current2 with both hooks requested but dormant, ordinary-on/Q-off3 and ordinary-on/Q-on3. 216 strict lives/2496 posts yield 216 unique PID-bound raw profiles. Equal raw inclusion, one canonical LLVM19.1.7 merge and one ACTUAL independent remerge into a fresh output produce byte-identical data. Only canonical output feeds the single ExtTSP use build; training is not timing evidence. Mode/options/requested threads/configured pre-input TIDs and actual native argv are independently bound. No profile weighting, mixture sweep or source change.

All 68 source inputs match the generic writer layout; 25 affected worker and 35 unaffected numerical/owner controls are reused. No unit suite rerun. Fresh use-image 14 CLI/two original08 affinity fallbacks with both flags and ONE cold production layout admission pass. The actual production Shared remains 7168 bytes, aligned to 64 with address phase 0; region offsets are 0/64/384/448/512/576/640/704. Each output 56+done 8 slot occupies 64 bytes (done at 440/504). The query is off throughout all training/comparison lives. No allocator/header extent is observed or required.

- New use image `a4ecf096d2144a79608b0ff4f3dc827bc8e5119730f2c43b29f46d1f7ffe62b5`, 7859744 bytes, shared by new1/new3.
- Own canonical profile `6cb9dcaab015c8b4c13f37040bb34cda9e4d7bc11b77ef8c4c99bd56987eae3b`, 127288 bytes; independent output is byte-identical.
- Retained f8 image `f8b829a79e43a90a0396c3baacb8f44f23476f6d9e7a9661626f5c1e8b467c62` serves old1/old3; old profile `bbb858b01018cea09311ac5fe3b5fb5bc18c3b716e2f6a7bb5df83c794527ed4`.
- Accepted serial `5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a`, original arguments. All 34 protected artifacts/profiles, including generic 8c/d2dd and parked fence 51e5, remain unchanged.

Compiler/recipe admissions match both old artifacts: Rust 1.85.1/LLVM19.1.7, GNU x86-64/target-cpu=x86-64, opt3/ThinLTO/oneCGU/debug1/panicabort, use-only ExtTSP. Original RMW handshake, numerical code, all observations, spins4096/sample512, one Shared/Arc, narrow concrete Cells Sync, owned input, actual done/reverse-output and close/park/join ownership remain. No padding, source, observer or transport retune.

All 270 original comparison lives reproduce 3120 ordered posts. All 491 training/comparison/idle native terminal receipts plus the separate joined cold layout process close. Mode3 dispatch counts match old/new for all 54 cases. Full54 replay/finite controls do not constitute mandatory/regular12/full3288 qualification.

Five configs rotate through original 54 order; exact slot counts are 10/11, not perfectly balanced:

- serial1: [11, 10, 11, 11, 11].
- retained1: [11, 11, 10, 11, 11].
- retained3: [11, 11, 11, 10, 11].
- inline1: [11, 11, 11, 11, 10].
- regions3: [10, 11, 11, 11, 11].

Five 250ms idle probes preserve ticks/resolution in results. Zero ticks mean below resolution, not literally zero work. Per-process RSS depends on case-specific TT sizes; sums of separate peak RSS are not simultaneous memory requirements. Whole CPU can remain much larger than serial even with lower elapsed search.

All eight native stages exit 0 first attempt; pipeline 1175.831s within the persisted 3600s ceiling. Training 595.115s within 2400; comparison 505.014s within 1800; life 180s. No native failure, completed-request repeat, profile regeneration or clock reset. Before the lane, the closer was frozen with validated three-element tuple projection. Its terminal metadata audit passes without an adapter. One pre-native freeze-harness import-path issue was repaired without changing source/tools or consuming a native clock.

Main 14/helpers 6,4 (trainingmode2 helper6), H 0-3,8-13, siblings 15/7/5 unassigned. Actual pre-input placement is gated and user-owned housekeeping restored; guest placement is not host exclusivity. Search wall is original go-write→move callback; wait4 all-thread CPU/lifetime/RSS includes startup/setup/joined shutdown and Python pre-exec. Readiness remains scheduling-sensitive with both owner hooks. Original residual join excludes eager generation and cannot isolate saved work. Active helpers can spin while Host callbacks block.

Setup 2e187c1d; raw profiles/builds/runs at `/home/legolas/rook2-experiments/writer-regions-own-pgo-20261026-01`. Closure binds 1276 paths and 34 protected artifacts. Native work is stopped. Retain exact a4ecf096/profile6cb9dcaa as the research performance leader after full54 review; preserve f8 and every predecessor. No source/profile/layout retune, qualification, canonical adoption or further native lane follows automatically.

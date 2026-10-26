# Q owner-local own-PGO/full54

Retain exact f8b829a7/profile bbb858b0 as the new research performance leader, preserving ordinary-only 3d914c, 67d and accepted serial. No qualification, canonical adoption or external action follows.

[All 54 rows](full54.csv), [results](results.json), [closure](closure.json), [plan](plan.md), [policy](policy.json). Direct sums use one observation per case/configuration, without warmups or repeated cells. These are descriptive research measurements, not medians, confidence intervals or compatible KingWCR/KingRE qualification.

| Configuration | Search wall sum, s | Joined native CPU sum, s | Lifetime wall sum, s | Mean / max per-process peak RSS, KiB |
|---|---:|---:|---:|---:|
| Accepted serial 5cf | 68.811008 | 68.899770 | 69.236865 | 22160.7 / 68816 |
| Retained ordinary-on 3d mode3 | 60.327621 | 180.993752 | 60.831367 | 22338.2 / 68784 |
| New inline1, both hooks dormant | 69.548826 | 69.632720 | 69.971413 | 22251.8 / 68728 |
| New ordinary-on / Q-off3 | 60.450227 | 181.359864 | 60.953336 | 22347.6 / 68864 |
| New ordinary-on / Q-on3 | 59.918858 | 179.768092 | 60.419887 | 22333.6 / 68784 |

| Comparison | Search-wall change | Whole CPU ratio | Faster / slower cases |
|---|---:|---:|---:|
| q-on3 / q-off3 | -0.8790% | 0.991223 | 46 / 8 |
| q-on3 / retained3 | -0.6776% | 0.993228 | 41 / 13 |
| q-on3 / serial1 | -12.9226% | 2.609125 | 54 / 0 |
| inline1 / serial1 | +1.0722% | 1.010638 | 3 / 51 |
| q-off3 / retained3 | +0.2032% | 1.002023 | 26 / 28 |

Q-on saves 0.531369s against matching Q-off across all 54 cases. The largest saving, profile-43, is 51.167ms (9.63% of the net saving). Unlike the three-case generic sample, the full54 net gain is spread across many cases: 46 improve against matching off and 41 against retained ordinary-on. Each cell still has only one observation; the counts do not establish per-case significance.

Every comparison retains its complete gain/loss list in results.json. Largest absolute and relative changes:

- q-on3/q-off3: absolute best profile-43 -51.167ms; worst profile-16 +5.382ms. Relative best profile-22 -2.956%; worst profile-12 +1.153%.
- q-on3/retained3: absolute best profile-43 -65.090ms; worst profile-07 +17.161ms. Relative best profile-22 -3.142%; worst profile-10 +2.097%.
- q-on3/serial1: absolute best profile-04 -660.456ms; worst profile-12 -1.963ms. Relative best profile-41 -20.080%; worst profile-51 -0.485%.
- inline1/serial1: absolute best profile-18 -0.699ms; worst profile-49 +45.299ms. Relative best profile-12 -0.714%; worst profile-15 +2.401%.
- q-off3/retained3: absolute best profile-43 -13.922ms; worst profile-07 +45.456ms. Relative best profile-12 -2.782%; worst profile-07 +1.827%.

A matching on/off comparison prices this complete Q mechanism. New inline/serial and Q-off/retained separately expose common source/profile/build drift. The profile mix differs from retained 3d: both hooks are requested but dormant in budgets 1/2, while both old/new mode 3 controls keep ordinary-on. No individual compiler, layout, readiness or kernel cause is assigned artifact-level changes. Faster elapsed search may still use substantially more aggregate CPU than serial. The earlier generic benefit was chiefly43; these full54 observations retain all outliers rather than extrapolating that small screen.

All five 250ms idle probes record 0 CPU ticks at 100Hz (10ms resolution). Zero ticks mean below tick resolution, not literally zero execution. Per-process peak RSS depends on each case TT configuration; sums of lifetime peaks are not simultaneous memory requirements.

Exact source 68 and 17 affected plus 42 retained controls are reused unchanged from generic closure 61f827b3. Training runs original 54 once in each inline1/current2/Q-off3/Q-on3 mode: 216 strict lives, 2496 posts and 216 unique PID-bound raw profiles. Both flags are requested/dormant in budgets 1/2. Rich training and replay rows independently bind requested threads, configured pre-input TIDs and actual native options/argv. Training is not timing evidence. Equal raw inclusion, one canonical LLVM19.1.7 merge and one ACTUAL independent remerge in a fresh output produce byte-identical profiles; only canonical output feeds the single use build.

- New shared inline1/off3/on3 use image: `f8b829a79e43a90a0396c3baacb8f44f23476f6d9e7a9661626f5c1e8b467c62`, 7842744 bytes.
- Own canonical profile: `bbb858b01018cea09311ac5fe3b5fb5bc18c3b716e2f6a7bb5df83c794527ed4`, 126144 bytes.
- Retained ordinary-only image: `3d914cddf415cfb109bdabaf6eaf5b2384c3ca537a37a2f37a691c28ac5e91cc`, old profile `bf909cd4b9a489f3de23e1b0b2d5bb45c0069f690354d76510636c8fed54cd1f`; no Q flag.
- Accepted serial: `5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a`, original arguments. All 29 protected artifacts/profiles remain unchanged.

Compiler/recipe admissions match both controls: Rust 1.85.1/LLVM19.1.7, GNU x86-64/target-cpu=x86-64, opt3/ThinLTO/CGU1/debug1/panicabort, use-only ExtTSP. Exact use-image 14 CLI and two original 08 requested 3 → effective 1/2 fallback controls pass with both flags requested. No source cleanup, second profile/use build, tuning or extra small screen.

All 270 original full54 lives reproduce 3120 posts; all five idle probes and actual pre-input TID placements pass the saved-raw audit. All 491 training/comparison/idle native terminal receipts and 2941 row hashes close. Existing color dispatch counts match retained/off/on for all 54. This finite evidence is not mandatory/regular12/full3288 qualification.

Exact rotating slot counts (10/11, not perfectly balanced):

- serial1: [11, 10, 11, 11, 11].
- retained3: [11, 11, 10, 11, 11].
- inline1: [11, 11, 11, 10, 11].
- q-off3: [11, 11, 11, 11, 10].
- q-on3: [10, 11, 11, 11, 11].

All seven native pipeline stages exit 0, with no failed build, replay, semantic comparison, repeat or clock reset. Pipeline 1166.118s within 3600s; training 600.001s within 2400; comparison 500.114s within 1800; each life bounded 180s. The metadata closer validates the three-element tuple and projects its saved record before execution; its prior-lane failure/adapter remain pinned, without repeating that failure or running an adapter here.

Main 14/helpers 6,4; housekeeping 0-3,8-13; siblings 15/7/5 unassigned. Actual masks are gated before setup input and reversible selected user-owned housekeeping is restored. Guest placement is not exclusive host isolation. Search wall is original go-write→move callback. Direct wait4 all-thread CPU/lifetime/RSS includes startup/setup/joined shutdown and Python pre-exec. No PMU or historical-host conversion claim. Original 512 samples retain owner_ready before eager generation and residual join after it: a shorter join is not saved work. Active helpers can spin while a Host callback blocks.

Setup 852f16bc6efc2960d3244f4d8028ad4817a3b56b; raw artifacts at `/home/legolas/rook2-experiments/q-owner-local-own-pgo-20261026-01`. Closure binds 1051 paths and 29 protected artifacts. Native work is stopped. Retain exact f8b829a7/profile bbb858b0 as the new research performance leader, preserving ordinary-only 3d914c, 67d and accepted serial. No qualification, canonical adoption or external action follows.

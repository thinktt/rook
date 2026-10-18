# Reported-only complete12-game CPU results

All48 lifetimes /2528 searches independently reconciled against original raw public protocol and receipt chains. One excluded warmup and three measured fresh native processes per game; within-game state persists. Artifact1dc996b2, generic x86-64 PGO. No focused-continuity/full3288 or formal performance qualification.

Raw ratios below compare different, uncalibrated hardware/resource profiles and are descriptive planning values only. They are not accepted pass/fail comparisons.

| Game | Searches | Median native lifetime CPU(s) | CPU min–max(s) | Median lifetime wall(s) | Raw uncalibrated CPU ratio | Unresolved measured search CPU samples |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| main-0000 | 54 | 83.410814 | 82.368368–84.442171 | 83.489070 | 1.5462 | 12 |
| main-0048 | 63 | 97.184032 | 97.181221–97.489088 | 97.275703 | 1.4145 | 16 |
| main-0072 | 56 | 55.082701 | 54.784466–55.191068 | 55.155032 | 1.4525 | 19 |
| main-0168 | 24 | 13.712177 | 13.629930–13.744428 | 13.742621 | 1.4759 | 43 |
| opening-000 | 30 | 57.074798 | 57.000849–57.201195 | 57.124656 | 1.4326 | 0 |
| opening-024 | 30 | 81.577021 | 80.664434–82.000030 | 81.630353 | 1.4324 | 0 |
| opening-048 | 30 | 75.042215 | 74.683234–75.359370 | 75.094060 | 1.4014 | 0 |
| opening-072 | 30 | 54.795305 | 54.760568–54.934307 | 54.844427 | 1.4055 | 0 |
| switching-000 | 122 | 170.801077 | 170.464629–171.438759 | 170.958211 | 1.4665 | 69 |
| switching-024 | 88 | 112.534047 | 112.346008–112.860894 | 112.648266 | 1.5577 | 42 |
| switching-048 | 49 | 68.828277 | 68.293442–69.523692 | 68.894746 | 1.4578 | 25 |
| switching-096 | 56 | 71.886323 | 71.812902–72.560522 | 71.958314 | 1.4641 | 39 |

Sum of12 per-game CPU medians: 941.928787s; raw reference sum644.222971s; ratio1.462116. This is a sum of unit medians, not one continuous session or batch elapsed time.

The36 measured lifetimes contain1896 search intervals, of which265 have unresolved zero-tick CPU. All three samples, including nulls, remain in analysis-first.json; a per-search CPU summary/rate is unavailable unless all three are positive resolved observations. Normal posts/SearchID do not supply terminal N/R.

The direct wait4 scope includes the small Python child pre-exec prefix. Search boundaries use /proc ticks before the mixed go chunk and after the first move-containing received chunk. No PMU, exact internal search timing, descendant-complete monitoring, private resource/no-swap profile, calibrated ratio or final uncertainty qualification is claimed.

Heavy owned builds/tests/other engines/profilers were held. The lead and some short source/status helpers inherited all16 CPUs; actual guest CPU14/15 interference was not quantified. This limitation remains part of these samples. After the collector actually terminated, the own lead/client threads were constrained to housekeeping CPUs in ../owned-helper-affinity-20261018/. No current sample is retroactively upgraded by that later correction.

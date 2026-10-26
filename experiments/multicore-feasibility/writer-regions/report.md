# Writer regions: tentative positive generic direction

Preserve the exact layout as a tentative positive generic option; all mode3 medians improve, but every range overlaps. Keep f8b829/profilebbb858 as research leader. The separately selected unchanged own-PGO lane is not executed by this record; no retune or adoption.

[Complete ranges](case-ranges.csv), [results](results.json), [closure](closure.json), [actual production layout](production-layout.json), [ownership](ownership-proof.md), [plan](plan.md).

| Configuration | Summed search-wall medians, s | Summed joined native CPU medians, s | Summed lifetime-wall medians, s |
|---|---:|---:|---:|
| preserved1 | 8.349792234 | 8.354894 | 8.374885856 |
| preserved3 | 7.499557033 | 22.498762 | 7.526672717 |
| inline1 | 8.386511793 | 8.390957 | 8.410076748 |
| regions3 | 7.449740630 | 22.349239 | 7.476097436 |

New3/old3 is **-0.664258% wall**,0.993354x CPU. Inline1/old1 is **+0.439766% wall**,1.004316x CPU. The mode3 result improves while the inactive-path total worsens; subtracting those changes would not isolate a layout/cache benefit. Three observations in one small window provide no per-case confidence interval or full54 prediction.

| Case | New3 / old3 median change | Observed mode3 ranges |
|---|---:|---|
| profile-35 | -0.2928% | overlap |
| profile-08 | -1.1486% | overlap |
| profile-43 | -1.0404% | overlap |

Case 43 contributes the largest absolute mode3 saving, 34.208ms of 49.816ms net, while its inline1 path loses 1.2540% with separated unfavorable ranges. 35/08 inline medians improve slightly and their ranges overlap. Retain that mixed common-path cost rather than assigning it to a specific compiler or padding cause. All mode3 ranges overlap; observed minima/maxima are not significance tests.

| Case / config | Search wall median [min,max], s | Native CPU median [min,max], s | Per-process peak RSS [min,max], KiB |
|---|---:|---:|---:|
| profile-35 / preserved1 | 4.486713 [4.457739,4.495828] | 4.487953 [4.458560,4.497442] | [19308,19408] |
| profile-35 / preserved3 | 3.828503 [3.810930,3.857653] | 11.484838 [11.432143,11.572061] | [19368,19600] |
| profile-35 / inline1 | 4.481855 [4.470204,4.484828] | 4.482798 [4.471218,4.485783] | [19380,19636] |
| profile-35 / regions3 | 3.817295 [3.790859,3.838459] | 11.451143 [11.372124,11.514851] | [19488,19736] |
| profile-08 / preserved1 | 0.396365 [0.395937,0.399360] | 0.398300 [0.398002,0.400792] | [19552,19660] |
| profile-08 / preserved3 | 0.383136 [0.382936,0.383821] | 1.150198 [1.148018,1.151521] | [19564,19592] |
| profile-08 / inline1 | 0.394468 [0.393438,0.397242] | 0.396506 [0.394965,0.399746] | [19328,19416] |
| profile-08 / regions3 | 0.378735 [0.376494,0.384488] | 1.137102 [1.130258,1.154231] | [19308,19600] |
| profile-43 / preserved1 | 3.466714 [3.461899,3.487282] | 3.468641 [3.463593,3.488694] | [19544,19640] |
| profile-43 / preserved3 | 3.287918 [3.281513,3.331539] | 9.863726 [9.844467,9.994443] | [19520,19584] |
| profile-43 / inline1 | 3.510188 [3.488937,3.522710] | 3.511653 [3.490367,3.523983] | [19348,19596] |
| profile-43 / regions3 | 3.253710 [3.251359,3.310706] | 9.760994 [9.753395,9.931858] | [19444,19504] |

One excluded warmup plus three rotating observations per cell gives 48 replay lives, 36 measured/12 warmups, plus four 250ms idle processes. Every measured sample and lifetime/nonsearch range is preserved in JSON/CSV. All four idle probes observe 0 ticks at 100Hz (10ms resolution), not literally zero work. Per-process peak RSS is a lifetime high-water mark, not allocation size or simultaneous memory requirement. New3/new1 uses 2.663491x CPU and 0.888300x wall on this population. Both old/new1 request both owner hooks but keep them dormant.

## Actual geometry and scope

The single cold opt-in query is from the actual production image and actual Shared instance with real parked helpers, generation 0 / Flight None / scopes 0. It reports testBuild=false, Shared 7168B / alignment64 / addressMod64=0. Region offsets and spans relative to that Shared:

| Region | Offset | Bytes | Alignment |
|---|---:|---:|---:|
| request | 0 | 64 | 64 |
| packet | 64 | 320 | 64 |
| white | 384 | 64 | 64 |
| black | 448 | 64 | 64 |
| lifecycle | 512 | 64 | 64 |
| latch | 576 | 64 | 64 |
| wait | 640 | 64 | 64 |
| control | 704 | 6464 | 64 |

White/black slots start 384/448; outputs occupy 56 bytes, done atomics 8 bytes at 440/504. Each complete slot occupies one 64-byte region and regions are disjoint. Packet 312, SideOutput 56, Cells 448, Mutex<Control>6448, lifecycle 64 and cold-wait 64 are actual candidate type sizes. This matches the fixed topology with no rescue/reordering. 64 remains a chosen line-size hypothesis, not proof of host cache geometry.

The actual Shared body is 7168 bytes; the prior generic Shared body 6960 is inferred from saved 6976-byte Arc allocation and 16-byte data offset. New body is 208 bytes larger on that basis. The approximately 7232-byte new Arc extent/+256-byte allocation delta remains an estimate: no allocator/header query was added. Neither RSS nor a body-size match proves coherence traffic or cache savings. More separately polled lines, payload/done polling, true request/latch sharing, alignment and startup/codegen costs remain priced in this complete artifact comparison.

Layout inspection is off in all 48 timing lives. Its cold CLI→Session→Evaluator forwarding adds no hot counters, calls or JSON. The production path rejects projection except at initial parked startup; cfg(test) geometry is explicitly marked and cannot satisfy admission. Existing 14 CLI and two original 08 requested 3→effective 1/2 fallbacks pass; the separate layout process exits/reaps normally. No binutils or general introspection framework was executed.

Original 24 affected worker/lifecycle controls plus one layout test pass, with 35 unaffected numerical/owner/Q controls reused. Source 68 has four changed paths: colors_worker.rs layout/projection/test and cold plumbing in bin/rook2.rs,evaluator.rs,session.rs. 26 operational bodies are byte-identical after only reversing field-path renaming, including kernel, dispatch/consume, all atomic/SC exchanges and close/failure paths. Packet, SideOutput, Control and all math/observation declarations remain unchanged.

One existing private Cells Sync covers the same three concrete payload cells plus auto-safe done atomics. No generic payload Sync, whole-slot mutable reference/copy/write across a live atomic, new per-reader allocation, pointer table, observer removal, kernel change or weaker ordering. Input publication, actual done retirement/output reverse edge, Flight/Discarding and real park/join ownership remain. Wake still pairs with Control and completed with Sleep. This uses the original RMW protocol, not the parked two-fence variant. Both readiness-conditional owner hooks remain; changed timing may change eager work/waste without altering semantic charges, so no causal savings are inferred.

- New generic image `8c217f96ceae16ea29e623276413145e976cbed6cf35e38fa38d029ce820e3ef`, 7902688 bytes, shared by new1/new3.
- Preserved Q generic `d2dd0ade6a96c0006663f08a7e3b7e7c5d87101e84a977315a232d69d7fce806`, 7881640 bytes; never rebuilt.
- Latest PGO leader f8b829/profilebbb858 and all 33 protected artifacts/profiles remain byte-identical. Exact source maps and identities are in preparation/closure.

All six stages exit 0 first attempt; 48 original replay lives reproduce 560 ordered posts, four idle processes and 52 unique comparison/idle native terminal receipts pass independent saved-raw audit. The one separate cold-layout process has its own joined/PID-absence status. Pipeline 203.178s within the original 3600s ceiling; collection 144.557s within 1800s; life 180s. No failure, completed-request repeat, source change during data or clock reset. Final closure binds 982 paths including layout raw/status and both outer housekeeping restorations.

Main 14/helpers 6,4; H 0-3,8-13; siblings 15/7/5 unassigned. Actual pre-input TIDs/affinities are gated and user-owned housekeeping restored. The separate cold layout query inherits H. Guest placement is not host exclusivity. Search wall is original go-write→move callback; wait4 CPU/lifetime/RSS includes startup/setup/joined shutdown and Python pre-exec. Original 512 readiness samples are not isolated cache/synchronization costs; residual join excludes eager inventory work. Production panic remains abort; focused unwind tests are not production panic recovery.

Raw runs/build/layout: `/home/legolas/rook2-experiments/writer-regions-20261026-01`. Setup 0a7860d1. Native work is stopped. Preserve this exact tentative option without retuning; f8/bbb remains leader. The separately selected unchanged own-PGO/full54 lane will be a new record after this closure, not an executed extension here. No qualification, adoption or external action.

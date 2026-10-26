# Q owner-local: positive generic result, chiefly case43

**Retain the exact generic extension for a separate production decision.** Q-on search-median sum 7.537384750s is 1.6592% below matching Q-off 7.664551710s and 1.1468% below preserved ordinary-on 7.624829798s. Common off/preserved drift is +0.5210%. Case43 supplies most of the gain; this does not establish breadth or predict PGO/full54. Preserved3d914c/profilebf909c remains the research performance leader until a separately selected comparison.

| Mode | Sum of search medians, s | Joined CPU median sum, s | Lifetime wall median sum, s |
|---|---:|---:|---:|
| preserved3 | 7.624829798 | 22.874687 | 7.651978179 |
| q-off3 | 7.664551710 | 22.993980 | 7.691423820 |
| q-on3 | 7.537384750 | 22.612502 | 7.564637016 |

| Case | Mode | Search median [min–max], s | CPU median, s | Per-process peak RSS range, KiB |
|---|---|---:|---:|---:|
| 35 | preserved3 | 3.845971022 [3.819831839–3.886059329] | 11.537371 | 19468–19672 |
| 35 | q-off3 | 3.861288128 [3.853630688–3.888905898] | 11.583326 | 19512–19664 |
| 35 | q-on3 | 3.843059037 [3.842387212–3.846854615] | 11.528601 | 19504–19628 |
| 08 | preserved3 | 0.385594199 [0.384414921–0.387892287] | 1.157532 | 19420–19680 |
| 08 | q-off3 | 0.389538459 [0.388647349–0.390404285] | 1.169468 | 19412–19508 |
| 08 | q-on3 | 0.384731357 [0.383998802–0.390455289] | 1.155090 | 19508–19560 |
| 43 | preserved3 | 3.393264577 [3.353849844–3.394098714] | 10.179784 | 19432–19676 |
| 43 | q-off3 | 3.413725123 [3.399074655–3.501874057] | 10.241186 | 19488–19548 |
| 43 | q-on3 | 3.309594356 [3.302596694–3.336301317] | 9.928811 | 19516–19764 |

| Case | On/off median change | On/preserved change | Range result |
|---|---:|---:|---|
| 35 | -0.4721% | -0.0757% | below off; overlaps preserved |
| 08 | -1.2341% | -0.2238% | overlaps both |
| 43 | -3.0504% | -2.4658% | below both |

Case43 saves 104.131ms against matching off and 83.670ms against preserved; the entire sums save 127.167ms and87.445ms, respectively. Case08 has one on observation above both controls despite a lower median. Do not present three median wins as three separated wins or a confidence estimate. Common source/layout changes are part of the off/preserved cost, not an isolated selector/branch/cache diagnosis.

On/off CPU ratio is 0.983410; all three 250ms idle probes record zero ticks at 100Hz, not literally zero CPU. Complete lifetime CPU includes startup/teardown. RSS is per-process, not a sum of lifetime peaks.

17 affected tests pass:6Q selector,6actual Q caller and5ordinary-hook compatibility. The remaining42 prior ordinary/arithmetic/color/lifetime controls are reused historical support, not newly run on this image. Actual sparse and refresh preparation, strict FAST-only edges/capture exception, ready/pending, supplied map/weights/R/retention, static discard, ordered empty/special/joined lists, counts/order/child stop and public/FRESH/observed/root/checked/reused/terminal-ply/modes1/2 exclusions are covered. Direct checked joined-EP producer controls are labeled conditional producer checks rather than admitted unchecked-Q witnesses. No new worker/error ownership is introduced; unchanged terminal query/complete evidence remains applicable.

All 14CLI controls and two original08 one/two-CPU fallback lives (20posts) pass; both flags are requested under the caps and actual modes recorded. All 36 original replay lives (27measured/9warm) reproduce 420 ordered posts, followed by 3idle. All 39 direct native/runner chains, source/image/raw/report/pre-input TID identities and independent saved-raw/pipeline closure pass first attempt. There were no source/tool repairs, failed native requests, repeats or clock resets in this lane.

Exact 68 source derives from tested ordinary66, with four changed production paths and two added test modules. Worker, ordinary and tactical producer bytes are unchanged. Both actual Q FULL seams use one shared selector and the original numerical body; sparse/strict refresh predicates, lazy Influence/Some authority and public Selection layout remain. Activation-local preparation skips only original tactical generation at demand. Accounting/sort/events/legality/child/polls remain original. FULL evaluation returns discard physical work without logical generated/N/R charges.

The separately proved 417<512 bound covers coherent joined/non-orthodox placements and prefix duplicates. No runtime validation/capacity/opposite-king probe or bounded-generator variant was added. No new worker, publication, sharing, row copy, allocation, cold report schema or hot census exists. The production build excludes test TLS/probes. Owner_ready stays before eager work; residual join starts afterward and excludes generation. A shorter residual join is not saved work. Historical Q demand fractions are not the current readiness-filtered population or timing data.

New generic image `d2dd0ade6a96c0006663f08a7e3b7e7c5d87101e84a977315a232d69d7fce806`, 7881640bytes. Preserved 4b40e2b541bea6e2dd0a8f760bdc9a85ea498ca77f1f108ef24259de33efdc8c is the old generic ordinary-on image. Every configuration requests --threads=3 --owner-local-inventory; only Q-on adds --q-owner-local-inventory. Matched Rust 1.85.1/LLVM19.1.7 GNU x86-64 opt3/thinLTO/CGU1/debug1/panicabort; no PGO. The normalized numerical body remains SHA256 81df054408184374bfb1bb0a2acd4d48183b2f9bc1faf57ebea6912d3a3e1393.

All seven stages exit 0. Pipeline 142.315s within3600, collection103.380s within1800, per-life 180s. Both housekeeping wrappers restore selected user-owned masks. Main 14/helpers6,4; H0-3,8-13; siblings15/7/5 unassigned. Guest placement is not exclusive host isolation. Go-write→move callback search wall and direct native joined all-thread wait4 CPU/lifetime/RSS retain original boundaries, including startup/setup/teardown plus the small Python pre-exec prefix.

[Results](results.json), [27 measured samples](timings.csv), [closure](closure.json), [frozen preparation](preparation.json), [plan](plan.md), [source review](source-review.md), [capacity proof](capacity-proof.md), [evaluator proof](evaluator-proof.md), [caller proof](caller-proof.md) and [source patch](source.patch) bind the finite study. Setup 493fb64c638a22322c1bcf55b0ee2d37708bcfc7; raw evidence outside Git at `/home/legolas/rook2-experiments/q-owner-local-20261026-01`. Closure binds764 paths and preserves 28 artifacts/profiles, including 3d/profilebf909c. Native work is stopped; no tuning, automatic PGO, qualification, adoption or external action follows from this result.

# Scoped borrowed FULL-input result

Park unchanged. Borrowing is **3.250% slower** than matching scoped owned, and **5.044% slower** than preserved7ac3. All three cases lose with separated observed ranges versus matching owned. The common scoped-owned path itself costs **1.738%** versus preserved3. This is a finite generic transport result, not a universal conclusion about borrowed data or an isolated cache cause.

| Mode | Sum of search medians, s | Sum of joined CPU medians, s | Sum of whole-life wall medians, s |
|---|---:|---:|---:|
| preserved3 | 7.779674002 | 23.339439 | 7.807427039 |
| scoped-owned3 | 7.914857270 | 23.745016 | 7.941501458 |
| scoped-borrowed3 | 8.172097763 | 24.516775 | 8.199497355 |

| Case | Mode | Search median [min–max], s | CPU median, s | Peak RSS range, KiB |
|---|---|---:|---:|---:|
| 35 | preserved3 | 3.856301368 [3.835553711–3.885632691] | 11.568355 | 19520–19620 |
| 35 | scoped-owned3 | 3.905699523 [3.893389632–3.916510934] | 11.716617 | 19480–19684 |
| 35 | scoped-borrowed3 | 4.010909056 [4.009724073–4.024261465] | 12.032440 | 19520–19616 |
| 08 | preserved3 | 0.395259068 [0.390248877–0.396845154] | 1.186565 | 19388–19784 |
| 08 | scoped-owned3 | 0.398060434 [0.396683258–0.401739269] | 1.195150 | 19540–19660 |
| 08 | scoped-borrowed3 | 0.421191421 [0.420824382–0.425165462] | 1.264494 | 19568–19788 |
| 43 | preserved3 | 3.528113566 [3.475779722–3.548342816] | 10.584519 | 19644–19712 |
| 43 | scoped-owned3 | 3.611097313 [3.567035717–3.628620455] | 10.833249 | 19620–19740 |
| 43 | scoped-borrowed3 | 3.739997286 [3.700482595–3.748828042] | 11.219841 | 19516–19616 |

Borrowed/owned CPU ratio is 1.032502. All three250ms idle probes record zero CPU ticks at100Hz; complete idle-lifetime CPU remains2.769–3.085ms and includes startup/shutdown. RSS is a per-process peak; the report does not add per-case peaks into a memory requirement. Every observed borrowed search range is above the matching owned range. Owned versus preserved ranges separate on35/43 and overlap narrowly on08.

49 focused controls pass:32 worker (21 original +11 scoped),5 new evaluator,8 original color evaluator,3 scope and1 whole-helper numerical control. This covers actual live input delay across owner unwind/helper failure, terminal drain/poison, concurrent close, rollback/reuse and unchanged SC registration; supplied custom maps, FRESH, root weights, pawn collision/reset and seeded search depths1/2 match. Production panic=abort and test-build unwind evidence remain distinct.14CLI controls and two original08 one/two-CPU fallback requests (20posts) pass.

All36 original protocol search lives (27measured/9warm) reproduce420 ordered posts, plus3idle lives. Source, raw replay, all39 native/runner terminal receipts, pre-input three-thread masks, cold reports and original clock pass the saved-raw audit and an independent pipeline closure. There were no failed attempts, repairs, completed-life repeats or clock resets. All9 command stages exit0. Pipeline142.817s and collection107.165s stay within3600/1800s. Source/tools/policy remained frozen. Both housekeeping wrappers restored their selected user-owned masks; their exact receipts are bound in results.json.

Main14/helpers6,4; housekeeping0-3,8-13; siblings15/7/5 unassigned. This is guest placement, not exclusive host isolation. Search wall is unchanged tap go-write through move-data callback; CPU/RSS cover the direct native lifetime, joined threads and Python pre-exec prefix. Post-move reporting and teardown are outside search wall but inside lifetime costs. No PMU attribution is made.

New mode3 uses the enclosing guard in both transports. Owned really snapshots Position/Influence; borrowed reads the exact caller inputs. Owner work has safe disjoint evaluator field borrows; numerical kernels, search/TT/learning/pawn ownership and final arithmetic are unchanged. Per-call retirement clears the descriptor after both actual readers, even under outer activation; terminal cleanup really joins. Cold healthy reports show matching request/done and retired:true, with epochs1574502/361835/2523136 for35/08/43 in both new modes. Idle epochs are zero. This verifies actual use, not an eligible-population census or exhaustive safety proof.

Avoiding input destination writes did not improve this implementation. Pointer/source cache transfers, shared publication/retirement, enum/common-guard costs and caller stack/source layout remain. Existing512-sample partitions do not isolate memcpy cost. Both new modes also lose against the preserved executable; keep positive epoch64/67d and park this exact derivative without tuning or PGO. The next decision belongs to the strategy lead.

Exact new ordinary image: `/home/legolas/rook2-experiments/borrowed-full-input-20261026-01/rook2-candidate`, SHA256 `70bb39ae243390bccaae8782df8a5a74861194c263c515c2fefee6a7fe6bc555`,7825544bytes, text565627bytes. Preserved control7ac72fc6 remains7798776bytes. Both use identical rustc1.85.1/LLVM19.1.7 GNU x86-64 generic settings, opt3/thinLTO/CGU1/debug1/panicabort; no PGO.65 candidate source inputs versus64 baseline: only color worker, evaluator, Session and private CLI changed, plus one test module.

[Results](results.json), [27 measured samples](timings.csv), [closure](closure.json), [frozen preparation](preparation.json), [plan](plan.md), [ownership proof](ownership-proof.md), [safe evaluator proof](evaluator-proof.md), [source review](source-review.md) and [source patch](source.patch) bind the experiment. Setup commit `f7d4ac4a473d4bc9d773796ef2ab6101b7c2e82f`; raw evidence at `/home/legolas/rook2-experiments/borrowed-full-input-20261026-01`. The closure binds724 paths and preserves23 artifacts, including the replica study images. Main/release/canonical source remain unchanged. No broad qualification, adoption or external action follows.

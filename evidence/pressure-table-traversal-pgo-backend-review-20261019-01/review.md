# Experiment32 own-PGO backend gate: inlined table traversal survives

**GO only to the parent's frozen own-PGO fixed70 pilot.** Both actual pressure-color paths use the intended existing target tables after profile-use compilation. No missing mechanism or new successful-path helper was found. Activity/root code and static stack references grow, leaving a real net-cost risk. No generic benefit is transferred and no own-PGO CPU gain is predicted.

Exact own25 image `51529cebf24ad91b0cf86e4ae497bc32bb7ad7a819f8b300f8b86028326b254a` is compared to32 `d2fac478bb7ba45019421f082cca31a03b4b1516bb4a553fbacb4294e3a1a212` (7,063,960 bytes). Receipts match generic target x86-64, rustc1.85.1/LLVM19.1.7, compiler executables, all23 tools, base flags and release Cargo source/settings. Each uses its own source-specific profile:25 `dd24b72ca62b7e98466f4539e8f162e571da905e05c03333200f785e63754b08`,32 `89cd873f3b1b4f049571a28809ebb50c6885179548b819bcd95bf032959512e3`. Actual profile bytes match their build/training/independent-remerge records; both recorded54 raw profiles and byte-identical independent remerges. Source46 matches its own training record; all69 build snapshot files match receipts before/after, with only activity.rs changed between variants. The differing own-profile paths are normalized only for comparing otherwise equal build environments. No profile transfer or fresh training/remerge is performed here.

Candidate's already-closed parent stages include training130e40/session54367→f2f84c/0, independent original54/raw/remerge d0e688/0, usebb2a5a/session41833→8abf47/0 and freezef314c7/0. This static review binds their exact receipt/profile/verification/image bytes; it does not repeat raw training verification or claim a broad use-image regression passed. Build stderr contains no selected missing/stale/hash-profile warning strings.

## Actual normal pressure path

Pressure is **inlined into activity::compute in both own-PGO images**. No standalone king_pressure function was selected from either symbol table, but absence is not the mechanism proof: the actual two inlined pressure bodies and their table/board/mark operations were captured. Generic's separate helper sizes or88→120 stack reservation do not apply to this pair.

Control coordinate ray blocks12ad6–12b02 and12d09–12d35 extract file/rank, add directional offsets, bounds-check and reconstruct a target. Candidate's corresponding pressure regions select existing ATTACK_RAYS using king-square×64, then direction/length bounds and target-byte iteration. Candidate operands12a2d and1301f resolve GOTecb58 to actual ATTACK_RAYS91340. First-color length/target operations are12a87/12ab0–12ab4; second13079/130a2–130a6. Their target masks63 eliminate the former coordinate reconstruction, while table loads, pointer/length tests and occupied-square stopping remain. This is not a claim that table traversal has no checks.

Knight pressure uses KNIGHT_SOURCES92340 at candidate13177 and13694/136b3, with actual target loads1319a and136c0 followed by masks. The old knight coordinate blocks are replaced by precomputed-target/count-gated traversal. Some successful knight-pressure blocks are placed after activity's first return by PGO layout; they are **not** classified as failures merely by address placement. Existing mobility code already uses both geometric tables, so table-symbol presence alone would have been insufficient. `table-operands.json` and `traversal-windows.json` distinguish the actual pressure sites from those earlier mobility sites.

Both color ray-pressure expansions retain the old software count arithmetic: candidate four IMULs12afa/12b0c/12b1d/12b2c and four130f7/13106/13117/13126. Whole compute IMUL count32→32. This is not experiment27 arithmetic; unchanged source mark construction excludes31 as well. No extra arithmetic variant is inferred.

|Actual own-PGO body|Bytes25→32|Entry rsp reservation25→32|Static stack-reference instructions25→32|
|---|---:|---:|---:|
|activity::compute (includes both pressure colors)|9064→9239|536→536|263→271|
|Q visit_q_impl|19329→19329|1480→1480|669→669|
|ordinary visit_ordinary_impl|27891→27891|1320→1320|1017→1017|
|full_impl|4936→4936|376→376|165→165|
|rook2::run|25873→25903|0x13000 probe+0x608→same|1228→1242|

Each entry additionally saves six registers. These are actual entry reservations and static textual memory references, not dynamic spill/copy/traffic counts, recursive peak stack or ABI/layout proof. Activity static instructions2118→2156 (+38); root4639→4640 (+1). Root source is unchanged; its small own-profile code/register differences are observed without attributing all of them to pressure. Q/ordinary/full instruction and call-site counts match in this scope, not a whole-body/data equivalence proof. ELF.text534107→534363 (+256),.rodata319768→319712 (−56); section changes alone do not predict instruction-cache or memory cost.

All activity call sites resolve to cold failure owners: slice_end_index_len_fail8→9, panic_bounds_check5→8, panic_fmt1→1 (total14→18). No successful pressure helper call was added. Actual full call25 36cda/32 36dba resolves GOTece60 to shared activity::compute115a0. No supplemental NoHost/layout probe was built and no arbitrary identical-demangle instance was selected. All actual matching ordinary-image scopes are retained in capture.json.

Gate judgment: coordinate work is actually removed inside the normal inlined pressure path, with retained table/check cost, +175-byte activity growth/+8 static stack references, and small root code/register differences. The frozen own70 against51529 must decide net CPU cost independently of generic. Native179 already passed separately; use54/eight-wire/full117/pre-gate remain deferred unless the own-PGO pilot advances and parent authorizes them.

Static capture actual6facd5/0 covers17 nm/objdump/size/version children, all actual exit0; offline relocation/role resolution actual26bf7a/0. All image/receipt/source/profile/tool inputs were pinned before and rehashed unchanged after. Helpers0-5,8-13/HOME TMPDIR only. No engine/test/build/training/merge/profiler/Git/archive/source edit or advisor contact occurred; all owned jobs are terminal. Parent owns measurement/admission.

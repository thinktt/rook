# Experiment32 generic backend gate: table traversal survives

**GO only to parent's focused correctness checks and fixed70 pilot.** The actual ordinary generic image removes per-square coordinate offset/reconstruction from pressure rays and removes the unrolled knight coordinate-offset blocks. The existing geometric tables are actually consumed. This is a present mechanism, not a source-only guess; a larger pressure frame/body and new indexing checks remain material costs. No CPU benefit or neutrality is predicted.

Control25 generic is `2940ae5c003fa396b31639749b4c3ba29e52e8aebabfc96a7dde565b6d9abd04`; trial32 is `240042991de840203d342f5a0f37a25af648b621266498431a83a22cb158ffbc`,7,007,672 bytes. Parent build actual709955/session18406→13ff20/0 and freeze6e0bcc/0 bind source69 graph3c8aeee3b726aa6de3edc1c2e7dde4fcc784c44b06616753ff83992b5d802e6a. Both receipt source/tool before/after maps are stable and match their retained source-before bytes; only activity.rs differs. Compiler/rustc1.85.1/LLVM19.1.7 executables, generic x86-64 flags, build settings and tools23 match. Trial32 changes pressure traversal plus its one test; there is no31 mark expression or27 pressure arithmetic composition.

## Actual loop change

Baseline ray-step block1a91f–1a94b extracts cursor file/rank, adds direction components, joins/range-checks the result, recomposes the square and checks its board bound. Trial target block1a97e–1a98d instead checks the ray length, loads a target byte from the indexed ray and masks it with63 before the board load1a991. The caller's source square and direction select ATTACK_RAYS, including the existing direction/length checks1a8c9–1a8dd. This removes the old offset work but introduces/retains table/index/count operations; it does not remove occupancy or stopping logic.

Actual ELF relocations resolve trial operands1a823 and1a836 (GOTe1b98) to existing `rook2::geometry::ATTACK_RAYS` at86500. Ray targets load at1a987 from `[r13+r11]`; the table length is loaded1a8d3. The existing first-blocker semantics remain visible: attacker-owned occupied targets skip scoring, an occupied defender target is scored and then exits that ray. This bounded backend review is not an independent functional/domain proof.

Baseline knight blocks starting1a990 compute up to eight offset/range combinations. Trial1aa26 selects `KNIGHT_SOURCES` at87500, reads length1aa31, then uses precomputed target loads/masks (first1aa4c/1aa4f); LLVM unrolls the up-to-eight targets with count gates. Thus coordinate work is removed here too, while target table loads/count tests and occupied-target admission remain. `traversal-windows.json` and both pressure raw assembly files preserve these exact windows.

The pressure_value byte masks/software counts remain: four IMUL instructions in the admitted ray-square expansion on both sides (baseline1a8be/1a8cc/1a8dc/1a8ee;32 1a919/1a92b/1a93b/1a94a). This is not experiment27's digit arithmetic. activity::compute retains its25 mark producer, not31.

|Emitted body|Bytes25→32|Entry rsp reservation25→32|Static stack-memory-reference instructions25→32|
|---|---:|---:|---:|
|king_pressure|1384→1504|88→120|34→29|
|activity::compute|7884→7884|456→456|198→198|
|Q visit_q_impl|7224→7224|1224→1224|343→343|
|ordinary visit_ordinary_impl|8766→8766|1064→1064|529→529|
|full_impl|2415→2415|312→312|77→77|
|rook2::run|28398→28398|0x13000 probe+0x498→same|1609→1609|

These entries each save six registers in addition to the shown entry reservation. Root's probe loop remains unchanged. Static stack references are textual counts, not dynamic spills, memory traffic, peak stack or copies. Pressure static instructions367→380, despite less coordinate work on visited-target paths; code growth partly reflects changed table bounds/failure and unrolled knight paths. ELF.text487835→487947 (+112),.rodata319720→319664 (−56). Existing shared tables are reused; the small section change is not proof of better cache behavior.

Pressure call sites3→7 resolve solely to cold bounds/slice failures: panic_bounds_check2→4, slice_end_index_len_fail1→3. No successful-path helper is added. Activity's two direct pressure calls remain1a460/1a474→1a720, with activity extent/frame/static counts unchanged. Full's actual GOT activity call remains explicitly resolved in both sides (exact operands in `*-full-activity-call.json`). Scoped ordinary/Q/full/root extents, entry allocations and static instruction/call counts remain unchanged. That is not whole-body/data/ABI equivalence: all anonymous operands were not exhaustively matched. Only actual emitted ordinary-image code was inspected; no supplemental NoHost/probe build was created or inferred.

Gate conclusion: the intended coordinate→table mechanism is present on both ray and knight paths. Its added ray index/length checks,120-byte pressure reservation and +120-byte helper extent are the bounded risk. If parent proceeds, only the selected9 focused tests and predeclared70-lifetime rule can establish correctness/net cost; no timing, broad qualification, further variant or gain is inferred here.

`capture.json` retains all19 nm/objdump/size/version commands and actual exit0 results; capture actual1400db/0. Offline exact relocation/cold-role resolution actual22375e/0. Input images, receipts, all69 source snapshots and tool executables were pinned before and rehashed unchanged afterward. All helpers ran on0-5,8-13/HOME TMPDIR. No engine/test/build/profile/Git/archive/source mutation or advisor contact occurred; all owned jobs are terminal. Parent owns admission.

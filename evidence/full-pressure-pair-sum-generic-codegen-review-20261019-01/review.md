# Experiment27 generic backend gate: GO for fixed prescreen

**GO for the frozen7-case/70-lifetime generic CPU prescreen.** Parent reports native179 (177lib+2dev) passed actual32546/d70c8e→5b53c1/0 with source69 stable. Parent will check original strict replay on every one of the70 pilot lifetimes; no separate54/eight-wire run is required before this development prescreen under the latest parent decision. The intended arithmetic replacement is present in the actual pressure loop, with no observed frame growth, new hot call, or table access. This is a bounded static gate, not a speed prediction or proof of ABI neutrality. Parent owns the launch/selection rule; no follow-on stage ran here.

| Actual emitted owner | Baseline2940 | Trial59497f6d |
|---|---:|---:|
| activity::compute bytes |7,884|7,884|
| activity fixed frame / static instructions / stack-reference instructions |456 /1,907 /198|456 /1,907 /198|
| king_pressure bytes |1,384|1,324|
| pressure fixed frame / static instructions / stack-reference instructions |88 /367 /34|88 /357 /23|
| pressure IMUL instructions |4|0|
| Whole `.text` |487,835|487,771|
| Whole `.rodata` |319,720|319,584|

Frame figures are `sub rsp`, excluding six saved-register pushes (48 bytes) in both functions. Stack-reference counts include static local/argument/result/spill accesses across the whole body, not dynamic spills or memory traffic. Full/evaluator, ordinary and Q symbol sizes remain2,415/8,766/7,224 bytes; sizes alone do not establish body-wide equivalence.

Both images retain **outlined** king_pressure at0x1a720. pressure_value is inlined into that owner, not emitted as a new called function. Actual activity::compute calls pressure twice at the same0x1a460/0x1a474 sites. Activity's frame, instruction count, call inventory and stack-reference count stay the same; pressure introduces no new hot call. Its three existing cold failure-call sites remain. No NoHost or supplemental probe was built.

The reached ray block loads marks and applies the existing ray mask (baseline0x1a8a5/0x1a8aa, trial0x1a8a0/0x1a8a5). Old arithmetic/accumulation0x1a8ad–0x1a914 has25 instructions, including the two generic u8 popcount expansions and their four IMULs by0x08040201/0x11111111. Trial0x1a8a8–0x1a8db has16 instructions: shift/AND/add pairs, a bit test and carry add for the low knight bit contribution, zero-extension and scaled accumulation. The four IMULs are absent from the **entire** trial king_pressure body. `arithmetic-blocks.json` records every instruction in these two scoped blocks; this comparison is after the common load/mask and before next-square/blocker control, not an assertion about whole-function equivalence or dynamic frequency.

The original two ray classes are still admitted from the attacker inventory, with masks0xf0 and0xcc (trial mask initialization0x1a7f2/0x1a809). The ray/blocker traversal remains around the changed arithmetic; it was not replaced or made speculative. The knight neighborhood still has its separate admitted path, mask3 and final pressure subtraction/clamp. Compiler specialization of bounded arithmetic includes a low `&7` where the source says`&15`; the pairs' digit bound makes that legal. No LUT/addressed data fetch replaces the arithmetic. The136-byte rodata reduction is reported as a section measurement only; no body-wide constant-pooling equality claim is needed.

Concrete residual risk is instruction scheduling: the new byte-register shifts/adds and BT→ADC flag dependency have different latency/port behavior from multiply-based popcount expansion. Fewer instructions, no IMULs, smaller text and fewer static stack references do not determine CPU performance. The unchanged88-byte pressure frame also does not prove unchanged register lifetimes or all layout effects. This is precisely what the unchanged predeclared matched prescreen must decide. No simulated Ir percentage is converted into a CPU gain, and no second variant or retry is proposed.

Exact baseline image:`2940ae5c003fa396b31639749b4c3ba29e52e8aebabfc96a7dde565b6d9abd04`.
Trial:`59497f6d557354ed70fe24dbfcae5dd73b8974f081c7102eec7ad13102f8589e`.

Both hashes match the exact frozen build images and adjacent receipts. All69 frozen source/tool members were individually checked: only activity.rs changes (the pressure_value body plus the new exhaustive256-mark test); the other68 members, all23 tools, Cargo/lock and release profile are equal. This is not phase-sharing26 composition. Build/compiler/effective environment match: generic x86-64, rustc1.85.1/LLVM19.1.7, opt3/thin-LTO/CGU1/panic-abort/debug1, no PGO. Parent's source/formula review and new exhaustive test declaration are pinned; this backend review did not execute the test. The native179 pass above is parent-reported actual evidence, not a reviewer rerun. Trial build actual11774/df6e0b→e3fe09/0 is bound by its real tool-terminal.json.

`capture.json` records exact argv/exits/output paths for eight successful own-image nm/size/scoped objdump commands. `input-pins.json` binds both images/receipts/source-before69, parent source/preparation records and binutils; all inputs rechecked unchanged. Actual outer capture8ad264/0 was sessionless and fully terminal. Later saved-text block analysis/report closes separately. All helpers ran on0-5,8-13 with HOME TMPDIR; parent native compilation may overlap on helpers, with no timing interpretation. No engine, build, test, profiler, timing, Git or archive was run by this reviewer. All owned jobs are terminal.

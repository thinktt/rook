# Experiment31 generic backend gate: mechanism present, growth risk remains

**Cautious GO only for parent-selected focused checks and the fixed finite pilot.** This is not identical code or an absent mechanism: all11 static mark OR sites in the actual generic activity body replace category compare/set/variable-count shift with arithmetic/fixed shift. No CPU gain is predicted. The enclosing body/frame/stack-reference growth is material and remains a reason for parent to decline or for the pilot to reject the change.

Exact generic25 `2940ae5c003fa396b31639749b4c3ba29e52e8aebabfc96a7dde565b6d9abd04` is compared to31 `dcdd3c43ec95cb0202ce6258640f332eb573eecc41e8e6371c294432f68e45b9` (7,007,296 bytes). Receipts match rustc1.85.1/LLVM19.1.7, compiler executables, generic x86-64 target flags, Cargo/build settings, all23 tools and source files except activity.rs. All source69 build snapshots match before/after receipts and retained source-before bytes. This is production25 source with only the mark expression; no26–30 code or test additions. Trial build actual40462a/session49704→d51fd5/0 is recorded by parent in its real tool-terminal file. This review performs no build or engine/test execution.

## Actual mark lowering

|Kind/site|25 instructions constructing mark byte|31 instructions constructing mark byte|
|---|---|---|
|Knight|18b83 cmp;18b87 setae;18b8a mov1;18b8d shl-by-CL|18b7f shr-by1;18b82 inc|
|Bishop|19129 cmp;1912d setae;19130 mov4;19132 shl-by-CL|19137 lea double;1913a and4;1913d add4|
|Rook|19703 cmp;19707 setae;1970a mov16;1970d shl-by-CL|19785 lea×8;1978d and16;19791 add16|
|Queen, representative|19a24 cmp;19a28 setae;19a2b mov64;19a2e shl-by-CL|19aec mov;19aee fixed-shift5;19af1 and64;19af4 add64|

The corresponding OR stores remain at25 18b90/19139/19715/19a35 and31 18b85/19145/1979a/19afc; further queen sites are retained in `mark-windows.json`. Old code was already branchless: this is removal of a compare/set/CL shift dependency, **not a removed branch**. Knight's local constructor4→2 instructions, bishop/rook4→3, queen4→4. Whole compute variable-CL shifts14→3, exactly the11 mark shifts removed. Static site multiplicity and local lengths do not measure how frequently any path runs or its latency/throughput. No new mark helper call or lookup table is emitted.

|Actual emitted body|Bytes25→31|Entry rsp reservation25→31|Static stack-memory-reference instructions25→31|
|---|---:|---:|---:|
|activity::compute|7884→8260|456→472|198→220|
|king_pressure|1384→1384|88→88|34→34|
|Q visit_q_impl|7224→7224|1224→1224|343→343|
|ordinary visit_ordinary_impl|8766→8766|1064→1064|529→529|
|full_impl|2415→2415|312→312|77→77|
|rook2::run|28398→28398|0x13000 probe+0x498→same|1609→1609|

The first five entries save six registers in addition to the shown reservation; root likewise saves six before its unchanged probing loop. These are emitted entry reservations and static textual stack references, not dynamic spills, total peak call-chain stack, layout or copy traffic. Activity static instruction count1907→1932 (+25), with changed register allocation/stack operands; source-level brevity does not imply a smaller body. ELF .text487835→488219 (+384), .rodata319720→319600 (−120); no memory-traffic or cache gain is inferred.

Activity's14→18 call-site increase consists of the same two successful king_pressure calls plus cold failure sites: slice_end_index_len_fail7→9, panic_bounds_check4→6, panic_fmt1→1. Those identities are resolved from each actual ELF RELATIVE relocation and nm symbol, not assigned from anonymous GOT comments. No new normal-path helper appears. Control full call3f6f8 and trial3f878 both resolve their GOT operand e1e60 to activity::compute18850; the emitted activity path is actually consumed. `resolved-activity-calls.json` and both `*-full-activity-call.json` retain exact call operands/targets.

Scoped ordinary/Q/full/root extent/frame/count equality is not a whole-machine equivalence or ABI-neutrality proof: anonymous operands and all instructions were not exhaustively matched. Only actual ordinary-image functions were inspected; no NoHost/probe build or arbitrary demangle-order comparison is used. `capture.json` preserves19 original nm/objdump/size/version commands, actual exit0 for every child, per-function raw text and static metrics. `mark-windows.json` gives each of the11 actual store windows. `compute-instruction-diff.txt` exposes the wider register/code differences without presenting them as a normalized equivalence proof.

Gate conclusion: the intended arithmetic survives and supplies a plausible local mechanism, with a larger activity frame/body and additional static stack accesses. Only focused correctness checks and the predeclared7-case/70-lifetime CPU rule can arbitrate net cost if parent proceeds. No new variant, PGO/full117/gameplay or speed claim is authorized by this review.

All own-image tools ran on0-5,8-13/HOME TMPDIR. Capture ACTUAL9693da/0 and offline resolution ACTUAL990e41/0 completed sessionlessly; all inputs including both images, receipts, frozen sources and tools were rehashed unchanged. No engine/native test/build/profiler/Git/archive/source edit or advisor contact occurred. All owned jobs are terminal; parent owns admission.

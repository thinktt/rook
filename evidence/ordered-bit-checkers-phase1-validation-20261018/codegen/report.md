# Phase1 ordered checkers — bounded codegen review

The emitted full and capped generation bodies call one new ordered bit-query helper using a direct pointer to Position's existing planes. generate_legal shrinks from 5,445 to 5,405 bytes; legal_replies_up_to_two from 5,423 to 5,399. Both reserve 0x108 local stack bytes instead of 0x128. At the new callsites the plane pointer is Position+0x80; no mailbox reconstruction or local32-byte view copy is emitted for that call. The helper is 1,554 bytes with0x18 local reservation, reads the existing four planes, and shares the unchanged mask/chronology tables. These are static observations, not a CPU-cost estimate or whole-search frame guarantee.

| Scope | d38 control bytes / local reservation | Phase1 bytes / local reservation |
|---|---:|---:|
| generate_legal (full generation) |5,445 /0x128|5,405 /0x108|
| legal_replies_up_to_two (capped generation) |5,423 /0x128|5,399 /0x108|
| AttackBits::ordered_attackers (cap2) |absent|1,554 /0x18|
| visit_q |7,451 /0x4a8|7,343 /0x4a8|
| visit_ordinary |7,983 /0x428|7,983 /0x428|
| evaluator full_impl |2,415 /0x138|2,415 /0x138|
| AttackBits Boolean attacked |527|527|
| mailbox Boolean cap1 finder |3,781|3,781|
| Whole .text |492,411|493,819|

Q's mailbox source route is unchanged, but Q machine code is not unchanged. In control, cap2 mailbox find_attackers is a3,800-byte out-of-line function shared by generation and Q's inlined route wrapper. In phase1 the mailbox cap2 query and route-output wrapper form a3,824-byte out-of-line check_routes instead; Q calls this via GOT and retains the3,781-byte cap1 mailbox finder for own-king safety. visit_q shrinks108 bytes, retains55 static calls and its0x4a8 local reservation, but registers/spills/branch layout change through the caller. Source Q still projects one mailbox and performs the original route/safety policy. There is no projected AttackBits/Q phase2 change. Removing a shared cap2 consumer changed compiler call partitioning, so source-only scope cannot imply identical emitted Q or CPU neutrality.

Both Q full_impl calls remain out of line (phase1 addresses0x3b25a/0x3b427); visit_ordinary keeps its one full_impl call. Full evaluation and ordinary bodies keep their original instruction sequences after link-address and anonymous-data label mapping. Boolean AttackBits::attacked and the correctly role-matched cap1 mailbox finder also retain instruction sequences under that mapping. Raw bytes generally differ with relocation/layout. Full_impl's14 RIP/GOT references have matching resolved native call names and its two data descriptors/windows and pointed-to Location filename/line/column agree. The ordinary, Boolean and cap1 reference records retain their windows/decoded Locations; ordinary's changed cold descriptors mainly reflect the isolated crate path. Opaque allocation/panic aggregates and dynamic memcpy/memset bindings are not exhaustively pointer-resolved, so no general semantic equivalence claim rests solely on normalized strings.

The entire existing MASKS table (6,208 bytes), KNIGHT_SOURCES (576 bytes) and ATTACK_RAYS (4,096 bytes) are byte-identical between images, verified from exact ELF data ranges. No new attack table or persistent representation appears. The Boolean kernel's normalized instructions and exact table contents support that bounded unchanged-kernel observation; this does not imply the new ordered query is free.

A monomorph-matching caveat is material: the two control find_attackers symbols demangle identically. The generic occurrence-order comparison incorrectly pairs old cap2 with new cap1. focused-role-and-data-review.json supplies the authoritative caller-based mapping: control cap2 at0x1f7f0, cap1 at0x3b6b0; phase1 cap1 at0x3bc30, combined mailbox check_routes at0x20130. The role-matched cap1 diff is empty after the stated label mapping. Do not interpret the naive find_attackers pair/new-removed list as a semantic body comparison.

Whole .text increases1,408 bytes. Role-correct accounting is new ordered helper+1,554, combined route helper versus old cap2+24, full/capped generator reductions−40/−24, Q−108, plus2 bytes layout padding. No CPU/time/retired-instruction/cache conclusion follows from this accounting. No full/capped output-order, charge or semantic-state owner was changed by this inspection; runtime evidence here is only the separately completed143 native tests. Strict54/wire/DIAG/qualification/performance were not run.

inputs.json binds exact receipts, each43 native+23 tool-source archived snapshots and two image hashes: d38ff03745c7fba981c22f12fdd7b10b78f539f9541faeb24b92bd263b116d45 control;132ba1356b06423763b4f6328825ef93b22b91ba374bc26ff92f0ef71e0e6c81 phase1. Both are generic x86-64 opt3/thinLTO/CGU1/panic-abort/debug1, rustc1.85.1/LLVM19.1.7, no PGO; isolated crate paths differ. Tool versions/executable hashes and stdout/stderr hashes are retained (binutils2.44, Python3.13.5). Capture15 tool invocations, analyzer and focused data review all reached actual exit0 on housekeeping CPUs0-5,8-13. No native protocol engine, profiler or measurement ran in this review. Parent owns later measurement/integration decisions.

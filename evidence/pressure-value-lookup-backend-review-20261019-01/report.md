# #39 matched generic backend — NO-GO

Reject this exact image before focused/native tests or fixed70 timing. The ray lookup materializes a256B constant-array temporary and calls memcpy on every admitted visited square. This invalidates the intended cheap immutable-table access mechanism. It is not a measured CPU regression, a functional failure or a request to retune source.

Control exact37 genericf8343eda98d0114a3a8364e7ae62ee6eed3c5b55f79a6711226fd2b5b2043555; candidatee72e79f6828da8ade089892f468c24d2240b6fefd3f589b0adc2f8283a007e30 (7047088B/0555), source72 graphea300b07ce76adca2f1fbe9d07fb726e20fe356298d6507a251c0ff78323cad0. Reviewed plan/51authority pins/source snapshots/compiler/environment/flags passed before and after capture. Exactly activity.rs changed; same49native+23tools/Cargo, generic defaultx86-64/thinLTO/CGU1/noPGO. Active plan/helpers/pinned inputs were not modified.

Actual default code has activity::compute at18850,7884B in both images. Source compute calls king_pressure for both colors; the function is outlined at1a720: control1384B versus candidate1337B. Candidate full_impl41528 calls GOTe4e60, captured relocation→activity18850. Activity entry still reserves0x1c8 bytes; no unrelated ordinary/Q/root frame recapture was needed. The activity→king_pressure callsites outside selected windows remain source-bound, rather than a claim of full-body assembly review.

**Concrete ray regression.** In control, admitted ray square1a8a0–1a914 loads marks/applies mask, executes the two software-popcount sequences/four IMULs and combines weighted bits. In candidate's empty-square branch:

-1a907–1a90f loads the actual mark.
-1a914 sets length0x100;1a919 forms destination[rsp+0x88];1a921 loads source rodata85ece.
-1a928 calls GOTe4f68, which readelf identifies as memcpy@GLIBC_2.14.
-1a92e–1a939 applies the ray mask and indexes the newly copied stack array;1a941 accumulates the widened byte.

The occupied-defender branch performs its own equivalent copy at1a983–1a997 and stack lookup at1a9a4. These are mutually exclusive branches: one256B copy per selected admitted ray square, not two copies per square. Loopback1a963→1a8f0 and1a9af→1a8a0/next direction repeat this construction; it is not one initialization per king_pressure invocation. The board/mask traversal surrounds the copies, and the copied array is read before the next iteration.

king_pressure's stack reservation rises0x58→0x188, +304B (pushes unchanged); the256B temporary occupies[rsp+0x88,rsp+0x188). Additional reservation/register staging is observed, not a dynamic spill-count estimate. No assumption that libc memcpy is free/inlined, or a cycle prediction, is made. A47B smaller function is not evidence of lower physical work.

**Cheap knight path.** Old1a9d3–1a9ec loads marks then SHL/AND/test/LEA/CMOVE computes the two low-bit contributions; popcounts were already gone. Candidate1aa06–1aa19 instead loads marks, AND3, takes rodata base85ece and performs a dependent indexed byte load. It does not copy256B in this inspected knight path, but introduces a read dependency versus arithmetic. Both actual caller classes were inspected; no generic benefit is inferred from the previous PGO software-popcount study.

Candidate source-before activity.rs:429 declares const PRESSURE_VALUES; pressure_value:449–450 indexes the const by mark. Actual lowering proves an addressable temporary in the ray context; this is not a language-wide claim that all const arrays always copy. The same rodata address85ece supplies both copies and direct knight lookups. nm has no dedicated table object containing it; disassembly's nearest DESTINATION_VALUES label is not table identity/extent evidence. Exact pool extent/uniqueness remains unproved and no broad data scan was added. Source declares256 entries, while ELF .rodata grows224B net321968→322192; do not mislabel that net change as an independently verified unique256B object.

ELF .text495883→495835 (-48B); .data.rel.ro19992 and .got2712 unchanged. Full_impl2415B and activity7884B extents remain; this is no body-wide equality or layout/copy-neutrality proof. No measured cost attribution, PMU/current Ir envelope, focused2 pass or speed result exists for39. Parent accepted the provisional NO-GO; no focused tests/timing/retune/source repair is performed here.

Finite gate: discoverycfee25/0, windowsfd6399/0, analyzer17f34f/0. Four windows/four bodies20999outputB, all lengths≤0x800, far below12/131072 ceiling. All18 recorded binutils children exit0, no collector error/cap, all inputs stable. The paired pressure windows stop at+0x400 and include the decisive ray/knight sequences; remaining tails/bodies are explicitly uninspected. Partial instruction tails are not semantic findings. All binutils/analysis tools are terminal. No engine/test/build/profile/Git/Herdr/advisor/source change or further capture occurred.

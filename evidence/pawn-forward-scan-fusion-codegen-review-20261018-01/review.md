# Pawn forward-scan fusion: bounded generic backend

The actual lowering supports a later matched, reported-only CPU trial once parent accepts fresh functional closure. It removes the duplicated forward traversal and the old per-pawn raw call. The tradeoff is real: the candidates body and its local frame grow, while the separate raw body disappears. No propagated caller growth was found. This is static evidence, not a prediction of CPU gain or adoption advice without measurement.

Control is frozen complete117 generic `39cadc627f110e651410933525ee7ab28dcb7f0eb1d9dc1fe25aad1d74e6bb2e`; trial is pawn-forward-scan-fusion generic `541d324cecf14a401c868d1a7910f13efc00241d27d5ed5db100d0449f86148f`. identity.json binds both exact images/receipts and rehashes source-before46 plus tools23 on each side. Only pawn_progress.rs differs. All23 tools and all other source files match; receipts retain identical before/after maps. Compiler/cargo identities, generic x86-64 target, jobs4, effective environment/flags, PGO=none and Cargo config maps match. Same Cargo profile/retained logs establish opt3, ThinLTO, CGU1, panic=abort, debug1. No compiler/build/version process ran here.

## Lowering observed in actual default image

Control candidates at0x2a460 has a path/protected forward loop at0x2a710-0x2a759, then calls raw at0x2a80b through GOT0xa2730. Relocation resolves that call to raw0x2a0d0. Raw separately runs its backward scan and forward progress loop (forward header0x2a274, backedge progression0x2a251-0x2a26e).

Candidate candidates itself starts at0x2a0d0. Its backward scan is inlined around0x2a3e0-0x2a459; its single forward loop is0x2a4d0-0x2a5cc. The board byte is read once at0x2a535. Own influence loaded0x2a586 supplies both the protected predicate and the comparison to opponent influence at0x2a598. The path accumulator updates at0x2a4f3 and protected at0x2a4f6-0x2a4f9 in that same traversal. The next-square progression is0x2a4fc-0x2a521. Thus the intended sharing survives compilation; it is not a source-only expectation.

raw_and_path<true> is fully inlined, with no emitted helper symbol or outgoing tuple call. Raw measure, path and protected are local register/stack values; no new tuple-result ABI handoff or allocation was found. The existing Paths output still uses the original three DWORD fields and two byte fields at offsets0,4,8,c,d (control0x2aa3f-0x2aa4e; candidate0x2a8d4-0x2a8e1). This is an observed output-store shape, not a new type-layout probe.

| Emitted scope | Control | Candidate |
|---|---:|---:|
| candidates bytes | 1644 | 2342 |
| candidates stack subtraction | 0xb8 | 0xe8 |
| candidates saved-register pushes | 6 | 6 |
| separate raw bytes | 907 | absent |
| separate raw stack subtraction | 0x48 | absent |
| candidates + raw bytes | 2551 | 2342 |
| whole .text delta | — | -208 bytes |
| whole .rodata delta | — | +24 bytes |

The local candidates frame grows48 bytes, and its static rsp-reference instruction count grows77→84. Across the old candidates+raw pair those counts were77+11; neither count is a dynamic spill or load measurement. Empty candidates calls also enter the larger local frame. For a nonempty old raw call, its six additional saved-register pushes,0x48 local allocation and8-byte return address required128 extra stack bytes below the candidates frame. Removing that nested call while growing candidates by48 gives an80-byte lower structural peak at that old call site, excluding common outer frames. This arithmetic does not prove dynamic memory traffic or a cache benefit.

Candidates has7 static calls before versus11 after, but the former includes the raw call plus six failure sites; its separate raw also has six failure calls. Every new candidates call resolves to a panic/unwrap/slice-bound failure routine. There is no successful-path helper call after fusion. Counts from two old bodies must not be confused with per-pawn dynamic executions, and failure-site code is not measured CPU cost.

## Consumers and propagated effects

The current raw-only false wrapper has no emitted body in this ordinary binary. A scoped native-source search finds raw_and_path<false> only in its public raw wrapper, and no production native raw caller remains after candidates switches to true. No raw-only false consumer or supplemental probe was captured, so this review makes no backend claim about a separately compiled diagnostic/external raw invocation. Its public scalar API is preserved by source; parent owns functional validation.

Selected retains two candidates calls, at control0x2aee3/0x2b0fa and candidate0x2ae13/0x2b02a. GOT0xa2778 resolves to the matching candidates body in each exact image. Evaluator retains its selected/ending call boundary, while ordinary/Q retain their full-evaluator and recursive transfers. The offline resolver checks static call offsets and actual named relocation targets, allowing GOT addresses to move when raw is removed; it does not equate same-looking GOT comments with same callees.

| Unchanged production body | Bytes both | Main stack subtraction both | Static calls both |
|---|---:|---:|---:|
| selected | 1691 | 0x68 | 7 |
| full evaluator | 2415 | 0x138 | 12 |
| ordinary | 8880 | 0x438 | 74 |
| Q | 7584 | 0x4a8 | 56 |

Pawn-ending also retains482 bytes and the same call boundaries. The default WireHost Search<false> production ownership is unchanged; no alternate Host/layout/ABI probe was built. Register/stack live ranges change within candidates, and its larger body/frame may cost instruction residency or spills despite removing a call and repeated reads. There is no new maintained state or source field in this one-file trial. The scoped caller observations do not constitute full operand/whole-function equivalence. Separate own-PGO lowering, if ever selected, would require its own evidence.

The concrete basis for a trial is the verified single forward traversal and removed successful-path call, balanced against the observed local growth. The gain/loss remains unknown; any later matched result must retain adverse outcomes. No engine test, CPU run or profiler was launched by this review. Parent reported native178 passed; strict54/eightwire validation was still running when this task was assigned, so this memo does not independently certify its eventual outcome.

## Actual closure

All shell/helper and static-tool processes used0-5,8-13; helper launches used HOME TMPDIR. Source diff b7b86b/1 is expected. Actual identity/nm/readelf capture436f6f/0 ran8 static children; body capture45ccf0/0 ran13 objdump children; saved-text analysis77f9ea/0 and call/section reconciliation a1fb97/0 completed. All were fast actual completions without session IDs. No engines, builds, probes, profilers, timing or Git ran. Parent untimed validation/DIAG work could overlap on housekeeping; no absolute idle claim is made. Root, source and other evidence remain unchanged. Final output manifest terminal is reported separately; all owned processes are closed.

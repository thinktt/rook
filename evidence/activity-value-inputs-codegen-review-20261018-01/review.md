# Activity destination-value backend review

The emitted generic candidate warrants a matched, reported-only CPU trial after parent clearance. Its intended coordinate-to-view lowering is present in the actual production image, with no observed frame or call-count regression. This is a static engineering judgment, not evidence of a CPU gain, cache effect or performance qualification. Parent reports native178 and strict54/eightwire24 now passed on this exact candidate; this review ran neither engines nor tests.

## Exact comparison

Control is `complete117-generic-build-20261018/rook2-exact`, SHA256 `39cadc627f110e651410933525ee7ab28dcb7f0eb1d9dc1fe25aad1d74e6bb2e`. Candidate is `activity-value-inputs-generic-build-20261018-01/rook2-exact`, SHA256 `7cf3980014506970ba8aaf885bcc1c983823307005aaae7efc5d0fdc7a43cd16`. `identity.json` rehashes both images, receipts and both complete frozen source-before snapshots. Actual snapshot count is 46 native/manifest files (44 Rust plus Cargo.toml/lock) and 23 tool files on each side, rather than 45. The sole changed file is activity.rs, control `07d1b062f5ce6a4ffb66bd57eb3570f9221f42d7105b1df1f11e3039caf93c38` to candidate `3a70e076efdd5744940d472810612965fc05412befd44de45f4ff3ca78f29740`; all other native and all tools match. Both receipts retain equal before/after source identities.

Receipts match compiler/cargo executable hashes and version output, generic x86-64 target/flags, effective build environment, PGO=none, jobs4 and empty Cargo configs. Rustc is 1.85.1/LLVM19.1.7. Both source Cargo profiles and retained verbose rustc commands establish opt3, ThinLTO, CGU1, panic=abort, debuginfo1. The build-path differences are provenance, not flags. No compilation or toolchain version process was run for this review.

Primary evidence is the actual ordinary WireHost binary. Frozen bin/rook2.rs:84-85 creates Session<false>; :105-113 supplies WireHost to go_live. Its emitted run calls ordinary at control0x45950/candidate0x45720; ordinary calls full evaluator at0x3e8b8/0x3e688. Evaluator calls activity at0x40938/0x40708 through the same GOT slot0xa2e60, whose RELATIVE relocation resolves to activity::compute0x18850 in both images. Q likewise reaches this same evaluator body. These transfers are captured in the saved assembly/relocations and `operand-verification.json`. The evaluator argument setup, destination return storage and frame are unchanged at that seam.

Only one emitted ordinary, Q, charge, full-evaluator and ordering body was found per image. The inspected root path binds them to actual WireHost use. No separately identifiable NoHost recursive body was present in the symbol captures, and no supplemental probe was built. This report makes no NoHost-specific lowering or layout/ABI claim.

## Observed lowering

| Actual scope | Control | Candidate | Observation |
|---|---:|---:|---|
| activity::compute bytes | 8975 | 8412 | -563 |
| whole .text bytes | 492507 | 491947 | -560, including alignment effects |
| whole .rodata bytes | 58784 | 58968 | +184 |
| activity stack subtraction | 0x1c8 | 0x1c8 | same six saved-register pushes |
| static decoded instruction lines in activity | 2125 | 1991 | not dynamic retired instructions |
| static conditional-jump sites in activity | 193 | 188 | not branch executions/mispredictions |
| static call sites in activity | 14 | 14 | two king-pressure calls plus failure paths; no view-helper call |
| static activity instruction lines referencing rsp | 220 | 208 | not a dynamic spill/load count |

Candidate emits one named 256-byte immutable DESTINATION_VALUES payload at0x84cf5. `verify-operands.py` reads the actual ELF bytes, verifies the entire physical-square/color/variant payload against the baseline matrix/rook-row construction, and finds exactly one full256-byte occurrence. Its four64-byte rows replace the original matrix64 plus rook-row8, matching net184-byte rodata growth. No runtime table construction, copy or allocation appears: candidate compute0x18a47-0x18a56 selects `table + color*128` with RIP-relative lea, shift7 and one saved pointer. The table has no imposed alignment in source; its actual address is not evidence of any particular hardware cache behavior.

For a representative knight destination, control0x18b7f-0x18bb2 computes rank, reflected rank/color select, file and two-dimensional address before load/multiply. Candidate0x18b88-0x18b92 loads the selected view pointer, loads one byte by physical target, then performs the original i64 multiply. Rank/file work remains elsewhere where independently needed (for example LOW_MOBILITY); it has not disappeared from the whole function.

For rooks, opposing-king relative rank/file is still examined before traversal. Candidate0x194b1-0x194e5 obtains the king condition;0x1952f-0x1957d selects the per-piece variant by shift6 and adds the saved color-view pointer. The selected pointer is in rbp during the ray loop: for example0x1978c loads the physical destination value, followed by the category multiplication and unchanged vertical weighting. The destination loop no longer selects ordinary versus seventh-row value by target relative rank at each square. The gate still has per-piece control/pointer work; the review does not assume it is free or hoisted out of every source-piece loop. Bishop/queen/knight helper calls have compiled away; nm contains only compute, king_pressure and the static table under activity.

## Propagation and unresolved costs

| Emitted production body | Bytes both | Main stack subtraction both |
|---|---:|---:|
| ordinary | 8880 | 0x438 |
| Q | 7584 | 0x4a8 |
| full evaluator | 2415 | 0x138 |
| IIO ordering | 2494 | 0x1f8 |
| charge/poll | 1209 | 0x128 |
| root run | 28398 | 0x13498 total probe allocation |
| king pressure | 1384 | 0x58 |

All retain the same static instruction, conditional-jump, call-site and rsp-reference counts in `bounded-analysis.json`. The saved signatures deliberately retain RIP referent names: they differ because anonymous constants/descriptors and jump tables receive different linker names/addresses. They are not whole-function equality proofs. The bounded operand audit verifies actual ordinary SIMD8/16-byte constants, all entries of three relevant Q dispatch tables and the charged-host command dispatch table; their targets, normalized to their own unchanged bodies, match. Evaluator-to-activity GOT transfer is independently resolved on both sides. Unrelated panic/format descriptors were not exhaustively reconciled; no equality or semantic pass is inferred from hiding those operands.

Within these observed scopes, no additional caller frame, activity/helper call, register-to-stack Result relay, state-copy operation or recursive function growth was found. This is not a measured count of copied bytes and does not establish spill neutrality on every executed path. Activity register allocation changes inside its unchanged frame; the selected pointer introduces an extra dependency/load and per-color/per-rook setup. Immutable data grows and other rodata addresses move. Instruction/data placement and branch alignment can alter CPU outcomes even though the central body is smaller. Own-PGO lowering could also differ from this non-PGO generic result; no generic-to-PGO result is transferred.

The positive static result is narrow: the actual default binary realizes physical indexing and per-piece rook-view selection without a new out-of-line helper, expanded frame or propagated hot-body size. Together with parent-reported functional pass, that is sufficient reason to spend a bounded matched CPU pilot, preserving both higher and lower outcomes. It is insufficient for adoption or a predicted gain. No performance run is authorized or launched by this review.

## Execution/provenance limits

All helper and nm/readelf/objdump child processes were pinned0-5,8-13, with HOME TMPDIR on helper launches. Own images only were inspected; no opaque implementation, engine execution, build, profiler, timing or Git was used. Initial optional source-path lookup returned79d865/2 because a guessed proposal directory did not exist; the correct parent-supplied frozen build/source snapshots were then used. It was a read-only lookup failure, not a build/runtime failure. Source diff bb9ff7/1 is the expected diff status.

Actual capture terminals: identity/nm/readelf c218ca/0 (8 children), function objdump6da103/0 (16 children), offline analysis659729/0, operand verification3c1b79/0. All were fast completions without a session; no IDs were fabricated. Final packaging/manifest helper terminal is reported separately. No owned native jobs or other processes remain live.

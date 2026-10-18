# Fullfresh81 ordinary codegen — bounded cold review, 2026-10-18

From: native child fresh_pawn_transport. To: parent imp2. Normal requested; actual speed readback/control unavailable. Review ownership is exclusively this new evidence directory. No root/proposal/receipt edits, build, test, compiler invocation, engine execution or profiler use occurred. Commands and helper descendants ran on affinity 0-5,8-13. No retained82 proposal was inspected.

The ordinary no-op observation path erases successfully in these frozen images: the sole emitted evaluator full_impl and the recursive ordinary function have exactly identical machine bytes, addresses and sizes. No added FullDetails copying/storage, observer callback, call argument, or stack-frame growth appears in that ordinary full-evaluation implementation. The inlined fast path in visit_ordinary is also covered by its exact equality. Quiescence has the same normalized instructions and only three table-base displacement changes. This is a static result for these artifacts, not a CPU neutrality or performance qualification claim.

## Artifact and input identities

| Artifact | Frozen binary SHA256 | File bytes |
| --- | --- | ---: |
| root79 | `9709f8e904326642a0fd8de162e7853b5a53aa78cc704cd0d78293d3e557a4ce` | 6737968 |
| fullfresh81 | `fd3acfa151636a4888799ab89bac3b1aee6a164b1f4a9b970e4d69dadad8d5d9` | 6738776 |

Input paths are `../production-eval-observers-build-20261018/{rook2-exact,receipt.json,source-before/}` and `../full-fresh-build-20261018/{rook2-exact,receipt.json,source-before/}`. `inputs.json` records absolute paths, receipt hashes, all source/tool-source hashes and recorded settings. All 43 manifest/lock/native-source hashes plus 23 tool-source hashes in each archived receipt snapshot were verified (66 files each), and rechecked before this report. The only differing native input is `src/evaluator.rs`: root79 `68e44e7a7af1349934423679f4717c281fc437c050ee0ccb93f66b808296535e`, fullfresh81 `a454071a803b39bd651bc2c4e852db1b4b74b871db273175c2b7e9f12e87516c`. The exact source diff is `source-diff.txt`.

Both receipts record generic x86-64 / x86_64-unknown-linux-gnu, rustc 1.85.1 with LLVM 19.1.7, release opt-level 3, thin LTO, codegen-units 1, panic abort, debug 1 and no PGO. These are receipt observations; rustc/cargo were not invoked during this review. The build directories differ: canonical `/home/legolas/rook2` versus `/tmp/imp2-full-fresh-proposal-20261018-92x348cj`. Absolute canonical versus temporary source paths are present in .rodata and affect the binary identity/layout.

## Focused machine-code comparison

| Function | Start | Bytes in each | Exact bytes equal | Normalized equal |
| --- | --- | ---: | --- | --- |
| `rook2::evaluator::Evaluator<_>::full_impl` | `0x40600` | 2415 | True | True |
| `rook2::evaluator::Node::child` | `0x1d450` | 937 | False | True |
| `rook2::evaluator::Parameters::bind` | `0x1d800` | 1335 | False | True |
| `rook2::ordinary::<impl rook2::engine::Search<_,H>>::ordering_phase` | `0x3d9f0` | 2494 | True | True |
| `rook2::ordinary::<impl rook2::engine::Search<_,H>>::store_ordinary` | `0x3e3b0` | 94 | True | True |
| `rook2::ordinary::<impl rook2::engine::Search<_,H>>::visit_ordinary` | `0x3e410` | 7983 | True | True |
| `rook2::quiescence::<impl rook2::engine::Search<_,H>>::visit_q` | `0x39400` | 7450 | False | True |

`full_impl` spans 0x40600..0x40f6f (exclusive), 2,415 bytes, SHA256 `f68b4e65aca8c4536ab2c0948de152225c6edd65b54b61140e2edf45de9ec1d7` in both. Its prologue reserves the same 0x138-byte local frame after six saved registers. Its result stores, retained-state writes and complete native-kernel call sequence are unchanged. `visit_ordinary` spans 0x3e410..0x4033f, 7,983 bytes, SHA256 `98f5580cb0bfe80611896c3030a9c9d86ade0ca25460326cb3d5b285fbf0d0a2` in both. Function-byte slicing uses the .text section file offset and nm size; raw byte identity does not depend on normalization.

Ordinary initialization/recursion calls the same sole emitted full_impl at 0x40600 from run 0x44b35, visit_ordinary 0x3eb16, and visit_q 0x3acdb / 0x3aea4. `root79-evaluator-calls.json` and `fullfresh81-evaluator-calls.json` list these and resolve full_impl native indirect calls from GOT file contents. The full_impl calls include native material, fresh_with_order on its miss branch, pawn compute, activity, shelter, selected progress, central/patterns, square balance and endgame adjust. No observer callback is introduced. The finish body is inlined: there is no emitted evaluator finish/finish_observed or endgame finish symbol, and the unchanged full_impl has the same single endgame-adjust callsite.

`visit_q` has exactly three changed instruction operands, all RIP-relative lea table bases: at 0x3a30a (0x8b908 -> 0x8b8c8), 0x3a3cf (0x8b940 -> 0x8b900), and 0x3a615 (0x8b928 -> 0x8b8e8). The focused diff is `visit_q-assembly.diff`. `quiescence-table-windows.json` decodes eight signed 32-bit relative words in a 32-byte window at each old/new base; all corresponding resulting code targets match. A window is evidence around a base, not a claim that every table has eight valid entries. The instructions, registers, local offsets, branches and native full_impl calls are otherwise unchanged.

Across the complete native image, all 829 matched t/T function symbols retain addresses and sizes, 622 have exact bytes, and 781 have equal normalized disassembly. These are inventory counts, not a complete semantic equivalence proof. Names normalize numeric LLVM module suffixes and retain occurrence indices for repeated demangled names. Instruction normalization strips displayed instruction addresses/comments, replaces annotated RIP displacements with canonical symbol+offset, and replaces displayed direct branch addresses with canonical targets. It retains register operands, immediates, non-RIP offsets, ordering and symbolic target offsets. Data-referent equality is not inferred from normalization; the quiescence target windows were checked separately. 48 functions remain unequal by that conservative normalization. Their complete differences were not exhaustively classified in this bounded review.

## Observer and FullDetails reachability

Frozen source has capture-free no-op Components/FullDetails arguments in ordinary full(), and capture-free finish no-op in fast(). The internal relay passed to finish_observed captures components/base/details at source level; it is not itself assumed to be zero-sized. The unchanged emitted full_impl provides the evidence that this relay and FullDetails construction/copy are removed for the ordinary instantiation. There is no added field in Node, Retained or Evaluator, and no FullDetails type stored there.

No standalone FullDetails, fresh_detailed_observed, full_observed, fresh_observed, observer, fast, finish or finish_observed evaluator symbol is emitted in either ordinary image. Symbol absence alone would not prove erasure because inlining can hide work; here it is backed by exact full_impl/visit_ordinary byte equality and normalized visit_q equality. The ordinary full_impl identity is inferred from its actual ordinary/init callsites, not solely from demangled `_` generic placeholders. Fast and select_noncheck have no separate emitted symbol and are reviewed within their ordinary/quiescence callers; this does not establish codegen for every generic instantiation or the separate diagnostic binary.

Native source still has one shared endgame::finish call in finish_observed. The detailed route observes that result; it does not add a second native finishing formula. The ordinary byte comparison confirms the refactor did not add finishing work to its emitted full_impl. `observer-source-references.json` records all frozen native references, including cfg(test) references that are not runtime ordinary calls.

## Layout, limits and reproducibility

Both .text sections are 492,411 bytes at 0x9050. Their hashes differ: root79 `f1f0dea58093903e107fd0d901b545d4fd8016c3076d524b5511d8813dbee6a1`, fullfresh81 `ccae273ff7eddf5de7b73c820a3bc79bbc25f00c182d57e8c9671085c589be37`; 1,422 corresponding byte positions differ. Thus equal text size is not used as evidence of identical whole-image instructions. .rodata grows from 57,936 to 58,184 bytes (+248); debug and relocation/data sections differ. The whole files differ by +808 bytes. Source/build paths, panic location data, anonymous symbol naming, data placement, LTO/monomorph decisions and code/data layout limit transfer of this finding to a canonical-path rebuild, another toolchain, PGO, another observer or another const/generic combination. Indirect targets were read from the frozen ELF GOT contents; this is not an exhaustive dynamic-loader/call-graph proof.

No CPU/cycle/retired-instruction/cache neutrality is claimed from source, byte equality of selected functions, normalized disassembly, equal addresses, or text size. Data movement/layout and the complete execution environment still matter. Parent owns execution checks, integration and any later measurement.

Inspection tools are GNU binutils 2.44 (nm, size, objdump, readelf) and Python 3.13.5. Version outputs are retained, executable paths/hashes are in `analysis-summary.json`, and static tool argv/exit codes/stdout/stderr hashes are in `commands.json`. `capture.py` reproduces the static capture/input verification; `analyze.py` reproduces matched function/normalization and quiescence-window analysis from captured outputs. Full raw nm/disassembly/section/size outputs, per-section hashes, focused diffs and all source/binary hashes are retained here. `output-sha256.json` inventories the final evidence outputs (excluding itself).

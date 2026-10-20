# Experiment43 generic mechanism gate

**Mechanism PASS; GO only to the parent's11 focused controls, then a fixed generic70 decision if they pass.** Per-source EXPANSION emission is replaced by inlined wrapping carry chains and one final transpose per slider-bearing color. The intended change is emitted, with explained counter-memory and fixed-transpose costs. This is not a semantic pass, speed prediction, PGO authority or adoption decision.

Control40 generic: adbf66a39b710bc0f44db2ceb99cac7b823fc02962e4c23a2d6ec12dfa92d664. Candidate43 generic: ea057f6a4a0c57ddc3ed35667d01363c7f2fc68d2de1d2fa745d2ba16f6e4a23,7046816 B. Candidate source72 graph is e89dcb3315e4d8aaa5089ec445d0a7d0bda7f0928001c502c6343899a5195aa5. Receipt/source-before/freeze and actual build terminal8c4328/0 are bound. Exactly attacks.rs/coherent.rs/coherent_tests.rs differ; the other46 native members and all23 tools match. Runtime permission, public scalar builder, evaluator/search callers and numerical consumers remain source-identical. Both receipts/compiler-file hashes and verbose builds agree on rustc1.85.1/LLVM19.1.7, generic x86-64, O3/thin LTO/one CGU and effective environment; neither image is PGO.

| Actual complete producer / ELF | Baseline40 | Candidate43 |
| --- | ---: | ---: |
| build_coherent at1ff00 |5485 B|5789 B (+304)|
| Local stack reservation, plus six unchanged GPR pushes |0x198 (408 B)|0x1c8 (456 B), +48 B|
| Whole .text |495739 B|496043 B (+304)|
| Whole .rodata |322192 B|320168 B (-2024)|
| Whole .data.rel.ro |19992 B|20064 B (+72)|
| Complete-body outgoing calls |8 cold length/bounds panics|9 cold length/bounds panics|

There are no outlined BitSums/carry/transpose hot helpers and no normal helper/memcpy call in either complete producer. The actual candidate calls214ef–21597 resolve through GOT e3cf0/e3ee0 to slice-length/bounds panics. `candidate-analysis.json` retains each call address, actual relocation target and resolved symbol, not demangled-name pairing alone.

The old four live XMM byte sums/per-source table expansion are gone on the active candidate path. The candidate symbol inventory contains no named EXPANSION, and the complete producer has no per-source EXPANSION access or paddb. All old production table/add code is cfg(test)-only in the frozen source. This scoped finding does not assert the absence of every coincidental byte pattern elsewhere in the ELF. Old source masks and existing MASKS remain; nonzero-slider P/N/K now consume the existing target masks and enter the same wrapping bit counters.

Eight counters are **not all register-resident**. Active pawn/knight chains20313–20392 use GPR XOR/AND carry propagation. King20738–2077c propagates through eight bits and ends with a read/modify/write of the top plane at[rsp+0x50]. Bishop normal commit20895–208b0 similarly updates the top plane in memory. Low-plane state loads from[rsp+0x28]/[rsp+0x10] on weak paths20b18–20b31; Q carry uses additional stack-held planes around21060 onward. `candidate-analysis.json` preserves27 static memory-instruction anchors mapped into BitSums add/add_slider debug context. These are actual memory operations, not27 dynamic spills per source, and their stack slots can have different roles across paths. Some weak handling is predicated (Q21031–21042 XOR/AND/CMOVE), so source weak==0 does not imply all such work disappears physically.

Final conversion is paid. Region20040–20217 (471 B of machine-code extent including reloads/store setup) reloads live counter state, performs the mask/shift/XOR swaps, then moves eight words into XMMs and uses baseline SSE2 unpack stages20187–2020d to write one64-byte color profile. There is no per-target scalar output loop or new table in this region. Carry dependency chains, memory traffic, the fixed transpose and +48 B frame can lose on small slider inventory; smaller rodata does not predict cache or CPU improvement.

The **real** no-slider branch202c7→203b0 selects old scalar pawn/knight/king targets/scatters and reaches the next-color/exit path20217 without counter accumulation or transpose. It still pays the function's larger frame, unconditional128-byte result zeroing and the same common borrowed-plane decode hoisted before color admission (1ff7c–2001a). No no-overhead claim is made. At21467–214cb, the temporary result still feeds eight16-byte loads/stores to the return pointer: the baseline128-byte output transfer survives. Register/counter reuse is a different cost from this result transport.

The new mnemonic set is movabs and punpckhdq/hwd/lbw/ldq/lwd, all ordinary x86-64/SSE2 operations. No added target feature or AVX/other ISA expansion appears in the captured producer. Numerical bit order, carries, multiplicity, leaper masks and public/supplied-map bypass remain obligations of the parent's source proof and pending focused controls. Source-identical caller/permission ownership is bound; no whole recursive/caller body or other generic instantiation was dumped or declared equivalent.

Candidate capture9c8afd/0 ran10 actual binutils children, all0, one complete5789 B symbol with104897 B raw/source-mapped disassembly. Combined with frozen baseline103766 B, this remains bounded. Offline comparison2167b1/0 reconciles the emitted facts and all before/after pins. No failure, compiler, test, native workload, timing, profile, annotation, Git or source mutation occurred here. Baseline files retain their original hashes; all owned static tools are terminal. Root owns focused execution and any later trial under the unchanged rule.

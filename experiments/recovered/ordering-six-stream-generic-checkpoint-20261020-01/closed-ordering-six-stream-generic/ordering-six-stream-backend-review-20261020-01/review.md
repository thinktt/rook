#54 six-stream generic backend review

**Selected mechanism is present on actual normal ordinary and Q routes.** No scope expansion or new capture is needed. This supports parent focused/screen consideration, not CPU benefit or adoption. Exact generic51 control460cbf5b… and54candidateceed19e2… are bound by the closed prep; candidate source75graphd8e4c072…. Discovery8927b8/0,11complete-bodycapturebd9fe8/0 and analysis8d68e8/0 recorded166unchanged inputs and552,084raw bytes inside their original180second capture window. This review reads cold text/source only; no ELF, tool, engine or clock renewal.

## Actual route and copy change

Ordinary control411e3 directly calls42ac0 `order_by`; candidate415a3 directly calls42e80. Control sorting call42c21/GOTe49b8 resolves38140 `priority_sequence`, followed by preferred-copy memcpy42c33. Candidate42fe4/GOTe5c60 resolves38330 `preferred_into`. The candidate supplies all three slice pointer/length pairs (rdi/rsi moves,n;rdx/rcx keys,n;r8/r9 output,n), so the new six-argument helper is a real ABI/call cost.

Q control3cd98/GOTe4fe0 resolves38330 `order_with_scratch`; candidate3d158/GOTe5fe0 resolves38700. Its control386a4/GOTe49b8 reaches the public sorter then386b4 preferred memcpy; candidate38a64/GOTe5c60 reaches the same new preferred helper38330. Relocation targets and actual sized symbols establish these roles, not names alone. Original callback/partition is source-byte-equal under the frozen proof; the ordinary callback still targets ordinary_policy::priority. Deferred tail copies remain: candidate order0 at38aa0 and order1 at43025. No blanket memcpy-removal claim.

## Complete preferred helper

Entry38330 is967B. It saves six registers and reserves0x38 **before** comparing n with7 at3834a. n<=6 falls through38356/GOTe59b0 to unchanged public sorter38140; output-length check3835c remains, then3837f tail-jumps memcpy after restoring the helper frame. Head cells are not initialized on this path, but the call/frame/prologue cost is paid. Do not call it a physical zero-setup path.

n>6 jumps38385. The old gap6 insertion survives at383a0–38434: predecessor index subtract6 at383c0, unsigned priority comparison383d1/383d4 stops on equal-or-greater; Move16 shifts383ed and priority32 shifts383f2, placements3841c/3842a. This is required retained work, not eliminated sorting traffic.

After gap6, six heads are materialized in stack cells[rsp+8]..[rsp+30],38446–384d2. The first head folds rank+1 as `(key<<9)+0x200`; later heads fold it as OR0x1ff,0x1fe,…0x1fb. These are exact rank+1 values, including full-u32 extrema and the exhausted-zero distinction. No new table or extra state is involved.

The selector384e0–385d7 reads all six head cells each emission and performs five unsigned comparisons, using SETA/CMOVA and two JAs while tracking winning streamr9. 38579/3857c subtract1 and mask low9bits; XOR0x1ff at38586 decodes511−low. The32bit DEC is sufficient because only low9bits are used. Source Move bounds check3858d remains;3859b directly stores one u16 into output[r15+byteoffset]. `0x205-low`385a0/385a5 is index+6. If it is beyond n,38500 zeros the winning head; otherwise a priority bounds check385b1, one key load, shift/or/INC385bd–385c8 reconstruct rank+1 and385cb updates the winner cell. The output iterator advances2bytes and repeats, then385dd returns.

There is no gap1 insertion shift loop or final preferred gather on the large path. Its only Move writes after retained gap6 are direct output writes; no normal callee is invoked during merge. Public `priority_sequence` retains both old passes for its public API and small path. Its source and481B extent are unchanged; linked machine hashes differ, so full linked-byte equality is not claimed.

## Emitted cost and decision limits

Ordinary stays8670B/reservation0x428; Q stays7321B/reservations0x4c8 plus existing0x8 path. Their decoded counts stay1731/1566. Q ordering helper1222→1211B and main order_by584→566B retain0x78/0x48 reservations. The new preferred helper is967B/0x38 with six register saves and226decoded instructions. Whole .text grows944B; .rodata size is unchanged but relocates; .data.rel.ro grows240B. This is static cost, not dynamic traffic or a savings denominator.

Important costs are the always-paid new helper frame, stack-resident six-head reads/winner write per emission, selector comparisons, rank arithmetic, remaining gap6 two-stream shifts, and bounds checks/cold failure paths. Equal-length debug assertions have not made all three slice bounds disappear: head construction checks priority lengths, source/next accesses check bounds, and small copying checks lengths. The short path adds a helper layer before the old sorter. No allocation, persistent field, SIMD/tournament or expanded ISA appears; the new normal arithmetic is baseline x86-64 scalar operations. No claim that every stack reference is an avoidable spill, or that pointer/Move traffic is unchanged.

This is the frozen distinct algorithmic replacement, not49's bounds-only trial or a post-result rescue. List-length/inversion distribution, branch prediction and generic/own-PGO economics remain unknown. Source induction/parity and actual parent focused results govern correctness; fixed measurement alone can price this tradeoff. Only the captured generic ordinary/Q monomorphs are claimed; no observed/public diagnostic or PGO clone coverage is invented. No source/prep/private evidence was mutated.

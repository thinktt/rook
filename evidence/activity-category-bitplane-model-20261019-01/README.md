# Offline64-lane relation/category feasibility model

**PASS, first execution, mathematical feasibility only.** No native candidate, geometry/mobility integration, storage choice or speed prediction is established. No runtime fixture/RELATIONS table was read. Only this new evidence directory was written.

`model.py` contains the candidate mask algebra; every input byte is represented as eight u64-like Python masks, one bit per independent lane. Its loops range over a fixed number of bits, radix digits, tiers or victim kinds, never lanes. It has no scalar relation classifier, byte lookup table, per-lane gather or hidden reference call. `verify.py` alone contains scalar transposition/unpacking, independent explicit-digit reference and finite test enumeration. A future native input transpose and consumer conversion are unresolved costs; the scalar test transpose is not a proposed production implementation.

## Algebra

- Decode normalized counts from bitplanes: weak bit0, queen bit1, rook bits2/3, minor bits4/5 and pawn bits6/7. Add the five digit values with four4-bit ripple adders; raw sum0..11 fits4 bits. `raw[2] | raw[3]` means sum>=4. Set capped count bits to `(raw0 & ~high, raw1 & ~high, high)`, representing0..4 exactly.
- Derive nonzero and mutually exclusive least-tier masks in priority order pawn1, minor3, rook5, queen9, weak99. At each step remove all lanes with a cheaper already-present tier.
- Subtract packed contribution2/4/16 by starting a borrow at bit1/2/4, propagating `out=x XOR borrow`, `borrow=borrow AND NOT x` through higher byte bits. Final borrow marks underflow; clear **all eight** resulting bits in those lanes. This preserves lower digits when borrowing succeeds and clears them too when saturation occurs. It is not removal of an uncapped physical attacker.
- Compare opponent/own three-bit capped multiplicities lexicographically from high to low. Form v>t and v>t+u as unions/intersections of fixed tier masks. Favorable is `aZero OR (dNonzero AND vGreaterT AND (a<=d OR vGreaterTPlusU))`; contested is `aNonzero AND dNonzero AND vEqualT AND a<=d`. They are disjoint and directly form category bit1/bit0. Their complement is category0.
- Decode victim kind masks from its low3 bits and nonempty test across all8 bits. Apply minor capture categories2/3 and rook categories2/3 by clearing/replacing the two result planes; queen has no such capture priority. Direct shortcuts set category2 for the exact native opponent-zero/empty/queen conditions. Moving color only selects occupancy admission here: empty or opposing occupant. Supplied own/opponent bytes already belong to the selected side.

The reference does repeated divmod by radices2,2,4,4,4, explicit category borrowing and the normative ordered scalar clauses. It does not subtract the scalar packed byte for its exclusion reference and does not use the candidate Boolean expression as its scalar classifier. This separation checks the borrow/cap/tier algebra rather than comparing a generator with itself.

## Finite controls actually executed

| Check | Coverage |
|---|---:|
|Capped multiplicity and least tier|all256 input bytes|
|Exact packed subtraction result versus explicit radix borrow|all256 bytes ×3 contributions =768|
|Relation mask versus independent scalar|all256×256 pairs ×4 tested tiers ×4 subtraction modes ×2 lane layouts =2,097,152 lane comparisons|
|Integrated direct categories|every byte pair ×N/B/R/Q ×2 layouts =524,288 comparisons, with varying canonical victim codes across lanes|
|Pure capture priority|all193 valid raw victim bytes ×2 mover colors ×4 base categories ×2 opponent-zero states ×4 kinds =12,352 comparisons|
|Direct shortcuts plus priority|same12,352 factored comparisons|
|Occupancy admission|3,088 cases|
|N/B direct equality, consistent reference states|1,930 exhaustive factored cases, plus every integrated full-pair batch|
|Malformed nonempty victim kind|all63 invalid raw byte encodings rejected by the model domain guard|

Layouts are the identity pair order and the bijection `(i*257+31) mod65536`; the latter varies own and opposing bytes within each64-lane pack. Exhaustiveness is over arbitrary normalized bytes, including values not arising in physical positions and normalized wrap outcomes. No raw physical count assumption restricts them.

Raw victim coverage includes canonical empty plus all bytes with low kind1..6 (including high-bit aliases), consistent with the source's low-bit kind/color decoding. Invalid nonempty kind0/7 is rejected before category evaluation. This is broader mathematical coverage, not an assertion that all such byte aliases are admitted production FEN pieces. Both colors and all four numerical categories0/1/2/3 are retained.

Direct all-byte-pair integration uses rotating canonical victim codes, not the entire byte-pair×victim Cartesian product. The independent exhaustive override product separately covers every valid raw victim byte, mover color, base category and opponent-zero flag. Together these verify the composition: the override has no other own/opponent dependency. N/B equality is asserted only on consistent direct relation states: when opponent is zero, adjusted relation is necessarily2 (independently verified above); otherwise both use the same supplied minor result. Knight/bishop shortcuts can differ physically but have the same final category. No equality is asserted for the impossible synthetic combination opponent-zero with adjusted category0/1/3.

## Cost and proof limits

The mask model establishes exact formulas, not economics. Profile features introduce a raw4-bit sum, capped3-bit count, five tier masks and nonzero mask, plus carry/equality temporaries. Each subtraction has a4/6/7-stage borrow chain and underflow clearing. Relation selection introduces comparison/greater-tier and tier-pair unions; a native compiler may fold fixed tests but this has not been compiled. Victim category processing adds type/empty/color masks and override temporaries. Inputs and intermediate planes may have significant construction, register, frame or spill costs. Python object counts/runtime are not native instruction, allocation, layout or speed evidence.

No claim follows about producing geometry masks, actual direct/additional destinations, per-piece C/T/curve/rounds, pressure presence/flush, semantic additional/source-R charge sites, public map provenance, or integrated search. In particular the earlier4.9% mapped frontend context is neither a saving bound nor a payoff for these formulas. Those obligations remain before any architecture/trial selection.

## Reproduction, identities and closure

Command actually run:

```
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/activity-category-bitplane-model-20261019-01/verify.py
```

Original stdout/stderr are retained. Actual outer initial2f26ed/session55347 → terminala5adab/exit0. It ran once and passed; no repairs or retries. Input/model/reference pins in result.json matched before/after and were rechecked during closure. `model.py` SHA7821f0c40d5968eb5fc80ba16005d573e2e7252feb1509b6271eb0e5e2bdedc9; `verify.py` SHAbb16b1d33f2e1f505fcbd1f25b644e886fa91902704c2fb686fc5130a19e0bbe. Native activity/influence/types and released activity/evaluation-relations pins are recorded there. No native/Rust/source production edits, compiler/build/engine/binutils/profiler/Git/archive/Herdr/advisor action occurred. No background work remains; all owned jobs are terminal.

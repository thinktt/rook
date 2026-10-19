# #40 generic shared-static pressure lookup — GO to focused checks and fixed70 only

The intended emitted mechanism is present in exact candidate adbf66a39b710bc0f44db2ceb99cac7b823fc02962e4c23a2d6ec12dfa92d664 against generic37 f8343eda98d0114a3a8364e7ae62ee6eed3c5b55f79a6711226fd2b5b2043555. Both complete king_pressure bodies were inspected. The candidate reads shared static storage directly; it has no memcpy, no 256-byte stack construction, and no call on the admitted normal pressure paths. Only the three existing bounds-panic tail calls remain. This supports focused semantic checks and a matched fixed70 trial, with no predicted speed or cache benefit.

The candidate has a named local read-only `rook2::activity::PRESSURE_VALUES` object at85ece, size0x100 (candidate-nm.stdout). The empty ray path masks the existing mark at1a8d5–1a8dd, obtains the table address at1a8e0, and loads its byte at1a8e7. The occupied-defender path does the corresponding mask/address/load at1a927–1a938. Backedge1a90f→1a8c0 and the direction loop1a94a→1a828 are inside the complete capture. There is no inner copy or initialization call on these loops. The control runtime-mask body at1a8b8–1a8f5 contains four software-popcount IMUL instructions; the entire candidate pressure body contains zero IMULs. Neither count is a dynamic instruction-saving estimate.

The cheap knight path remains a real cost risk. Control1a9d3–1a9ec already folds popcounts into bit shifts/masks, LEA, TEST and CMOVE. Candidate1a98a–1a99f instead masks to3, forms the table address and performs a dependent byte lookup. The remaining knight destinations use the same static object. The ray path also pays this address/load dependency; an immutable256-byte table does not establish profitability. No #39 timing result exists to transfer, and #39 is preserved separately without source repair.

| Observed emitted extent/storage | Generic37 | #40 |
|---|---:|---:|
| king_pressure body |1384B|1235B|
| king_pressure stack reservation (excluding equal register pushes) |0x58|0x48|
| activity::compute extent |7884B|7884B|
| activity entry stack reservation |0x1c8|0x1c8|
| full_impl extent |2415B|2415B|
| .text |495883B|495739B|
| .rodata |321968B|322192B|
| .data.rel.ro / .got |19992B /2712B|19992B /2712B|

The named table proves an emitted256-byte static object and the pressure references above target it; this review does not claim global absence of unnamed duplicate payloads. The rodata delta is224B, not an assertion that the sole binary change is exactly256B. Smaller extents/frame reservation are static observations, not CPU results or a complete spill/ABI analysis.

Actual candidate full_impl call414c8 targets GOTe4e60; the captured relocation resolves that slot to activity::compute18850. The activity entry is captured, and frozen activity.rs152–153 calls king_pressure for both colors. This ties the lookup to the actual evaluation owner; no arbitrary monomorph counterpart or standalone probe is used. The small full window begins mid-instruction and ends mid-instruction: its boundary fragments are ignored; the complete decoded call414c8 and its relocation are the evidence. Other recursive bodies/frames and full activity internals are uninspected.

capture.py preflight verifies same default x86-64 generic/thinLTO/CGU1 compiler, effective environment and tools23, source72 (49native+23tools), identical Cargo and activity.rs-only delta, actual successful build terminals, exact frozen image/receipt/source snapshots, and all53 required parent pins. Source graph216c8f5198088d5a1815fb01c75f9f23be7151dad779da409266ba60ac9907b1 and freeze835c19c90fde2c66e1e7a43d7b847a89d722e82264ce278d103c705997ec8875 are bound by the activated plan. The final offline closure rechecked every discovery input pin; all remain unchanged.

Actual sessionless outer terminals: discovery3f5162/0, finite windows4ed8f8/0, analyzer593d1d/0. All18 binutils children exited0. Four windows in four named bodies total28071 output bytes, under12/131072/0x800 caps; both pressure windows cover their exact complete symbols. No failure or cap, no engine/test/compiler/profile/timing/Git/source changes. Every owned tool is terminal. Parent alone decides focused2 and fixed70; this gate does not establish semantic equivalence or authorize follow-on execution.

# #40 own-PGO pressure static lookup — GO to fixed70 only

Exact own-source PGO candidate c3166899f9380812b0fcb114d613021ba308699e46b0f7de48ffafaf4ff0e5a7 is compared with retained37 own-PGO54be65520cbe5e3324e94021ff49eed096027fd871f17150c97bdfb21a3c023f. The actual sampled pressure ray paths replace software-popcount arithmetic with masked indexed byte loads, without the #39 per-ray256-byte temporary/copy. The cheap knight path gains a dependent lookup. This is a bounded favorable mechanism gate for a matched own-PGO fixed70 decision, not a speed prediction, semantic qualification or inherited generic result.

No standalone king_pressure symbol exists on either side; pressure is inlined in activity::compute. Control ray13976–139ef loads the masked mark and executes two software count-ones expansions/four IMULs. Candidate ray1394b–1395d instead loads the mark, masks it and reads a byte through r8; its loopback1397c→13932 repeats that lookup with no intervening call/copy. The occupied-square path13985–13997 uses the same indexed register-base read. The other color's corresponding paths1374e–13760 and13795–137a7 show the same form. The inspected ray loops contain no call/256-byte stack initialization; this is not a whole-activity absence proof.

Candidate-nm.stdout identifies local read-only PRESSURE_VALUES at90d06, size0x100. Selected lookup instructions use r8 as base; its defining LEA is outside these finite windows, so the exact operand-to-object dataflow is not independently closed by this capture. Source and named emitted object support the intended storage identity, but they do not replace that missing instruction-level provenance or prove global absence of duplicate payloads. We retain that uncertainty instead of expanding the bounded gate.

The control cheap knight path13c98–13cb2 has already folded popcounts to shifts/mask, LEA, TEST and CMOVE. Candidate13c22–13c32 loads the mark, AND3, performs an indexed byte load and adds it. The new dependent memory access and register/table-base lifetime can erase the removed arithmetic; neither smaller code nor a small immutable table establishes benefit.

| Actual emitted observation | Own37 | Own40 |
|---|---:|---:|
| activity::compute extent |9061B|8739B|
| activity entry stack reservation |0x218|0x218|
| full_impl extent |4936B|4936B|
| .text |541387B|541211B|
| .rodata |322016B|322240B|
| .data.rel.ro / .got |19880B /2864B|19880B /2864B|

These are static extents/reservations, not dynamic work, a complete spill/copy audit or CPU effects. Candidate full_impl3837a calls GOTefe60, whose actual relocation is activity121d0; that activity entry is captured. Symbol sizes, full call, and source evaluator ownership locate the normal production evaluation route; no arbitrary demangled counterpart or probe is introduced. Recursive bodies/frames, most activity code and all pressure paths beyond the finite windows remain uninspected. Mid-instruction window-boundary fragments are ignored.

The unchanged PGO preflight passed exact own-source instrumentation/training/use matching and per-side profile identities, distinct own profiles, original54 raw-profile declarations, same compiler/tools23/default x86-64/thinLTO/CGU1 settings and exact source72 activity.rs-only delta. Only per-side declared profile paths are normalized in effective RUSTFLAGS/CARGO_ENCODED_RUSTFLAGS. Parent activation binds the separate independently original54/raw/PID/byte-identical-remerge proofs and real four-stage terminals; capture does not rerun those checks. Candidate profile7f79529773da099060bb1b73a1d92a7d03b52b228bc3d754607b76980981c75a; controlcea116a718d778a6c31ec306aa8ec88e659a517cad83a8b0aaa2a9f233ea1dc8. All discovery input pins were rechecked unchanged after review.

Actual outer terminals: discoverc88c38/0; first5windows9dc94b/0; first analyzer3fc7a3/0; two additional minimal windows7fc40d/0. All21 binutils children exited0; seven windows/three bodies/18749 output bytes stay within12/131072/0x800 caps. Analyzer rerun101aa4/1 is preserved: exclusive creation refuses the existing five-window window-analysis.json. No file/helper was repaired or overwritten. That original analysis remains five-window-only; the added setup/control-entry raw windows were manually read. This metadata failure is not an engine/semantic failure and adds no performance evidence.

All owned processes are terminal. No engine/test/compiler/build/merge/profile/timing/Git/source changes occurred. Parent alone admits the fixed70 trial or further checks; no follow-on execution is automatic.

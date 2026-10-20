# GO: selected generic clipping mechanism is present

This is a static mechanism gate, not a performance/adoption claim. Compare generic57 `5d10b2fa…` with immutable61 `2c7d2bf5…` (7,064,984B,0555), source74 `f3529e17…`. All source/tool maps, compiler/settings, images and source archive were checked before/after capture. Generic x86-64/noPGO settings and toolchain/tools23 match. Nine complete consumed bodies,354,123 stdout bytes (<10/2MiB); no engine/test/build/profile runs. Parent library compilation overlapped untimed H work; no timing interpretation.

## Actual ownership and permission route

Only one emitted Activity scoring owner exists: `compute_for_search` at18850,7918B, versus baseline compute at18850,7884B. At18861 it spills incoming R9d to rsp+c0; at1a3b2 it tests that byte once at the pressure tail. True calls clipped1ac20 at1a3d1/1a3e4, false calls scalar1a740 at1a43f/1a452. Both routes make two pressure calls, one per defender; the extra two static call sites are mutually exclusive, not two extra dynamic calls. The scoring/marks owner is shared, not duplicated into giant const-bool bodies.

Actual native ordinary at40bb9 loads the Search permission byte, spills its widened value at40be9 to rsp+38, reloads R9d at40d23 and calls full_impl42a80 at40d28. FULL spills R9d at42a91 to rsp+0; reloads R9d at42d26 and calls through GOT e45d0 at42d41. Independently reading the ELF load mapping/GOT resolves this slot to18850, the actual shared Activity owner; baseline e4e60 likewise resolves to baseline18850. RDI remains the existing output pointer, RSI position, RDX supplied map, ECX material, R8 packed weights, R9 geometry bool at the Activity boundary. No seventh stack argument is introduced there. This is real caller/callee evidence, not inference from demangle.

Source audit covers all four native full routes: ordinary.rs812, root preparation quiescence.rs153–157, Q sparse evaluator.rs688 and refresh710 forward their existing permission; evaluator.rs409 forwards to Activity. Public full339 supplies false; observed/fresh/detailed wrappers356/365/376/386 supply false. Supplied Some Influence remains the numerical owner for marks/mobility; no map-derived permission. Root/Q complete bodies were not gratuitously captured, so no emitted frame-neutrality claim is made for them. Their flag transport is source-proved, and the paired ordinary/FULL/Activity chain above prices one real native route.

## Clipped target work and retained costs

The true kernel is an actual outlined1695B owner at1ac20. It decodes inventory and the king before gating. With no opposing sliders,1acd7 jumps to1b00b before plane loads1acef–1ad12, ray addressing or clipping. Thus pawn/king/knight-only paths still pay the pressure-call prologue/inventory/king work, but not eager bitplane setup. Orthogonal test1ad31 skips four orthogonal clips; diagonal test1ae90 skips four diagonal clips. Existing MASKS are addressed directly at1ad1c; rows are borrowed scalar loads, not copied64B rows or reconstructed geometry. There is no allocation or normal-path helper call in this kernel; its three call instructions are cold bounds/panic exits.

For active families the four clips are unrolled. Each blocked ray uses guarded TZCNT or BSR, the blocker-index outward MASKS row load, attacker BT plus conditional endpoint mask, inversion/AND and union. Up to eight such computations remain real setup. Empty blockers branch around scans. The orthogonal selected-target loop1ae70–1ae8e and diagonal1afe0–1affc consist of bit index, clear-low-bit arithmetic, mark load, original0xf0/0xcc mask, PRESSURE_VALUES byte load and add. Neither loop reads mailbox occupants, decodes color/kind, checks coordinate bounds or stops on a per-target victim. These eliminated tests have not moved into another per-target helper. Separate family loops retain the required wrong-family exclusion.

At1b00b the unchanged knight inventory gate begins; its offset/mailbox/color/mark work survives from1b014 onward. Final subtract12/clamp is1b268–1b271. Source old scalar king_pressure and knight numerical logic remain literal. Scalar fallback still has1235B and reservation0x48; the new kernel uses0x18. Static change is not whole-call-chain traffic reduction: the clipped owner adds bit arithmetic and ray loads, and both retain six callee-saved pushes.

## Code/frame/ABI costs, not a gain forecast

|Owner|57 bytes/reservation|61 bytes/reservation|
|---|---:|---:|
|Shared Activity|7884 /0x1c8|7918 /0x1c8|
|Scalar pressure|1235 /0x48|1235 /0x48|
|Clipped pressure|absent|1695 /0x18|
|FULL|2415 /0x138|2421 /0x138|
|Actual ordinary|paired raw captured|8704 /0x428; same reservation as57|

Every listed owner saves six registers. Existing scalar pressure also addresses below its reservation, so this table is not an absolute stack high-water proof. The bool adds actual stores/reloads despite unchanged Activity/FULL/ordinary reservations. Static rsp-memory instruction rows increase Activity201→209 and FULL88→90 (not dynamic counts or bytes); scalar12, clipped8. Whole .text grows0x6e0=1760B; .rodata shrinks40B. No code, frame, copy, spill, cache or CPU neutrality is asserted. No new census, PMU or instruction profile was collected.

GO only for the selected mechanism: shared ownership and explicit permission survive, true slider loops remove the intended per-target classification, and inactive-family plane/clip work is skipped. Parent must judge the1695B extra owner and setup/boolean/call/frame costs, meaningful tests and any separately authorized fixed native screen. Existing profile attribution is not a measured saving. No source retune or broader capture is requested.

# Cold generation-ray prototype

Sender: Imp2 child generation_ray_prototype
Recipient: Imp2 parent

Prototype: `/tmp/imp2-generation-rays-20261018`
Only modified copied file: `src/movegen.rs`.
Root source was not edited. Copied only Cargo.toml, Cargo.lock, src, and tools
(excluding Python bytecode/cache), with no target or evidence directory.

## Identity

Root Git HEAD: `7d5809fd21561f7c171e0d9339b736568a11d702` (root has pre-existing dirty files).
Released spec HEAD: `1c89c21a4645ec85adf28285616d822b3cd91f73`.
Root copied-tree SHA-256: `365315bfebad94a046558b2cb26c87749a1fdec930b956ae289054fba5b626ec`.
Prototype copied-tree SHA-256: `275aaf4ee832ed2c7e27f071f26ed83dda4c58330293c4bd2618e3d532b8cfc0`.
Root movegen SHA-256: `9e645384baf5177697c5125df2e15db70eefac440ed63289435adddf6a514617`.
Prototype movegen SHA-256: `7cc206a18173a460b39bd3b4e7c99a8eb495588d8db72d45aa0f201e313588db`.
Geometry SHA-256: `582a2e8ad2672a937062ae829ae596ee263b69c6ec52103c55c658a6ecc225f1`.
Full file hashes and the tree-hash format are in `identity.json`.
Static file comparison found these differences only: src/movegen.rs.

## Change and order proof

Runtime `pieces(..., kind: PieceKind)` remains. Knights iterate existing
KNIGHT_SOURCES[from], whose constructor applies KNIGHT offsets in original
array order and removes only off-board destinations. Although named sources,
this is exactly the original source-plus-offset sequence when indexed by from.
Bishops consume ATTACK_RAYS[from][0..4]; rooks [4..8]; queens and kings [0..8].
The ray constructor steps from the source using DIRECTIONS in unchanged order,
appending near-to-far squares until the board edge. Both arrays exactly match
released search-candidate-production.md Base generation order. Kings break
immediately after the first square of each nonempty ray, whether blocked or
considered for admission. Knights skip own/king victims and move to the next
leap; sliders stop before an own/king victim, or after an enemy capture.
The existing admission call and LIMIT return stay at the same point per
pseudo-destination. Source iteration and outer chronological type iteration
are unchanged, as are EP, castles, pawns, single-check prefixes, king-safety
masks, copied-child ownership, and semantic accounting.

The original coordinate pieces function is retained verbatim except its name
as cfg(test) coordinate_pieces. FORCE_PROJECTION dispatches pieces to it and
still bypasses summary acceptance for the old mailbox-projection admission.
The existing full ordered-inventory comparisons consequently now compare
independent non-pawn producers. Their 10,000 constructed setups and joined
witnesses also invoke both LIMIT=2 routes and compare capped ordered lists.
Existing capped walk/count/reuse tests remain intact.

## Tradeoffs and pending validation

This isolates table-supplied destinations from const-kind specialization or
known-check reuse. It removes runtime per-destination coordinate offsets from
pieces at the cost of table loads/slices and separate knight traversal; any
speed benefit remains unmeasured. Board lookup uses the established table
square & 63 mask with debug assertions for table bounds.

No build, rustc, test, engine run, profile, simulation, or formatter was invoked.
Only file reads/copy/edit/diff/hash helpers ran, all under taskset 0-5,8-13.
Requested Normal speed could not be read back or changed by this child.
Parent should review, build, run broad ordered/full and capped tests, and
measure only after current full54 collection reaches actual terminal state.

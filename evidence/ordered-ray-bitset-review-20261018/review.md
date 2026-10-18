# Ordered sliding destinations from existing tag planes

Source/text-only study during the parent's live CPU collector96272/PID480262. Native basis is frozen117 `/home/legolas/rook2-work/imp2-complete117-ledger-test-proposal-20261018-9a56f133`, previously identified by the parent as root833bd34 native46. No implementation, parsing/build/test/engine run, hashing, archive, profiling or broad inventory was performed. Authority consulted: public `search-candidate-production.md`; own current native source and own historical generation-rays notes/source only. No independent-implementation architecture was inspected.

This is a distinct candidate from the parked destination-table trial: precompute the first occupied stop from existing planes, then emit ordered legal candidates through unchanged safety. It can avoid per-square mailbox occupancy/type/color decisions and coordinate stepping in the slider producer. It does not avoid enumerating available destinations, legal admission, projections, move encoding or list storage. Current cost and benefit are unknown.

## Narrow scope worth considering

Select only **complete, nonchecked B/R/Q production** (`LIMIT == MOVE_CAPACITY`, checker count zero). Leave checked production, LIMIT2, knight/king/pawn production, EP/castling, checker discovery, safety, ranking and Q's separate tactical producer unchanged. This scope deliberately avoids setup overhead in early-stopping capped replies and preserves the current king-first bounded behavior. A later wider scope would need separate evidence. Selectivity here concerns implementation dispatch, not admission: every full nonchecked slider still emits the same complete ordered sequence.

Current `movegen.rs:565–605` iterates retained piece-source chronology, direction order, then coordinate offsets near-to-far. It reads the destination Piece, stops before an own piece or opposing king, calls `add_if_safe`, checks LIMIT, then stops after any other occupied destination. Even a capture rejected by safety ends its ray. Full generation (`671–729`) first handles EP/castles/pawns, including existing prefixes; legal checking/pin summaries stay authoritative.

## Supply is already present; visibility is missing

`AttackBits` has four coherent exact Piece-tag planes (`attacks.rs:7–10`). `Position` owns one view; `set_square` maintains it and existing projections operate on copies. Tags1..6 encode P/N/B/R/Q/K; bit3 is Black. Inside the existing owner, `[a,b,c,black]` yields:

- occupancy `O = a | b | c`;
- own pieces `F = O & (Black ? black : !black)`;
- opposing kings `K = (!a & b & c) & opponent_color_mask`.

The occupancy intersection matters for White: `!black` alone includes empty squares. Exact valid tags/coherence are required; no new admission or reconstruction from sorted lists is needed. Existing `attacks.rs:12–66` already has immutable `MASKS.rays[square][direction]` and increasing-direction metadata, used by actual attack/checker kernels. Planes and masks are private: movegen cannot currently read them directly. A narrow owner-local snapshot/query abstraction could expose these derived values and ray targets without exposing arbitrary plane mutation or adding Position/Node/Search fields, new maintained state, tables, global caches or child copying. This is a proposed seam, not implemented or an ABI-cost assertion. Derive the local masks once per selected generation invocation, preferably only when the selected slider work is actually reached; do not charge paths returning after prefixes for unused setup.

## Ordered kernel and exact boundaries

For a source/direction, let `R` be its existing immutable ray mask and `B = O & R`.

1. If `B` is empty, the geometric reachable ray is all `R` (including the empty-ray case). Do not scan zero or invent a sentinel square.
2. Otherwise scan once for nearest occupied square `q`: least index when `df + 8*dr > 0`, greatest when negative. The geometric ray through the stop, **including q**, is `R & !MASKS.rays[q][direction]`. The existing ray lookup excludes its origin, so this removes only squares beyond q without a shift-by64 boundary trick.
3. Remove forbidden destinations `F | K` from that already truncated mask. Own pieces and the opposing king stop the ray and are not capturable; they must remain in the occupancy used to find q. Filtering them out before finding the blocker would illegally expose farther squares.
4. Enumerate remaining bits with nearest-first low-index scans for increasing directions, high-index scans for decreasing directions. Each emitted target still goes through the original `add_if_safe` and LIMIT check. No candidate after q is considered even if q's capture fails legal admission.

The one nearest-blocker scan is additional to bit scans used to enumerate targets; this is not one scan total per direction. The direction sequence remains NE,SW,NW,SE,N,S,E,W; bishop first four, rook last four, queen all eight. Increasing flags are true,false,true,false,true,false,true,false under a1=0 indexing. Board-coordinate direction order does not reverse for Black. Never merge all directions into one globally ascending mask. Likewise, source enumeration remains `piece_squares(side,kind)` chronology, never bit-index source order. Empty/border rays and square0/63 need explicit nonzero guards.

This is legal-generation occupancy semantics: both kings block sliders. Evaluation Influence's opposing-king transparency and friendly-slider transparency do not apply. The destination kernel says nothing about own-king safety, pins or check evasion. `GenerationSafety::accepts` still owns its current safe-summary versus projected-safety decisions. Retain exactly the existing current Position view and projection owner; do not replace per-candidate projection with the parent occupancy snapshot or produce a semantic child earlier.

Broad joined EP is outside the selected slider producer and must keep its actual prefix, removal/projection and exceptional ingress handling. Its permitted nonpawn victim is not a reason to narrow admission or shortcut double check. The selected view is derived from the final current Position, not guessed from standard-EP ancestry. Promotion, capture, castling and subsequent child maintenance stay unchanged; they supply the next coherent Position. Q's tactical list and its single projected view stay unchanged.

## Distinction from the historical rays trial

The parked `/tmp/imp2-generation-rays-20261018` source replaced coordinate destinations with existing ordered `ATTACK_RAYS`/`KNIGHT_SOURCES`. It still loaded each destination Piece, classified own/king victims and stopped after capture. Thus it removed coordinate stepping but did not compute a blocker once or remove per-target occupancy decisions. It also changed knights/kings and capped/checked traversal, whereas the scope above would not.

Own historical pilot notes describe a weak generic result, all six ranges overlapping, and larger emitted generator bodies; the source was parked. Those costs are not current117 costs. Current planes, king-first caps, Q projection, ordinary/observer and compiler interactions differ. Neither the historical flat result nor successful prior ordered tests establish a gain or regression for this distinct kernel.

## Meaningful future tests and rejection criteria

- Independent pure-ray oracle: retain coordinate `Square::offset` plus mailbox walk, not the same ray masks or nearest-bit helper. Compare exact ordered target sequences for all sources/directions/colors, empty rays, each nearest blocker distance/type/color, multiple blockers, boundary0/63 and representative/all ray occupancy subsets. Ensure material behind q never leaks through; both kings block and only enemy nonking q can be captured.
- Full inventories: preserve an independent old coordinate producer and old mailbox legal projection together. Compare entire ordered full lists on broad coherent placements and chronological legal histories. Explicit same-placement/different-source-chronology tests must change the source-group order as before. Include pinned captures, blocked rays, captures that expose the king, promoted sliders and source relocation/capture compaction.
- Guard scope: full checked and LIMIT1/2 outputs, reuse behavior, zero/one/two replies, single-check pawn prefixes, EP/castles/promotion and joined nonpawn-EP witnesses must remain exact, exercising fallback rather than treating passing shared producer prefixes as independent proof. Verify B/R/Q candidates rejected by safety do not permit farther destinations through their occupied target. Plane coherence checks must use independent mailbox reconstruction after actual transitions.
- Later functional/strict/whole-component checks must preserve logical N/R work, retained P/G/cache order, candidate ranking, history and interruption chronology. No relation accounting is added by geometric supply.

Reasons to reject include snapshot/setup overhead when few sliders exist, first-square blockers where the old walk is already minimal, sparse empty rays where every target must still be enumerated and per-target scans replace cheap steps/loads, extra dependent ray lookups, register pressure, ABI/frame/spills, code duplication/inlining or larger generator bodies. Building masks before a capped/prefix return would be unnecessary work. Maintaining new board state or broadening scope to amortize a weak result would defeat the narrow premise. Future authorized codegen and matched current generic/own-PGO evidence would be required before selection; no such work was done here.

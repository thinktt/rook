# Fresh coherent Influence fused into the existing color request

**Recommend one bounded integrated discriminator, if selected:** preserved7ac3,
matched new unfused3, and new fused3. Use the same refactored image for both new
modes; preserve67d/profile948747. This document authorizes no implementation,
build, census, timing or fourth worker. Inventory/layout work stays closed.

Base: exact 64-source positive epoch workspace
`/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01`, bound by
[own-PGO preparation](../../experiments/multicore-feasibility/epoch-own-pgo/preparation.json).
Pins below refer to that source, not the inventory or whole-helper derivatives.

## Actual FULL admission and one shared body

Propose a private `full_for_search(node, scratch, checked, coherent)` returning
both Evaluation and a reference to the caller-owned canonical map. Fuse only
configured3 + scratch None + the existing private search geometry permission.
The root seal is `engine.rs:195–206`: native entry validates/binds the position;
public/direct preparation clears it. Do not infer permission from an Influence
or from public Position fields. Optional child-preparation combinations keep
the existing path so their prepared-map authority is not bypassed.

| Exact seam | Change only after FULL is settled |
|---|---|
| ordinary.rs:813–814 | Replace ensure+full with the private combined call. The earlier FAST pressure/threat ensure at800 stays unchanged; if it filled scratch, FULL uses that Some map. Checked ordinary FULL remains eligible. |
| quiescence.rs:143–164 | Root preparation uses the combined call after begin_search/learning/table reset. Ordinary575 and timed520 already bind permission first. Public prepare_root clears permission and falls back. |
| evaluator.rs:934–948,957–965 | In private nonobserved sparse/refresh branches, use the combined call only after the same selection/FAST decision. |
| quiescence.rs:288–303 | Ordinary unchecked Q reaches those private branches. Checked Q and last-ply FAST have no FULL opportunity. Observed stage routes pass false permission and keep their current path. |
| evaluator.rs:523–548; quiescence.rs:402 | General ensure remains lazy and serial: FAST pressure and capture destination-support may need a map without FULL. Never launch Activity here. |

Scratch Some, supplied/custom maps, noncoherent input, public/FRESH observers and
budgets1/2 retain the existing map/dispatch route. “Fresh map” means scratch None;
it does not mean the public forced-FRESH pawn-cache bypass.

Factor current full_impl startup into a typed FullLaunch (scope, transport token,
material/phase/root-bound weights), followed by **one numerical full body**
from pawn selection onward. Supplied calls create the normal launch. Eligible
fresh calls acquire the one-call scope before publishing Position, launch once,
acquire/install the map, then enter that same body with the existing token.
They must not call the old dispatcher again. Preserve pawn/cache order, supplied
map authority, rounding, retained/R publication and host polls. Consume the scope
at the existing pre-composition/callback boundary (evaluator.rs:695); standalone public/FRESH
callbacks must still see parked helpers; an existing outer scope retains its ownership. Return only the canonical scratch map,
never a reference into worker storage.

## Shared native row extraction

Extract the color loop of influence/coherent.rs:16–83 into one `build_row` that
fills a 64-byte destination. The serial coherent builder calls it twice; each
helper calls it once. Zero the row before scalar P/N/K additions, preserve their
source-list order/multiplicity and wrapping, retain the zero-slider shortcut,
BitSums modulo256 carry and native transpose/slider_masks. Read both colors'
placement planes as before; no parent-map seed or duplicated row algorithm.
Public scalar construction stays unchanged.

## Chosen two-phase storage and retirement

Use two concrete initialized `UnsafeCell<[u8;64]>` row cells and matching rowReady
AtomicU64 epochs. Packet holds immutable Position and a tagged input mode:
Supplied(actual map) or FreshCoherent. Root inputs are copied into launch metadata.
After request publication, Packet is never written and no mutable whole
Cells/Influence is formed. Only the separate row cells mutate before their
publication; there is no per-call allocation.

1. Under Control/None, checked next generation initializes the packet and
   publishes request(g) Release. Helpers Acquire it. Supplied jobs use the old
   path, touching neither row cells nor rowReady; future fresh jobs require
   equality with their exact generation, not a latest/at-least check.
2. Each fresh helper mutates only its own row cell through a short lexical
   borrow. End that borrow, then rowReady[i]=g Release and the unconditional
   existing SC notification exchange. Packet remains immutable/leased.
3. Helpers actively poll peer-ready with Acquire and stop checks, without
   Control or registering a condition-variable waiter. After both rows are
   ready, each copies both into a local 128-byte Influence and ends all row
   references before running its unchanged own-Activity/opposite-Shelter chain.
   This pays 128 bytes per helper; no direct shared-map variant is proposed.
4. The sole coordinator waits for both exact row epochs with the existing
   spin/Sleep/SC handshake, then drops Sleep and takes Control. Revalidate
   matching FreshProducing flight and nonterminal ownership. Copy both rows into
   caller scratch, end all row references, mark FreshDelivered, release Control.
   Charge exactly one logical influence_builds event here (and the existing
   coordinator coherent-build test event), never one per helper. Pawn/local
   work begins only after this canonical map is available.
5. Helpers publish their usual scalar outputs and actual done Release only
   after all input/map/output borrows end. Completion requires FreshDelivered,
   both done Acquires and output consumption under Control before None. Thus
   helpers finishing early cannot retire a map the owner has not yet copied.
   Current side combination/rounding and R publication stay canonical.
6. Reverse ownership is transitive: owner row-copy ends before Delivered/None;
   each peer row read ends before its done; both done are acquired before the
   next request Release, acquired by each next writer. Final close owns
   Discarding until both real parked/exited acknowledgments. RowReady is
   publication, never input retirement or permission for the next write.

Only the coordinator registers/waits. Both rowReady and done publications,
plus terminal publication, perform unconditional SC latch exchanges. An early
row notification during done-wait merely causes a predicate recheck. Notifiers
may still briefly take Sleep after consuming registration; that cost remains.
Drop Sleep before taking Control; phase spin/Sleep waits hold no Control.
Existing lifecycle condition-variable waits retain their unlocking behavior.

Before/between-phase failure sets stop and wakes the owner; the peer exits its
poll and ends borrows. Scope zero must not park a helper with unseen work or in
an active peer wait: finish/drain the request or actually exit on stop. Close
races with owner row-copy are serialized by Control. No fake rowReady/done,
wall-time retirement or postlaunch serial retry. Checked epoch exhaustion stays
terminal. Production panic=abort is not unwind recovery. The existing final
scope/error ownership applies, rather than promising rollback of partial pawn
work after a terminal helper failure.

## Economics and the smallest later test

Schematic elapsed paths (not measured bounds):

`retained3 = M + Pmap + max(C, Awhite, Ablack) + J`

`fused3 = Pposition + B + max(K + C, Lwhite + Awhite, Lblack + Ablack) + J`

M is serial native map construction; B includes two row producers, pickup,
publication/peer barrier and owner readiness; K installs canonical scratch;
L assembles helper-local maps. Position publication is serial. Count 128 bytes
of row production plus 384 bytes of row-to-map copying, two extra rowReady stores
and SC exchanges, peer Acquire polling and owner Control acquisition. Pawn/local
work cannot overlap an unavailable map; the faster side waits for the slower.
Current3 and fused3 each have **one dispatch**. Short zero-slider endgames,
imbalance, cache transfer and code/layout drift can erase the saving.

The prior ordinary freshness samples (Some128/1430,0/427,74/1594) omit root/Q
population; the 206ns proxy belongs to instrumented coarse producers. Neither
prices this barrier or bounds native universal savings. No new census is needed
to decide whether one integrated experiment is informative.

If selected later, use original35/08/43 and existing collection machinery for
preserved7ac3 versus same-image unfused3/fused3 (a small 36+3 screen is sufficient).
Unfused3 shares row extraction, launch/body refactoring, physical fields and
observation policy, but serially builds the map and uses supplied dispatch.
Report fused/unfused separately from both new modes/retained3, complete CPU,
joined lifetime and idle. Existing 512th-epoch report intervals would include map
work on fused jobs; label that boundary without adding a new census/framework.
No PGO, broad qualification or automatic extension is proposed.

Focused controls should cover native row-byte equality (mixed scalar/bit paths,
wrapping/multiplicity), actual ordinary/root/unchecked-Q demand and Some-map
fallback, unchanged FAST-only requests/build charges/N/R/cache/retained values,
public/FRESH parking and1/2 fallback. Force delays/failures before row publish,
after first readiness and during owner copy; stale epochs across Supplied gaps,
spurious/late notifications across phases, reverse reuse, close/shutdown and max
epoch must exercise the new seam. Reuse existing numerical/lifecycle evidence.
One bounded Sol source challenge found no blocker subject to these ownership,
single-waiter, zero-initialization and cost conditions. No implementation, build, engine run, new census or profile was performed
for this design.

# Experiment35 source-only contract

Owner selects a complete invocation-local activity frontend, starting exact retained25 (no26–34 composition). Public Activity/compute signature stays. Keep original scalar implementation as private compute_scalar for faithful fallback and reference. New compute uses complete batch frontend for every applicable inventory, with ONLY absence-of-class and malformed-tag fallback gates; no tuned density rule. Pay all setup/geometry/classification/value/mark conversion on each invocation. No persistent fields, Session permission, target-feature expansion, cached scores or lookup answers.

## Disjoint source ownership

- fresh_pawn_transport: ONLY src/activity.rs, frontend geometry/accumulation/integration plus E/activity-category-masks-frontend-preparation-20261019-01.
- next_hot_path_review: ONLY NEW src/activity/batch.rs, bitplane producer/classification plus E/activity-category-masks-planes-preparation-20261019-01.
- score_context_transport: ONLY NEW src/activity/batch_tests.rs, independent coordinate/byte controls plus E/activity-category-masks-tests-preparation-20261019-01.
- root: proposal and parent review/final source freeze; no overlapping source writes.

All work source-only, small text/hashes on housekeeping0-5,8-13/HOME TMPDIR. No Rust parse/format/compiler/test/engine/binutils/profiler/Git/archive/Herdr/advisor calls. Parent reviews final combined source and native lowering before execution. Existing178 test bodies remain unchanged. New tests are declarations only until explicitly activated.

## Fixed interface between source owners

activity.rs declares `mod batch; #[cfg(test)] mod batch_tests;` and retains existing Mobility fields/categories:i64,total:i64,queries:u64.

In batch.rs, all interface items are pub(super):

```rust
#[derive(Clone,Copy,Debug,Default,PartialEq,Eq)]
struct Category { pub low:u64, pub high:u64 } // category bits0/1, exact0..3
impl Category { fn mask_for(self, category:u8)->u64; }
#[derive(Clone,Copy,Debug)]
struct Board { pub empty:u64, pub colors:[u64;2], pub kinds:[u64;6] }
#[derive(Clone,Copy,Debug)]
struct ClassViews { pub direct:Category, pub additional:Category }
struct Inputs { pub board:Board, /* private actual supplied-map planes/features */ }
impl Inputs {
 fn new(position:&Position,influence:&Influence)->Option<Self>;
 fn class_views(&self,color:Color,kind:PieceKind,with_additional:bool)->ClassViews;
}
fn transpose64(bytes:&[u8;64])->[u64;8]; // actual native producer, lane=square
#[cfg(test)] fn relation_for_test(own:&[u8;64],opponent:&[u8;64],tested:i32,remove:u8)->Category;
```

Inputs.new may returnNone only for nonempty raw mailbox tags with invalid low kind bits, WITHOUT kind() panic. Preserve all193 valid byte aliases using actual byte-zero/colorbit3/lowkind semantics; fallback happens before any partial result and calls unchanged scalar. Use the supplied128 map bytes even when custom/inconsistent with placement; never rebuild native Influence or read private AttackBits. Features use normalized packed digits, capped4 multiplicity for classification only, fixed tiers1/3/5/9/99 and saturating packed subtraction16/4/2. Queen/minor/rook capture overrides and exact class3 remain. Knight/Bishop direct masks share numeric classification. Additional views are unadjusted with same capture overrides and are computed only if requested. No additional view forQ.

Baseline x86-64 SSE2 transpose is permitted, with four bounded unaligned16-byte loads per64bytes and explicit local safety proof; no CPU feature changes. Independent actual-byte/lane tests are mandatory. Safe board.map(|p|p.0) copy is acceptable initially; include its cost. Pure algebra helpers must not hide per-lane scalar LUT/classification. Borrow features/inline judiciously; record temporary/returned-aggregate risk, no neutrality claim.

In activity.rs, tests can access this shared actual frontend helper:

```rust
fn batch_destinations<const KIND:usize>(
 position:&Position, view:&batch::Inputs, class:&batch::ClassViews,
 color:Color, source:Square, values:&[u8;64]
)->(Mobility,u64); // exact C/T/R and all direct targets (including category0)
```

Use actual chronological piece_squares inventory/presence, existing phase, opposing-king/rook value-row and unchanged per-piece curve/source-penalty/uncapped profile_sum. Per-ray P is through first occupant; X through first nontransparent under *activity* rules. D=P minus friendly; A=(X minus P) minus friendly; include opposing opaque endpoints. Keep vertical rook subsets for T only. Rays are disjoint per source, but never deduplicate different sources' C/T/A charges. R includes every A even category0/overridden endpoints. Sparse existing-V sum is preferred; avoid dense multiple software-popcount dot products.

Accumulate direct weak/strong masks percolor/kind as OR presence and flush into fresh byte Marks before unchanged king_pressure. Category0 makes weak; A makes no mark; preserve OR bits of other kinds. Keep score/pressure/weight numerical composition in one shared owner, preserving all original rounds. Scalar frontend remains unchanged except function rename and a mechanically shared final composition helper if needed. New public compute must exercise batch path on valid active inputs, not silently route everything to scalar.

## Independent focused falsifiers

New test declarations use common `activity_batch_` prefix. Actual native transpose all lanes/block boundaries/colors/bytes; exhaustive256² pairs×4tiers×(unadjusted/2/4/16) vs independent radix scalar reference; complete coordinate-oracle C/T/R/D and mark/Activity/shelter parity, not new bitset/prefix helpers as oracle. Broad legal-transition/chronology placements and arbitrary supplied maps; raw193 aliases, unvisited malformed tags and visited short-circuit/must-panic cases with faithful scalar fallback; stale private planes via direct mailbox mutation. Advisor witnesses: Bc1/ownNd2/enemype3/Kf4/ownBg5; Rd4/ownQd5/emptyd6/enemypd7 with vertical T-only doubling, mirrors/other directions; cross-piece additional intersection charged twice/no mark; edges/no blocker/both scan directions; category0 and mark-label union; signed round/rook gate boundaries. Reuse old178 untouched and compare complete Activity plus downstream shelter.

No production win is assumed. Generic full-construction backend/focused/native pilot precedes own-source PGO; broad qualification only after both frozen timing screens pass. Independent advisory critique received and reviewed; decisions remain root-owned.

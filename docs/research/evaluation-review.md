# Root material and square-term review

Date: 2026-10-17. Scope: independent source review of the initial Imp2
`src/evaluation.rs` against released `root-material-context.md`,
`material-balance.md` and `positional-values.md`. No engine source was edited,
no new requirements are proposed, and no engine or fixture check was rerun.

Reviewed evaluation source SHA256:
`93915f4c1cb72157c20f73976fba56af07227b12b35e8c2ba9a34fe173fd816f`.
Line references below bind this snapshot; later changes need their own review.

## Conclusion and concrete gaps

I found no mismatch in the implemented material or square-balance formulas
for validated positions and admitted parameter values. Root/current ownership,
White orientation and the important signed-rounding distinctions are preserved.
This is a source-review conclusion, not full fixture coverage or qualification.

1. **Public parameter domains are wider than their stated contract**
   (`evaluation.rs:35,50,75,100`). `percentages: [[u16;5];2]` admits values above
   the specified 0..1000, and `average_depth: i32` admits values outside −100..100.
   There is no check or documented bound at the constructor. The current caller
   is neutral 100/average-depth 0, so this is a latent API-boundary gap, not an
   observed error on an admitted request. The parent had already identified
   the percentage gap; the same consideration applies to average depth.

   The count-difference/depth multiplication is performed in i32 **before**
   conversion to i64. It is safe within the released domain, but an unrestricted
   public average-depth value can overflow before the wider arithmetic begins.
   This does not create specified overflow semantics outside the admitted
   domain. Validate those bounds at the eventual cold ingress or state a
   prevalidated internal precondition; arbitrary public diagnostic input must
   not reach this helper as though its Rust type enforced the domain.

2. **The existing APIs cannot execute the full arithmetic fixture domains.**
   `RootContext::new` obtains phase from a root placement; `material` obtains
   current counts from a Position; `square_balance` obtains current phase from
   placement. The component contracts deliberately permit independently
   supplied phase triples, material values and counts. The current inspect
   command therefore cannot exercise all of those fixtures exactly. This is
   an interface/coverage limit, not a reason to change the formulas or demand
   a particular module organization. Do not fabricate placements or expected
   answers to claim the missing arbitrary-input coverage.

3. **Search-root replacement needs explicit ownership at integration.**
   The evaluated terms correctly retain their root context for descendants.
   The development `Search::new(root)` creates that context once, whereas
   `Search::run(position, depth)` can accept another Position without refreshing
   it. Present CLI repeats use the same root, so no current wrong result is
   established. If a persistent caller later supplies a new search root, it
   must establish the new root context at that boundary. Rebuilding context
   inside descendant material/square evaluation would break the specified
   ownership and is not a suitable fix.

## Root and current state

`RootContext::new` records root side, root phase and root counts by value, then
computes color-specific material and non-king square values once
(`evaluation.rs:35–76`). Its percentage argument is explicitly White/Black
owned. An eventual own/opponent personality adapter must bind those arrays
using the **root** side once, including a Black root; it must not alternate
them with current side to move. `neutral` cannot by itself validate asymmetric
ownership because both colors receive 100 percent.

`material` uses current piece counts with retained root values. The root count
total, current count total and root side determine the average-depth term;
current side to move does not enter this White-oriented contribution. The
count total covers the five non-king kinds, so promotion does not itself
change that total. The side-to-move sign conversion occurs later in
`development_score`, rather than being mixed into either contribution.

`square_balance` uses each current non-king piece's square/type with the
retained root-phase table (`evaluation.rs:130–143`). For kings it forms three
White-minus-Black oriented basis differences, then blends those differences
once using **current** phase (`evaluation.rs:138–148`). It does not add root
king values or subtract two individually rounded current king values.
Only rank is reflected for Black (`square ^ 56`); files retain their identity.

The doubling gate is based on presence of current knights/bishops/rooks/queens
on either side, independent of their material values. It doubles the complete
non-king-plus-king contribution only when none is present, including king-only
and pawn-only endings. Captures/promotions consume the current piece lists;
no root placement inventory is substituted for them.

## Arithmetic and bounds checked

| Rule | Source observation and implication |
| --- | --- |
| Phase interpolation | `blend` uses i64 products, adds 128, then mathematical floor by 256. Negative halves round toward positive infinity as specified. |
| Material percentages | Root base is rounded before percentage conversion; the percentage weight is independently rounded with +50/100; value then rounds with +512/1024. For admitted nonnegative inputs, ordinary Rust division here equals floor. |
| Signed average depth | `floor_div((R*avd+1),2)` preserves odd negative cases. For example, R=1, avd=−4 and R=−1, avd=4 each give −2, not −1. |
| Advantage selection | The average-depth adjustment precedes sign selection, threshold checks and clipping. The losing side excludes pawns; favored pawn weighting uses its current weighted pawn total. |
| Non-pawn presence | `any_heavy` comes from counts, so a zero-valued non-pawn still enables the adjustment. |
| Losing-heavy division | A negative numerator uses floor before max(...,0). This is the required ordering. |
| Final advantage division | Its numerator is nonnegative in the admitted domain, so `/512` is equivalent to floor; it does not introduce signed truncation error. |
| Final clamp | The signed advantage is applied before clamping to −7000..7000. |
| Square interpolation | Each current non-king lookup was rounded independently when the root table was constructed. The king difference receives only the single later round. |

Within EVAL-MATERIAL's independent domain, at most 30 counted pieces each worth
at most 10000 bound a side's weighted total by 300000. The root/current count
difference is within ±30 and admitted average depth within ±100; their product
plus one fits comfortably in i32. The advantage factors are nonnegative and
bounded by 150 losing-heavy units plus 100 pawn units, with at most 250 extra
magnitude. No in-domain `abs` overflow or i32 total overflow is apparent.

For constructor-generated material values, admitted percentages yield weights
at most 10240 and values at most 9000. Root/current phase components produced by
Position are within 0..256 and sum to 256. The normative square basis ranges
from −99 through 35, so its valid convex rounded blends fit the i16 storage.
These bounds rely on validated inputs and unchanged context fields; public
mutable fields do not themselves enforce them.

The generated square table was independently flattened and compared, entry by
entry, against all **1,152** normative basis values in rank 1 to rank 8 internal
order. All entries matched. Normative data SHA256:
`33f1b39c468b9e3e39ef0b335a75d5c0ea1ac989533fe525e191d87486636bb7`.
This was a read-only Python/static-data control on housekeeping CPUs. It did
not run an engine or provide full interpolation-fixture coverage.

## Source-level repeated work worth measuring later

These are candidate experiments, not measured bottlenecks or required changes.

- Root construction computes 320 phase blends for White non-king squares and
  another 320 for the reflected Black table. Material percentages do not affect
  these adjustments, so the second set could be mirrored from the first or a
  single oriented table used. This is root setup cost; it must remain included
  in complete-lifetime measurements, and avoiding it may add per-piece lookup
  work later. Do not choose a representation from operation count alone.
- `material` sums ten root count fields on every invocation even though their
  total is constant for a RootContext. A retained root total could avoid that
  source-level work. In the current average-depth 0 baseline this entire
  correction is mathematically zero; compiler elimination and actual whole-search
  impact have not been established.
- The development leaf computes current phase in activity, in square balance
  and again for tempo. A phase value produced once at the same evaluated
  position could be shared without changing root-phase ownership. Current
  phase includes a small five-kind normalization and maintained starting-square
  measure, so this is a modest candidate, not evidence of a major cost.
- `square_balance` tests for a king within each piece loop and sets the heavy
  flag repeatedly for non-pawns. Separate king/non-king loops and a count-based
  heavy gate might reduce repeated branches. They may equally compile to
  similar or worse code; retain the readable baseline until integrated evidence
  warrants a replacement.

The review did not request new microbenchmarks or change the accepted baseline.
Neither these source counts nor the earlier CPU/work measurements identify an
exclusive cost for material or square balance.

## Coverage boundary and next checks

The first external core projection run passed three compatible neutral-root
material cases and two compatible bridged square-balance cases, alongside
phase and position checks. Its unsupported cases and omitted fields remain
explicit. It does **not** establish arbitrary material-value, asymmetric
percentage, average-depth or independent-phase coverage. No core check was
repeated for this review.

When actual cold APIs accept those inputs, useful existing anchors include
`material-zero-value-nonpawn-enables-adjustment`,
`material-promotion-preserves-total`,
`material-net-count-not-capture-value`,
`material-depth-crosses-negative-boundary`, the signed clip/advantage-cap
cases, and `square-balance-single-round-{127,128,129}-kings` with their
reflections. Execute their actual inputs and exact expected results; do not
approximate them using root-placement bridges. Position-to-descendant root
retention and future root replacement remain separate lifecycle checks.

The next planned external checker extension is pawn structure and shelter,
after the coordinator publishes actual inspect fields and a new binary.
No engine source was modified, and the old binary's core check was not repeated.

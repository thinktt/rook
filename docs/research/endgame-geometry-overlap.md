# Endgame geometry during the remaining FULL wait

2026-10-26; source-only recommendation after writer-region PGO closure
`db64b9da`. One disjoint Sol reader challenged totality and score dependencies.
No engine edits, build, test, census or native measurement. Toby paused the lead
goal: commit this recommendation and the pending orientation documents, then stop.

**Park universal or two-side preparation.** One smaller hypothesis survives:
prepare a side-tagged `rook_against_pawns` reduction boolean, after the winning
inventory hook and only while the matching color pair remains unfinished. This
has a safe pure producer and avoids preparing two sides, but its frequency,
remaining slack and integrated cost are unknown. It is a possible later
discriminator, not selected implementation or a predicted gain. Preserve research
leader `a4ecf096` / profile `6cb9dcaa` and all predecessors.

## The score dependency is real

Current `full_impl_prepare` dispatches the helpers, performs pawn/local work,
records owner readiness, optionally generates the original inventory, then joins.
Activity also supplies tempo. Only afterward does it publish retained terms,
stats/R and observers, compose the actual subtotal and finish the score. Geometry
may move earlier; these effects, numerical operations and their order must stay.
FAST also invokes finishing, with no helper interval available.

In [endgame.rs](../../src/endgame.rs), finishing first adds root preference and
identity variation. At endgame phase `E >= 192`, `material_blend`:

1. Selects pawn files from the actual subtotal sign, zero choosing White. Span
   coefficients are −10 for spans0–3, −6 for4, zero for5 and3 for6–8. With `c`, computes
   `floor((S * (4096 + (E - 192) * c) + 2048) / 4096)` in native wide arithmetic.
2. Selects a side again from that result. Pawnless potential uses truncating
   divisions of a nonnegative magnitude, then restores the sign. Minor-mate
   geometry can replace the value. The one-pawn/one-minor branch conditionally
   substitutes progress before floor division by two.
3. Applies the actual material blends: floor `(3*progress + 5*adjusted)/8` for
   matching rook material or opposite-bishop/rook material, or floor
   `(progress + adjusted)/2` for opposite single bishops. Those material tests
   ignore pawn counts. Progress can therefore change the final selected side.

`adjust` initializes bounds, performs its material draw-bound assignments, and
selects a side **from the blended score**, zero choosing White. Exactly one
ordered shape arm then applies. Do not forecast this side from material, turn or
a partial score, or replace bound assignments with a different algebraic form.
The geometry/effect split is:

| Native arm | Score-independent preparation, under its original population guards | Effect that must remain at the actual arm |
|---|---|---|
| Pawn race | Eligible pawn/rank and native race outcome; preserve empty and multi-file early returns before indexing | White win: `L=max(L,floor(S/4)+700)`; Black win: `U=min(U,floor(S/4)-700)`. White loss: `U=min(U,11-rank)`; Black loss: `L=max(L,rank-11)` |
| Bishop and pawns | Nonempty pawn file/rank, indexed bishop/kings and fortress predicate | Fortress bound `sign(side)*2*(9-rank)`: minimize White upper or maximize Black lower |
| Rook and one pawn against rook | Native predicate, guarded by both rooks and the single own pawn | Floor `S/4` |
| Rook against pawns | Native per-pawn reduction predicate; unchecked only | Floor `S/8` |
| Queen against one pawn | Native predicate, guarded by own queen, enemy pawn and kings | Fortress bound floor `3*S/32`, applied to the selected side's bound |

Pawn-span coefficients, minor-mate geometry and guarded bishop colors are also
pure, but preparing both colors can add scans never demanded by native finishing.
Bishop-pawn shapes can qualify both sides. Other shapes often identify only one
eligible side; eligibility still does not select the eventual numerical arm.

After the arm, retain native score/bound clamping, score clipping to ±7900,
halfmove scaling and side-relative score/bound conversion. Halfmove scaling after
11 is floor `(max(23*(100-h),0)*clipped + 1024)/2048`. Signed floor divisions must
not become Rust's truncating `/`, nor be moved across blends or sign selection.

## One concrete policy survives

Keep existing private coherent ordinary/Q FULL admission, owned packets and
inventory behavior. Public, FRESH, custom/observed, FAST-only, checked-Q and reused
Q routes acquire no eager obligation. No extra evaluation or Influence demand.

At the existing configured-colors3 private preparation seam, execute the winning
inventory decision first, unchanged. After that closure, and immediately before
the original completion call, admit geometry only when:

- existing private preparation/coherence permission holds, `E >= 192`, and the
  supplied native check flag is false;
- one side has zero pawns and exactly one rook with no knight, bishop or queen,
  while its opponent has at least one pawn; and
- one additional read-only, current-token completion probe says the pair is still
  pending. Errors follow existing failure handling; false readiness promises no
  duration of remaining slack.

The material condition permits **opposing nonpawns**. It identifies at most one
eligible side, since the opposite side has pawns. Carry only `None` or
`{ side, reduce: bool }` in this FULL activation. `Some(false)` is a computed
negative, distinct from unprepared. At the original post-blend arm, consume it
only if the actual selected side and rook-against-pawns arm match; otherwise use
native finishing. Apply floor division by eight there, never to an estimated
score. No persistent Node cache, key or generalized symbolic evaluator is needed.

Factor one native pure boolean predicate from the existing loop, shared by lazy
finishing and preparation. Keep the original score application shared too. A
small optional private finishing input is enough; other wrappers supply none.
This common-body change still costs branches, live storage and possible codegen
drift even where no geometry is prepared.

## Totality and ownership

`Position::validate` requires at most16 pieces and8 pawns per side, exactly one
king, valid distinct squares and coherent lists/mailbox/planes. Maintained private
ancestry plus the exact rook-material guard supplies both king indices and the
rook index. The nonempty opponent pawn list has at most8 entries. Point transforms,
distances and small additions are bounded; synthetic Point offsets here never
index the board. This argument covers admitted joined setups without assuming
orthodox reachability or adding an opposite-king/check probe.

Preserve a public extraction trap: `rook_against_pawns` currently returns before
indexing when checked, and its empty pawn loop also performs no king/rook access.
Do not hoist those accesses ahead of the short circuits while sharing the
predicate. The private shape guard does not strengthen public preconditions.

Preparation reads the same immutable Position while helpers read their owned
packets; it mutates no authoritative state or N/R charge. The activation-local
result survives no recursive call. Existing completion and reader retirement
remain authoritative on success, error and stop. The extra pure interval can
extend physical stop latency, but must add no logical poll or fabricated output.

## Economics and decision point

Finishing is demanded after successful late FULL, but this geometry is demanded
only for the actual selected arm. Inventory already occupies the same wait.
Putting geometry second preserves inventory's original decision, while leaving
less residual slack. The additional shape/probe, unused-side result, geometry
overrun, finishing option and source/layout changes can exceed any hidden work.
The native loop also exits on its first witness. Universal preparation makes
these costs larger without evidence of a useful population.

No existing evidence prices the intersection of private late unchecked FULL,
this material shape, post-inventory pending helpers and actual selected side.
The [full54 report](../../experiments/multicore-feasibility/writer-regions-own-pgo/report.md)
establishes the retained image's aggregate result, not this cost pool. Old sampled
joins/generation times, endgame case labels and reference whole-request timings
are different populations. Even aggregate finishing time would include FAST.
A future join timer inside `complete` would exclude eager inventory **and**
geometry; a shorter residual join alone would not demonstrate saved time.

Thus keep broad preparation parked. If work is later resumed and this hypothesis
selected, the smallest useful discriminator is the single policy above with
preserved and same-image off/on controls, including serial/common-finisher cost;
no new census or framework is justified now. This note selects no execution.

Source basis: writer-region source68, bound by its
[PGO preparation](../../experiments/multicore-feasibility/writer-regions-own-pgo/preparation.json).
`endgame.rs` SHA256 `4f382e7b5359f1956a0e155328aad08f35dab74252ee0794d61dafcd1cd2214a`
is identical in the canonical tree and retained source workspace;
`evaluator.rs` is `0c5308cd796e6f153c6eab3e799837ffedd5c4dd88cb1b8025c10ea744ea4c44`.
Relevant anchors: endgame192/224/280–504/529, evaluator664–833,
Position validation431–479 in that exact source. No implementation is adopted.

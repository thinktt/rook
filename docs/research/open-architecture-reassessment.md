# Open architecture reassessment: test certain-demand colors before another queue

2026-10-26. Source/evidence only under the restored mission; no engine edit,
prototype, build, native helper execution, timing or adoption. Accepted main and66/8f
remain preserved. Two disjoint Sol readers examined side partitioning and frontier
batches; Imp2 checked publication/inventory/null boundaries. This is a proposed
next discriminator, not authority to execute it.

**Recommend one fresh-publication colors-only3 experiment:** coordinator retains
pawn cache/local terms/finish; two helpers each compute one attacker color's
Activity and the opposite defender's Shelter term. Compare it with the positive
current2 and inline1. This is simpler and more certain-demand than adding legal
inventory first, and reaches all existing FULL calls, including root/Q. Wider
inventory dataflow remains genuinely untested; prior negatives did not combine it
with the positive FULL helper. No existing evidence establishes a win for either.

| Mechanism | Genuinely new opportunity | Remaining discriminator |
|---|---|---|
| Colors-only3 | Split the existing certain-demand helper chain; one immutable packet, two consumers | Pickup/join, side imbalance, coordinator critical path |
| Activity+inventory3 | Preserve current FULL helper while another helper prepares ordinary inventory | Shorter available overlap, discard/drain/list-return costs |
| Colors+inventory4 | Both additions together | Combined critical path, fan-out and inventory settlement |
| Prior-iteration frontier batches | Collect owned future inputs earlier and amortize batch publication, without private search/TT snapshots | New pure demand, lead time and collection/delivery costs remain unmeasured |

## Side split: independent chains, original rounding

In `src/activity.rs:94–157,163–179,240–243,453–508`, attacker color c writes only
marks[c]. Pressure for defender opposite(c) reads only those marks. A helper can
therefore perform c's existing per-kind/per-source mobility traversal, produce its
piece value, then compute opposite(c)'s pressure and Shelter term. Shelter's
components read Position/Influence, with no dependency on the other helper
(`src/shelter.rs:52–73,102–110,286–305`). No shared mark writes, mark exchange or
inter-helper barrier is needed.

Preserve source chronology, per-piece curves and all local division/rounding.
Keep the color raw sum before `(276*score+128).div_euclid(256)`. Return piece[c],
pressure[opposite(c)], Shelter term[opposite(c)] and local R. Coordinator performs
the existing cross-color Activity weighting/phase rounding and Shelter combine;
these formulas cannot be replaced by separately rounded signed contributions.
Pawn selection/collision chronology, retained writes, tempo, observer publication,
finish and one combined pawn+Activity R charge remain on their current owner
(`src/evaluator.rs:556–694`). FAST remains local; lazy refresh uses the same actual
FULL seam. No search/learning/TT/host-poll state is delegated.

Let P be owned publication, C the coordinator branch, A the old whole helper
chain, L pickup, J acquisition/join, and F the unchanged final composition. Both
models omit the common pre-publication Influence/material work; it is not hidden
by changing helpers. Then:

- Current2: `P2 + max(C, L+A) + J2 + F`.
- Colors3: `P3 + max(C, Lw+Aw, Lb+Ab) + J3 + M + F`, where M is cross-color
  weighting moved from the helper to the coordinator.

This is a dependency model, not measured latency. With unchanged transport and
placement costs, arithmetic savings are capped by the shorter color chain and
vanish if C dominates. Sparse/asymmetric pieces and ray lengths can produce
imbalance. The old350.98ns direct chain measurement used
pre-shared inputs; halving it does not predict native savings. The practical
own-PGO option's54-case64.369s vs accepted69.056s establishes a gain, not a
color/coordinator decomposition ([configured report](../../experiments/multicore-feasibility/configured-full/report.md)).

## Shared publication is a real ownership change

Current `evaluator_worker.rs:231–270,339–381` copies one owned Position/Influence
packet, then the sole helper takes it out of `Option<Packet>`. Two readers cannot
both take it. A replacement must retain one immutable packet until every admitted
consumer has acknowledged completion/discard, with per-consumer output/readiness
and terminal wake predicates. No lock may serialize all numerical kernels.
Reusable storage and search-lifetime ownership can avoid an allocation per call;
that is a design target, not a demonstrated free Arc/refcount protocol. Two remote
cache reads, pickups, completion signals and result acquisitions still cost.
Weights/material/supplied map must refresh for every actual FULL, including public
contrary maps and root rebinding. No slot reuse or new node publication before
both readers release it; failure and parked shutdown must drain both readers.

For inventory3, a single post-Influence publication can share Position with the
FULL consumer, but loses the old trial's Influence-overlap interval. Generation
itself reads only Position (`movegen.rs:634–712`), so an early Position publication
can start it before Influence. That requires staged readiness: Position immutable
first, Influence/material/weights published later in separate fields, with no
reader observing fields still being written. One allocation/Position copy does
not imply one release/pickup or zero additional cache traffic. This more complex
early protocol is not the recommended first experiment.

At ordinary entry the legal list is demanded only after FULL bounds and possible
threat/null cutoffs (`ordinary.rs:750–885`). The old inline census's191–370ns
median generation and positive slack do not show it fits the *shortened* parallel
FULL, much less colors3. The old inventory trial delivered99.86–100% of demanded
lists yet lost6.44% to current2, while explicitly replacing the FULL helper
([report](../../experiments/multicore-feasibility/same-node-inventory/report.md)).
It measured transfer/admission/locking/waste together; no individual overhead can
be declared removed merely by sharing a packet.

Generated counts/order/learning/TT/extension consumers remain at original demand.
Any extra inventory job must settle and release its shared slot before recursive
null entry; keep a completed parent list locally or in a proved unused per-ply
buffer until original demand/discard. Reusing that buffer might avoid the old
null-path Box, but needs an explicit same-ply/reentry proof and is unmeasured.
Other early returns drain/discard without logical charges. Preserve the prior
coherent-ancestry/king-domain admission rather than eagerly widening native input
execution. Checked Q has no evaluation overlap and reused reply lists are not new
generation. Colors3 avoids this entire speculative consumer/lifetime boundary.

## Frontier batches

A genuinely different source is an owned frontier input stream collected during
iteration d, expanded into *new* pure children while d and the prefix of d+1 run.
Ordinary→Q entry exposes Position (`ordinary.rs:719–742`); its worker-side one-ply
legal expansion does not need search, TT snapshots, learning or pawn selection.
A narrower alternative collects children skipped by frontier estimates after the
parent already has its full legal inventory (`ordinary.rs:867,997–1014`). A skipped
child is uncomputed at that visit, not necessarily absent from prior transpositions.
Nonchecked Q leaves have tactical rather than full legal lists, so expanding them
adds legal-generation cost (`quiescence.rs:316`). Preserve owned-input/king-victim
domain admission before eager child construction.

Retaining old values is ordinary memoization; dispatching first children only when
the current parent activates repeats the failed queue. Prior-iteration collection
instead offers earlier lead time and one parent Position plus move descriptors per
batch. It is genuinely untested, but no frontier catalog survives today: candidate
buffers are per-ply scratch, while root scheduling carries ranking/work, not a
frontier (`engine.rs:34`, `root_schedule.rs:209`). New costs include capture,
bounded storage/dedup, expansion, kernels, index/payload retention and demand lookup.

Exact root epoch/Position inputs must cover chronology/starting_units; chain use
must match actual supplied Influence/material/root weights. Canonical FAST/FULL
selection, finish and logical charges stay untouched. New iteration TT hits,
windows, cutoffs, ordering and extensions can remove demand. Starting batches only
after d ends supplies no guaranteed head start; streaming earlier adds remaining-d
lead time, but early stopping discards work and whole-batch publication may delay
its first useful result.

The old first6 queue's13–21% useful-task rates and19.50%/46.51% regressions do not
price earlier amortized publication; the coarse census's5.596ms ceiling does not
measure these new frontier inputs. Neither supports a positive forecast. If this
alternative is selected later, first use one predeclared bounded adjacent-iteration
cohort: collect owned parents/moves, produce pure children without search, join only
those bounded keys against prior production and actual next-iteration demand, and
report collection/expansion/storage cost plus new first-demand work and lead time.
No optimized consumer or parallel campaign is needed to establish whether useful
new work exists. All-ready matches alone would again be insufficient. Colors3 is
the stronger immediate discriminator because its actual demand is already known.

## Smallest useful next discriminator

If selected, make one shared numerical side seam with inline combination and a
reusable two-reader packet. Retain a matched current2 path and a preserved generic
control so serial/refactor/publication costs remain visible. Focused checks should
compare full component/pressure/Shelter/retained/R outputs, nonneutral/zero weights,
contrary maps, cache reuse/FRESH/root rebinding, asymmetric positions, delayed
readers, failure and packet-reuse/parking boundaries. No broad qualification yet.

One small same-image inline1/current2/colors3 original replay comparison, including
35/08/43, should measure complete search wall, all-thread CPU, startup/idle/joined
shutdown and original replay/work behavior. Sparse paired owner-ready/per-side-ready
observations can distinguish imbalance from pawn/transport limits; their
instrumentation must not be presented as an uninstrumented speed result. Do not
add inventory4, PGO, balancing policies or a parameter sweep to this discriminator.
If colors3 has no margin, that prices this decomposition/protocol, not all wider
same-node architectures. Scaling beyond these finite chains remains open.

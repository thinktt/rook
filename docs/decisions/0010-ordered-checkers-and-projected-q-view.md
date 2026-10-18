# Ordered checker identities and one projected Q view

Status: adopted in the exact105 source integration. Final own-PGO, cost and
gameplay qualification remain open.

Use the existing placement-owned tag planes for capped ordered checker
identities in complete and capped generation. Preserve pawn, knight and ray
order, adjacent-king interleaving, blockers and the exact first-two cap. The
public diagnostic classification retains its independent mailbox finder.
Persistent storage itself was selected by the matched experiments in decision0004;
this decision extends consumers of that representation.

In nonchecked quiescence, make one32-byte projected tag-plane view and use it
for both ordered check-route classification and final own-king safety. Remove
the projected mailbox and its two consumers together. Keep optimistic best
updates, eligibility, reply probing, prepared child, repetition/history,
recursive ordering and logical charges at their existing boundaries. Do not
infer moved-piece participation from membership beyond the first two routes.
No new position/search fields or child-plane handoff are introduced here.

The separate phase1 and phase2 trials pass broad independent mailbox oracles,
including pre-legality unsafe candidates, joined nonpawn EP, promotions,
adjacent kings and third-route/order witnesses. Their own-source PGO pilots
support composition: phase1 is1.227320% lower in summed medians; phase2 is
2.024566% lower, with all six phase2 observed ranges separated. These are
different artifact comparisons and their percentages are not added or
transferred.

The exact composed native1befaa6d passes158 native tests,54 strict replays and
eight interruption fixtures/24 searches. The105 frontend9809cb49 freshly passes
182 adapter tests and7519 unique cases across102 complete original files;
native43/tools23 reuse is byte-bound and independently reconciled. The source
integration also includes shared generation, fixed/seeded iteration and clock
transports. Source is103 files; operation count105 is a different measure.

Accepted codegen risks remain explicit: relative102, Q text grows226 bytes,
its frame shrinks32, and ordinary text grows144 with the same frame. Both add
one static call. The supplementary forced default fixed-loop object grows178
bytes with the same frame and two more static calls; seeded/observer branches
are pruned in that inspected body. Full evaluation retains its examined call
scope. Cumulative Stats/outcomes grow8 bytes relative95 and Search fields move
despite unchanged total size. Static allocation/memcpy referents do not prove
dynamic effects, frequencies or cost equivalence.

The direct generic95-to-composed comparison independently reconciles60 native
lifetimes:14.4239440s versus14.0816565s in summed case CPU medians,2.373051%
lower. All six medians improve and their observed sample ranges are separated.
This supports adopting the net change; it does not assign a speedup to each
component or establish universal improvement. Whole-suite siblingCPU15 has11
nonidle ticks, with no pervariant attribution. No cycle/CPI result is available.

Source promotion preserves the tested native43/tools23/frontend37 closure and
named frozen artifacts. It performs no canonical-path rebuild. The new root
scheduler, post lifecycle owner and projected-plane child transport remain
separate experiments. The canonical-command admission review for goOutcome,
broader production review and complete performance/gameplay gates remain open.

Evidence: [composition integration](../../evidence/ordered-q-actual-timed105-integration-20261018/README.md),
[matched generic cost](../../evidence/ordered-q-seeded103-combined-cpu-pilot-20261018/README.md),
[codegen scope](../../evidence/ordered-q-seeded103-combined-validation-20261018/codegen/report.md),
[whole105 validation](../../evidence/actual-timed105-bits-validation-preparation-20261018/report.md).

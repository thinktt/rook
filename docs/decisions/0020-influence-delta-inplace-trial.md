# Park in-place influence delta after experiment30

Retain candidate25. Experiment30 changes experiment29's by-value delta producer
to update the owned scratch map in place, preserving its private provenance,
fresh fallback and182 native tests. Actual lowering removes the updater-local
128-byte map and its return copy. An outlined fill still stages initialization
through a128-byte temporary, and its frame prologue now precedes the ready check.
Copy-stage removal alone does not establish a CPU benefit.

The independently matched generic70 pilot reports14.1134935→14.163152 seconds
in summed median native CPU (0.351851% higher), only2/7 lower case medians and
worst ratio1.026579. It fails all three frozen advancement criteria: aggregate
ratio≤0.995, at least5 lower cases, and worst≤1.02. All70 original strict replay
checks pass live and independently;14 warmups and56 measured samples remain.
No own-PGO, separate54/wire regression, full117,12-game gate or source promotion
follows. These local reported-only results do not establish final qualification.

Trials29 and30 use separate matched-control runs; their totals are not a causal
29→30 CPU comparison. A separately authorized diagnostic demand census is not
a production candidate or timing claim. See
[the decision evidence](../../evidence/influence-delta-inplace-decision-20261019-01/README.md)
and [compact checkpoint](../../evidence/influence-delta-inplace-checkpoint-20261019-01/README.md).

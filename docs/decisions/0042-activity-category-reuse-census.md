# Decline Activity category caching after encounter census

A category for a fixed color/kind/target can be reused within one immutable
Activity computation, but value identity alone does not establish worthwhile
reuse. A prior dense category producer was slower. The new diagnostic observes
completed direct calls without skipping or replacing the original classifier.

Three selected cases show repeat shares of2.0347%,1.7079% and0.0206%. In current51's
profile35 hotspot, adjusted repeats are only0.2810% of all classifications;
most repeats already use the cheap shortcut. Counter/value handling would also
charge first encounters. Decline the cache without implementation or timing.
These counts support this engineering choice; they do not predict CPU savings
or establish a universal bound.

All11 focused tests and three original live/offline replay pairs pass, with
independent raw/PID/count reconciliation. This is a diagnostic, not optimization57.
Production remains51 and its existing qualification obligations remain open.

See the [census report](../../evidence/current51-activity-category-census-20261020-01/README.md)
and [decision](../../evidence/current51-activity-category-census-20261020-01/decision.json).

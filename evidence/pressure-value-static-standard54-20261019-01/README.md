# Candidate40 standard54 local timing

Exact ordinaryc3166899 completes216 fresh lifetimes:54 excluded warmups and
162 measured samples, one natural search per lifetime. All432 offline original
checks pass, with2496 semantic posts. Search CPU sums70.500000s in case medians;
whole-native user+system CPU sums70.968677s. Whole-native wall sums71.178042s.
All samples/ranges remain in independent-reconciliation.json; timings.csv
supplies per-case medians.

Previous37 sums71.424373s whole-native CPU in a separate window. The new total
is0.638012%lower, a descriptive cross-window comparison, not a paired whole54
causal estimate. The matched own-PGO fixed70 independently showed0.877002%lower.

The historical generic RustPGO reference totals63.277733s search and63.431779s
whole CPU. Raw current/reference ratios are1.114136search and
1.118819whole. Different hardware/windows/accounting and unsettled comparison
uncertainty prevent formal qualification. Current12 costs remain pending.

Engine CPU14 and helper housekeeping affinities/identities are checked. Guest
CPU15 delta records32111 idle ticks and1 iowait tick, zero user/system/IRQ/softIRQ/
steal ticks. Finite guest observations do not establish exclusive host ownership.
PMU metrics remain unavailable. Native wait4 includes the small Python preexec
prefix; search uses10ms /proc ticks. Captured stdin.write excludes the cleanup
stdin.end quit; strict completion and direct normal exits remain verified.

All collection bytes are retained in a fully reopened closed-collection.tar.gz.
No new Bee result, external3288 run or final performance/gameplay qualification.

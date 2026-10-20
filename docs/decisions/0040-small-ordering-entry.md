# Park outer small-list ordering entry after experiment55

Experiment55 gives ordinary/Q ordering callers a preferred<=6 direct path to
the unchanged public sorter and copy. Larger lists call experiment54's exact
full-domain six-stream helper, including its existing inner small-list guard.
Callback chronology, preferred reversal, deferred suffix, opaque Move values,
workspace ownership and semantic charges remain unchanged.

The actual compiled ordinary/Q routes branch before helper entry. Small lists
avoid its six saved registers and56-byte reservation:104B of explicit stack
adjustment, excluding the return address. This is relative to54's helper route;
production51 already sorts small lists directly. Caller frames remain unchanged,
ordering bodies grow67/89B, and whole text grows1136B versus51. Large calls pay
both guards and helper arguments. These static facts imply no dynamic saving.

Twelve focused tests pass, including exact preferred counts0..7 and shared
large/small/large scratch reuse. All70 fresh original live/offline replay checks
and native receipts independently reconcile. The fixed generic case-median sums
are13.5667655 baseline51 and13.524396 candidate55 CPU seconds, a ratio of
0.9968769637832982:0.3123036%lower,6of7lower,worst1.002118181. The required
aggregate ratio<=0.995 fails. Park without retry, own-PGO or adoption; no full198
suite, diagnostic/broad qualification or whole54/12 timing follows.

Production remains51 at69.417194 whole54 and698.491201 whole12 CPU seconds in
prior separate local windows. Final behavioral/performance qualification and
external gameplay remain open. See the
[closed decision](../../evidence/ordering-small-entry-generic-decision-20261020-01/decision.json),
[independent screen](../../evidence/ordering-small-entry-generic-screen-20261020-01/independent-reconciliation.json)
and [backend review](../../evidence/ordering-small-entry-backend-review-20261020-01/review.md).

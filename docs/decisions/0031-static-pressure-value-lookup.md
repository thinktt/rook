# Stage shared static pressure lookup after generic timing

Experiment40 changes only activity.rs from retained37. A shared immutable
256-byte table replaces pressure-value arithmetic for all possible u8 marks;
all256 values match offline and all185 old tests remain exact. It differs from
rejected39 solely by const-to-static storage. Complete actual king_pressure
has direct table loads, no inner copy, and a16-byte smaller stack reservation.
The already-cheap knight path gains a dependent load, so profitability remained
an actual measurement question.

Two focused native checks and all70 original strict/live/offline pilot replays
pass. The fixed generic comparison independently sums13.9486585→13.8302790s
in whole-native CPU case medians:0.848680%lower,6/7lower,worst1.000070128.
The predeclared rule passes. Every sample is retained, with no retry/outlier
deletion. At that generic milestone, broad functional checks had not run for40.

Advance only to fresh source-matched PGO training/remerge/use and its separate
comparison against retained37 own-PGO54be6552. No generic improvement transfers
to PGO, production or qualification. Retained37 remains unchanged. See the
[generic decision and samples](../../evidence/pressure-value-static-generic-decision-20261019-01/README.md)
and [actual backend](../../evidence/pressure-value-static-backend-review-20261019-01/report.md).

Fresh own-source PGO now passes the same separately frozen rule:12.4871975→
12.3776845seconds,0.877002%lower,7/7lower,worst0.995248202. All70 strict
original/offline checks reconcile. Full185 native tests and optimized54/wire24
subsequently pass. Mandatory117/7673 and regular12 pre-gate remain in progress;
retained37 stays production until their independent closures. See the
[PGO milestone](../../evidence/pressure-value-static-pgo-milestone-20261019-01/README.md).

All broad functional gates subsequently pass:185native/209diagnostic tests,
7673cases/117operations/115wholefiles, optimized54/eight-wire24 and regular12/
632searches,continuity8 and seed11/persistence3. Parent independently reopens
both complete source/fixture archives, all30796 conformance archive members
and all215 regression/pre-gate archive members. Exact source115 graph7c022b82
is integrated, changing only activity.rs. Retain ordinaryc3166899 and companion
a8720c47 as tested isolated-path immutable artifacts. No canonical rebuild is
implied. Full40 whole54 timing remains pending; final performance, production
review and external3288 qualification remain open. See the
[source promotion](../../evidence/pressure-value-static-integration-20261019-01/source-promotion.json).

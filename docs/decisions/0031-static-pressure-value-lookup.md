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
deletion. Full185/117/54/wire/games have not run for40.

Advance only to fresh source-matched PGO training/remerge/use and its separate
comparison against retained37 own-PGO54be6552. No generic improvement transfers
to PGO, production or qualification. Retained37 remains unchanged. See the
[generic decision and samples](../../evidence/pressure-value-static-generic-decision-20261019-01/README.md)
and [actual backend](../../evidence/pressure-value-static-backend-review-20261019-01/report.md).

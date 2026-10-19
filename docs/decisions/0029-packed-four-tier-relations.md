# Park packed four-tier relations after generic timing

Experiment38 packs the four relation tiers for each original byte pair into one
byte, shrinking the immutable payload from262144 to65536 bytes. Only native
influence.rs/relation_table.rs change from retained37. Safe enum decoding keeps
King dispatch before the opponent-zero shortcut, all five saturating exclusions,
caller charges and public contracts. No mutable state or ownership changes.

Offline exhaustive checks and two focused native tests pass. All185 old test
bodies remain exact, but the complete186-test suite was not run. Actual generic
code has the intended single64KiB table and unchanged observed frames; numeric
activity consumers add branches or conditional moves. Smaller data alone does
not establish a saving.

The fixed70 comparison independently sums13.8680260→13.9646995s in case-median
whole-native CPU:0.697096%higher,1/7lower,worst1.01273664. All original strict
replays/accounting pass, but aggregate<=0.995 and>=5lower fail. Park without
retry, decoder retuning, own-PGO, full186/117/54/wire/games or source promotion.
This is a generic prescreen against generic37, not a comparison of production
PGO binaries. Retained37 and its qualification boundaries remain unchanged.

See the [closed decision and samples](../../evidence/packed-four-tier-relations-generic-decision-20261019-01/README.md)
and [actual backend report](../../evidence/packed-four-tier-relations-backend-review-20261019-01/report.md).

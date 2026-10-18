# Formula-derived relation state table — source preparation only

This isolated prototype is uncompiled, untested and unmeasured. Root native
source and the live full12 CPU collection remain unchanged. `prepared.json`
binds the baseline, exact prototype source/tools, generator and independently
read-back archive. The generator reads no fixture or expected-answer data.

EVAL-RELATIONS depends only on capped multiplicity and least-value tier for
each normalized profile. The byte domain therefore has16 feature states:
empty; multiplicities1..4 for pawn/minor/rook least tiers; multiplicities1..2
for queen; and multiplicity1 for weak. A256-byte profile-to-class map and four
16-by16 one-byte outcome arrays occupy1280 bytes. This is a smaller candidate
than the earlier262144-byte direct-pair table, with two additional dependent
class loads. Lower footprint does not establish lower CPU cost.

The existing opponent-zero shortcut remains. Adjusted exclusion still saturates
the original normalized byte before classification; merged class identities
cannot replace that subtraction. Uncapped profile sums, influence production,
activity/query selection and all semantic charges remain unchanged. Position
and Node sizes, chronology, fingerprints and mutable cache/table state are
unchanged. This is a pure function implementation experiment.

After the original collection handle37105 is authoritatively terminal, run
all128 library and two development-CLI tests. The existing independent digit
oracle exhausts every byte pair, all four tested tiers, bishop/minor equality
and every adjusted-removal category. Freeze the generic native image/source,
run all54 strict public replays, then compare the same six declared pilot
cases against generic e7344948 with an excluded warmup and balanced repeats.
Preserve failures and all samples. No PGO or production adoption is implied.

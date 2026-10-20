# Park the aggregate pawn Influence seed

Experiment58 seeds fresh bit counters from two edge-correct directional pawn
masks, preserving overlap as XOR/AND planes6/7. Existing scalar no-slider and
pawn-empty branches remain. No persistent state or map authority changes.
Independent source review and196 library tests support the bounded change.
An initial new test used parser-rejected backrank pawns; the preserved failure
was corrected only in the fixture. Pure constructor tests retain all backranks.
The necessary verification rebuild produced byte-identical ordinary code.

Actual generic code removes the pawn loop but grows the producer104B and common
stack frame16B. The compiler hoists a kind-only decode before the source guards.
Existing result transfers remain. These facts do not identify the cause of the
measured outcome.

The sole fixed70 comparison passes all original live/offline behavioral replays,
but improves summed CPU medians only0.171598%, with4of7 lower cases and worst
ratio1.017251803. It fails the preset0.5%aggregate and minimum5lower gates.
Park without retry, own-PGO, full54/12 measurements or adoption. Production57,
its exact source and its69.051049/689.783349 whole CPU results remain current.
See the [decision](../../evidence/pawn-influence-seed-generic-decision-20261020-01/decision.json)
and [independent timing reconciliation](../../evidence/pawn-influence-seed-generic-screen-20261020-01/independent-reconciliation.json).

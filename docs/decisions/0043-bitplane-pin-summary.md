# Advance the placement-plane pin summary to own-source PGO

Experiment57 replaces the unchecked legal generator's mailbox pin scan with
nearest/next occupied-square extraction on existing placement planes. The first
piece must be own; the second must be an enemy matching bishop/rook/queen. This
is exactly the old sole-blocker rule under the existing plane/mailbox invariant.
No new state or cache is added. All checked-node, king, EP, promotion, castling,
ordering and semantic work behavior retains its current owner.

All193 library tests pass. Actual normal and bounded consumers call the changed
shared summary, which is2548B smaller with16B more stack. The sole generic fixed70
screen passes all original live/offline replays and native accounting:1.0570045%
lower summed CPU medians, all7cases lower. It passes the predeclared advancement
gates, so select fresh own-source PGO and a separate matched70 comparison.
Production stays51; no generic result transfers to PGO or the full54/12 corpus.

The source-level stale-plane counterexample remains a proof limit. A false check
flag does not certify geometry; actual Position constructors/recomputation and
maintained transitions supply the imported invariant.

See the [closed generic report](../../evidence/bitplane-pin-summary-generic-checkpoint-20261020-01/README.md),
[generic decision](../../evidence/bitplane-pin-summary-generic-decision-20261020-01/decision.json)
and [PGO selection](../../evidence/bitplane-pin-summary-pgo-selection-20261020-01/selection.json).

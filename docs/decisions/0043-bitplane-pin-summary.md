# Retain the placement-plane pin summary

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

Fresh own-source PGO now passes54 training/original raw/profile checks and an
independent byte-identical remerge. The intended mechanism remains in both real
optimized consumers. The first own-PGO fixed70 comparison passes original
live/offline replays at1.1563291%lower CPU medians,7of7lower,worst0.992175033.
Advance to full functional validation and the regular12 pregate. Production
remains51 until every required validation gate passes; full54/12 performance
and final qualification remain separate.

See the [own-PGO checkpoint](../../evidence/bitplane-pin-summary-pgo-checkpoint-20261020-01/README.md)
and [full-validation admission](../../evidence/bitplane-pin-summary-pgo-decision-20261020-01/decision.json).

The full validation and regular12 pre-gate now independently pass: fresh195
native/209 diagnostic tests, all7673 mandatory cases across117operations and
115wholefiles, optimized54/eight-wire24, regular12/632 and continuity8/seed11/
persistence3. Every raw output/exit is reconciled. Retain57 by exact two-file
promotion and full117 equality; all115 other files are unchanged. No canonical
rebuild is claimed. Full57 whole54/12 measurements remain pending, with51's
69.417194/698.491201whole CPU seconds still the best completed results.
The scoped production review supports the geometric identity under the imported
coherent canonical Position invariant. All inherited domain/composition and
final performance/external3288 obligations remain open.

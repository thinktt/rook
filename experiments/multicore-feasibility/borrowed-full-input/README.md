# Scoped borrowed FULL-input discriminator

Prepared, not yet executed. Positive epoch64 remains preserved; both new modes
use the same enclosing per-call guard/owner body and original color kernels.
`--borrow-full-inputs` switches new mode3 from genuine input snapshots to guarded
caller input references. The private guard retires both actual readers on every
return/error/unwind before either input borrow ends, including under outer search
activation. Legacy token dispatch is always owned. This introduces no additional
arithmetic width or search-state replication.

See [plan](plan.md), [ownership proof](ownership-proof.md), [safe evaluator proof](evaluator-proof.md),
[source review](source-review.md) and [frozen inputs](preparation.json). Reproduction
source is [source.patch](source.patch) against the positive64 inventory, not an
edit to canonical source. Raw evidence/binary output belongs outside Git at
`/home/legolas/rook2-experiments/borrowed-full-input-20261026-01`.

The finite selected lane is49 focused controls, one ordinary generic panic-abort
build,14CLI controls/two original08 affinity fallbacks, then original35/08/43
preserved3/scoped-owned3/scoped-borrowed3:36 replay lives plus3idle. One3600s native
clock, no repeated completed life or tuning. The focused test-build unwind
controls do not claim recovery for production panic-abort. No PGO, adoption,
broad qualification or external action is selected.

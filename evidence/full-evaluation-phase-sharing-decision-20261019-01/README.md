# Experiment26: full-evaluation phase sharing

Parked after the generic seven-case CPU prescreen. Candidate25 remains the
retained production source and immutable own-PGO package. The trial reuses the
full evaluator's existing Phase across activity, shelter, pawn terms and opening
patterns; it adds no stored state or new computation policy.

Candidate25 generic `2940ae5c` totals **14.1149620s** in seven case medians.
Experiment26 generic `a26e8bef` totals **14.0856475s**, **0.207684% lower**.
Five cases are lower and the worst ratio is1.000951, but the fixed advancement
rule also requires aggregate ratio<=0.995 (at least0.5% lower). The trial fails
that requirement. There were70 fresh native lifetimes:14 excluded warmups and
56 measured samples. No retries, discarded outliers or threshold changes.

|Case|Candidate25 generic CPU median(s)|Experiment26 generic CPU median(s)|Lower by|
|---|---:|---:|---:|
|profile-01|1.0699520|1.0598420|+0.945%|
|profile-02|0.7354210|0.7289210|+0.884%|
|profile-04|4.5683870|4.5555850|+0.280%|
|profile-05|2.4861120|2.4873710|-0.051%|
|profile-29|0.2507355|0.2501580|+0.230%|
|profile-35|4.6106165|4.6150010|-0.095%|
|profile-08|0.3937380|0.3887695|+1.262%|

The exact same compiler/target settings were used. CPU is native wait4 user+sys,
including startup and the disclosed tiny Python pre-exec interval. These figures
are not the search-only full54 totals quoted for the delivered own-PGO package.
All70 original strict replay checks passed during collection and independently
passed again offline; raw accounting, images, samples and fixed rule reconcile.
Actual collection session44137:0eb414 -> ad0185/0; independent reconciliation
992d87/0. See the complete raw pilot and its immutable plan.

Before timing, the generic trial passed178 native tests,54 strict replays and
eight interruption fixtures/24 searches. Fresh diagnostic work passed209 units
and all7673 cases/117 operations/115 whole files; independent raw reconciliation
passed (95818:bac4df -> d07103/0). The frozen direct178-test repeat closes the
original Cargo output-identity limitation; it is not an additional178 unique
tests. Exact diagnostic image is9bd64dc6, combined112-source graph1209104b.

Actual generic lowering removed the selected duplicate phase derivations but
increased full-evaluator stack traffic and the patterns frame. Static savings
did not establish a useful measured net gain. The checked-node shortcut was a
separate rejected design idea, never this binary. No own-PGO build/training,
12-game pre-gate or promotion is performed for experiment26. Its unused PGO
preparation is preserved separately with launch clearance false.

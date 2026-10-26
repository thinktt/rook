# Fixed epoch-slot colors transport

Status: closed; [results](report.md), [summary](results.json), [bound identities](closure.json).
32 fresh controls,13CLI+2affinity controls and fixed48+4/560posts pass firstattempt.
Epoch3 median sum7.735016s vs old3 8.368089s/current2 8.029709s:7.57%/3.67% lower,
with1.445x current2 CPU. Retain for separately selected own-PGO/full54; no adoption.
[Plan](plan.md), [policy](policy.json), [reviewed ownership proof](ownership-proof.md).
One isolated transport change compares against preserved old colors3 and sibling
current2/inline. No numerical changes, tuning campaign or production adoption.

Only `src/colors_worker.rs` differs across the64-file source map. Apply the
zero-context patch to the retained old colors source using
`git apply --unidiff-zero prototype.patch`. New focused scope is21 protocol plus
11 actual Evaluator/scope controls; baseline numerical bodies remain unchanged.

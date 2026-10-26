# Fixed epoch-slot colors transport

Status: implementation/tool preparation, before any build or native run.
[Plan](plan.md), [policy](policy.json), [reviewed ownership proof](ownership-proof.md).
One isolated transport change compares against preserved old colors3 and sibling
current2/inline. No numerical changes, tuning campaign or production adoption.

Only `src/colors_worker.rs` differs across the64-file source map. Apply the
zero-context patch to the retained old colors source using
`git apply --unidiff-zero prototype.patch`. New focused scope is21 protocol plus
11 actual Evaluator/scope controls; baseline numerical bodies remain unchanged.

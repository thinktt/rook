# Park experiment60: Activity kind totals returned by value

A six-argument noinline typed accumulator returns local score/query scalars;
the caller immediately adds each pair in the original color/kind order. Only
activity.rs changes; old owner bodies/tests are retained and two old-piecewise
aggregation oracle controls pass with all195 library tests. Actual machine code
confirms six register inputs and RAX/RDX returns, with eight unconditional
empty-inclusive calls and scalar spills. Caller plus four group bodies grow
7884→8679 bytes; maximum scoped active frame chain remains504 bytes.

The one fixed70 generic comparison gives13.3564595s control versus13.494918s
candidate,1.0366407355% higher,0/7 lower and worst ratio1.0236420387. All70
fresh processes pass original live and independently rerun offline oracles.
This fails the frozen aggregate≤.995, minimum5 lower and worst≤1.02 gates.
No retries, retuning, PGO, broad qualification or source adoption follow.

Production57 and its117 source hashes are unchanged. Best completed whole54
remains69.051049s; whole12 remains689.783349s. This seven-case pilot does not
replace either whole-corpus result or establish final qualification.

See [decision evidence](../../evidence/activity-kind-return-generic-decision-20261020-01/decision.json) and [full backend review](../../evidence/activity-kind-return-backend-review-20261020-01/review.md).

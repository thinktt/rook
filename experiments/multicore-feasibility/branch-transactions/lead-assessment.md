# Lead assessment: capped logs do not explain away this sample

The unchanged whole-branch transaction pilot is negative for the observed sample.
The [original report](report.md) correctly records zero accepted ahead tasks and
large certificate overflow. Its suggestion that those caps obscure substantial
potential reuse needs qualification: independent canonical executions already
provide another necessary test, even when the certificate is incomplete.

On 2026-10-24, all six raw stdout hashes were verified against the committed
[results.json](results.json). Filtering their candidate records to
`ahead_distance > 0` gives:

- 36 ahead tasks, containing 330063 speculative nodes and 197310 canonical nodes.
- 34 have different speculative and canonical node counts. They cannot be
  accepted as unchanged whole-branch transactions with their recorded work deltas.
- All 12 ahead tasks with overflowed certificates are among those 34.
- Only profile08/queue2/index4 (85 nodes) and profile04/queue2/index5 (975 nodes)
  have equal node counts. Both were rejected for changed complete move order.
  Equal node counts alone do not establish equal relation work, control flow,
  outputs or state, and do not establish that either task could be accepted.

Those two tasks contain 1060 of 197310 canonical ahead nodes (0.537%). Their
observed canonical execution time totals 1051299ns out of 238070442ns (0.442%).
These elapsed observations are not statistical timing estimates. They bound the
observed cost still eligible under this necessary equality check, not the possible
gain of another algorithm or unseen workload. No new native execution was used.

Decision: do not enlarge the log cap or build a general executor for this unchanged
whole-branch design from these results. Cheaper snapshots and compact events could
reduce prototype overhead, but would not fix the observed work disagreement.
Different roots, deeper iterations and other task boundaries remain untested.

The next promising question is whether speculative work can provide useful pure
calculations even when its complete branch cannot commit. Study actual demand,
reuse, wasted work and delivery cost before implementing a scheduler. Distinguish
direct child preparation from a shadow branch that predicts future demands; neither
should be described as successful whole-branch transaction reuse. Preserve the
positive integrated FULL split as the separate demonstrated research baseline.

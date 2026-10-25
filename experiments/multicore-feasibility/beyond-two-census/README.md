# Ordinary/Q branch-work census

Bounded count-only discriminator for the restarted scalable-queue research.
This is neither an executor nor a performance/qualification run. The successful
configured FULL split remains preserved; canonical engine source is unchanged.

The trial starts at `b87a7126be2639623796999c633027dedb059996`, whose engine source
matches frozen66. `prototype.patch` binds the isolated opt-in
`branch-work-census` instrumentation. Source readers' findings are checkpointed
at `9e321052b47eb3a05bf75e23c297d23138d1155b`:

- [Work-distribution design](../../../docs/research/beyond-two-work-distribution-design.md).
- [Actual transaction conflicts](../../../docs/research/beyond-two-transaction-conflicts.md).
- [Lead Q-window hypothesis](../../../docs/research/q-window-reuse-hypothesis.md),
  an alternative under source investigation, without a selected executor.

The census records charged ordinary and Q calls, complete/partial subtree sizes,
native N/R, actual FULL/FAST/map demand, early returns, and candidate groups.
Scout and retry share one ordinary-main candidate item; IIO passes, mate probes,
and recursive Q groups are separate. Ordinary-to-Q handoffs receive no duplicate
ordinary node. Forest totals, exclusive costs, and each separate fixed-ply cut
must agree. Inclusive populations and all-parent sibling widths overlap and
cannot be summed as independent available work.

Retrospective substantial siblings are counted at N thresholds 32/128/512/2048/
8192. Separate ordinary-main direct-Q cohorts expose full-window/no-retry/no-tail-
IIO opportunity without treating extended or interrupted children as equivalent.
Q roots report an optimistic node span: local charged N plus maximum immediate
Q-child span, assuming visited siblings were magically ready. It is not a CPU
speedup bound. Deterministic bounded samples illustrate groups; summaries count
the complete observed population.

One frozen generic instrumented image runs original profiles35/08/43 once each,
with `--threads=2`, coordinator14, FULL helper6, siblings15/7 idle, and supervisors
on0–5,8–13. External placement gating and original replay checking are reused.
Guest placement does not establish host isolation. Count collection is capped at
180 seconds per life,900 seconds for the three-case stream,4MiB per census.
The pipeline has a1800-second overall ceiling and stops on failures. Focused
counter/equality tests precede the build and collection; no PGO, repeats, retuning,
full suites, or instrumented speed comparisons are selected.

Reproduce the selected lane from a fresh output directory after applying the
patch to the stated baseline:

```bash
taskset -c 0-5,8-13 /usr/bin/python3 experiments/multicore-feasibility/beyond-two-census/pipeline.py \
  --crate /absolute/path/to/isolated/trial \
  --output /absolute/path/to/fresh/evidence \
  --test-selector branch_work_census::tests
```

`build.py` archives exact source, tools, compiler options and protected baseline
hashes. `collect.py` retains original streams, native accounting, placement and
bounded census JSON. `reconcile.py` independently checks source/artifact pins,
raw replay, native lifetimes, and count partitions. `pipeline.py` supervises the
finite lane without retries. Raw receipts, binaries and build trees remain under
`/home/legolas/rook2-experiments/beyond-two-census-20261025-02`.

The first focused-test compilation failed before tests or workload lives ran;
its01 receipts are preserved and bound in `preparation.json`. The repair changes
only test-body type assumptions. The continuation uses fresh02 evidence.

Status: prepared for the continuation. Results and the next queue
recommendation will be recorded after independent closure.

# First integrated FULL Activity–Shelter experiment

One optional worker seam lives in the existing evaluator. Budget1 executes the
shared chain inline with no worker; budget2 has one coordinator plus a persistent
worker pinned CPU6. The ordinary research CLI accepts `--research-threads=1|2`;
default1 remains serial. A fresh owned packet copies the actual Position,
authoritative supplied Influence, material and current mobility/shelter weights.
Dispatch precedes the coordinator's pawn-cache selection, and joining precedes
its existing tempo, retained updates, relation ledger and finishing computation.
There is one composition body and no worker access to search/TT/history/Host.

This prototype deliberately busy-spins between jobs and searches. Startup,
completion and shutdown waits have a bounded fatal failure policy; Drop joins.
No idle-policy or transport sweep is selected. One-thread refactor cost and all
fresh publication costs must be measured, not inferred from the earlier corpus
probe. No accepted main or release artifact is modified.

## Build and focused checks

The executed pre-integration control is a core-source archive from`aa3d9483`,
which retains engine source from accepted main`a3de19d0`. The candidate is copied
to the same external build-source path before a fresh separate-target build.
Both use `/usr/bin/cargo` and Debian Rust1.85.1/LLVM19.1.7, generic x86-64,
O3/ThinLTO/oneCGU/panic-abort/debug1, no PGO and no external engine dependencies.
The raw source maps/build receipts preserve both snapshots. Relevant tests are
`cargo test --offline --lib evaluator:: -- --test-threads=1`, including focused
budget1/2 comparisons of components, finishing, retained/R, weights, supplied
maps, cache collision/reuse, rebinding and repeated/early-stopped searches.

## Measurement

After focused checks pass, run one stream with original cases35,08 and04,
contrasting checked/generation and evaluation workload families from prior
screens. `collect.py` keeps each original personality, allowance, work-clock mode,
post/move oracle and natural seed behavior. One warmup/config/case is excluded;
three measured repetitions interleave the3 configurations in a rotating order.
No case is retried. The original released replay checker owns behavioral assertions.

```sh
taskset -c 0-5,8-13 python3 experiments/multicore-feasibility/integration/collect.py \
  --control /external/target-control/x86_64-unknown-linux-gnu/release/rook2 \
  --candidate /external/target-candidate/x86_64-unknown-linux-gnu/release/rook2 \
  --output /external/ABSENT-result-directory
```

Search wall time spans the existing tap's timestamp before original go-write to
its move-data callback. `account_threads.py` adapts the existing wait4 supervisor
only to accept the declared one/two native threads, observe their14/6 affinities,
and preserve that identity in receipts. Whole-process CPU includes all worker
threads, including idle spinning, and startup/setup/shutdown. RSS is whole-process
peak. The tap CPU tick samples are not the primary CPU metric. A separate250ms
idle probe/configuration observes actual process ticks; it does not alter the
selected search inputs. Startup/exit controller timings are inclusive observations,
not isolated worker-only costs.

Coordinator14/worker6, no owned work15/7, helpers0-5,8-13. Guest topology and point
observations cannot establish continuous host isolation. The collector is bounded
by30 minutes and existing original replay limits, with raw stream caps and owned
cleanup on failure. No full suite, full54/12 collection, PGO or new transport is
selected. Raw runs/build products go outside Git under
`/home/legolas/rook2-experiments/multicore-first-integration-20261024-01/`.

Completed outcome: [report.md](report.md) and [results.json](results.json). `reconcile.py RAW-MEASUREMENT-DIR` rechecks the original captured receipts without running an engine.

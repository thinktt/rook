# Unchanged writer-region own-PGO/full54

Frozen scope is in [plan.md](plan.md) and [policy.json](policy.json).
No result yet. Raw images/profiles/runs remain outside Git at
`/home/legolas/rook2-experiments/writer-regions-own-pgo-20261026-01`.

Prepare once, collect once using the same persisted deadline:

```sh
taskset -c 0-3,8-13 python3 experiments/multicore-feasibility/writer-regions-own-pgo/prepare.py --preparation /home/legolas/rook2-multicore/experiments/multicore-feasibility/writer-regions-own-pgo/preparation.json --output /home/legolas/rook2-experiments/writer-regions-own-pgo-20261026-01 --stage prepare
taskset -c 0-3,8-13 python3 experiments/multicore-feasibility/writer-regions-own-pgo/prepare.py --preparation /home/legolas/rook2-multicore/experiments/multicore-feasibility/writer-regions-own-pgo/preparation.json --output /home/legolas/rook2-experiments/writer-regions-own-pgo-20261026-01 --stage collect
```

One216 training mixture/canonical+actual remerge/use build, cheap admissions,
fixed270+5. No source/layout/profile retune or adoption.

# Q owner-local own-PGO discriminator

Frozen scope is in [plan.md](plan.md) and [policy.json](policy.json).
Exact68 source and prior control/evidence bindings are in `preparation.json`.
Raw data, images and profiles belong outside Git at
`/home/legolas/rook2-experiments/q-owner-local-own-pgo-20261026-01`.

Prepare once, then collect once under the same persisted3600s clock:

```sh
taskset -c 0-3,8-13 python3 experiments/multicore-feasibility/q-owner-local-own-pgo/prepare.py --preparation /home/legolas/rook2-multicore/experiments/multicore-feasibility/q-owner-local-own-pgo/preparation.json --output /home/legolas/rook2-experiments/q-owner-local-own-pgo-20261026-01 --stage prepare
taskset -c 0-3,8-13 python3 experiments/multicore-feasibility/q-owner-local-own-pgo/prepare.py --preparation /home/legolas/rook2-multicore/experiments/multicore-feasibility/q-owner-local-own-pgo/preparation.json --output /home/legolas/rook2-experiments/q-owner-local-own-pgo-20261026-01 --stage collect
```

No timing, qualification or adoption claim is made by this setup record.

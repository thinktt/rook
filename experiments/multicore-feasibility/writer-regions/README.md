# Fixed eight-region transport

Selected generic discriminator; no result yet.
[Plan](plan.md), [ownership](ownership-proof.md),
[design](../../../docs/research/writer-owned-transport-layout.md).

Source `/home/legolas/rook2-experiments/workspaces/writer-regions-20261026-01`.
Raw `/home/legolas/rook2-experiments/writer-regions-20261026-01`.
After freeze and quiet announcement, run each existing supervised stage once:

```sh
taskset -c 0-3,8-13 python3 experiments/multicore-feasibility/writer-regions/native.py prepare
taskset -c 0-3,8-13 python3 experiments/multicore-feasibility/writer-regions/native.py collect
```

Both use the original persisted deadline and restore selected housekeeping.

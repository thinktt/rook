# Two-fence completion notification

One selected generic discriminator; no result yet.
[Plan](plan.md), [ownership proof](ownership-proof.md),
[independent challenge](independent-challenge.md), [source patch](source.patch).

The publisher-only variant is unsound. This candidate includes both the publisher
SC fence and an explicit cold-waiter SC fence after every registration.

Source: `/home/legolas/rook2-experiments/workspaces/completion-fence-20261026-01`.
Raw output: `/home/legolas/rook2-experiments/completion-fence-20261026-01`.

Run the existing supervised stages once, after the quiet-window announcement:

```sh
taskset -c 0-3,8-13 python3 experiments/multicore-feasibility/completion-fence/native.py prepare
taskset -c 0-3,8-13 python3 experiments/multicore-feasibility/completion-fence/native.py collect
```

Both stages use the same persisted deadline. The launcher restores selected
user-owned housekeeping affinities; it changes no host/global settings.

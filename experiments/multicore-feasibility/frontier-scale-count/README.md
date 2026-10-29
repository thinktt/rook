# Aggregate frontier scale observation

Selected implementation and one original35 replay; results pending. This isolates
constant-storage E6/S6/M7/F7 and6/7 boundaries on exact single-owner69. No keys,
payloads, snapshots, per-node clocks, service model or executor.

[Plan](plan.md), [policy](policy.json), [source freeze](preparation.json).
Raw: `/home/legolas/rook2-experiments/frontier-scale-count-20261029-01`.
Source: `/home/legolas/rook2-experiments/workspaces/frontier-scale-count-20261029-01`.
Source patch is applied over single-owner69 with `git apply --unidiff-zero`.
Native activation must follow frozen setup and quiet announcement. Only one
fresh original35 request is authorized; no repeats or automatic follow-on.

# Old-layout storage without observations

Closed mixed result. Search-wall median sums retained3/observed3/observed4/
lean3/fixed3/fixed4:7.716113/7.856971/7.799535/8.243957/7.817264/7.721670s.
Fixed3 recovers 5.18% versus lean3; fixed4 gains 1.22% versus sibling3 but remains
0.072% above retained3 at 1.334x CPU. Preserve without promotion or another lane.

Compiled old allocation/hot offsets match before timing. 40 controls+15 CLI+
2fallback and72 replay lives/840posts+6idle pass; one pre-data manual operand
check correction is preserved. No source change, completed-life repeat or reset.
[Report](report.md), [ranges](timings.csv), [results](results.json),
[closure](closure.json), [plan](plan.md), [policy](policy.json),
[source review](source-review.md), [layout reference](layout-reference.json).
The patch is relative to lean65; use git apply --unidiff-zero.
Raw: `/home/legolas/rook2-experiments/fixed-layout-no-observations-20261026-01`.
Keep 67d/profile948747 as strongest full54 candidate; no PGO, padding sweep,
broad qualification, adoption or external action. Native work is stopped.

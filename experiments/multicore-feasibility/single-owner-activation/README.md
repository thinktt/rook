# Single-owner activation: tentative generic result

New3 is **0.5223% lower** than preserved writer3 in the three-case median sum:
7.355324s versus7.393941s, with all three ranges overlapping. New inline1 costs
0.2041%. This does not isolate a lock/cache saving or establish a production gain.
Research leader a4ecf096/profile6cb9dcaa and all old artifacts remain preserved.

[Report](report.md), [ranges](case-ranges.csv), [results](results.json),
[closure](closure.json), [actual layout](production-layout.json),
[plan](plan.md), [policy](policy.json), [preparation](preparation.json),
[source patch](source.patch), [ownership proof](ownership-proof.md),
[test-only repair](test-repair.json).

All70 selected logical controls pass across71 executions (one preserved fixture
failure, then its exact repair);14 CLI/two fallback admissions, cold layout and
48replay/560posts+4idle pass. Initial setup15c11c98 and repair c1b1a949 share the
original native clock. No completed test control or wire request is repeated.
No native job remains; quiet window is released. The lead separately selected
unchanged-source own-PGO/full54; no source retune/adoption/qualification follows.

Source69: `/home/legolas/rook2-experiments/workspaces/single-owner-20261028-01`.
Raw/image: `/home/legolas/rook2-experiments/single-owner-20261028-01`.
Canonical branch source and accepted main/release remain unchanged. Reconstruct
the derivative by copying the68 verified controlSource paths and applying
source.patch with `patch -p1`; the existing external workspace is preserved.
Frozen source/tool admission and continuation scripts retain the failed receipt
and original clock. Results are finite research evidence, not a broader gate.

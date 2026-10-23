# Static glibc in Alpine: CPU14 performance

The existing optimized **non-PGO** static-glibc main binary passed both selected
lanes inside Alpine. The entire container, including collectors and supervisors,
was restricted to CPU14 as requested; no work was assigned to CPU15.

| Workload | Native CPU | Native wall | Result |
|---|---:|---:|---|
| Standard54, sum of per-case medians |77.554450 s|77.973047 s|54 cases, 216 fresh processes, 162 measured samples pass|
| Single 12-game pass, sum of lifetimes |781.715662 s|786.921638 s|632 searches and 5801 posts pass|

Standard54 excludes one warmup per case and measures three fresh repetitions.
The 12-game pass runs once per complete game, preserving state within each game;
its total is not a median estimate. Times cover the native process lifetime,
including setup/exit and a small pre-exec prefix, not only go-to-move intervals
or total container runtime. No native runs were repeated after collection.

Main SHA256: `3094bf0180162d081d3b76800670e7fde4e75afd6aa7c4b46466ad5283a48c1e`.
The existing [builder validation](../../build/linux-builder/static-validation.json)
binds its source, compiler recipe, static ELF checks and artifacts. No rebuild
or artifact replacement occurred here.

[results.json](results.json) binds raw receipts and concise totals. Independent
post-processing checked all 228 native receipts, artifact identities, CPU14
placement observations, reported comparisons and game raw-stream hashes.
The post-processing summation check was repaired to tolerate a one-ulp difference
between Python float summations (about 1.14e-13 seconds); no sample changed.

Earlier Alpine dynamic-musl own-PGO measurements were 70.885691 s for standard54
and 711.863507 s for one 12-game pass. Those are separate-window observations with
different PGO and helper placement, so these results do not isolate static
linking's performance impact. They also do not establish final performance,
full conformance, focused continuity or external 3288-game qualification for
these new bytes. Candidate68 remains unchanged.

Reproduce into a fresh external directory, with the existing Alpine rootfs and
static build available:

```sh
taskset -c 0-5,8-13 python3 experiments/static-glibc-alpine-performance/run.py \
  --output /home/legolas/rook2-experiments/NEW-STATIC-ALPINE-RUN \
  --build /home/legolas/rook2-experiments/debian-static-glibc-builder-20261023-01 \
  --alpine-root /home/legolas/rook2-experiments/alpine-dynamic-musl-20261021-01/rootfs
taskset -c 0-5,8-13 python3 experiments/static-glibc-alpine-performance/reconcile.py \
  /home/legolas/rook2-experiments/NEW-STATIC-ALPINE-RUN
```

The runner overlays local helper copies with only their housekeeping-affinity
constants changed to `{14}`. Canonical collectors and released comparators remain
unchanged. Its explicit build-receipt adapter checks the actual builder artifact
and source map before satisfying the older collector's receipt interface.
Raw runs remain outside Git at
`/home/legolas/rook2-experiments/static-glibc-alpine-performance-20261023-01/`.

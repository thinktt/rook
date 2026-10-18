The fixed, authorized opaque calibration executable completed all 216 lifetimes (54 cases, one excluded warmup and three measured samples each). Independent reconciliation reran the released strict checker against every retained native stdout/stderr and checked the public reference arithmetic. See [results](../opaque-calibration-cpu-reconciliation-20261018-01/README.md).

`calibration-evidence.tar.gz` preserves all 1,159 original files from preparation, preserved failed offline controls, execution and independent reconciliation. `manifest.json` records each original path, size and SHA256; every archive member and original was independently rehashed after packaging. The executable itself is excluded. Extraction at the repository root restores the original evidence paths.

The local/reference CPU ratios describe this fixed calibration program only. They do not establish candidate KingRE performance acceptance or a universal hardware conversion. PMU counters remain unavailable.

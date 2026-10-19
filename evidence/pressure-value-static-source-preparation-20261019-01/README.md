# Experiment40: shared static pressure lookup — source closed

Trial `/home/legolas/rook2-work/imp2-pressure-value-static-20261019-01` copies the exact retained37 source72 (49 native/Cargo +23 tools). Only `src/activity.rs` differs. All other71 files, root72 and experiment39 are preserved. No experiment38 composition.

The sole runtime-source difference from separately parked39 is `const PRESSURE_VALUES` becoming immutable `static PRESSURE_VALUES`. The initializer, 256 u8 elements, bit weights, full-u8 index and widening are identical. This explicitly requests one shared object instead of a const value at each use; actual lowering/stack/copy elimination remains a parent backend gate, not a source claim.

Relative to37 the original count_ones expression becomes a lookup. Every mark bit has its original weight16/24/8/16/8/16/8/16. Compile-time partial sums cannot exceed112. The independent offline old-formula check covers all256 possible inputs, including coexistence, yielding payload SHA a001834848c9ebea7c64fd3385aacf4c26068a72771047a1d1876382fa0cde63. No invalid mark domain exists. Callers, traversal, masks, charges, API, permission and mutable state/layout are unchanged. All185 old test bodies (183 library +2 development) are byte-exact; no tests added.

`source-before.json`/`source-after.json`, full activity snapshots, `native.patch`/inverse and `storage-only-vs39.patch` expose endpoints. `input-pins.json` and `offline-helper-adaptation.patch` expose proof reuse and retargeting: the helper uses its own experiment40 directory, checks the static declaration and the preselected payload hash. `verify_offline.py` is analytical only; it does not compile or parse Rust.

Parent selected40 before any40 speed data to correct storage semantics;39 remains parked and unchanged. Compilation, native tests, engine execution, binutils, PGO, Git and promotion have not occurred here. Backend, regression and timing are parent-owned. Normal speed requested; no speed readback available.

# Experiment39: full-byte pressure lookup — source closed

Trial: `/home/legolas/rook2-work/imp2-pressure-value-lookup-20261019-01`.
Basis: exact promoted37 source72 (49 native/Cargo +23 tools), verified against `coherent-influence-masks-integration-20261019-01/source-promotion.json`. Root and experiment38 remain untouched. Only `src/activity.rs` changes.

A compile-time loop builds an immutable `[u8;256]` from bit weights `[16,24,8,16,8,16,8,16]`. `pressure_value` indexes by the entire u8 mark and widens to i32. Every intermediate sum is nonnegative and at most112, so u8 addition and widening are exact. All marks including coexisting weak/strong bits retain their old value. No runtime fill, state, fields, API, permission, allocation, charges, masks, traversal or caller change. Public/custom-map input domain is unchanged.

`verify_offline.py` analytically checks all256 marks against the original independent masked count_ones formula and writes the expected256-byte payload. This is an offline algebra check, not a Rust test or emitted-layout proof. Existing185 test declarations and bodies (183 library +2 development) remain byte-identical; no new native tests.

`native.patch` / `native-inverse.patch`, source-before/after maps and full activity snapshots expose the exact endpoint. All other71 source files and root72 hashes match. No experiment38 packed relation table is included.

Backend/table emission, instruction/cache cost, native regression and fixed-rule matched timing remain parent-owned pending gates. No compilation, engine, tests, binutils, profiling, Git or source promotion performed. Normal speed requested; no runtime speed readback available.

Offline reproduction on housekeeping CPUs: `taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 verify_offline.py` from this directory.

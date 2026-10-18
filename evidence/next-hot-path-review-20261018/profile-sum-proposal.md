# Isolated profile-sum proposal

Source directory: `/tmp/imp2-profile-sum-table-native43-20261018-bv1mw_4j`.

Only `src/influence.rs` differs from the 43-file current root/canonical source snapshot. `profile-sum-proposal.json` records every before/after hash and the patch hash. `profile-sum-only.patch` is the complete native edit. The private const table is generated at compile time from the original formula; `pub const fn profile_sum(u8) -> u8` now indexes it. No persistent state, layout, unsafe, alignment or consumer changes are proposed. Pressure-value lookup remains unimplemented.

I inspected the existing exhaustive independent digit-model test, which already compares every profile byte's sum using division/remainders and checks 255 -> 11. Its test-module source bytes are unchanged. No implementation-mirroring test was added. This proposal is uncompiled and unexecuted; no build, rustc, native test, engine, profiler or benchmark was run. Parent owns the requested native/coordinate-oracle54 checks and balanced generic CPU comparison against the c946104a control, followed by any PGO decision. Source construction is not a compilation or performance receipt.

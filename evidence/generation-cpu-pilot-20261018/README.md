# Whole-native CPU comparison of generation alternatives

This reported-only local decision experiment fixed four released anchor cases
before launch: profile-01 (tactical middlegame), profile-02 (sparse endgame),
profile-04 (middlegame) and profile-05 (early opening). Each used one excluded
warmup per variant followed by four measured rounds in alternating forward/
reverse order. All80 complete fresh-process lifetimes passed the unchanged
strict public replay comparator and native accounting checks (16 warmups,
64 measured). Both summary variants also passed all54 replay cases before this
pilot. No owned builds, other engine collections or profilers ran during it.

| Case | Baseline median CPU s | Geometry median CPU s | Pins median CPU s | Pins + evasion median CPU s | Final / baseline |
| --- | ---: | ---: | ---: | ---: | ---: |
| profile-01 | 1.782362 | 1.699780 | 1.6245775 | 1.3732795 | 0.7705 |
| profile-02 | 1.1754895 | 1.1063795 | 1.085208 | 1.0550385 | 0.8975 |
| profile-04 | 6.377237 | 6.2299815 | 5.8589075 | 5.6578115 | 0.8872 |
| profile-05 | 3.490923 | 3.4422725 | 3.3180985 | 3.158351 | 0.9047 |
| Sum of case medians | 12.8260115 | 12.4784135 | 11.8867915 | 11.2444805 | 0.8767 |

All four final medians improve, by about9.5–23%. The four-case sum of medians is
about12.3% lower. This is enough to select the local generation algorithm for
integration with regression checks, not a global performance acceptance claim.
Position/Node layout and copy-child restoration remain unchanged. Direct codes
alone had no established benefit in the preceding profile-01 pilot; that result
is not reinterpreted as an independent speedup for the combined implementation.

`analysis.json` retains every measured sample, ranges/spreads, paired differences
and exact ratios. `suite.json`, each case manifest and the native receipts bind
artifact/driver/comparator/recorder/input identities and the fixed schedule.
Before/after context includes local cgroups and /proc CPU counters; these are
point observations, not evidence of exclusive host ownership. Engine CPU14 and
housekeeping helper placement are observed in native receipts. CPU includes the
whole native lifetime plus the small child pre-exec launcher prefix, excluding
comparator/supervisor CPU; no protocol relay is used. No PMU counts or qualified
cross-host reference ratios are claimed. Published54 and12 performance
collections, calibration and measurement uncertainty remain open.

Frozen artifacts are in the sibling baseline, attack-geometry, generation-safety
and generation-evasion build folders. The final variant is
`aff147eeaa5cf19b5cd34a00637c3b2dcd91ea06d1c6ca73cf54435861c9e0f3`.
The integrated production artifact has its own build/replay identity and does
not inherit this prototype's hash or final qualification status.

# Current57 complete game12 CPU

Exact own-PGO image `af849f920897ec1f174b16718be5d6886158913ee4819f84273f15bd8c23e5b8`. All48 fresh native lifetimes passed:12 warmups and36 measured repetitions,2528 exact searches total. All raw streams and native exits were independently reconciled before this report.

The sum of12 per-game median whole-native CPU times is **689.783349s**. The historical supplied Rust-PGO reference is **644.222971s**; reported ratio **1.070721443**. This is a cross-machine/window reported comparison, not a qualification pass or universal conversion factor.

`unit-medians.csv` contains all12 medians and ranges. `reference-comparison.json` retains all three CPU samples per unit and descriptive ratio envelopes. Whole-native wait4 user+system includes the disclosed small pre-exec prefix; this is not internal prepared-loop CPU. Per-search quantized CPU remains unresolved where unavailable. No PMU measurements or external full-game gate are implied. CPU14/15 field deltas are retained with iowait separate.

`closed-games12.tar.gz` preserves every file in the closed preparation/raw directory; `archive-inputs.json` names every member and its exact bytes/mode. The archiver reopened every member and compared each original. `archive-closure.json` binds the archive. Source/tool/spec authority identities and original comparator streams remain inside that closure.

Previous retained51 measured698.491201s in a separate window;57 is1.246666%lower, with all12 game medians lower. CPU15 recorded2 nonidle ticks and2 iowait ticks; the51 window recorded501 nonidle ticks. These differing conditions prevent attributing the complete observed reduction to the source change alone.

All285 unresolved measured per-search CPU values remain null. An independent arithmetic recheck of all2528 original intervals finds2144 positive resolved tick deltas and384 zero-tick nulls across warmups and measurements, exactly matching the existing wire recorder. Whole-native wait4 CPU is available independently of those quantized search intervals. See historical-comparison.json and search-cpu-arithmetic-recheck.json.

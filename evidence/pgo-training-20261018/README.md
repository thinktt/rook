# Retained compiler training and merge provenance

The workflow follows the [official rustc PGO procedure](https://doc.rust-lang.org/rustc/profile-guided-optimization.html):
instrument a fixed build, run normal inputs, merge the profiles, and rebuild
with the result using the same source and target/release settings. Actual tools
are Rust1.85.1/LLVM19 and `llvm-profdata-19`, identified by the receipts.

A single full unchanged public54 ordinary replay passed using frozen instrumented
artifact `a357ad2a309ad0a5986ae7cebc7760e1c6115b0ee8e8a4f8e9204482ebceff9c`.
These public inputs also trained the approved reference. Every raw profile maps
to exactly one replayed native process PID; source before/after and driver hashes
match. The merged profile archive is lossless and independently rehashed after
decompression. `training.json` binds raw/merged bytes, input/checker identities,
merge command/tool and instrumented build receipt. Raw54 profiles remain local
and ignored; `merged.profdata.gz` is retained for reconstruction of the use build.

`profile-summary.stdout` contains IR instrumentation counters (311 functions),
not PMU instructions, CPU cycles or native timing. No time from instrumentation
training is used as production performance. `verification.json` records the
executed source/profile/PID checks. The profile-use stage binds the immutable
profile and complete provenance and emits no missing-function warnings.

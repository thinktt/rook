# Release PGO inputs

These text-form LLVM instrumentation profiles are production build inputs, not
raw run evidence or executable files. `build/release.json` pins their checksums
and the source graph they belong to. The builder recreates indexed profiles with
its pinned LLVM 19 tool, then supplies them only to the corresponding main engine.

`glibc.proftext` preserves the original candidate's training counts. An indexed
profile recreated from this text has different serialization bytes from the old
archive, but produces the exact original main executable. The static profile is
trained independently with the same pinned toolchain and static-link flags.
Neither profile is interchangeable with another runtime's or changed source.

Raw `.profraw`/`.profdata`, training runs and full receipts remain outside Git.
To prepare a new static profile and run the finite local checks, use the local
supervisor documented in `release/README.md`. Future source changes require
explicit profile preparation and qualification; the tag workflow never trains.

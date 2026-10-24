# Linux release builder

This Debian 13 slim image contains one pinned Debian Rust 1.85.1 toolchain. It
builds four unstripped x86-64 executables: `rook` and `rook-diag` under each of
`glibc/` and `glibc-static/`. The static pair requires no installed glibc and is
qualified locally on Alpine. Diagnostics stay non-PGO; main engines use each
variant's own checked-in text profile.

The base-image digest, signed APT snapshot and Rust package versions are pinned.
Diagnostic dependencies are downloaded and checksum-verified while assembling
the image. Compilation is offline, with fresh targets, explicit flags and fixed
paths. No engine source, test corpus or training output is baked into the builder image.

From the repository root:

```sh
python3 release/build.py --output /absolute/fresh/build-output
python3 release/package.py --build-output /absolute/fresh/build-output \
  --version v1.0.0 --output /absolute/fresh/release-assets
```

`build/release.json` binds the engine/diagnostic source graph, profile checksums
and build layout. Its legacy source, Cargo and dynamic-profile paths are inside
the container: preserving those strings reproduces the qualified candidate's
embedded debug paths and Cargo identities. The host does not need those paths.
This compatibility data is configuration, not hardcoded into build scripts.
Changing it creates new bytes that need a new qualification manifest.

The Dockerfile is only the tool environment. `build.py` creates the four
artifacts and build receipts; [release tooling](../../release/README.md) handles
hash verification, packaging and tag-triggered publication separately.

To update diagnostic dependencies, copy `diagnostic/Cargo.lock` to
`build/linux-builder/diagnostic-Cargo.lock` and rebuild the image. Refresh
source-bound profiles and local qualification before publishing changed bytes.

For local training, `release/build.py --mode generate --variant glibc-static`
accepts a fresh `--profiles-out` directory. `--mode plain` is available for
controlled diagnostics, but release packaging accepts only PGO release builds.
The local supervisor in `release/prepare.py` trains and qualifies a static pair;
it is not invoked by the release workflow.

The earlier `validation.json` and `static-validation.json` are frozen exploratory
records for older upstream-Rust/musl builder commits. Current release identities
and qualification are in `release/qualification.json`; those historical files
are not inputs to this builder.

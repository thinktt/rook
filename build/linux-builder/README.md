# Debian builder for dynamic/static GNU and dynamic-musl Rook

One x86-64 Debian13-slim build image produces the main engine and JSON diagnostic companion for three runtime variants, using upstream Rust1.85.1/LLVM19.1.7. GNU uses Debian’s native linker/runtime, with separate dynamic-glibc and fully static-glibc outputs. Musl uses an isolated Alpine musl1.2.5-r12 sysroot and its musl-built `libgcc_s`; it is dynamically linked, not static. The builder checks interpreter/library imports and rejects glibc imports in the musl output.

The Debian and Rust image digests are fixed. APT uses the signed2026-10-21 Debian snapshot; Rust's musl standard library and all three Alpine sysroot APKs are SHA256-locked. Compilation runs offline in a clean environment, with fixed internal paths, generic x86-64 CPU flags, locked Cargo inputs, separate target directories, disabled incremental builds and a fixed epoch. The builder copies only native crate inputs, excluding `.cargo` configuration, Git history, fixtures and unrelated evidence. The ordinary crate currently has no external dependencies. Image creation downloads the diagnostic lockfile’s 11 registry packages, verifies every archive against its Cargo.lock checksum and prepares Cargo directory sources. Engine compilation then needs neither network access nor an external Cargo cache.

Build the builder from this directory (no engine source/profile enters the image):

```sh
docker buildx build --platform linux/amd64 --load \
  -t rook-builder:rust1.85.1 build/linux-builder
```

Create a fresh output directory, then build all six optimized **non-PGO** binaries:

```sh
mkdir /path/to/fresh-output
docker run --rm --platform linux/amd64 --network none --read-only \
  --user "$(id -u):$(id -g)" \
  --tmpfs /build:exec,mode=1777 --tmpfs /tmp:exec,mode=1777 \
  --mount type=bind,src="$PWD",dst=/source,readonly \
  --mount type=bind,src=/path/to/fresh-output,dst=/out \
  rook-builder:rust1.85.1 --variant all --mode plain
```

On Vic, restrict build helpers with `--cpuset-cpus 0-5,8-13`. Outputs are `rook` and `rook-diag` in each of `glibc/`, `musl/` and `glibc-static/`. Each runtime directory contains both binaries, `SHA256SUMS`, compiler/source/flag metadata in `build.json`, a main-engine profile template and separate main/diagnostic compiler logs. Output must be empty and `/build` fresh; failed outputs are retained. Use `--variant glibc`, `--variant musl` or `--variant glibc-static` for one runtime. `--variant all` is the default; `--variant both` preserves the earlier two-dynamic-runtime selection. Static glibc uses `target-feature=+crt-static`; ELF checks require no interpreter, shared-library dependencies or GLIBC symbol-version requirements. It needs no installed glibc for the tested engine paths. Glibc APIs that load modules dynamically remain outside that finite compatibility claim. The image builds files; it never executes engines, benchmarks, publishes or promotes them. Test the dynamic-musl output in Alpine with musl and `libgcc` installed. Determine the GNU artifact's actual glibc floor from its ELF; the base image does not guarantee a particular minimum.

## PGO

`--mode generate` creates instrumented **main engines** plus `profile-template.json` for each selected runtime. Diagnostic companions remain optimized non-PGO in every mode, including `generate` and `use`; they use separate Cargo target directories and receive no main-engine profile flags. Also mount a fresh writable directory at `/profiles-out`; the generated default raw-profile paths are `/profiles-out/<variant>`. Training and correctness checks are separate runtime operations. Override `LLVM_PROFILE_FILE` appropriately when running those images outside this builder. The image includes `llvm-profdata-19` for merging.

After verified training, merge each target's own raw profiles. Store `<variant>.profdata` in a profile directory, and copy that runtime’s template to `<variant>.json`, adding `"profile_sha256": "<SHA256 of the merged profile>"`. Mount the directory read-only at `/profiles` and use `--mode use`. Source map, compiler identity, builder recipe fingerprint, CPU/linker flags, target and epoch must match; the merged file is checked before/after use. Profile use enables the existing profiled-only ExtTSP policy and rejects missing/stale profile diagnostics. The manifest is an input-consistency check, not proof that training/correctness happened.

Never reuse dynamic-glibc, static-glibc and musl profiles interchangeably, including the two variants that share the GNU target triple. The previous Debian-packaged-Rust candidate68 and Alpine-native trial used different toolchain distributions/linker paths; their existing profiles are not automatically admitted. New profiles should be trained with this builder and their training receipts preserved.

## Updating diagnostic dependencies

The image’s `diagnostic-Cargo.lock` must exactly match the mounted source’s `diagnostic/Cargo.lock`; a mismatch stops before Cargo runs. After deliberately changing diagnostic dependencies, refresh the builder input from the repository root and rebuild the image:

```sh
cp diagnostic/Cargo.lock build/linux-builder/diagnostic-Cargo.lock
```

The vendor helper rejects altered archives and unsupported dependency sources. Cargo verifies the generated directory-source file checksums during offline compilation. Builder recipes and both crates’ source inputs are included in profile provenance, so recipe/dependency changes require matching new training manifests.

## Validation and limits

The previous two-runtime helper successfully compiled all four dynamic binaries offline using the exact upstream Rust components and Alpine sysroot. Both diagnostic companions passed the released 25-case position-setup fixture; musl ran inside the archived Alpine filesystem. Altered crate archives and a changed diagnostic lock were rejected. Both instrumented main engines also compiled; their diagnostic companions stayed non-PGO and exactly matched the plain-build diagnostic hashes. Precise raw bindings are recorded in [validation.json](validation.json). Current raw validation is under `/home/legolas/rook2-experiments/debian-four-builder-20261022-01/`; earlier ordinary-only/profile-rejection checks remain under `/home/legolas/rook2-experiments/debian-dual-builder-20261022-01/`.

The static-glibc extension compiled both main and diagnostic binaries offline. Inside the archived Alpine filesystem, the diagnostic passed 25 position-setup and 4 joined-search cases; the main engine passed 8 interruption sessions / 24 searches with exact semantic comparisons and clean exits. Engines ran on CPU14; helpers stayed on housekeeping CPUs and no work was assigned to CPU15. Both ELF files have no interpreter or shared-library requirements. These are optimized non-PGO builds; static-glibc profile generation/use has not been tested. [static-validation.json](static-validation.json) binds the current recipe and raw evidence at `/home/legolas/rook2-experiments/debian-static-glibc-builder-20261023-01/`. No timings or full conformance/12-game claim follows.

Docker is not installed on Vic, and the earlier rootless BuildKit attempt lacked subordinate-ID support. Local namespace checks exercise build/link logic, not the full Dockerfile/APT/image-assembly path. Full Docker frontend validation and independent two-build SHA256 reproduction remain to be run on a Docker-capable host. A successful trained profile-use build with this recipe has not been tested. New outputs are unqualified artifacts: matching historical candidate68 or Alpine-trial hashes, performance or qualification is not claimed. The existing packaged candidate remains unchanged. This recipe produces a builder image, not a release pipeline or a runtime container; image/layer digest reproducibility is also a separate check.

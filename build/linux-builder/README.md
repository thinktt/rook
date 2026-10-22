# Debian builder for GNU and dynamic-musl Rook

One x86-64 Debian13-slim build image produces both ordinary-engine variants, using upstream Rust1.85.1/LLVM19.1.7. GNU uses Debian's native linker/runtime. Musl uses an isolated Alpine musl1.2.5-r12 sysroot and its musl-built `libgcc_s`; it is dynamically linked, not static. The builder checks interpreter/library imports and rejects glibc imports in the musl output.

The Debian and Rust image digests are fixed. APT uses the signed2026-10-21 Debian snapshot; Rust's musl standard library and all three Alpine sysroot APKs are SHA256-locked. Compilation runs offline in a clean environment, with fixed internal paths, generic x86-64 CPU flags, locked Cargo inputs, separate target directories, disabled incremental builds and a fixed epoch. The builder copies only native crate inputs, excluding `.cargo` configuration, Git history, fixtures and unrelated evidence. The ordinary crate currently has no external dependencies; diagnostic packaging/vendoring is a separate task.

Build the builder from this directory (no engine source/profile enters the image):

```sh
docker buildx build --platform linux/amd64 --load \
  -t rook-builder:rust1.85.1 build/linux-builder
```

Create a fresh output directory, then build both optimized **non-PGO** variants:

```sh
mkdir /path/to/fresh-output
docker run --rm --platform linux/amd64 --network none --read-only \
  --user "$(id -u):$(id -g)" \
  --tmpfs /build:exec,mode=1777 --tmpfs /tmp:exec,mode=1777 \
  --mount type=bind,src="$PWD",dst=/source,readonly \
  --mount type=bind,src=/path/to/fresh-output,dst=/out \
  rook-builder:rust1.85.1 --variant both --mode plain
```

On Vic, restrict build helpers with `--cpuset-cpus 0-5,8-13`. Outputs are `glibc/rook` and `musl/rook`, each with checksums, compiler/source/flag metadata and compiler logs. Output must be empty and `/build` fresh; failed outputs are retained. Use `--variant glibc` or `--variant musl` for one target. The image builds files; it never executes engines, benchmarks, publishes or promotes them. Test the dynamic-musl output in Alpine with musl and `libgcc` installed. Determine the GNU artifact's actual glibc floor from its ELF; the base image does not guarantee a particular minimum.

## PGO

`--mode generate` creates instrumented images plus `profile-template.json` for each target. Also mount a fresh writable directory at `/profiles-out`; the generated default raw-profile paths are `/profiles-out/glibc` and `/profiles-out/musl`. Training and correctness checks are separate runtime operations. Override `LLVM_PROFILE_FILE` appropriately when running those images outside this builder. The image includes `llvm-profdata-19` for merging.

After verified training, merge each target's own raw profiles. Store `glibc.profdata` / `musl.profdata` in a profile directory, and copy that target's template to `glibc.json` / `musl.json`, adding `"profile_sha256": "<SHA256 of the merged profile>"`. Mount the directory read-only at `/profiles` and use `--mode use`. Source map, compiler identity, builder recipe fingerprint, CPU/linker flags, target and epoch must match; the merged file is checked before/after use. Profile use enables the existing profiled-only ExtTSP policy and rejects missing/stale profile diagnostics. The manifest is an input-consistency check, not proof that training/correctness happened.

Never reuse GNU and musl profiles interchangeably. The previous Debian-packaged-Rust candidate68 and Alpine-native trial used different toolchain distributions/linker paths; their existing profiles are not automatically admitted. New profiles should be trained with this builder and their training receipts preserved.

## Validation and limits

The exact upstream Rust components and Alpine sysroot were tested locally: a dynamic-musl smoke executable linked without glibc imports and ran successfully in the archived Alpine container. The builder script successfully compiled both ordinary variants in plain and instrumented modes. A wrong-target PGO manifest was rejected before Cargo ran; a successful trained profile-use build was not selected. [validation.json](validation.json) records the checks; local raw validation lives under `/home/legolas/rook2-experiments/debian-dual-builder-20261022-01/`.

Docker is not installed on Vic, and the earlier rootless BuildKit attempt lacked subordinate-ID support. Local namespace checks exercise build/link logic, not the full Dockerfile/APT/image-assembly path. Full Docker frontend validation and independent two-build SHA256 reproduction remain to be run on a Docker-capable host. New outputs are unqualified artifacts: matching historical candidate68 or Alpine-trial hashes, performance or qualification is not claimed. The existing packaged candidate remains unchanged. This recipe produces a builder image, not a release pipeline or a runtime container; image/layer digest reproducibility is also a separate check.

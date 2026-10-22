# Frozen dynamic-musl Alpine build recipe

This recipe targets the candidate68-source Alpine trial described in [the study](../../experiments/alpine-dynamic-musl/README.md). It is an ordinary dynamically linked musl executable, not a static binary or a promotion. Source, own musl PGO profile, two build APKs, platform, base-image digest, compiler version, CPU target, paths, epoch and final binary SHA256 are fixed. Docker `RUN` steps have no network, Cargo is locked/offline, and a clean environment excludes inherited build flags and host CPU detection. There are no compiler cache mounts or profile-training runs.

Prepare a curated context outside the repository (the output must not exist):

```sh
python3 build/alpine-dynamic/prepare.py \
  --source "$PWD" \
  --profile /home/legolas/rook2-experiments/alpine-dynamic-musl-20261021-01/merged.profdata \
  --output /home/legolas/rook2-experiments/alpine-build-context
```

Preparation downloads only the exact musl/musl-dev APK files pinned by SHA256 in [inputs.lock.json](inputs.lock.json). For fully offline preparation, supply `--apk-cache` pointing to the preserved `build-apks` directory. Preserve the profile and verified APKs as CI inputs; future public availability is not guaranteed. No fixture/oracle, unrelated source, credentials, historical binaries or Git history enters the context.

On a Docker/BuildKit host:

```sh
docker buildx build --platform linux/amd64 --no-cache \
  --target binaries --output type=local,dest=./alpine-binaries \
  /home/legolas/rook2-experiments/alpine-build-context
```

The output contains `rook2-musl` and `SHA256SUMS`. Its expected binary hash is `74a5c62b02362fba13e211f20da7d742d6ad9edbb13fb881f9e77cb70addef52`; a mismatch fails the build rather than silently publishing another executable. This is a candidate-specific frozen recipe: changed source/profile/toolchain requires an intentional new lock, hash and validation. The artifact-export stage uses `scratch` only to export files; it is not a runnable image for this dynamic executable. An Alpine runtime needs musl and `libgcc`.

Validation: two independent empty Cargo target directories matched this hash inside Alpine. The actual [build.sh](build.sh) also matched it from a fresh curated context with normalized source mtimes and an empty target directory (`abcae9/0`). **Docker/BuildKit frontend execution remains unverified here:** Docker is absent and a rootless BuildKit attempt hit a subordinate-ID limitation. The tested namespace container exercised the same build script; this does not assert reproducible image/layer digests, independently repeated fresh training or cross-machine reproduction. Candidate68's original glibc bytes remain preserved.

#!/bin/sh
set -eu
cd /work
sha256sum -c input.SHA256SUMS
mkdir -p /work/cargo-home /out
cd /work/source
flags='-C target-cpu=x86-64 -C target-feature=-crt-static -C profile-use=/work/merged.profdata -C llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false'
encoded=$(printf '%s\037%s\037%s\037%s\037%s\037%s\037%s\037%s' '-C' 'target-cpu=x86-64' '-C' 'target-feature=-crt-static' '-C' 'profile-use=/work/merged.profdata' '-C' 'llvm-args=-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false')
# Fixed paths and a clean environment; no host CPU detection, cache or network.
env -i PATH=/usr/local/cargo/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  HOME=/root RUSTUP_HOME=/usr/local/rustup CARGO_HOME=/work/cargo-home \
  LANG=C LC_ALL=C TZ=UTC RUSTUP_TOOLCHAIN=1.85.1-x86_64-unknown-linux-musl \
  CARGO_NET_OFFLINE=true CARGO_INCREMENTAL=0 CARGO_BUILD_JOBS=4 \
  SOURCE_DATE_EPOCH=1742256000 RUSTFLAGS="$flags" CARGO_ENCODED_RUSTFLAGS="$encoded" \
  /usr/local/cargo/bin/cargo build --offline --locked --release --verbose \
  --target x86_64-unknown-linux-musl --jobs 4 --target-dir /work/target-use \
  --manifest-path /work/source/Cargo.toml --bin rook2 \
  > /work/build.stdout 2> /work/build.stderr
cat /work/build.stderr
if grep -Ei 'no profile data available for function|profile data may be out of date|profile data mismatch|malformed instrumentation profile data|hash mismatch|unprofiled function' /work/build.stderr; then
  echo 'Profile compatibility check failed' >&2
  exit 1
fi
cp /work/target-use/x86_64-unknown-linux-musl/release/rook2 /out/rook2-musl
cd /out
printf '%s  %s\n' '74a5c62b02362fba13e211f20da7d742d6ad9edbb13fb881f9e77cb70addef52' 'rook2-musl' | sha256sum -c -
sha256sum rook2-musl > SHA256SUMS
chmod 755 rook2-musl

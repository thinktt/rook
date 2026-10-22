# Build from this directory: docker buildx build --platform linux/amd64 --load -t rook-builder .
FROM --platform=linux/amd64 rust:1.85.1-slim-bookworm@sha256:3490aa77d179a59d67e94239cca96dd84030b564470859200f535b942bdffedf AS rust-toolchain

FROM --platform=linux/amd64 debian:trixie-slim@sha256:4876fdea29cac1a33a3195f1eb1952feb1fca7dd6dd00be3e2f1879cf20d34d2 AS builder
COPY --from=rust-toolchain /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
# Freeze the entire dependency resolver, including transitive packages. Keep signature checks.
RUN rm -f /etc/apt/sources.list /etc/apt/sources.list.d/* \
    && printf '%s\n' 'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian/20261021T000000Z/ trixie main' > /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl xz-utils gcc libc6-dev binutils musl-tools python3 llvm-19 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=rust-toolchain /usr/local/rustup/ /usr/local/rustup/
COPY --from=rust-toolchain /usr/local/cargo/ /usr/local/cargo/
ENV PATH="/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin" \
    RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/build/cargo-home \
    RUSTUP_TOOLCHAIN=1.85.1-x86_64-unknown-linux-gnu \
    LANG=C LC_ALL=C TZ=UTC

# Checksum-locked official Rust musl standard library; no floating rustup update.
RUN curl -fsSL https://static.rust-lang.org/dist/2025-03-18/rust-std-1.85.1-x86_64-unknown-linux-musl.tar.xz -o /tmp/rust-std.tar.xz \
    && echo 'a2a99b60e86214a836e53396f3a0716a48724902b9dd8c69f146897efc76691e  /tmp/rust-std.tar.xz' | sha256sum -c - \
    && tar -xJf /tmp/rust-std.tar.xz -C /tmp \
    && /tmp/rust-std-1.85.1-x86_64-unknown-linux-musl/install.sh --prefix=/usr/local/rustup/toolchains/1.85.1-x86_64-unknown-linux-gnu --disable-ldconfig \
    && rm -rf /tmp/rust-std*

# An isolated Alpine target sysroot, including its musl-built shared GCC runtime.
# Debian's glibc-built libgcc_s must never enter the dynamic-musl output.
RUN mkdir -p /tmp/apks /opt/musl-sysroot \
    && curl -fsSL https://dl-cdn.alpinelinux.org/alpine/v3.21/main/x86_64/musl-1.2.5-r12.apk -o /tmp/apks/musl.apk \
    && curl -fsSL https://dl-cdn.alpinelinux.org/alpine/v3.21/main/x86_64/musl-dev-1.2.5-r12.apk -o /tmp/apks/musl-dev.apk \
    && curl -fsSL https://dl-cdn.alpinelinux.org/alpine/v3.21/main/x86_64/libgcc-14.2.0-r4.apk -o /tmp/apks/libgcc.apk \
    && printf '%s\n' \
       'abfcfe822d37bb6fa621d7d682e26eba95152c642dc5619b768b4e4a9789133e  /tmp/apks/musl.apk' \
       '0b0357736d51253ddf82a4338378848cfbbe6d695aba60cf7790423670d61b2a  /tmp/apks/musl-dev.apk' \
       '8675867db77b5af11b88fd19186450333202d94cccd84a76a066dccd5b6e8cf1  /tmp/apks/libgcc.apk' | sha256sum -c - \
    && tar -xzf /tmp/apks/musl.apk --ignore-zeros -C /opt/musl-sysroot lib \
    && tar -xzf /tmp/apks/musl-dev.apk --ignore-zeros -C /opt/musl-sysroot usr/include usr/lib \
    && tar -xzf /tmp/apks/libgcc.apk --ignore-zeros -C /opt/musl-sysroot usr/lib/libgcc_s.so.1 \
    && ln -sfn ../../lib/libc.musl-x86_64.so.1 /opt/musl-sysroot/usr/lib/libc.so \
    && sed -e 's|/usr/lib/x86_64-linux-musl|/opt/musl-sysroot/usr/lib|g' \
           -e 's|/usr/include/x86_64-linux-musl|/opt/musl-sysroot/usr/include|g' \
           /usr/lib/x86_64-linux-musl/musl-gcc.specs > /opt/musl-sysroot/musl-gcc.specs \
    && rm -rf /tmp/apks

COPY Dockerfile build.py musl-linker.sh /opt/rook-builder/
RUN chmod 755 /opt/rook-builder/musl-linker.sh \
    && mkdir -p /source /out /profiles /profiles-out /build \
    && rustc --version && cargo --version \
    && test -d "$(rustc --print target-libdir --target x86_64-unknown-linux-musl)"
WORKDIR /build
ENTRYPOINT ["/usr/bin/python3", "/opt/rook-builder/build.py"]
CMD ["--help"]

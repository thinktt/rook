FROM --platform=linux/amd64 debian:trixie-slim@sha256:4876fdea29cac1a33a3195f1eb1952feb1fca7dd6dd00be3e2f1879cf20d34d2

# Freeze package resolution as well as the base image. Signature checks stay on.
RUN rm -f /etc/apt/sources.list /etc/apt/sources.list.d/* \
    && printf '%s\n' 'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/20261021T000000Z/ trixie main' > /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       rustc=1.85.1+dfsg1-1+deb13u1 cargo=1.85.1+dfsg1-1+deb13u1 \
       gcc libc6-dev binutils llvm-19 python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Fetch checksum-locked dependencies once; actual engine builds are offline.
COPY vendor.py diagnostic-Cargo.lock /opt/rook-builder/
RUN python3 /opt/rook-builder/vendor.py \
    --lock /opt/rook-builder/diagnostic-Cargo.lock --output /opt/rook-builder/vendor
COPY build.py /opt/rook-builder/
ENV LANG=C LC_ALL=C TZ=UTC
WORKDIR /build
ENTRYPOINT ["python3", "/opt/rook-builder/build.py"]

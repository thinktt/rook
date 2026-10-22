# Pinned x86-64 Alpine/Rust toolchain. Use a prepared, curated context.
FROM --platform=linux/amd64 rust:1.85.1-alpine3.21@sha256:813376c206852d4250641eb86720c04fd20fbc6547d1a030c93a45b22a1303a3 AS build
COPY apks/ /apks/
RUN --network=none cd /apks && sha256sum -c SHA256SUMS && apk add --no-network ./musl-1.2.5-r12.apk ./musl-dev-1.2.5-r12.apk
WORKDIR /work
COPY source/ /work/source/
COPY merged.profdata build.sh input.SHA256SUMS /work/
RUN --network=none /bin/sh /work/build.sh

# An artifact-export stage, not a runnable static-binary image.
FROM scratch AS binaries
COPY --from=build /out/ /

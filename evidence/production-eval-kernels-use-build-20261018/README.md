# Canonical evaluation-kernel PGO artifact

Exact ordinary binary:
`8c4619a7c3f33bed6eb17c396a7d9d8d223262dd1595c4f23812e5de17809953`.
The retained generic x86-64 build uses Rust1.85.1/LLVM19, optimization3,
thin LTO, one codegen unit, debug1 and panic abort. The ordinary executable
contains no JSON adapter or expected-answer data.

The canonical repository source matches the measured combined prototype's43
native source/manifest files byte for byte. Its verified66-file source/tool
archive has SHA256
`22441e6443d30e44ad703fb023fb1ef02a8413c71bec03de94be4e3f1d71fee2`.
Source integration and134 native tests are retained in
`../eval-kernels-integration-20261018/`.

The repository has its own instrumented artifact18df5d17 and54 unchanged public
training replays. All54 unique raw profile files, strict results, merge inputs
and source/tool identities are independently verified under
`../production-eval-kernels-training-20261018/`. Merged profile SHA256 is
`7858420d117e3defd609ef7949a237ec2640a598536075170f56059e07bf10f1`.
The use build emits no profile warnings; its unrelated unused private
constructor warning is retained.

This exact binary passes all54 strict ordinary replay cases and eight wire
interruption fixtures/24 searches. Checks, actual successful terminal receipt
and original streams are in `../production-eval-kernels-use-check-20261018/`
and `../production-eval-kernels-interruption-wire-20261018/`.
The independent adapterab8b7c3c passes36 units/2215 cases across49 operations
against this same native source.

Its own [complete54 CPU collection](../production54-cpu-eval-kernels-20261018/README.md)
totals81.828432s in case medians across216 lifetimes. Earlier prototype timings
are decision evidence only and are not transferred to this artifact.
Mandatory diagnostic completion, production audit, current-artifact gameplay
and final performance qualification remain open.

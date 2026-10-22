# Alpine dynamic-musl deployment trial

Candidate68's unchanged52 native source inputs were built for `x86_64-unknown-linux-musl` with **dynamic** C-runtime linkage, inside Alpine. The ordinary trial binary is3,689,728 bytes, SHA256 `74a5c62b02362fba13e211f20da7d742d6ad9edbb13fb881f9e77cb70addef52`. It requires `/lib/ld-musl-x86_64.so.1`, `libc.musl-x86_64.so.1` and `libgcc_s.so.1`. It is not a static portable binary or a promoted candidate. Existing candidate68 binaries/tags are unchanged.

| Collection | Result | Native CPU time |
|---|---|---:|
| Released standard54 (the owner's52 referred to this existing54-case suite) | All216 fresh lifetimes /2,496 expected posts pass; one warmup + three measured runs per case | **70.885691s**, sum of case medians |
| Independent12-game pre-gate set | All12 individual game reports pass;632 searches /5,801 expected posts | **711.863507s**, sum of single-pass game lifetimes |

The12-game summed native wall time is712.605331s. It has no excluded warmup or repeated median estimate. These are direct `wait4` user+system whole-native lifetimes, including a small Python child pre-exec prefix; they are not Bee's quantized go-to-move-only endpoint. All228 benchmark native PIDs had post-exec single-thread/CPU14 observations and were reaped. Raw game stdin/stdout/stderr hashes and search-boundary CPU14 observations reconcile. Helpers stayed on `0-5,8-13`. No PMU, exclusive-host, memory/no-swap or formal performance qualification is claimed.

The earlier Vic glibc build's54-case result was68.569086s; this trial is descriptively3.3785% higher across separate windows. This changes the C runtime, compiler distribution and observer versions together, and does not isolate a musl-only effect. No current-glibc full12 comparison was rerun.

## Build and runtime

The pinned base is official `rust:1.85.1-alpine3.21@sha256:813376c206852d4250641eb86720c04fd20fbc6547d1a030c93a45b22a1303a3`, Alpine3.21.3, Rust1.85.1/LLVM19.1.7. The runtime was updated to musl1.2.5-r12; `libgcc`14.2.0-r4. Observer tools were Python3.12.15 and Node22.23.2. Exact package inventory/runtime hashes are bound in result.json's environment receipt.

Generic x86-64, O3/thinLTO/one-CGU/panic-abort/debug1, plus `-C target-feature=-crt-static`. A fresh instrumented dynamic-musl build trained all original54 once. All54 strict replays, direct native placement/image receipts and PID-bound raw profiles pass; independent LLVM19 remerge is byte-identical. The own profile is `be4d84416dcff15ad937a46717a6da28a1953dd0f5f18c6a0952148fc421e129`; production used profiled-only ExtTSP with no missing/stale profile warnings. Two empty-target builds matched exactly. A third shell-recipe rebuild with copied/timestamp-normalized source also matched.

## Scope and preserved failures

The twelve literal individual reports pass. The optional released combiner rejects their different per-game accounting `--record` paths as different launch configurations (`ed504a/1`). Reports were not normalized or edited, and no games were rerun. The independent reconciler verifies the complete12-game union and all native/raw bindings; **there is no literal combined report or complete-focused-replay/full-game qualification claim**. Continuity/seed/persistence/wire extras were not selected for this trial.

Pre-native setup failures are retained: rootless BuildKit lacked subordinate GID mappings; the first safe Python tar extraction rejected an absolute image symlink; an initial APK invocation omitted `/sbin`; the first instrumented link lacked `musl-dev`; and the first recipe validation lacked its `/out` mount directory. The corresponding repairs changed environment/launch preparation only. No engine source changed and no benchmark/native request failed or was retried.

Docker is absent on Vic. The actual Alpine containers used unprivileged bubblewrap user/mount/UTS/network namespaces, the verified official image layers plus recorded APKs, and read-only runtime mounts during native collection. Host PIDs remained visible for accounting. The Docker/BuildKit frontend did not complete on this host; this limitation is separate from the successful Alpine builds/runs.

## Artifacts and reproduction

[Aggregate result](result.json), [54 timings](timings54.csv), [12 timings](timings12.csv), and the study scripts are retained here. Raw source snapshots, compiler logs, complete reports/streams, runtime filesystem, profiles and binaries remain outside Git at `/home/legolas/rook2-experiments/alpine-dynamic-musl-20261021-01/`. The benchmarked image is `artifacts/rook2-musl`. Actual native lane terminal `a5ed30/0`; independent closure `9d1ce3/0`.

The scripts assume this raw directory's archived Alpine rootfs/source and mount them at `/work`. Copy them to a fresh prepared study directory before repeating; existing outputs are deliberately not reused. `build.py instrumented`, `train.py`, host `merge.py`, `build.py use`, `build.py repeat`, then host `run_benchmarks.py` define the executed order; `container.py` wraps the inside-Alpine commands. See [the frozen Docker build recipe](../../build/alpine-dynamic/README.md) for a curated context and offline reproduction of the final exact binary. No profile retraining determinism, cross-host reproducibility, source adoption, new candidate tag, READY, external transfer or release action follows.

# Candidate68 clean rebuild: exact binary matches

On 2026-10-21, both Rook `1.0.0-candidate68` binaries were rebuilt successfully into initially absent Cargo target directories. Their complete SHA256 hashes and sizes match the packaged, externally tested candidate. No engine execution or substitution/promotion occurred.

| Artifact | SHA256 | Bytes | Result |
|---|---|---:|---|
| Ordinary | `5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a` | 7118416 | Exact match |
| Diagnostic | `68a1c304f76435e4c100086d1a303b8dc94d8b5ecd63d26be834e3737bca2dda` | 14038952 | Exact match |

The original 118-file candidate map, 75 ordinary native/tool inputs, compiler/Cargo executable hashes, recorded compiler version and original PGO/profile-receipt hashes were checked before building. Source and original images were checked afterward; packaged aliases also retain their hashes. Both builds used four jobs on housekeeping CPUs `0-5,8-13`, offline locked dependencies, Rust1.85.1/LLVM19.1.7 and the recorded generic x86-64 flags. Ordinary reused its immutable `fda4b7fd…` profile with profiled-only ExtTSP; diagnostic used its separate non-PGO recipe. No PGO training was rerun. Every diagnostic compiler artifact was reported `fresh:false`; the ordinary verbose log records compilation without a Fresh result.

The source stayed at the original isolated candidate path; only Cargo output paths changed. This establishes a same-machine clean rebuild with preserved inputs. It does not establish independence from source paths, portability to another toolchain/machine/container, fresh-training determinism or a complete archived dependency/toolchain closure.

Raw plans, executed script, complete compiler logs and result JSON remain outside Git at `/home/legolas/rook2-experiments/candidate68-clean-rebuild-20261021-01/`. Both Cargo processes exited0; the parent terminal was `b4aaed/0`. The original source/build directories, audited package, delivery bundle and candidate tags were not replaced.

To repeat with the preserved inputs, choose a fresh output directory:

```sh
taskset -c 0-5,8-13 /usr/bin/python3 \
  experiments/candidate68-clean-rebuild/rebuild.py \
  --output /home/legolas/rook2-experiments/candidate68-clean-rebuild-repeat
```

[rebuild.py](rebuild.py) repeats the executed recipes with a configurable output root. It requires the original recorded source, receipts, cached dependencies and profile; it does not modify engine source or run the resulting binaries. Rebuilding the profile or relocating source is a separate experiment.

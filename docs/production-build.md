# Current local production candidate

The separate [Debian dual-target builder](../build/linux-builder/README.md) can build GNU/glibc and dynamic-musl main engines and diagnostic companions in one container. It pins an upstream Rust toolchain and isolated target sysroots. Its new outputs are unqualified; it does not automatically reproduce or replace the archived candidate below, and profiles must belong to its own target/toolchain/source.

The **first-main corrected build** is the current locally adopted candidate for continuing qualification. The source is the tested correction with its test additions; the existing exact ordinary and diagnostic artifacts remain at their isolated build paths. Adoption did not rebuild either artifact. Retained62 is preserved as the initial comparison control.

Let `corrected_root` below mean `/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01`.

| Existing item | Absolute path |
|---|---|
| Ordinary image | `/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/use-build/rook2-exact` |
| Separate JSON diagnostic | `/home/legolas/rook2-experiments/first-main-cutoff-correction-20261020-01/diagnostic-target/x86_64-unknown-linux-gnu/release/rook2-diag` |
| Own merged profile | `/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/training/merged.profdata` |
| Training provenance | `/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/training/training.json` |
| Independent training verification | `/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01/training/verification.json` |
| Ordinary build receipt / source archive | `corrected_root/use-build/receipt.json` / `corrected_root/use-build/verified-source-before.tar.gz` |

```text
ordinary: 5cf0120892065f80bbf4a22297596358bfc28c4945c86c0bf3f65d38b8bff82a
DIAG:     68a1c304f76435e4c100086d1a303b8dc94d8b5ecd63d26be834e3737bca2dda
profile:  fda4b7fd45465c66c6bbda9a6aa249f5bd78b5f9f1dba4d8d98170524021594c
training: f503aeee706339450320ba580cd1d9b98c35c655996f320875062bb2a88640b4
```

Ordinary is7,118,416 bytes; DIAG14,038,952 bytes. The [adoption manifest](../experiments/first-main-cutoff-adoption/manifest.json) binds paths, sizes, hashes, source/build/profile archives and exact evidence. Its [promotion record](../experiments/first-main-cutoff-adoption/source-promotion.json) verifies118 mapped source files and preserves the extra canonical archival utility separately. All52 native source/build inputs exactly equal the fresh training map;23 mapped tool inputs accompany them in the75-file ordinary source archive. These counts do not identify the entire evolving repository.

The ordinary recipe is Rust1.85.1/LLVM19.1.7, generic`target-cpu=x86-64`, target`x86_64-unknown-linux-gnu`, O3/thinLTO/one-CGU/panic-abort/debug1. A separate instrumented build trained each original54 once; all native PID/profile bindings and original replay checks passed, and independent remerge was byte-identical. The measured ordinary image then used that fresh profile with profiled-only use-stage ExtTSP and zero missing/stale warnings. DIAG is the separate generic non-PGO corrected companion used for the mandatory suite.

Default Cargo/build-helper invocations do not select this tested PGO/ExtTSP artifact automatically. The following documents a **new, unvalidated ordinary rebuild**, using the corrected source's own profile/training receipt. It was not executed during adoption. The output directory must be absent; build/runtime inputs and effective compiler settings must be verified for any new artifact.

```sh
corrected_root=/home/legolas/rook2-experiments/first-main-cutoff-production-20261020-01
PATH=/usr/bin:/bin TMPDIR=/home/legolas/rook2-build-tmp \
  taskset -c 0-5,8-13 /usr/bin/python3 tools/build.py \
  --mode generic --bin rook2 --jobs 4 \
  --pgo-use "$corrected_root/training/merged.profdata" \
  --training-record "$corrected_root/training/training.json" \
  --ext-tsp-profiled \
  --output /home/legolas/rook2-experiments/fresh-first-main-rebuild
```

The ExtTSP switch emits the single combined LLVM value:

```text
-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false
```

A canonical-path rebuild is a new image. Paths, toolchain and metadata can alter its bytes/profile mapping; it needs its own warning checks and validation before substitution. A source change needs corresponding training provenance. The tested artifacts were built from `/home/legolas/rook2-experiments/first-main-cutoff-correction-20261020-01/candidate`; copying those exact source bytes into canonical does not claim a canonical-path rebuild. The build receipt's `fresh_training:false` means the helper did not launch training itself; the separately recorded fresh training/profile chain is authoritative.

The [paired54](../experiments/first-main-cutoff-production/README.md) records68.569086 corrected versus68.446861 retained62 CPU s, summed per-case medians; descriptive+0.178569%. [Gameplay](../experiments/first-main-cutoff-gameplay/README.md) is a single behavioral12/632 plus focused controls and wire8/24, with a literal original combined receipt. It supplies no full12 performance result. The corrected source/DIAG evidence reuses196 library,209 diagnostic,2 development tests and7,673 mandatory cases; those checks were not repeated during local adoption.

## Preserved retained62 control

Retained62 ordinary `01237e6d…`, diagnostic `eda652ab…` and own57 profile `b4806420…` remain at their original relocated paths under `/home/legolas/rook2-experiments/original-worktree/evidence/`. The [unchanged retained62 handoff](../experiments/retained62-game-handoff/manifest.json) supplies complete exact identities and its old source/build/profile archives. Its native source was unchanged from57 and its existing own57 profile belongs to that old source. The corrected source uses its own `fda4b7fd…` profile above.

Retained62's historical54=67.640360 CPU s and12=675.156653 CPU s are retained62 observations from their original windows. They are not measurements of the corrected build. Earlier historical statements/maps remain preserved; the new promotion record binds the old source commit and after-adoption map separately. [Current status](../STATUS.md) and the lead-owned review/qualification notes distinguish local evidence from final acceptance. No new payload copy, external transfer, READY signal or full3288 execution is authorized by this guide.

# Retained production build62

Candidate62 is the retained ordinary image, with candidate57's native engine and
the exact57 diagnostic companion. It changes the profile-use compiler layout,
not the native engine source. Default `tools/build.py`/Cargo builds do **not**
select this profile or ExtTSP recipe automatically.

The archive root below is `/home/legolas/rook2-experiments/original-worktree`.
Paths in frozen records still begin `/home/legolas/rook2/evidence/`; resolve their
missing raw files under the archive root. See [storage layout](evidence-layout.md).

| Retained item | Path relative to archive root |
|---|---|
| Ordinary image | `evidence/exttsp-profiled-pgo-use-build-20261020-01/rook2-exact` |
| Diagnostic companion | `evidence/bitplane-pin-summary-conformance-build-20261020-01/rook2-diag-exact` |
| Own57 merged profile | `evidence/bitplane-pin-summary-pgo-training-20261020-01/merged.profdata` |
| Training provenance | `evidence/bitplane-pin-summary-pgo-training-20261020-01/training.json` |

SHA256 identities:

```text
ordinary: 01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d
DIAG:     eda652abd182cb536736dd758d330f779e94b1e7ad0e779ff7792c2235fffde2
profile:  b4806420937681c8228903507018233d7176be0333ef98881a73d34c66df3a5c
training: bd876da38bc812d43fa2e475b9582cd8d60c6e2a32354521f8c6999c6749ad05
```

The ordinary image is7118376 bytes; DIAG is14038464 bytes; both remain mode0555.
Retained source manifests (not the entire evolving documentation/setup tree) are
117 files, graph`32f3da5d7713aa588b170322a9bea828975c07a79804764b0e919f08e18ebdb7`,
and74 native/tools files, graph`9729230374cb947d3e469140f634b670edf4df6ae87d9af4ab394f5bbc4e9cd0`.
The [source promotion](/home/legolas/rook2-experiments/original-worktree/evidence/exttsp-profiled-integration-20261020-01/source-promotion.json)
binds these identities and finite checks. Do not silently substitute a rebuild.

The existing own57 profile is valid for62 because **candidate57 and62 have the
same native engine source**. The training record contains51 engine-source file
hashes, all matching retained62. This file count is distinct from candidate51:
57 changed `attacks.rs` and `movegen.rs` relative to candidate51. Future native
changes require matching training provenance; blind profile reuse is invalid.
Frozen shorthand such as “Native51” is left intact in historical records; use
actual manifests rather than inferring a candidate identity from that label.

A recipe for a **new, unvalidated rebuild** from the current matching engine is
shown below for reference; it was not executed for this documentation update.
The output directory must be absent, and the recorded compiler/runtime inputs
must be available and checked before comparing artifacts.

```sh
archive=/home/legolas/rook2-experiments/original-worktree
python3 tools/build.py --mode generic --bin rook2 --jobs 4 \
  --pgo-use "$archive/evidence/bitplane-pin-summary-pgo-training-20261020-01/merged.profdata" \
  --training-record "$archive/evidence/bitplane-pin-summary-pgo-training-20261020-01/training.json" \
  --ext-tsp-profiled \
  --output /home/legolas/rook2-experiments/fresh62-rebuild
```

The recorded build uses rustc1.85.1/LLVM19.1.7, O3/thinLTO/one codegen unit,
panic-abort/debug1, target`x86_64-unknown-linux-gnu`, generic`target-cpu=x86-64`.
The ExtTSP switch requires profile use and emits one combined LLVM value:

```text
-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false
```

Missing/stale-profile checks remain enabled. Paths, toolchain and build metadata
can affect a new image; this recipe does not promise byte-for-byte reproduction
or transfer the existing artifact's validation to a rebuild. The original
[receipt](../evidence/exttsp-profiled-pgo-use-build-20261020-01/receipt.json)
records exact compiler hashes, arguments, environment and source snapshots.
No fresh training or canonical-path rebuild was performed when62 was retained.

New62 ordinary-image54/wire/regular12 checks are separate from reused195 native,
209 diagnostic and7673 mandatory-case evidence for unchanged engine/DIAG source
and the exact companion. Finite success is not final qualification; see
[current status](../STATUS.md) and [remaining obligations](qualification-gaps.md).

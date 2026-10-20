# Retained production build62

The tested ordinary image is `evidence/exttsp-profiled-pgo-use-build-20261020-01/rook2-exact`,
SHA256 `01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d`.
The exact retained diagnostic is the57 companion, SHA256
`eda652abd182cb536736dd758d330f779e94b1e7ad0e779ff7792c2235fffde2`.
Do not silently replace either image with an unvalidated rebuild.

Build62 uses explicit `--pgo-use` with the immutable own57 `merged.profdata`
and its `training.json`, together with `--ext-tsp-profiled`. Consult the helper's
argument definitions and the immutable62 receipt for all required paths/options.
This document records a recipe; it does not claim another build was executed.

The emitted LLVM argument is a single combined value:

```text
-pgo-warn-missing-function -enable-ext-tsp-block-placement=true -ext-tsp-apply-without-profile=false
```

The recipe remains O3/thinLTO/one codegen unit/panic-abort/generic x86-64. Default
builds remain unchanged and do not implicitly select62's layout. The new switch
rejects non-profile-use builds. Missing/stale-profile checks remain enabled.
Existing own57 training source is valid because engine source51 is unchanged;
future native-source changes require valid training provenance rather than blind
reuse. Build/source/tool/environment receipts are retained at
`evidence/exttsp-profiled-pgo-use-build-20261020-01/receipt.json`.

Root copied only the reviewed helper into canonical source after all new main
artifact checks. No canonical-path rebuild or fresh training occurred. Original
unit/mandatory/diagnostic checks are reused unchanged-source/companion evidence;
actual62 main-image checks and exact source117 promotion are recorded separately
in `evidence/exttsp-profiled-integration-20261020-01/source-promotion.json`.

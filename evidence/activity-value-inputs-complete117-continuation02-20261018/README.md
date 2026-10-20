# Activity-only complete117 corpus continuation02 — HOLD

Reviewable preparation only. No build, unit, engine/corpus, strict/wire, Git, timing, profiler, PGO or codegen command was launched. `execution-clearance.json` is false; a new parent continuation clearance is required. Attempt01, all its scripts/plans/logs/images and its failed outer terminal remain untouched.

## Actual failure and reusable proof

Attempt01 DIAG outer20878/e7032c→588af9 exited1. Its verification remains `complete:false`. All four observed children exited0: unit compilation, the frozen209-test image, adapter build and archive helper. The failure occurred after these children and before creating raw-cases or conformance streams. This is not a successful completed stage and is not relabeled as one.

The concrete assertion confused two scopes. `tools/build.py --crate diagnostic` snapshots tools inside that diagnostic crate, which has no tools: `tool_sha256_before/after == {}`. The23 root tools belong to the separate112-file closure and native generic receipt, not that crate-local map. `crate-tool-scope-correction.patch` shows the exact two assertion corrections independently of the lean continuation adaptation. Root23 is still required/hashed separately; nothing is dropped from source coverage.

`partial-proof.json` is backed by actual metadata-only checks (`prepare_continuation.py`, d362ba/0):

- Exact209 test stdout count and original child return, frozen unit SHA `e9a720a631c572d327bca9df95f07a0aac90757cecc8685fa316d89d66296aae`.
- Exact frozen adapter `0e5eb3e074e81835ae791f00b0f98c838cbd9c5cdf01ef7f5b74965a355a9e80`, successful build receipt, identical generic compiler/settings, source-before/after43, crate-local tools0, archive receipt and reopened43-member archive.
- Full112-source graph `d49e7e3fb4b2af77da9ab5e9ee801ba3e9d6673d00be8e73e0389afba9260b03`, native46/root tools23/cold43 unchanged across frozen and execution copies, exact original source archive. No pawn fusion or other engine change.
- Attempt01 corpus paths absent, original outer failure1 and every child stream/exit pinned. Native178, generic7cf,54 strict/eight-wire24 and their actual terminals/independent raw evidence remain byte-bound reuse.

No unit or build needs repeating to correct this metadata assertion. Public semantic corpus results are still entirely unproduced.

## Concrete continuation

`run_corpus.py` contains only the original released run.mjs invocation over the same115 whole originals/117 operations/7673 unique cases, through byte-identical `record_case.py`, on the same frozen0e adapter. There is no compiler, unit, native178, strict or wire execution branch. A fresh absent `corpus/` output permits one attempt; failure/raw output is retained, with no retry loop.

The guard checks the partial proof before and after future stages, including actual01 failure1, green children0, untouched source/dependency/archive/image hashes and corpus-never-started01. It retains the accepted source advancement receipt but **old01 execution permission does not authorize this new scope**. New parent clearance must bind this continuation plan SHA/source graph, closed CPU windows and reviewed acceptance. Every helper/adapter inherits exact0–5,8–13 with HOME TMPDIR.

After future corpus actual exit0, `reconcile.py` independently compares every original case's full request, expected output, official actual output, raw stdin/stdout/stderr, adapter PID/exit, whole header, ID/order and operation counts. It verifies reused209 proof separately from new corpus success, and rechecks recorded native/strict/wire evidence offline. Its diagnostic receipt/archive checks use crate-local tools0; root23 remains covered by guard and generic/native receipt. `finalize.py` requires actual new corpus/reconciler terminals, retains the actual failed01 terminal in the new summary, and uses the already-reviewed safe evidence-relative metadata packager. Source/input archives are reused rather than rewritten.

`continuation-adaptation.patch` exposes all changes from01 guard/stage/reconciler/finalizer; the recorder is unchanged. Five Python sources were AST-checked during preparation; no validation entry point was invoked. The offline preparation imports only guard definitions/metadata checks and starts no subprocess.

`commands.json` lists the future three commands (corpus → independent reconciliation → metadata finalizer), all explicitly unauthorized now. Each outer actual terminal must be recorded before the next command. Stop on any failure before correction. No source promotion, full-domain/full-game qualification or performance claim follows from this continuation.

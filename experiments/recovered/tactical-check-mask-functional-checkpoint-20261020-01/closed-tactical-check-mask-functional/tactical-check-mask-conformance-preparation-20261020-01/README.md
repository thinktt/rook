# Experiment51 inert full-native/mandatory conformance workflow

Source staging: `/home/legolas/rook2-work/imp2-tactical-check-mask-conformance-20261020-01`,117 exact files, graph3b816cf8b63af3d6a3b1662d9fa0a53110a9704cf6c13fb456db56e37072f801. Frozen51 native74 graph05a848bb (51native+23tools) plus43 retained diagnostic files byte-identical to accepted43. Versus accepted43 combined115, only tactical.rs/Q and new check_masks.rs/check_mask_tests.rs differ. Root, W51, prior evidence and fixtures remain untouched.

Adapted EXACT accepted43 conformance method. `method-src/` preserves all five helpers; helper-adaptation.patch exposes namespace/source-count changes,193native=191lib+2dev and the current parent decision schema. stage.run/units/build bodies are byte-identical; record_case.py is wholly byte-identical. Native193 and diagnostic209 are separate package test executions: the adapter does not duplicate native193 when running its209 own tests. All counts are declarations, not newly observed passes. No full193 or209 execution is claimed here.

Native and DIAG unit compilation uses Cargo --no-run, records discovered exact target binaries, freezes each image, then invokes each once --test-threads=1 with actual PID/exit/raw/hash checks. Separate native stage precedes DIAG build/corpus. The diagnostic companion links exact51 native sources through unchanged Cargo path dependency; it is a distinct generic image, not the ordinary own-PGO48ee57b1 image. Generic reference460cbf and source-matched own-profile1ce0e391/use48ee57b1 receipts, stage/training/independent-remerge proof and parent full-validation decision are pinned. No previous suite, strict54/wire/game or timing qualification transfers.

All115 ORIGINAL whole fixture files were reopened and independently enumerated:117operations,7673 unique IDs, no partial files/new routes/duplicate IDs. Headers/hashes/counts match accepted43 exactly. Original run.mjs and its authority dependencies remain bound. Every original request/stdout/stderr/child PID/exit is recorded; independent reconciliation compares every raw response against original expected data AND official actual result, checks all native/DIAG raw pass lines/image identities and reopened source/official/build archives. Expected answers remain outside engine source. Existing domain limitations and external3288 exclusion remain explicit in validation-plan.json.

All execution-clearance.json stages are FALSE; root must review and activate exact plan plus parent-final-validation decision and actual quiet admission. Explicit commands, from this directory after root activation only:

```text
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 stage.py freeze
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 stage.py native
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 stage.py build
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 stage.py corpus
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 reconcile.py
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 finalize.py
```

All builds, unit/adapter engines and helpers inherit H0–5,8–13/HOME TMPDIR. Output paths must remain absent until the owning stage; do not precreate compiler/build targets. Root observes each actual outer completion and writes that output/tool-terminal.json before the dependent stage. Required shape: actual_tool_terminal_observed:true, exit_code:0, genuine initial_chunk_id and terminal_chunk_id (equal if sessionless). Preserve any failure and halt dependents; no retries or source repair. No native/compiler/helper import/parser/run, engine, archive, Git or profiling occurred during this preparation. Runtime/artifact/actual fields remain null until execution.

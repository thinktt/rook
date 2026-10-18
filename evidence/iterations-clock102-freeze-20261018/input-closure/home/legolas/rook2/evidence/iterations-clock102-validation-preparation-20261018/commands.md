# Future commands only: execution is not currently authorized

After explicit parent clearance and actual successful pilot/reconciliation terminals, create execution-clearance.json with:

```json
{"authorized":true,"scope":"iterations-clock102-untimed-validation","conflicting_cpu_windows_closed":true,"phase2_cpu_pilot":{"actual_tool_terminal_observed":true,"session_id":123,"initial_chunk_id":"ACTUAL","terminal_chunk_id":"ACTUAL","exit_code":0},"phase2_independent_reconciliation":{"actual_tool_terminal_observed":true,"session_id":null,"initial_chunk_id":"ACTUAL","terminal_chunk_id":"ACTUAL","exit_code":0}}
```

The numbers above describe schema, not observed handles; replace with the actual terminal records. Never copy these example records into an authorization receipt. Then run serially, observing the actual tool terminal and externally recording each stage tool-terminal.json before the next command:

```sh
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/iterations-clock102-validation-preparation-20261018/stage.py freeze
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/iterations-clock102-validation-preparation-20261018/stage.py generic
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/iterations-clock102-validation-preparation-20261018/stage.py native
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/iterations-clock102-validation-preparation-20261018/stage.py codegen
```

STOP: deliver capture and material findings to parent before source fixes or strict/DIAG. After parent accepts the actual bounded codegen result, codegen-acceptance.json must contain accepted_by_parent:true, strict_and_diag_authorized:true, codegen_capture_sha256 (actual future hash), and parent_review_reference. No acceptance file is supplied now. Only then:

```sh
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/iterations-clock102-validation-preparation-20261018/stage.py strict
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/iterations-clock102-validation-preparation-20261018/stage.py diag
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/iterations-clock102-validation-preparation-20261018/reconcile.py
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/iterations-clock102-validation-preparation-20261018/finalize.py
```

No source/build/output directories are precreated during preparation. No source repairs, CPU/PGO/profiler, control rebuild or separate first/clock validation are authorized by this file.

Prepared commands only. Parent authorization is absent. Set TMPDIR and run each stage serially; capture actual outer session, final chunk and exit in an external terminal record before advancing. `tool-terminal.template.json` is not evidence.

```
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/complete117-pgo-preparation-20261018/build_stage.py instrumented
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/complete117-pgo-preparation-20261018/train.py
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/complete117-pgo-preparation-20261018/verify.py
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/complete117-pgo-preparation-20261018/build_stage.py use
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/complete117-pgo-preparation-20261018/check.py
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/complete117-pgo-preparation-20261018/reconcile.py
```

Expected outer terminal records in order: instrumented-build/tool-terminal.json; training/tool-terminal.json; training/verify-tool-terminal.json; use-build/tool-terminal.json; use-check/tool-terminal.json; reconciliation/tool-terminal.json, using the full directories in plan.json. Child-return records are supplemental, never substitutes for observed outer tool terminal. On any failure preserve all files and actual terminal; report before repair/retry; use new labels for retries. Never precreate training/raw: build.py requires absent raw and creates it. The build helper creates training/ only after clearance; no source copy/archive is made during preparation. Training engine alone is taskset14; Node/helper/merge/build and all post-use regression engines inherit housekeeping0-5,8-13. Parent reviews sibling15/interference; no absolute idle assertion. No CPU timing/PMU/codegen command is supplied.

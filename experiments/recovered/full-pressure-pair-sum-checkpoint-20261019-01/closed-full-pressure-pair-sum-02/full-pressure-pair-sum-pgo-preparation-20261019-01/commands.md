Prepared future commands only. Each actual outer exit/terminal must be recorded before advancing; false clearance blocks all stages. No current generic result is assumed.

```
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/full-pressure-pair-sum-pgo-preparation-20261019-01/build_stage.py instrumented
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/full-pressure-pair-sum-pgo-preparation-20261019-01/train.py
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/full-pressure-pair-sum-pgo-preparation-20261019-01/verify.py
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/full-pressure-pair-sum-pgo-preparation-20261019-01/build_stage.py use
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/full-pressure-pair-sum-pgo-preparation-20261019-01/check.py
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/full-pressure-pair-sum-pgo-preparation-20261019-01/reconcile.py
```

Actual outer receipts, in order: instrumented-build/tool-terminal.json; training/tool-terminal.json; training/verify-tool-terminal.json; use-build/tool-terminal.json; use-check/tool-terminal.json; reconciliation/tool-terminal.json. Use full paths from plan.json. Child-return records never replace actual outer receipts. Never precreate build outputs or training/raw; build.py creates the absent raw directory. Preserve failed attempts and stop dependent stages; no silent source fix or favorable retry.

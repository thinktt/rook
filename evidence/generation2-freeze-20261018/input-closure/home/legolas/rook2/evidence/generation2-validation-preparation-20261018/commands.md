# Authorized future stage order

Parent has now explicitly cleared execution after pilots53579/df8bc0+6ab661 and55883/ace2ea+c7bf06 actually exited0. First finish/inspect the plan/scripts, then write execution-clearance.json with those actual records. No source strengthening. Run serially, observe each actual outer terminal, and write the stage output's tool-terminal.json before next command. Generic stage outputs verification in preparation/generic-stage-logs, exact artifact/receipt in generic-build; DIAG parent terminal covers its unit+build+case children.

```sh
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/generation2-validation-preparation-20261018/stage.py freeze
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/generation2-validation-preparation-20261018/stage.py generic
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/generation2-validation-preparation-20261018/stage.py native
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/generation2-validation-preparation-20261018/stage.py strict
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/generation2-validation-preparation-20261018/stage.py diag
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/generation2-validation-preparation-20261018/reconcile.py
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/home/legolas/rook2-build-tmp python3 /home/legolas/rook2/evidence/generation2-validation-preparation-20261018/finalize.py
```

No old151/149 or7393 result is substituted. All152native,156DIAG/7447/97/92 and54strict/eightwire24 are fresh. Freeze copies exactly100 declared source files to unique HOME path, then archives source and original input bytes only after clearance. No prior source/evidence/root changes. Build/parser/semantic failure: retain actual terminal and logs, report before source fix; do not rerun into same output paths.

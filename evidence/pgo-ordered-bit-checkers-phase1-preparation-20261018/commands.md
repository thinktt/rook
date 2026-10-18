# Future commands — DO NOT EXECUTE until parent authorization

Run serially, observe each actual terminal and write the documented external terminal record before continuing. No CPU timing command is provided. Parent must verify sibling15 idle before training14.

```sh
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/pgo-ordered-bit-checkers-phase1-preparation-20261018/ready.py
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/pgo-ordered-bit-checkers-phase1-preparation-20261018/build_stage.py instrumented
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/pgo-ordered-bit-checkers-phase1-training-20261018/train.py
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/pgo-ordered-bit-checkers-phase1-training-20261018/verify.py
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/pgo-ordered-bit-checkers-phase1-preparation-20261018/build_stage.py use
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/pgo-ordered-bit-checkers-phase1-use-check-20261018/check.py
taskset -c 0-5,8-13 env PYTHONDONTWRITEBYTECODE=1 python3 /home/legolas/rook2/evidence/pgo-ordered-bit-checkers-phase1-preparation-20261018/reconcile.py
```

`execution-clearance.json` intentionally absent. It is an explicit parent authorization record, not a timeout/readiness inference. The train driver preserves original replay-check.mjs invocation and records54 unique child PIDs corresponding exactly to54 native-%m-%p.profraw files. verify.py independently parses all child exits, rehashes every raw file and remerges into a new file, requiring byte equality. Post-use strict54 and wire8/24 use housekeeping engines and root-equivalent frozen tools/check_live.py. Both build modes freeze exact image and archive immediately after actual build-child return; external actual outer terminal records are still mandatory.

Final reconciliation deliberately revisits both baseline's existing evidence and candidate's fresh evidence, preserving raw stdout/stderr, reconstructed stdin labels for original replays (not a stdin tap), literal wire bytes, native child exits, source/tool closure, profile gzip and independently remerged bytes. It never rebuilds/retrains/reexecutes baseline.

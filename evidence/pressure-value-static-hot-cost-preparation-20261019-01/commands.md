INERT: after parent source review, final conformance/adoption proof binding and explicit quiet-window activation only:

    taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 profile.py

Run from this preparation directory or use its absolute profile.py path. Observe actual outer session/chunk/exit before advancing, preserve any failure; parent writes real output/tool-terminal.json only after actual successful termination. Then:

    taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Again record actual terminal, do not infer from files. Both clearance flags and final accepted proof must be bound before the first run; do not change them between profile/verify. New private output path must be absent; the accepted driver handles only original35→08, native14/helpersH. No retries or automatic follow-on measurements.

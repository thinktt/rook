# Future separate commands — HOLD

Parent must review sources/pins and replace false clearance first. Run ONE stage at a time, record actual outer session/chunk/exit, preserve any failure and stop. These commands do not authorize themselves.

```sh
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 /home/legolas/rook2/evidence/placement-pure-cache-validation-preparation-20261018-01/stages.py build
```

```sh
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 /home/legolas/rook2/evidence/placement-pure-cache-validation-preparation-20261018-01/stages.py native
```

```sh
taskset -c 0-5,8-13 env TMPDIR=/home/legolas/rook2-build-tmp PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 /home/legolas/rook2/evidence/placement-pure-cache-validation-preparation-20261018-01/stages.py regression
```

After real stage closure parent writes functional-result.json using accepted TT schema with status GENERIC184_STRICT54_EIGHTWIRE24_PASS, native/library/development184/182/2, new_pure_cache_tests_pass true ONLY from all six actual raw tests, strict54/wire8/24, exact source/image/receipt/archive/native/regression hashes and real B/N/R terminals. No output/result/PASS was created by this preparation. Separate independent clearance then authorizes ONLY offline verify.py.

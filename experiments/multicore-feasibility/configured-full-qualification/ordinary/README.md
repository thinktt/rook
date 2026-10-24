# Frozen ordinary PGO qualification setup

This setup binds source `66f35e44` and ordinary image SHA256
`8f26d39fd1a69bc8a3aa6da2c364b6ddb4b065bc585a27c7420ae994566f8b1b`.
It runs no build or training and changes no engine or released comparator source.
Preparation and syntax checking do not establish a passing qualification result.

Run each command on helpers `0-5,8-13`, under the parent's announced, serialized
native window. All paths below are absolute after preparation. A fresh raw
destination is required; no native failure is retried.

```text
python3 prepare.py --output /ABS/FRESH/ordinary
python3 ../../configured-full/verify.py --engine /home/legolas/rook2-experiments/configured-full-20261024-01/production/rook2-pgo --output /ABS/FRESH/ordinary/configuration
python3 run.py /ABS/FRESH/ordinary/mode2
python3 run.py /ABS/FRESH/ordinary/mode1
```

`setup.json` provides the exact absolute configuration-verification and lane
commands. `run.py` requires the completed same-image verification first. Each
lane has its own frozen `plan.json`, raw streams, original reports, stage exits,
native receipts, `independent-reconciliation.json` and `lane-outcome.json`.

| Configuration | Selected ordinary coverage | Native lifetimes | Aggregate cap |
|---|---|---:|---:|
| Requested/configured 2 | Released regular12, continuity8, seed11, persistence3, wire8/24, literal original combine | 33 | 1200 s |
| Requested/configured 1 | Continuity8, seed11, persistence3, wire8/24 | 21 | 300 s |

The reused `configured-full/verify.py` adds 13 inspection/invalid-request
processes and two original08 lives; those are separate configuration checks.
The original game, continuity, seed and wire limits remain unchanged. Each lane
also caps address space at 8 GiB per process, files at 256 MiB and retained
streams at 512 MiB. These are resource limits, not memory qualification.

All 22 mode2 and 10 mode1 search-owning processes begin with permitted CPUs
`6,14`. The frozen `usable-full/account_threads.py` supervisor verifies the
configured task count, places main on 14 and helper on 6, and writes a ready
receipt. The input gates verify this receipt before forwarding the first setup
byte. CPU 7 and 15 are excluded from owned work. No engine affinity is widened.
The wire adapter calls the original `Process.__init__` unchanged, records its
PID, and gates its first `send`; the original checker assertions remain intact.

The released synchronous seed controls supply their input eagerly. Their 11
no-search children per mode therefore use a narrow direct-`wait4` supervisor
with permitted `6,14` and actual or unavailable post-exec task observations.
Eight expected parser exits are 1. These controls do not establish pre-input
placement or threaded-search coverage. No observation is forced or retried.
This limitation is recorded separately from the fully gated search lifetimes.

The unchanged released `combine.mjs` is invoked only in mode2. Its output is
retained literally. Mode1 has no games or combine directory and explicitly
reports `completeFocusedReplay:false`. Neither lane claims the full3288 gate,
performance qualification, adoption or external delivery.

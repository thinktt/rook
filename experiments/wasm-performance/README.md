# Native / Node / Chromium search performance

Use the unchanged released54 workload and correctness oracle. Compare the frozen
PGO native release with the existing non-PGO WASM ordinary module; this measures
these actual builds, rather than isolating WebAssembly overhead alone.

The collector alternates runtime order by case/round, with one excluded warmup
and three measured repetitions for each runtime/case: 648 runs, 486 measured.
Report the sum of the 54 per-case medians and retain every sample/range. A fresh
engine process is used for native/Node; Chromium uses a fresh context, renderer
and worker, with a shared browser parent. The same semantic posts/work/move must
match for every run. No fixture answers are supplied to the engine.

The measured interval is `go` dispatch through selected-move receipt. Startup,
WASM instantiation, setup and shutdown are excluded. Linux `clock_getcpuclockid`
and `clock_gettime` sample the live process CPU clock, including all its threads,
without `/proc/stat` tick quantization. An independent Node worker-burn control
checks inclusion of worker CPU. Clock resolution is recorded; it is not an
accuracy guarantee for the surrounding receipt boundary. See the Linux manuals
for [process clocks](https://man7.org/linux/man-pages/man3/clock_getcpuclockid.3.html)
and [CPU-clock scope](https://man7.org/linux/man-pages/man2/clock_gettime.2.html).

Chromium's unique renderer is identified by its dedicated-worker thread. Every
renderer thread is pinned to the chosen CPU before search; browser/GPU/utility
processes, HTTP server, clock helper and controller remain on CPU0. Renderer CPU
includes its page, worker and background compilation threads, but excludes other
browser processes. Extra in-page wall time is retained alongside the outer CDP
request wall interval. Browser quit is an observed worker command status2,
projected to the comparator's clean-exit field, not a POSIX engine-exit receipt.

All native/Node threads are also pinned to CPU14. Leave sibling15 idle and
coordinate a quiet build/native window. Snapshots are finite observations, not
continuous proof of exclusive host ownership. No PMU/cycles/IPC data are collected.
The study is a local comparison, not KingRE performance qualification.

Compile the small read-only clock sampler outside the repository:

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror tools/process_clock.c -o /external/process-clock
```

Run the collector from a housekeeping CPU with explicit local tool/artifact paths:

```sh
taskset -c 0 node tools/benchmark_wasm.mjs \
  --output /external/fresh-results --native /path/to/qualified/native/rook \
  --clock /external/process-clock \
  --playwright /path/to/playwright/index.mjs --chromium /path/to/chromium \
  --cpu 14 --repeats 3
python3 tools/check_wasm_benchmark.py /external/fresh-results
```

The collector records and rechecks supplied artifact identities; no candidate
hashes are hardcoded. The exact collector source is retained with each run. The
recorded run used an earlier identity-guarded version; its archived source matches
the plan hash. The reusable version removes that fixed artifact restriction,
with the same measurement loop.
Use `--cpu 0 --case profile-01 --repeats 1` only as a tooling pilot, not as the
54-case result. The collector does not build or rebuild engines. Browser
runtime libraries may need their own local `LD_LIBRARY_PATH` on a minimal VM.

Raw data belong outside Git. The collector checks correctness at every run,
retains exact inputs/artifact identities, and stops on failure. It bounds search,
readiness, total time and output sizes. HTTP logs are drained to a file; a 1 MiB
logging regression control precedes collection. The initial incomplete batch
stalled at browser startup on an undrained server-log socket and is excluded;
its metadata/partial records remain preserved. Final results are recorded only
from one complete fresh batch after that repair.

## Recorded result

All648 runs pass exact behavioral checks, including an independent offline oracle
recheck. One warmup is excluded; each cell sums54 case medians from three measured
runs per case.

| Runtime | CPU seconds | Wall seconds | CPU time / native |
|---|---:|---:|---:|
| Native PGO | 67.899 | 67.930 | 1.000 |
| Node20.19.2 / WASM | 118.947 | 118.932 | 1.752 |
| Chromium145.0.7632.6 / WASM | 113.520 | 113.637 | 1.672 |

Median per-case CPU sample-range/median: native0.679%, Node0.877%, Chromium0.604%.
Worst case ranges: native1.789%, Node4.353%, Chromium2.344%. These are observed
three-sample ranges, not confidence intervals. Chromium used4.56% less renderer
CPU than Node's process CPU on this workload.

[Concise result metadata](result.json) bind the raw plan,
receipts, collector source and independent closure. All54 case summaries and raw
files are outside Git at
`/home/legolas/rook2-experiments/wasm-performance-20261102/full54-final`.
All653 recorded owned process identities were absent at terminal release.
No further native measurement is selected.

GuestCPU15 recorded8.43s of busy time across the batch (about0.66%), despite the
team reservation. This is disclosed background activity; neither its source nor
a precise effect on CPU14 is inferred. The quiet window is not an absolute host
isolation claim.

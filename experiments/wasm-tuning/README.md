# WASM compilation and runtime study

This study changes compiler flags and host settings only. Rust source and the
previously qualified ordinary/diagnostic artifacts remain unchanged. Raw runs,
builds and frozen inputs are outside Git at
`/home/legolas/rook2-experiments/wasm-tuning-20261103`.

## Reproduce the selected compiler recipe

Use the Rust 1.85.1 Debian compiler and matching `wasm32-unknown-unknown` standard
library used by the original module. The control build reproduces its SHA256
`91e4c4ab50a5bb5b73004e508ca8329ab4378bfb7fc7b7085618609077750c5e`.
Choose a new output directory; the helper never writes `wasm/dist`:

```sh
python3 experiments/wasm-tuning/build.py \
  --output /absolute/new-output-directory \
  --sysroot /absolute/matching-rust-sysroot \
  --variants experiments/wasm-tuning/selected-build.json
```

The recipe retains optimization level 3, one codegen unit, aborting panics,
debug level 1 and an 8 MiB stack. It selects full LTO, SIMD128 and bulk-memory
instructions. It does not introduce engine intrinsics or change Rust source.
The resulting experimental ordinary module is 1,945,839 bytes, SHA256
`0974bb96e645928120c8f389555a58f0ca1832b535865cb2d0864a02c091e0c4`.

## Experiments

- Resident Node instances with a fresh Rust engine handle per query reduced the
  six-case CPU median sum by 3.28%. Short cases benefited most. WASM compilation,
  memory and allocator warmth remain shared; this does not isolate JIT effects.
- Full LTO plus SIMD reduced the six-case sum by 2.48% with normal V8 settings,
  or 6.33% with eager optimizing compilation. Thin LTO/SIMD separately helped
  less. Binaryen `wasm-opt -O3 -g` did not improve that screen and was parked.
- Adding bulk-memory instructions reduced the three-case sum by 4.82% under
  normal V8 settings, or 8.14% with eager compilation, versus the original
  module under normal settings. These screens selected the full54 confirmation;
  they are not whole-suite estimates.

Eager settings are `--no-liftoff --no-wasm-tier-up
--no-wasm-lazy-compilation`. They move compilation before search and raise
startup cost (roughly 0.10 to 0.31 seconds in the Node compiler screen).
Websites cannot enable these flags through JavaScript. The browser API already
keeps its worker and module alive; persistence needs no production change.
See [V8's compilation pipeline](https://v8.dev/docs/wasm-compilation-pipeline).

The bulk build's original driver exited 1 after both successful compiler waits:
its report assumed a control variant existed. The original report and traceback
are preserved. `bulk/build-completion.json` reconciles both artifact hashes and
unchanged inputs; no compiler stage was repeated. The helper now handles a
variant list without a control. LLVM PGO was not attempted because the matching
WASM profiler runtime is absent from this local sysroot.

## Collection and validation

`screen.py` and `session.mjs` implement bounded Node cold/resident screens;
`recheck.mjs` checks saved streams against the released replay oracle.
`serve.py` supplies explicit named artifact routes for the shared benchmark
page. The generic `tools/benchmark_wasm.mjs --profiles <json>` collector accepts
named native, Node and Chromium profiles with module paths and optional V8
flags. It records source/artifact identities and fresh process CPU boundaries.
`tools/check_wasm_benchmark.py <run-directory>` independently checks its saved
full54 arithmetic, lifecycle and CPU placements.

For a new full54 collection, supply a JSON object of named profiles, for example
`{"native":{"kind":"native"},"browser":{"kind":"chromium","wasm":"/absolute/selected.wasm"}}`.
Node profiles use `"kind":"node"`; an optional `"flags":[...]` sets V8 flags.
Use absolute module paths. The frozen six-profile configuration for this study
is `confirmation-final.json` in the raw directory. Invoke the collector with
`--profiles <json> --server experiments/wasm-tuning/serve.py
--page wasm/benchmark.html --cpu 14 --repeats 3 --seconds 3600`, plus the usual
`--output`, `--native`, `--clock`, `--playwright` and `--chromium` paths documented
in [the original benchmark](../wasm-performance/README.md). Then run both the
Python saved-data checker and `node experiments/wasm-tuning/recheck-full54.mjs
<run-directory>`. Coordinate a fresh quiet window before executing measurements.

## Full54 confirmation

One excluded warmup and three measured samples per case/configuration produced
1,296 exact searches. The table sums the 54 per-case medians, in seconds.
CPU includes all threads of the measured native/Node process or Chromium
renderer. Search spans go dispatch through selected-move receipt.

| Configuration | Search CPU | Search wall | CPU/native | CPU through move, including setup |
|---|---:|---:|---:|---:|
| Native PGO control | 68.016 | 68.044 | 1.000 | 68.149 |
| Original WASM, Node default | 119.232 | 119.220 | 1.753 | 127.002 |
| Selected WASM, Node eager | 105.366 | 105.388 | 1.549 | 124.374 |
| Original WASM, Chromium default | 113.766 | 113.877 | 1.673 | 116.603 |
| Selected WASM, Chromium default | 105.271 | 105.403 | 1.548 | 108.039 |
| Selected WASM, Chromium eager | 101.053 | 101.123 | 1.486 | 122.963 |

**The practical browser result is 7.47% less search CPU with normal settings**:
53/54 cases improved, with the remaining case 0.81% higher. Including renderer
startup/setup, the reduction is 7.34%. No special browser launch flags are needed.

Node eager reduces search CPU by 11.63% (54/54 cases), but only 2.07% including
startup/setup. Chromium eager reduces search CPU by 11.17% (54/54 cases), yet
increases cold-start CPU through the move by 5.45%. Eager compilation is useful
evidence about compilation placement, not a recommendation for one-shot browser
searches. Median pre-search CPU is 0.145s versus 0.352s for original/default and
selected/eager Node, and 0.053s versus 0.407s for Chromium. These include setup;
they are not isolated compiler timers. The through-move column takes medians of
the actual cumulative CPU samples, rather than adding separately chosen medians.

The timing checker reconciles all 1,296 raw receipts, all clock deltas, placement
snapshots, 648 distinct Chromium renderers and totals. An independent offline
released-oracle pass checks all streams again. Final preservation checks confirm
all 94 Rust files, all 99 build-input pins and both original modules unchanged;
1,305 recorded process IDs, including the collector, are absent after cleanup.
The collector's actual joined exit is 0. See [result.json](result.json) for exact
identities, evidence hashes and ranges. Median per-case three-sample ranges are
0.59–0.99% of the median across WASM configurations; maximum range is 7.64%
for original/default Node. Results are descriptive, without a confidence model.

Measurements used CPU14; sibling15 had 5.26s aggregate busy time over the roughly
46-minute window (about 0.19%), despite the requested quiet window. No competing
team native lane was active. Node was v20.19.2; Chromium was 145.0.7632.6.
The native control uses PGO and WASM does not. Chromium excludes browser-parent,
GPU and utility CPU, so the through-move column is not whole-browser cost.
No retired instructions/cycles were collected; no single cause for the remaining
gap is established.

No new module is promoted by this study. The selected ordinary module passes
this finite54-case scope; its mandatory diagnostic suite and12-game pre-gate were
not rerun. The original diagnostic module and qualification records remain the
originals. There was no full3288-game gate or native architecture change.

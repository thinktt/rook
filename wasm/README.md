# Rook WebAssembly

Two modules share the Rust engine with the native build:

- `rook.wasm`: a persistent ordinary engine for a browser worker.
- `rook-diag.wasm`: the existing JSON diagnostic dispatcher with a string boundary.

There is no JavaScript engine implementation, WASI runtime, wasm-bindgen glue or
runtime npm dependency. The JS files are ordinary ES modules. Keep them together
with a `dist/` directory containing the two built modules.

## Build

Use Rust 1.85 or later, with the matching `wasm32-unknown-unknown` standard library
and a WASM linker. With rustup:

```sh
rustup target add wasm32-unknown-unknown
python3 wasm/build.py
```

Cargo dependencies must already be cached (`cargo fetch --locked --manifest-path
wasm/diagnostic/Cargo.toml` on a connected machine). Builds use the committed
locks, release optimization, an 8 MiB stack and retained debug information. PGO
is not used. `--output DIR` selects a different output directory. Debian's matching
`libstd-rust-dev-wasm32` also works; `--sysroot DIR --linker /usr/bin/wasm-ld-19`
can select an extracted local sysroot without changing the system installation.
Build receipts contain flags, compiler identity, sizes and module hashes.

The Rust changes are platform guards around Linux input and x86-64 SSE2, plus
access to the existing diagnostic dispatcher and WASM clock imports for the
natural-seed diagnostics. The portable transpose is checked against SSE2 in the
native influence tests. Search, evaluation, move ordering, work-clock arithmetic
and game state remain in the shared core. WASM is a 32-bit target; fixture passes
are evidence of observed parity, not an assumption that pointer widths cannot
matter.

## Browser

Serve this folder using the supplied development server:

```sh
node wasm/serve.mjs
# Open http://localhost:8080/
```

The root page serves `rook-test.html`. Open the browser console and send
`window.worker.postMessage('demo')` to run the included example, or pass a raw
XBoard command such as `window.worker.postMessage('cm_parm rnd')`. The worker
loads `dist/rook.wasm` directly and logs engine output to the console. It receives
new commands between searches.

### Benchmark worker

`benchmark.html` uses `worker.mjs` and a SharedArrayBuffer command queue. The
WASM engine polls that queue at search boundaries and publishes output as
worker messages.

Browsers require a secure, cross-origin-isolated context for this command buffer.
Set these response headers on your page and serve the JS/WASM on the same origin:

```text
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

Localhost is suitable for development. Production uses HTTPS. These headers can
require changes to third-party resources or integrations on an existing site;
the supplied server is only a local demo. See the
[SharedArrayBuffer hosting requirements](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer#security_requirements)
and [Rust target limitations](https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html).

## Playwright checks

Install Playwright and its Chromium browser in your test environment. The script
checks the minimal demo, benchmark worker, and diagnostic module in `dist/`.

```sh
node wasm/test-browser.mjs
node wasm/test-browser.mjs --spec /path/to/king-spec
```

The Node process serves the files and controls Playwright. Chromium loads and
executes the WASM.
If Playwright is installed elsewhere, set `PLAYWRIGHT_MODULE` to its
`index.mjs` path.

`--spec` adds the released mandatory diagnostic component fixtures. The browser
compiles the diagnostic module once, creates a fresh instance per request and
compares each response with the released expected output. The prior gameplay,
seed, and wire qualification lanes remain historical results in `validation.json`.
The separate Chromium benchmark still compares the standard54 search traces
against the released oracle.

### Recorded local result

Before the switch to Playwright, the exact pair in `validation.json` passed 115 mandatory files / 7,673 cases,
standard54, the 12-game / 632-search pre-gate, continuity, seed/persistence
controls and eight interruption sessions / 24 searches. Native library and
adapter tests passed; Chromium exercised the browser API and 20 immediate-stop
races. `setPonder` forwarded all three released work-clock presets.

The diagnostic module initially exposed one missing host-clock import; after
repair it passed all mandatory files fresh. A final wire helper failed during
CPU-affinity setup, before launching an engine. Its original empty output
directory/failure remains preserved; only the missing wire sessions ran on CPU0.
The frozen lane driver is retained with its original hash. The future driver
contains the CPU0 bootstrap correction; the entire corrected lane was not rerun.

Local raw reports live under `/home/legolas/rook2-experiments/wasm-qualification-20261102-05`
and `wasm-wire-completion-20261102-01`. Modules/build products live under
`/home/legolas/rook2-experiments/wasm-build-20261102-01`; ignored local symlinks
keep the default `dist/` and Cargo paths convenient. No binaries are committed.
CPU overlap was subsequently reported by another agent, so these runs establish
behavioral observations, not isolated performance measurements.

The [matched native/Node/Chromium benchmark](../experiments/wasm-performance/README.md)
records a separate54-case CPU/wall comparison with startup excluded.

The [compilation/runtime study](../experiments/wasm-tuning/README.md) found
7.47% less Chromium search CPU with full LTO, SIMD128 and bulk-memory enabled,
without Rust changes or browser launch flags. Its recipe and experimental
artifact are separate from the qualified default modules above. Eager V8 flags
improve search-only timing further but add substantial startup cost.

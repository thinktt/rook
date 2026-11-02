# Rook WebAssembly

Two modules share the Rust engine with the native build:

- `rook.wasm`: a persistent ordinary engine, usable from Node or a browser worker.
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

## Node: use the existing harnesses

Node 20 was tested. Both commands accept ordinary stdin and produce ordinary
stdout/stderr with a meaningful exit status:

```sh
node wasm/rook.mjs --work-clock=kingwcr --diagnostic-seed-command
node wasm/rook-diag.mjs
```

The ordinary runner accepts the native launch flags. `--wasm PATH` selects its
module; the diagnostic runner accepts its module path as the first argument.
Defaults are relative to these scripts, not the caller's working directory.
The executable scripts also have Node shebangs for harnesses that accept only one
executable path.

The released harnesses remain external and unchanged:

```sh
node /path/to/king-spec/conformance/run.mjs -- node wasm/rook-diag.mjs
node /path/to/king-spec/conformance/profiling/replay-check.mjs -- node wasm/rook.mjs
node /path/to/king-spec/conformance/gate-replay/run.mjs \
  --report /fresh/output/games.json -- node wasm/rook.mjs
```

The first command includes the two optional diagnostics by default. To run our
mandatory-only and focused qualification selection, with raw reports outside Git:

```sh
python3 wasm/qualify.py --spec /path/to/king-spec --output /fresh/external/results
```

That runs standard54, the mandatory component files, 12 games, continuity,
seed controls, seed persistence and eight interruption sessions, then verifies
input hashes. It pins the lane to CPU14; the unchanged wire helper starts on CPU0 and applies
its housekeeping affinity. Leave CPU15 idle. There is a three-hour aggregate
ceiling, stage deadlines and a 2 GiB report budget. After a deliberate stop,
`--resume /previous/results` can reuse completed standard54/component reports
only when their module bytes, Node host and specification inputs still match.
A changed diagnostic module requires fresh component checks; it does not
invalidate an unchanged ordinary module's replay. Prior
reports are copied with provenance; partial files are run afresh. No automatic retries, timing
acceptance or full 3,288-game gate are included. Inspect `summary.json` after exit.
Released executable-hash fields identify Node or the launcher; `inputs.json`
additionally binds the WASM bytes and host scripts.

## Browser

Serve this folder using the supplied development server:

```sh
python3 wasm/serve.py
# Open http://localhost:8080/
```

Or import the small wrapper from your own application:

```js
import Rook from './rook.js';

const engine = await Rook.create({
  onPost: line => console.log('analysis', line),
  onMove: move => console.log('move', move),
  onLine: line => console.log(line),
  onError: message => console.error(message),
});

await engine.setPersonality(personality.out); // Or pass the whole personality.
await engine.setPonder('easy'); // easy, hard or gm work-clock presets
// Or: await engine.setTimeControl({ remainingMs: 60_000, incrementMs: 1_000 });
await engine.playMove('e2e4');
const reply = await engine.go({ moveTimeMs: 1_000 });
await engine.newGame();
engine.close();
```

The personality shape is the `out` object in yeoldwizard's `personalities.json`:
parameter names mapped to integers or decimal integer strings. The wrapper resets
parameter defaults before applying those weights. It does not implement opening
books, faces or personality metadata. Pondering stays disabled (`easy`).

`playMove` uses coordinate notation and keeps the engine in force mode. `go`
searches for the current side, applies its selected move and resolves with that
move (or undefined if no move is published). One search may run at a time.
`stop()` requests the best move so far; `abort()` cancels without requiring a move.
`newGame()` and `setPersonality()` abort a live search before changing state.
Await idle configuration methods. `send(line)` is the low-level ordinary command
escape hatch; use `stop`/`abort` for search controls rather than serialized `send`.
`newGame` resets the board and game history, retaining the native personality and
session reset behavior; it does not destroy/recreate the WASM instance.

`setPonder('easy' | 'hard' | 'gm')` wraps `setTimeControl` with the released
remaining-clock inputs: 66,370 / 94,830 / 181,000 milliseconds, respectively, and
the standard five-minute base schedule. Names are case-insensitive; omitted mode
means easy. This selects a clock preset; it does not enable background pondering.

Time controls are forwarded to the existing King work-clock engine. The caller
owns the real chess clocks and supplies current remaining time. `baseMs` defaults
to `remainingMs`; `moves` defaults to sudden death; increments use whole seconds.
`go({moveTimeMs})` adds an optional real-wall deadline by requesting a finish.
That is cooperative: worker polls, browser scheduling and background-tab timer
throttling can delay it. It is not a hard wall-time guarantee or a replacement
for the native work-clock contract.

### Worker and hosting

Each Rook owns one persistent worker and private WASM memory. Input commands use
a small single-producer/single-consumer SharedArrayBuffer queue; output comes back
through worker messages. WASM imports poll the queue at the engine's existing
search boundaries. Thus a blocked synchronous search can still see stop/reset
requests. A control arriving just after search ends is marked separately, so it
cannot complete an unrelated idle request. WASM threads/shared linear memory
are not required.

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

## Checks and release scope

```sh
node --test wasm/test-node.mjs
# Optional real-browser test tool, outside the runtime dependencies:
node wasm/test-browser.mjs /path/to/yeoldwizard/personalities.json
```

The browser test needs Playwright/Chromium; `PLAYWRIGHT_MODULE` can point to a
separate installation. It checks personality application, persistent moves,
cooperative deadline/stop, live reset and repeated immediate/late-control races.

This feature does not publish assets or modify the native qualification manifest.
The frozen v1 native binaries and their records remain preserved. Shared-source
edits change the native release build's source identity, so the existing
hash-locked native workflow is not a release recipe for this feature commit.
A future native release requires its own updated build/qualification records.
WASM has separate artifact identities and does not inherit the native full-game
or performance results. See `validation.json` for the local finite checks.

### Recorded local result

The exact pair in `validation.json` passed 115 mandatory files / 7,673 cases,
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

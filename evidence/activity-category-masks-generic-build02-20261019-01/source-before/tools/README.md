# Development tools

These helpers record development evidence. They do not qualify behavior or
performance, and do not change global Cargo, CPU or PMU settings.

## Offline build

From the repository root, inspect a generic x86-64 plan:

```sh
python3 tools/build.py --output evidence/fresh-build --dry-run
```

Remove `--dry-run` to build. The default is `cargo build --offline --locked
--release` with four jobs on housekeeping CPUs `0-5,8-13`. The helper explicitly
selects target `x86_64-unknown-linux-gnu` and `target-cpu=x86-64`. It replaces
inherited Rust flags, disables Rust compiler wrappers for the invocation, and
records overrides; it does not edit crate or global configuration. Dependencies
must already be cached, and an existing Cargo.lock is required.

`--mode native` opts into `target-cpu=native`. Generic and native outputs use
separate `target/dev-generic` and `target/dev-native` directories and remain
different artifact modes. Changing target mode does not enable PGO; use the explicit options below. `--jobs N` changes the
default; `--crate PATH` selects another crate.

`--bin rook2` builds the ordinary production-wire executable; `--bin rook2-dev`
builds the native development executable. Both record the selected binary's
SHA256. The helper never runs the compiled binary or tests.

Every actual build requires a fresh receipt directory. It retains
`receipt.json`, `build.stdout` and `build.stderr`, including failures. The receipt
binds Cargo.toml, Cargo.lock and every file under src, optional build.rs/toolchain
files, available Cargo configuration hashes, git HEAD/status, tool versions,
actual build arguments/environment overrides, before/after input identities,
timestamps, outcome and optional executable hash. An unborn git HEAD is
recorded as unavailable, not invented. Source changes during compilation make
the result unsuitable for an exact input-identity claim even if Cargo succeeds.
External/path-dependency/generated-input closure is not automatically attested.

The helper also preserves pre-Cargo source/tool bytes, verified against the
recorded hashes. Frozen evidence may include a verified compressed copy of that
tree; exact binaries and uncompressed working copies stay local.

## External native correctness checks

`check_policies.py --output evidence/new-policy-check` builds a separate Rust
test crate from selected released policy expectations. `check_evaluation.py`
uses a data-driven test crate to cover the larger evaluator and composed root
sequences without expanding every query into compiler input. Expected records
remain outside the engine. The latter preserves actual move kinds, complete
root steps, native component results and charged work observations.

`check_timing.py` uses the same external data-driven approach for the work
ledger, adaptive limits, iteration terminal stop, root randomness/aspiration
and selected actual recursive timed-search observations. It compares native
root/time/stop/capture state and complete semantic post/move trails. It also
checks schedule allocation, parameter commands, idle clock setup, fresh joined
search projections, persistent clock-seeded sessions and deterministic live
host interruption/status events. Literal wire I/O and strict diagnostic
validation remain separate.

`check_live.py --engine /absolute/path/rook2 --output evidence/fresh-live-check`
replays all eight released interruption fixtures through the ordinary byte
stream. Each fixture retains one process across its three searches. It sends
the queue with `go`, waits for the move/abort boundary before later setup,
compares every semantic event and abort diagnostic, and retains raw input,
stdout/stderr, clean exits and identities. Its empty ordinary parameter query
observes setup order without changing settings. It runs on housekeeping CPUs
and is not a timing sample or a strict DIAG parser check.

These require a fresh output directory and use housekeeping CPUs. Their receipts
bind input fixtures, generated source/data, native source and raw results.
These are native seam checks, not DIAG validation, gameplay or whole-engine
performance qualification. Their correctness collection includes compilation;
it is not an engine timing sample.

`--release` copies the engine's release optimization settings to the external
test crate. Its harness uses panic unwinding; production retains panic abort.
The recorded manifest/profile and build environment distinguish these checks
from both debug tests and production executable measurements.

## CPU/wall development recording

`account_native.py --engine ENGINE --record FRESH.json --known-single-process`
is a transparent supervisor for the released ordinary correctness replays.
Engine launch flags follow those arguments. The native child inherits the
comparator's stdin/stdout/stderr directly, without relaying bytes. The supervisor
uses housekeeping CPUs; the child uses CPU14. Its private placement pipe and
post-exec observation check the child identity, affinity and one native task.
Direct kernel wait4 accounting includes native startup, setup, search,
destruction and a small Python child pre-exec prefix. It excludes the waiting
supervisor and comparator. External bounded supervision remains required.
The declared source must perform work in that one native process; one task
observation is not continuous descendant supervision. Do not use this launcher
with the released main-PID CPU benchmark, which would sample the supervisor.

`compare_ordinary.py --variant NAME=ENGINE ... --case profile-01 --output
evidence/fresh-pilot` uses that supervisor and the unchanged released strict
replay checker. It freezes one warmup per variant followed by four alternating
forward/reverse measured rounds, stops at the first failed run, and retains
native receipts and full comparator output. It is a local balanced pilot,
not the full54 schedule or a performance acceptance decision. Its process,
time, stream and accounting limits are recorded before launch.

Recorder controls:

```sh
python3 -m unittest discover -s tools -p test_account_native.py -v
```

`clock_profile.py` is a diagnostic gprofng launcher that routes collector
messages away from ordinary output and preserves native streams. Initial
controls reported a changed/unreliable timer, including on a separate native
CPU control. Those sampled percentages are not a qualified hotspot profile.
Instruction simulation is also a separate diagnostic and must not be labeled
retired instructions or native cycles.

`measure.py --help` describes the known-single-process, noninteractive recorder.
It pins the child to CPU14 and its recorder to the housekeeping mask. Supply
`--fidelity`, `--semantic-description` and any input/build-record identities.
Use `--dry-run` to inspect a plan before launching a workload.

Its behavior checks, interactive protocol driving, PMU collection and descendant
accounting are unavailable. See
[measurement design](../docs/research/measurement-design.md) for boundaries,
fidelity stages and the retained synthetic validation. Recorder branch controls:

```sh
python3 -m unittest discover -s tools -p test_measure.py -v
```

`archive_build.py evidence/BUILD` packages the exact pre-build source/tool bytes
already retained by `build.py`. It verifies every recorded hash before archiving,
reads the completed archive back, and checks the locally frozen executable
against the build identity. Archives are fresh files with normalized metadata;
the helper neither runs the engine nor invents an external dependency closure.

## Staged compiler PGO

For ordinary `--bin rook2`, `build.py --pgo-generate /absolute/fresh/directory`
adds compiler instrumentation and uses a separate target directory. It never
runs training. `--pgo-use /absolute/merged.profdata --training-record FILE`
uses an immutable profile and completed `rook2-pgo-training-v1` provenance that
must match source, target, base flags and profile hash. Profile/provenance inputs
are rehashed after compilation. The use build enables LLVM missing-function
warnings and retains complete compiler output. Generic, instrumented and PGO
artifacts each have their own identity and evidence; instrumentation timings
are never substituted for production CPU samples.

The intended procedure follows the
[official rustc PGO workflow](https://doc.rust-lang.org/rustc/profile-guided-optimization.html):
use the same source/release/target settings, run real ordinary inputs through
the instrumented artifact, merge profiles with the matching LLVM tool, then
rebuild using that profile and regress the new production artifact. The public54
inputs also trained the approved reference. PGO does not close behavioral,
hardware, uncertainty, or whole-engine performance qualification.

`collect_ordinary.py --engine ENGINE --build-record BUILD/receipt.json --output
evidence/FRESH` freezes the complete54-case stored corpus order, with one
excluded warmup and three measured fresh native lifetimes per case. Every
run uses the unmodified strict replay checker and direct wait4 supervisor.
The manifest freezes deadlines, byte guards, identities and accounting scope;
first failure stops later launches. Before/after local resource snapshots and
all samples are retained. This development collection is reported-only; it
does not claim compatible reference resources, calibration or final uncertainty.


## Complete selected-game CPU recording

`collect_games.py --engine ENGINE --build-record BUILD/receipt.json --output
 evidence/FRESH` follows the stored12-game fixture order. Each complete game
has one excluded warmup followed by three measured fresh-process repetitions.
The unchanged released independent-game runner checks every command/seed,
semantic post, move, result and normal shutdown. The direct wait4 supervisor
accounts actual native CPU separately from the Python launcher identified by
the replay report. An explicit `--game ID` selection is supporting subset work
and cannot establish a complete12 collection.

The preloaded `tap_wire.mjs` adds controller-side listeners to the original
native pipes and taps stdin writes before forwarding the original call. A
private configuration declares the sole exact launch. It retains original
stdin/stdout/stderr before the comparator's assertions, binds stream hashes,
and brackets external go/move observations with native `/proc` CPU ticks.
It does not relay or replace pipes. Zero tick deltas are unresolved and have
no reciprocal CPU rate; no terminal N/R or PMU work is inferred. Point native
identity/placement checks do not establish continuous descendant ownership.

Before launch, the collector records deadlines, caps, inputs, native/build
identity and inherited resource observations. The first failed lifetime stops
the schedule. It retains capped prefixes as invalid, and uses a fixed5s owned
cleanup deadline. Original complete streams are reconciled with released
comparator byte/record counts and normal native/supervisor exits. All timing is
reported-only pending the final resource, observer, uncertainty and calibration
profile. This does not replace focused continuity or full gameplay qualification.

Four retained tap controls are in `evidence/wire-tap-controls-20261018/`. A
separate stubborn-child cleanup control verifies reconciliation within5s.
A balanced full-game observer pilot precedes the first collection; its result
remains separate from the final measurement profile.

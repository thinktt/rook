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
different artifact modes. Neither mode enables PGO. `--jobs N` changes the
default; `--crate PATH` selects another crate.

`--bin rook2-dev` builds the current native development executable and records
its SHA256. The helper never runs the compiled binary or tests.

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

Both require a fresh output directory and use housekeeping CPUs. Their receipts
bind input fixtures, generated source/data, native source and raw results.
These are native seam checks, not DIAG validation, gameplay or whole-engine
performance qualification. Their correctness collection includes compilation;
it is not an engine timing sample.

## CPU/wall development recording

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

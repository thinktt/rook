# Unattended static-glibc own-PGO trial

`run.py` builds an instrumented static-glibc main engine using the pinned Debian
builder, trains it on all54 released standard cases inside Alpine, merges the
54 verified native profiles, and rebuilds using that exact profile. The main
engine uses the existing profiled-only ExtTSP policy. Its non-PGO diagnostic
companion must exactly match the earlier plain static-glibc diagnostic.

It then reuses the previous measurement and reconciliation setup for standard54
(one excluded warmup plus three measured repetitions per case) and one complete
12-game pass. All Alpine processes share CPU14; builds, merging and supervision
use the inherited housekeeping affinity. CPU15 receives no work from this trial.

The supervisor writes atomic stage receipts, enforces stage deadlines and a4GiB
artifact budget, stops on any failure without retry, and cleans up its live
descendants on timeout. It prompts its owning Herdr pane on failure or completion.
There is no per-case notification or requirement for interactive monitoring.
Raw profiles, binaries and measurements remain outside Git. This does not
promote a candidate, transfer artifacts or claim final qualification.

Completed 2026-10-23: all six supervisor stages exited zero. Saved-record
reconciliation checked 228 measurement receipts and 54 training receipts,
artifact/profile/source bindings, reported comparator passes and game raw-stream
hashes. No additional native run was made during this audit.

| Workload | Native CPU | Native wall | Coverage |
|---|---:|---:|---|
| Standard54, sum of per-case medians |67.192095 s|67.553958292 s|216 lifetimes; 54 excluded warmups + 162 measured samples pass|
| Single 12-game pass, sum of lifetimes |676.375347 s|680.527493049 s|632 searches and 5801 posts pass|

These are **reported-only** timings of each native process's whole lifetime,
including setup/exit and a small Python pre-exec prefix. Helper CPU is outside
that total, although all Alpine helpers share CPU14. Context snapshots do not
establish exclusive host ownership; no retired-instruction/cycle data is available.
The game total has one repetition, not a median or uncertainty estimate. Training
used the same 54 cases later measured, so standard54 is not a held-out workload.

Main SHA256: `22ccc29b1fc9bb0981e8ccf98cd61704132e220c496df90be53ddec18bbd2ce1`.
[outcome.json](outcome.json) binds the concise totals to saved receipts under
`/home/legolas/rook2-experiments/static-glibc-pgo-alpine-20261023-01/`.
Against the [earlier plain static-glibc record](../static-glibc-alpine-performance/README.md)
with the same accounting and helper placement, native CPU is descriptively
13.361393% lower for standard54 and 13.475528% lower for games12. These are
separate measurement windows; the build changes include own-PGO and profiled
ExtTSP. This establishes no cross-engine parity, candidate adoption or final
performance/full3288 qualification.

Launch from the repository root with a fresh output path:

```sh
taskset -c 0-5,8-13 python3 experiments/static-glibc-pgo-alpine/run.py \
  --output /home/legolas/rook2-experiments/NEW-STATIC-PGO-RUN \
  --notify-pane "$HERDR_PANE_ID"
```

The setup currently reuses the explicitly named archived Alpine filesystem,
verified vendored crates and standalone upstream compiler from the earlier
builder checks. Full Docker image assembly remains untested. Source and builder
inputs are frozen separately for this run; generated adapters bind the existing
measurement code while changing only admitted build-mode paths and labels.

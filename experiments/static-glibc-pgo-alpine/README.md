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

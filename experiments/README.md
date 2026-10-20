# Experiment setups

See [the short catalog](../docs/performance-experiments.md) for ideas and outcomes,
and [the storage layout](../docs/evidence-layout.md) for full historical evidence.
Existing experiment patches/scripts/plans remain in their historical `evidence/`
paths; recovered variants are under `recovered/`. Large records live outside Git.

Compiled-source snapshots use a deduplicated source-object pool. List a snapshot
prefix, then restore it to a new directory (this does not build or run it):

```sh
python3 tools/restore_experiment_snapshot.py --list
python3 tools/restore_experiment_snapshot.py --prefix 'evidence/current62-generation-safety-census-build-20261020-01/source-before/' --output /tmp/rook2-census-source
```

Archived recipes keep their original source/artifact bindings. Rebind paths
explicitly before reuse and respect their recorded failure/no-retry limits.

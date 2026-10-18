# Shared-evaluation-geometry PGO training

One complete unchanged54-case ordinary replay trained frozen sourceb3b7651.
All cases passed. The54 raw profiles match the replayed process PIDs; driver,
source, profile and all raw hashes are retained/verified, including after the
production pilot. The merged profile can be restored from its lossless gzip
archive. The separate use build consumes that exact profile with matching source
and target/release settings and emits no missing-function warnings.

Training is instrumentation, not CPU/PMU measurement. The sibling production
pilot retains its own native timings and observations. Raw profiles remain
local/ignored; the merged profile, source archives and provenance are retained.

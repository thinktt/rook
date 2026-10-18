# Initial mandatory diagnostic transport

The separate diagnostic artifact
`../diagnostic-build-20261018-first/rook2-diag-exact` has SHA256
`455c002f27f95437e433b5a3a9fdab545aafd5e654ee9cd63d96b6a3f53e4269`.
The unchanged released `conformance/run.mjs` passed 246 cases across the complete
time-schedule, time-allowance, personality-configuration, selective-depth and
output-score fixture files. The last file exercises both score operations.
`conformance.json` is the external protocol result. Unsupported mandatory
operations still fail explicitly; the adapter is not complete.

Build/source receipts and verified adapter source are in the sibling build
folder. Its build helper intentionally does not close external/path dependencies.
The linked native-engine before/after maps agree exactly with
`../attack-codes-build-20261018/receipt.json`'s `source_sha256_before` map; that
folder's verified source archive retains the linked engine bytes. To reconstruct,
extract that archive as the parent crate and the adapter archive into its
`diagnostic/` directory. `diagnostic/Cargo.lock` pins the public registry package
versions and checksums; no registry source or dependency is part of ordinary
production `rook2`.

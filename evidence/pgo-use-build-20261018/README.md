# Staged compiler PGO build

This folder binds one compiler stage, its exact command/environment, executable
and verified source/tool bytes. It is distinct from ordinary generic builds.
`receipt.json` identifies instrumentation versus profile-use and immutable inputs.
The training and merged-profile archive are retained in
`../pgo-training-20261018/`; the production use stage also binds their hashes
before/after compilation. No engine is run by the build helper.

The instrumented executable is for training only. Production use artifact
`3660fecfa0c4a681e6a7152009417199d91706fa9acf0508e073c76427e18438`
passed all54 unchanged public replays and eight wire interruption fixtures.
Its build emitted no LLVM missing-function warnings. CPU measurements belong
to the separate `../pgo-cpu-pilot-20261018/` experiment. Full gameplay and complete
performance acceptance remain open.

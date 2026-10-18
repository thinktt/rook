# Independent legality-generation experiment

Generic x86-64, opt3/thinLTO/codegen1/panic-abort, without PGO. The build receipt
and verified pre-build source/tool archive identify all root-crate inputs.
`rook2-exact` is retained locally and verified against that receipt.
Native tests include old-projection differential checks over10,000 constructed
placements and adversarial joined-domain witnesses. The library and cold binary
unit suites passed (128 +2 tests); exact stdout/stderr is retained here.

All54 unchanged public profiling replays passed; the sibling check directory's
`identity.json` binds the report and build. Correctness runs are not CPU samples.
See `docs/decisions/0002-geometric-legality.md` and the separate four-case balanced
CPU pilot before interpreting this variant's production suitability.

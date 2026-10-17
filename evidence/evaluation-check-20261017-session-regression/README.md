# Release evaluator/root regression after session integration

All 1,352 native evaluation/root cases pass with release optimization settings
on the same engine source as the 193-case session/output check and frozen build.
The original case scope remains documented in
`../evaluation-check-20261017-roots/README.md`.

The external test manifest copies release opt-level, thin LTO, codegen units
and debug settings while using panic unwinding for the harness. Production
retains panic abort. Receipts and the verified test archive bind exact source,
fixtures, generated data, manifest/lock, toolchain/environment and results.
This is regression evidence, not a transport or performance qualification claim.

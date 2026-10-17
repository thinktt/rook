# Frozen source and generic development executable

Generic x86-64 release development executable SHA256:
`4a7a7ef792440cc594949362841e7e332f2899fa30355e028580c218557ad6a2`.
The exact binary remains locally as `rook2-dev-exact`; the original build
receipt records compiler/settings/environment and stable source/tool hashes.
The verified source archive preserves the pre-Cargo bytes. Native suite output
records 122 library and two CLI tests passing.

The 193-case session/output and 1,352-case evaluator/root release test crates use
these same engine source bytes. The development executable exposes its existing
native modes; session checks directly link the actual session model in the
external crate. This binary does not yet provide the live ordinary wire adapter.
No new CPU measurements or speedup claim are attached to this build.

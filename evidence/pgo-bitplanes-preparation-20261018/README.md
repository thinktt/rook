# Persistent bitplane compiler-PGO trial — in progress

The generic matched trial in `../bitplanes-20261018/` independently reconciles
all90 lifetimes: persistent summed medians are2.131794% lower, and this explicit
local supply strategy is0.475616% higher. Both pass133 native tests and54 strict
replays. This supports advancing a candidate, without production adoption.

The successful persistent source is copied to a fresh isolated clone at
`/tmp/imp2-bitplanes-pgo-20261018`. Rustfmt changes only attacks.rs/movegen.rs;
source before/after and the exact origin build are bound in source-preparation.
Root native source remains unchanged. The independent instrumentation build is
under `../pgo-bitplanes-instrumented-build-20261018/`; the planned54-case training
and profile merge are under `../pgo-bitplanes-training-20261018/`.

After the instrumented build actually terminates, freeze/archive its exact
image and verify source identities before training. Retain training failures
and poll the original process handle rather than restarting on observation
timeout. A successful profile-use build requires its own all54 strict replay,
wire interruptions and matched six-case PGO CPU pilot against frozen1dc996b2.
Instrumentation timings are not performance samples. No generic/PGO transfer,
production representation change or full54/12 qualification is claimed yet.

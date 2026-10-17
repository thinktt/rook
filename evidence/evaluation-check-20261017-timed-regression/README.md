# Evaluator/root regression after work-timed integration

All 1,352 external native cases pass on the same source as the work-timed
build and timing checker. The case scope remains the one documented in
`../evaluation-check-20261017-roots/README.md`. This rerun verifies that the
new controller and 4096-node hook preserve existing fixed-iteration behavior.

`receipt.json` binds generated source/data, fixtures, engine sources and
manifest/lock, with before/after stability checks. Exact generated test bytes
are preserved in the compressed verified archive. No full transport,
public-event or whole-engine qualification claim is made.

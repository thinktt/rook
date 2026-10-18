# Complete focused gameplay replay

The unchanged released `conformance/gate-replay/run.mjs` passed all12 focused
games (632 searches) serially against frozen ordinary artifact
`../live-wire-build-20261018-frozen/rook2-exact`:
`da82041f29091ed8db54f2cd2ffd0c338da5ae5216cae3caea6130974573e648`.
`games.json` binds the runner, fixture, artifact and exact command. Search posts
and move/result assertions belong to the released runner.

The unchanged `combine.mjs` combined that report with the same artifact's
`../live-wire-check-20261018-frozen/continuous.json`. Its `combined.json` reports
`completeFocusedReplay=true` and `completeGameplayQualification=false`.
The full3288-game gate remains required. These runs are behavioral evidence;
they are not timed repetitions for performance acceptance.

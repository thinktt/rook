# Diagnostic placement/progress/work/learning routes — preparation and verification

The expanded frozen adapter c4cd8566 passes27 operations/1130 cases and23
adapter unit tests in `../diagnostic-placement-20261018-02/`. This source adds
twelve mandatory routes to the prior15 using existing native APIs, with no
production search/library changes: clock.workSequence, evaluation.activity,
evaluation.boardPatterns, evaluation.centralInfluenceBalance,
evaluation.positionCentralBalance, evaluation.pawnProgress,
evaluation.pawnCandidates, evaluation.pawnCandidateEnding, evaluation.pawnEnding,
search.cutoffMemory, search.rememberedResults and search.orderCandidates.
No fixture IDs/expected-answer lookup or fixture reads enter adapter runtime.

Decimal work counts avoid floating-point conversion and preserve native unsigned
to signed clock-word observation. Position diagnostics use bounded placements;
controlled central samples retain distinct-square and profile bounds. Pawn
candidate membership/uniqueness checks preserve supplied order; path measures
remain independent while absence and promotion-terminal domains are validated.
All math and charge-producing decisions call the existing native library.

Learning events enforce the supplied-candidate component domain without adding
complete chess legality. Initial killer/hint descriptors need not fit a board.
Remembered-result labels map injectively to opaque native identities and groups;
the sixteen-group bound spans the entire request, including clears. Native
policy retains bounds, score-miss distinction, mate mutation and hint endpoints.
This direct component transport does not resolve the separate uncertified-hint
composition question in `docs/research/uncertified-hint-completion.md`.

Preparation ran no native workload while the full12 CPU collection was live.
After original tool handle37105 returned terminal0, the first1022-case attempt
passed21 units and1010 external cases, failing12 unsupported orderCandidates
queries bundled into the cutoff fixture. That failed attempt remains intact.
The added ordering transport and complete108-case ordering file produce a fresh
1130-case run across22 complete fixture files plus the prior25-case selection.

All three preparation archives/metadata remain: v1 for nine new routes, v2 for
eleven and v3 for twelve. `plan-v1.json`/`plan-v2.json` and prior verifiers retain
the historical plans; the current executed `plan.json` remains immutable as an
input record. `prepared-adapter-v3.tar.gz` and `source-preparation-v3.json` bind
the successful source/verifier identity. Compiled source archives and exact
unit/adapter binary hashes are retained separately with each actual attempt.

`run_after_collection.py` refuses overlapping collection/native processes,
freezes and runs the actual compiled test binary, builds/archives the generic
adapter, and invokes the released conformance runner on all declared files.
It records source/dependency identities before and after. Outputs are fresh;
first failure is retained and requires an explicit new attempt label. The
collection's failure or success does not replace its actual terminal/ownership
check. A missing tool handle requires inspection, not a restarted collection.

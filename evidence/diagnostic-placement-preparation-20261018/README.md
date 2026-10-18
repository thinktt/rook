# Diagnostic placement/progress/work routes — unverified source preparation

The last verified adapter remains93293f8d:15 operations/510 cases. This source
prepares nine additional mandatory routes using existing native APIs, with no
production search/library changes: clock.workSequence, evaluation.activity,
evaluation.boardPatterns, evaluation.centralInfluenceBalance,
evaluation.positionCentralBalance, evaluation.pawnProgress,
evaluation.pawnCandidates, evaluation.pawnCandidateEnding and evaluation.pawnEnding.
No fixture IDs/expected-answer lookup or fixture reads enter adapter runtime.

Decimal work counts avoid floating-point conversion and preserve native unsigned
to signed clock-word observation. Position diagnostics use bounded placements;
controlled central samples retain distinct-square and profile bounds. Pawn
candidate membership/uniqueness checks preserve supplied order; path measures
remain independent while absence and promotion-terminal domains are validated.
All math and charge-producing decisions call the existing native library.

The source was formatted but not compiled or tested while the full12 CPU
collection runs. The source archive was read back against every adapter file
hash. `plan.json` binds a planned843-case unchanged external regression across
18 complete fixture files plus the prior25-case phase/identity selection, and
17 adapter unit tests. Those are planned counts, not pass claims.

After the existing collection tool handle37105 is authoritatively terminal,
`run_after_collection.py` refuses overlapping collection/native processes,
freezes and runs the actual compiled test binary, builds/archives the generic
adapter, and invokes the released conformance runner on all declared files.
It records source/dependency identities before and after. Outputs are fresh;
first failure is retained and requires an explicit new attempt label. The
collection's failure or success does not replace its actual terminal/ownership
check. A missing tool handle requires inspection, not a restarted collection.

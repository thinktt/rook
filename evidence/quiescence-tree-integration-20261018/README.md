# Recursive quiescence observation integrated

Current source matches the tested combined88 closure:43 native files,31 adapter
files and23 tool files. Nativefed8a40a passes145 tests,54 strict profiling
replays and eight interruption fixtures/24 searches. Adapter75097e2a passes133
unit tests and6161 unique mandatory cases across88 operations/83 complete files.
All original expected/actual bytes and child exits reconcile independently.
Remaining mandatory inventory is29 operations/1512 cases.

The new `search.quiescenceTree` route calls the actual shared recursive search,
including evaluation stages, child/history restoration, cache lifetime, entry
work, returned scores and PVs. A static observer sends snapshots to a cold sink
outside Search. It adds no fields to Search, Node, retained evaluation or host
state. The frontend keeps supplied and produced admission domains separate.

The reviewed default NoTrace specialization has55 calls and one direct
recursive call with the preceding ABI. No surviving observer arguments,
dispatch, record allocation, evaluator work or wrapper detour was found in
that bounded scope. Its Q body is116 text bytes smaller and its local frame32
bytes larger than85. That stack increase is accepted as a bounded engineering
risk; static inspection does not establish CPU neutrality. Full/fast evaluation
scope and the main ordinary-search body retain their reviewed behavior.

The initial native attempt failed one new terminal-stage test: its synthetic
63-null history reached repetition admission before the intended fast stage.
The corrected copy changes only the test's initial halfmove byte from0 to193;
the63 null increments then wrap it to0. Original source, output and failed
terminal remain preserved. Production code needed no correction.

`integration.json` binds exact source maps, artifacts and dependency receipts.
Parent observed promotion terminate at chunke6b4e3/exit0. This is exact tested
source promotion using named frozen artifacts, without a canonical-path rebuild.
The numeric delta binding preserves previous bounded proof premises and the
unresolved hint-composition domain. No own-PGO, CPU, gameplay or final
qualification result transfers to this source.

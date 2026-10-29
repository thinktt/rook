# Evidence and history layout

The working repository keeps engine/tool history, experiment patches and scripts,
small plans/schemas/build receipts, concise reports and a
[brief ideas/results catalog](performance-experiments.md).
Bulk records are outside Git at `/home/legolas/rook2-experiments`.

- `original-worktree/`: the entire original checkout, including its original
  `.git`, tracked/untracked evidence, binaries and local build products.
- `original-history.git/`: independently verified original-history mirror.
- `migration/`: full relocation/recovery logs, selection lists and audit records.
- `catalogs/`: detailed working catalogs; only the brief summary is in the repo.
- `workspaces/`: previous `/home/legolas/rook2-work` experiment workspaces;
  the old outside-repo path remains a compatibility symlink.

The original HEAD was `18ca16d66dde64c13c6161302ccd3bdf54bd568a`.
All168 original commits remain in the cleaned history; bulk evidence paths were
removed and therefore commit hashes changed. The
[commit map](history-migration/commit-map.tsv) connects original IDs to the current rewritten IDs.
[Verification](history-migration/verification.json) compares every original
non-evidence root tree, author/committer identity and timestamp, and parent edge.
Original commit citations in old records refer to the preserved history.

For a historical path `/home/legolas/rook2/<relative-path>` missing here, look at
`/home/legolas/rook2-experiments/original-worktree/<relative-path>`.
Frozen records retain their original bytes, hashes and absolute paths; their
presence is not permission to rerun a closed experiment or claim new results.
Old scripts may need explicit path rebinding before reuse. They also depend on
the released king-spec, external runtimes, private profiles and sometimes old
temporary paths; the small repository alone is not the full execution closure.
No reference-engine source was introduced by this cleanup.

Additional setup files were recovered from readable existing archives. The
[archive index](../experiments/archive-setup-index.json) records archive hashes
and notes two pre-existing empty archives whose contents could not be recovered;
the original bytes remain preserved. This is not a claim that every historical
recipe can run unchanged on a fresh machine.

Repeated compiled-source snapshots are stored once by content hash in
`experiments/source-objects/`, with paths/modes in
`experiments/source-snapshots.json`. Use `tools/restore_experiment_snapshot.py`
to restore a chosen source prefix to a new directory. Snapshot files and recovered
historical setup code are preserved records, not part of the engine build.

Future raw outputs, binaries, profiles and build products belong in the external
archive. Keep new reproducible setups under `experiments/`, and short outcomes in
the catalog/decision records. Do not add raw case streams or packed checkpoints
to Git. Existing tracked historical `evidence/` summaries remain for navigation;
new `evidence/` material is ignored by default.

The owner subsequently requested Tobias Toland as the primary author and
committer throughout the cleaned history. The
[attribution map](history-migration/attribution-commit-map.tsv) connects the
169 pre-attribution commits to their rewritten IDs. Its
[verification](history-migration/attribution-verification.json) confirms identical
trees, parent relationships and timestamps. Existing Codex trailers were kept;
57 earlier commits received the required co-author/director trailers. This is
local history rewriting; no remote push was performed. Repository-local Git
identity is `Tobias Toland <github@thinktt.e4ward.com>` for future commits.

## 2026-10-29 research closeout

Eleven detached experiment worktrees under `workspaces/` were retired as Git
worktrees. Their complete non-Git contents remain at the original paths as frozen
evidence snapshots, including experimental changes not committed in those old
checkouts. Main and the research checkout remain registered. Git administrative
backups, status/patches and before/after content verification are stored under
`/home/legolas/rook2-experiments/research-closeout-20261029-01/`.
See the [handoff](research/multicore-handoff.md) and
[compact cleanup receipt](../experiments/multicore-feasibility/research-closeout/cleanup.json).
No source, binary, profile or raw receipt was moved or discarded.
